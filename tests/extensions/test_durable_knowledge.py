"""Durable B, E2 budget protection and crash recovery without external services."""
import asyncio
import hashlib
import json
from dataclasses import replace

import pytest

from research_agent.contracts import ContinuousConfig
from research_agent.extensions.knowledge_agent.delegation import attach
from research_agent.extensions.knowledge_agent.delegation import mode_for
from research_agent.extensions.knowledge_agent.delegation import TaskStore
from research_agent.experiments.store import prepare_experiment
from research_agent.regimes.continuous.control import RuntimeState
from research_agent.observability.recording import encoded
from support import ScriptedClient, save_arguments
from support.continuous import make, call, text, execute
from support.knowledge import payload, finish, writer, service










def test_store_precedes_child_and_reports_verified_integration(tmp_path):
    agent, _, clients = service(tmp_path, [writer(), finish()])
    integration = agent.knowledge
    original = integration.client_factory

    def factory():
        task = integration.store.get("advance1")
        assert task["status"] == "pending" and task["attempts"][-1]["status"] == "running"
        return original()

    integration.client_factory = factory
    result = asyncio.run(integration.register(**payload()))
    assert result["status"] == "integrated" and result["semantic_validity_assessed"] is False
    assert agent.workspace.path("nota.md").read_text() == "Avance"
    assert integration.used == 2
    assert len(clients[0].requests) == 2
    names = {t.name for t in clients[0].requests[0]["tools"]}
    assert {"finish_integration", "read_integration_task", "record_research_advance"} <= names
    assert not names & {"integrate_knowledge", "search_web", "calculate", "run_python"}
    assert integration.state.declarations[-1]["source"] == "knowledge_agent"
    assert not integration.state.declarations[-1]["semantic_validity_assessed"]


def test_no_resources_is_durable_and_duplicate_is_idempotent(tmp_path):
    agent, request, clients = service(tmp_path, [writer(), finish()])
    k = agent.knowledge
    k.available = lambda: {"calls": 5, "tools": 200, "seconds": None}
    result = asyncio.run(k.register(**payload()))
    assert result["status"] == "pending" and result["reason"] == "resources"
    assert clients == []
    same = asyncio.run(k.register(**payload()))
    assert same["task_id"] == result["task_id"] and same["attempts"] == 0
    with pytest.raises(ValueError, match="different content"):
        asyncio.run(k.register(**payload(finding="Otro avance")))
    # Renewal does not discard the queue; an activation receives a new reserved budget.
    agent._prepare(request, "activation2", "interaction2")
    k.begin(request, RuntimeState())
    k.available = lambda: {"calls": 100, "tools": 200, "seconds": None}
    asyncio.run(k.drain())
    assert k.store.get("advance1")["status"] == "integrated"


@pytest.mark.parametrize("budget", [{"calls": 14, "tools": 200, "seconds": None},
                                  {"calls": 100, "tools": 23, "seconds": None},
                                  {"calls": 100, "tools": 200, "seconds": 180}])
def test_never_starts_without_full_reservation(tmp_path, budget):
    agent, _, clients = service(tmp_path)
    agent.knowledge.available = lambda: budget
    asyncio.run(agent.knowledge.register(**payload()))
    assert clients == []


def test_store_failure_never_constructs_child(tmp_path, monkeypatch):
    agent, _, clients = service(tmp_path)
    monkeypatch.setattr(agent.knowledge.store, "save", lambda value: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(OSError):
        asyncio.run(agent.knowledge.register(**payload()))
    assert clients == []


def test_invalid_paths_and_references_do_not_register(tmp_path):
    agent, _, _ = service(tmp_path)
    for data in [payload(scope=["../outside"]), payload(evidence_refs=["nota.md"]),
                 payload(evidence_refs=["archivo/no/missing.json"]), payload(task_id="../bad")]:
        with pytest.raises((ValueError, OSError)):
            asyncio.run(agent.knowledge.register(**data))
    assert agent.knowledge.store.tasks() == []


def test_pending_evidence_requires_explicit_retry(tmp_path):
    agent, _, clients = service(tmp_path, [finish("pending", documents=[], pending_reason="evidence",
                                              unresolved=["Falta fuente primaria"])])
    k = agent.knowledge
    asyncio.run(k.register(**payload()))
    assert k.store.get("advance1")["reason"] == "evidence"
    asyncio.run(k.drain())
    assert len(clients) == 1
    k.client_factory = lambda: ScriptedClient([writer(), finish()])
    result = asyncio.run(k.retry("advance1"))
    assert result["status"] == "integrated" and result["attempts"] == 2


def test_no_changes_has_versions_and_no_writes(tmp_path):
    agent, _, _ = service(tmp_path, [finish("no_changes")])
    agent.workspace.write_file("nota.md", "Avance")
    result = asyncio.run(agent.knowledge.register(**payload()))
    assert result["status"] == "no_changes"
    assert agent.tools.files_written == []


def test_partial_write_cancel_then_reconcile_without_duplicate_write(tmp_path):
    agent, request, _ = service(tmp_path, [writer(), asyncio.CancelledError()])
    k = agent.knowledge
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(k.register(**payload()))
    assert agent.workspace.path("nota.md").read_text() == "Avance"
    assert k.store.get("advance1")["attempts"][-1]["status"] == "running"
    agent._prepare(request, "activation2", "interaction2")
    k.begin(request, RuntimeState())
    assert k.store.get("advance1")["reason"] == "recovery"
    k.client_factory = lambda: ScriptedClient([finish()])
    asyncio.run(k.drain())
    assert k.store.get("advance1")["status"] == "integrated"
    assert len(list((agent.recorder.root / "transacciones").glob("*.json"))) == 1


def test_publication_before_result_store_failure_is_recoverable(tmp_path, monkeypatch):
    agent, request, _ = service(tmp_path, [writer(), finish()])
    k = agent.knowledge
    original = k.store.save

    def fail_after_declaration(task):
        if task["status"] == "integrated":
            raise OSError("result publication failed")
        original(task)

    monkeypatch.setattr(k.store, "save", fail_after_declaration)
    with pytest.raises(OSError):
        asyncio.run(k.register(**payload()))
    agent._prepare(request, "activation2", "interaction2")
    k.begin(request, RuntimeState())
    task = k.store.get("advance1")
    assert task["status"] == "integrated" and task["result"]["documents"]


def test_namespaces_isolate_workspace_and_mandate(tmp_path):
    agent, request, _ = service(tmp_path)
    k = agent.knowledge
    k.available = lambda: {}
    asyncio.run(k.register(**payload()))
    original = k.store
    k.begin(replace(request, mandate="Otro mandato"), RuntimeState())
    assert k.store.tasks() == [] and len(original.tasks()) == 1
    other = TaskStore(original.root.parent, type(agent.workspace)(tmp_path / "different"), request.mandate)
    assert other.tasks() == []


def test_packet_boundaries_missing_sections_and_original_evidence(tmp_path):
    agent, _, _ = service(tmp_path)
    k = agent.knowledge
    k.available = lambda: {}
    ref = agent.recorder.artifact({"source": "x" * 4000})
    agent.workspace.write_file("nota.md", "# H1 Fundamento\n" + "x" * 10000)
    asyncio.run(k.register(**payload(evidence_refs=[ref],
                affected_documents=[{"path": "nota.md", "section_id": "H1"}])))
    packet = k.packet(k.store.get("advance1"))
    assert len(encoded(packet)) <= 65536 and packet["partial"]
    assert any(v.get("exists") is False for v in packet["views"])
    assert any(v.get("kind") == "evidence" and v.get("next_offset") for v in packet["views"])
    assert packet["handoff"]["interpretation"] == payload()["interpretation"]


@pytest.mark.parametrize(("total", "research"), [(60, 42), (70, 49), (100, 70)])
def test_full_e2_budget_counts_children_and_protects_reserve(tmp_path, total, research):
    agent, request = make(tmp_path, [call("integrate_knowledge", **payload()), *[text()] * 100],
                          config=ContinuousConfig(max_llm_calls=total, max_tool_calls=200))
    attach(agent, lambda: ScriptedClient([writer(), finish()]), "prepared")
    result = execute(agent, request)
    assert result.error is None and result.stop_reason == "call_limit"
    assert result.llm_calls == sum(result.llm_calls_by_phase.values()) <= total
    assert result.llm_calls_by_role == {"A": research, "B": 2}
    assert result.llm_calls == research + 2  # Unused B reserve is not transferred to A.
    assert result.llm_calls_by_phase["integration"] == 2
    assert result.state.files_written == ("nota.md",)
    assert any("knowledge_tasks" in str(r["input_items"]) for r in agent.client.requests[1:])


def test_mode_is_frozen_and_b_instructions_excluded_from_a(tmp_path):
    root = tmp_path / "experiment"
    prompts = prepare_experiment(root, new=True, knowledge_agent="prepared")
    assert mode_for(root) == "prepared"
    assert not {"agente-conocimiento.md", "delegacion-conocimiento.md"} & {p.name for p in prompts}
    with pytest.raises(ValueError, match="frozen"):
        prepare_experiment(root, new=False, knowledge_agent="off")


def test_checkpoint_does_not_shrink_child_budget(tmp_path):
    from research_agent.core.context_budget import ByteCounter
    from research_agent.regimes.continuous.policy import POLICY
    from research_agent.regimes.continuous.policy import context_seed
    from research_agent.regimes.continuous.control import INSTRUCTION
    from importlib.resources import files

    class AtCheckpoint(ScriptedClient):
        delegated = False

        async def respond(self, **kwargs):
            if not self.delegated and "Context renewal approaching" in str(kwargs["input_items"]):
                self.delegated = True
                self.requests.append(kwargs)
                return call("integrate_knowledge", **payload())
            return await super().respond(**kwargs)

    agent, request = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=100, max_tool_calls=200))
    agent.client = AtCheckpoint([text("x" * 30000), *[text()] * 100])
    attach(agent, lambda: ScriptedClient([writer(), finish()]), "prepared")
    system = "\n\n".join(files("research_agent").joinpath(n).read_text(encoding="utf-8")
                         for n in ("instructions/agent.md", "capabilities/state/instructions.md", "extensions/deliberation/instructions.md", "extensions/knowledge_agent/prompts/delegation.md"))
    size = ByteCounter().measure(system + POLICY + INSTRUCTION, context_seed(agent, request, "initial"), agent.tools.specs(), 128)
    request = replace(request, continuous=replace(request.continuous,
                      consolidation_threshold_bytes=size["budgeted_bytes"] + 12000))
    result = execute(agent, request)
    assert result.error is None and result.llm_calls <= 100
    task = agent.knowledge.store.get("advance1")
    assert task["status"] == "integrated"
    manifest = next(agent.recorder.current.glob("integraciones/*/manifiesto.json"))
    assert json.loads(manifest.read_bytes())["limits"]["max_llm_calls"] == 15


def test_full_reserve_is_globally_charged_and_third_task_survives(tmp_path):
    agenda = "Investigar la pregunta pendiente."
    turns = [call("integrate_knowledge", **payload("advance" + str(i))) for i in range(3)]
    agent, request = make(tmp_path, [*turns, *[text()] * 100],
                          config=ContinuousConfig(max_llm_calls=100, max_tool_calls=200))
    child_turns = [*[call("list_files", path=".")] * 14,
                   finish("no_changes", path="agenda.md", content=agenda)]
    attach(agent, lambda: ScriptedClient(child_turns), "prepared")
    result = execute(agent, request)
    assert result.error is None
    assert result.llm_calls == 100 and result.llm_calls_by_role == {"A": 70, "B": 30}
    assert result.llm_calls == sum(result.llm_calls_by_phase.values())
    tasks = agent.knowledge.store.tasks()
    assert [t["status"] for t in tasks] == ["no_changes"] * 2 + ["pending"]
    assert tasks[-1]["reason"] == "resources" and tasks[-1]["attempts"] == []


def test_scope_rejects_entire_batch_and_original_materials(tmp_path):
    changes = save_arguments(path="nota.md", content="Avance")
    changes["changes"].extend(save_arguments(path="fuera.md", content="Fuera")["changes"])
    agent, _, _ = service(tmp_path, [call("record_research_advance", **changes),
                         finish("pending", documents=[], pending_reason="conflict", unresolved=["Ámbito"] )])
    result = asyncio.run(agent.knowledge.register(**payload()))
    assert result["status"] == "pending" and result["reason"] == "conflict"
    assert not agent.workspace.path("nota.md").exists()
    with pytest.raises(ValueError, match="read-only"):
        asyncio.run(agent.knowledge.register(**payload("source", scope=["materiales/"],
                    affected_documents=[{"path": "materiales/source.json", "section_id": None}])))


def test_no_false_integration_without_receipts_or_with_stale_versions(tmp_path):
    agent, _, _ = service(tmp_path)
    k = agent.knowledge
    k.available = lambda: {}
    asyncio.run(k.register(**payload()))
    task = k.store.get("advance1")
    outcome = finish().function_call.arguments
    with pytest.raises(ValueError, match="confirmed changes"):
        k.validate_outcome(task, outcome, [])
    agent.workspace.write_file("nota.md", "Versión diferente")
    with pytest.raises(ValueError, match="version_conflict"):
        k.validate_outcome(task, dict(outcome), [{"path": "nota.md"}])


def test_child_capture_error_preserves_receipts(tmp_path, monkeypatch):
    from research_agent.extensions.knowledge_agent.delegation import ChildRecorder
    original = ChildRecorder.artifact

    def broken(self, value):
        if isinstance(value, dict) and value.get("operation") == "record_research_advance":
            raise OSError("capture unavailable")
        return original(self, value)

    monkeypatch.setattr(ChildRecorder, "artifact", broken)
    agent, _, _ = service(tmp_path, [writer(), finish()])
    result = asyncio.run(agent.knowledge.register(**payload()))
    assert result["status"] == "integrated"
    assert agent.knowledge.confirmed(agent.knowledge.store.get("advance1"))
    assert agent.recorder.capture_errors


def test_child_time_is_independent_of_a_operation_limit(tmp_path):
    from research_agent.contracts import AgentLimits

    class SlowerThanA(ScriptedClient):
        async def respond(self, **kwargs):
            if not self.requests:
                await asyncio.sleep(1.2)
            return await super().respond(**kwargs)

    agent, request = make(tmp_path, [call("integrate_knowledge", **payload()), *[text()] * 100],
                          config=ContinuousConfig(max_llm_calls=100, max_tool_calls=200))
    agent.limits = AgentLimits(timeout_seconds=1, finalization_seconds=.2)
    attach(agent, lambda: SlowerThanA([writer(), finish()]), "prepared")
    result = execute(agent, request)
    assert result.error is None
    assert agent.knowledge.store.get("advance1")["status"] == "integrated"


def test_recovery_preserves_evidence_blocker_after_result_failure(tmp_path, monkeypatch):
    agent, request, clients = service(tmp_path, [finish("pending", documents=[], pending_reason="evidence",
                                                       unresolved=["Fuente no recuperada"])])
    k = agent.knowledge
    original = k.store.save

    def fail(task):
        if task["reason"] == "evidence":
            raise OSError("publication failed")
        original(task)

    monkeypatch.setattr(k.store, "save", fail)
    with pytest.raises(OSError):
        asyncio.run(k.register(**payload()))
    agent._prepare(request, "activation2", "interaction2")
    k.begin(request, RuntimeState())
    assert k.store.get("advance1")["reason"] == "evidence"
    asyncio.run(k.drain())
    assert len(clients) == 1


def test_unresolved_version_conflict_does_not_auto_retry(tmp_path):
    stale = {"changes": [{"path": "nota.md", "action": "edit", "content": None,
                         "expected_sha256": "0" * 64,
                         "operations": [{"kind": "replace", "target": "Viejo", "content": "Nuevo"}]}],
             "reason": "Actualizar", "source_refs": []}
    agent, request, clients = service(tmp_path, [call("record_research_advance", **stale)] * 15)
    agent.workspace.write_file("nota.md", "Viejo")
    k = agent.knowledge
    result = asyncio.run(k.register(**payload()))
    assert result["reason"] == "conflict"
    agent._prepare(request, "activation2", "interaction2")
    k.begin(request, RuntimeState())
    asyncio.run(k.drain())
    assert len(clients) == 1


def test_unprepared_mode_is_not_available(tmp_path):
    with pytest.raises(ValueError):
        mode_for(None, "protected")
    with pytest.raises(ValueError):
        prepare_experiment(tmp_path / "rejected", new=True, knowledge_agent="protected")
    assert not (tmp_path / "rejected").exists()


def test_b_closes_with_write_and_pending_after_ordinary_budget(tmp_path):
    turns = [call("list_files", path=".")] * 11 + [writer(), finish(
        "pending", pending_reason="evidence", unresolved=["Comparación sin evidencia suficiente"])]
    agent, _, clients = service(tmp_path, turns)
    result = asyncio.run(agent.knowledge.register(**payload()))
    assert result["status"] == "pending" and result["reason"] == "evidence"
    assert result["result"]["documents"] and agent.workspace.path("nota.md").exists()
    closing = clients[0].requests[11]
    assert "Runtime integration closing" in str(closing["input_items"])
    assert closing["allow_tools"]
    assert agent.knowledge.used == 13


def test_plain_response_requires_declaration(tmp_path):
    agent, _, clients = service(tmp_path, [text("He terminado"), finish(
        "pending", documents=[], pending_reason="evidence", unresolved=["Falta evidencia"])])
    result = asyncio.run(agent.knowledge.register(**payload()))
    assert result["status"] == "pending" and result["attempts"] == 1
    assert len(clients[0].requests) == 2


def test_pending_must_reconcile_all_published_versions(tmp_path):
    agent, _, _ = service(tmp_path, [writer(), finish("pending", documents=[],
        pending_reason="evidence", unresolved=["Falta contraste"]), finish(
        "pending", pending_reason="evidence", unresolved=["Falta contraste"])])
    result = asyncio.run(agent.knowledge.register(**payload()))
    assert result["status"] == "pending" and agent.knowledge.used == 3
    assert result["result"]["documents"][0]["path"] == "nota.md"


def test_packet_recovers_recent_a_actions_and_previous_declaration(tmp_path):
    from runtime_contracts.llm import ConversationMessage
    agent, _, _ = service(tmp_path)
    k = agent.knowledge
    k.available = lambda: {}
    agent.history.extend([ConversationMessage("assistant", "old" * 6000),
                          ConversationMessage("assistant", "Comparación ADBE pendiente")])
    asyncio.run(k.register(**payload()))
    task = k.store.get("advance1")
    task["attempts"].append({"status": "interrupted", "declaration": {"unresolved": ["Contrastar MSFT"]}})
    packet = k.packet(task)
    view = next(v for v in packet["views"] if v["kind"] == "A_history")
    assert view["partial"] and "Comparación ADBE" in str(view["items"])
    ref = view["recovery"]["reference"]
    assert "oldold" in agent.recorder.read_artifact(ref)["text"]
    assert packet["prior_attempts"][0]["declaration"]["unresolved"] == ["Contrastar MSFT"]


def test_b_ordinary_timeout_preserves_closing_time(tmp_path, monkeypatch):
    import research_agent.extensions.knowledge_agent.delegation as module
    monkeypatch.setattr(module, "LIMITS", replace(module.LIMITS, timeout_seconds=1, finalization_seconds=.4))
    agent, _, _ = service(tmp_path)

    class SlowOrdinary(ScriptedClient):
        first = True

        async def respond(self, **kwargs):
            if self.first:
                self.first = False
                await asyncio.sleep(.8)
            return await super().respond(**kwargs)

    client = SlowOrdinary([finish("pending", documents=[], pending_reason="resources",
                                 unresolved=["Lectura interrumpida"] )])
    agent.knowledge.client_factory = lambda: client
    result = asyncio.run(agent.knowledge.register(**payload()))
    assert result["status"] == "pending" and result["result"]["unresolved"]
    assert agent.knowledge.used == 2


def test_last_opportunity_only_allows_declaration(tmp_path):
    agent, _, clients = service(tmp_path, [call("list_files", path=".")] * 14 + [finish(
        "pending", documents=[], pending_reason="resources", unresolved=["Trabajo sin completar"])])
    result = asyncio.run(agent.knowledge.register(**payload()))
    assert result["status"] == "pending" and agent.knowledge.used == 15
    assert {t.name for t in clients[0].requests[-1]["tools"]} == {"finish_integration"}
    assert clients[0].requests[-1]["allow_tools"]

