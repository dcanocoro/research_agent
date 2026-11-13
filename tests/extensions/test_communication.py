"""Local communication checks: no providers or remote databases."""
import asyncio
import json
from dataclasses import replace

import pytest

from support import ScriptedClient
from support.bounded import agent, request, response
from support.continuous import make, text, call
from research_agent.contracts import AgentLimits, ContinuousConfig
from research_agent.composition.policies import compose_policy
from research_agent.extensions.communication.configuration import CommunicationConfig
from research_agent.extensions.communication.policy import HookController
from research_agent.extensions.communication.prompts import PERMANENT, REMINDER
from research_agent.extensions.communication.service import PublicationService, snapshot
from research_agent.observability.recording import encoded


def attach(a, mode="hook", client=None, callback=None, max_calls=20):
    a.communication = (CommunicationConfig(mode, max_calls), client, callback)


def query():
    return response(call=("read_file", {"path": "indice.md", "offset": 0, "max_bytes": 1000}))


def updates(a):
    path = a.recorder.current / "comunicacion/publicaciones.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def test_off_preserves_base(tmp_path):
    a = agent(tmp_path, [response()])
    result = asyncio.run(a.run(request()))
    assert result.status == "completed"
    assert not (a.recorder.current / "comunicacion").exists()
    assert "publish_progress" not in str(a.client.requests)
    assert PERMANENT not in a.client.requests[0]["system"]


def test_hook_publishes_last_window_call_and_cleans_up(tmp_path):
    turns = [query() for _ in range(8)] + [response(call=("publish_progress", {
        "message": "He comprobado la información disponible.", "evidence_refs": []})), response()]
    a = agent(tmp_path, turns, AgentLimits(max_llm_calls=20, max_tool_calls=30))
    seen = []
    attach(a, callback=lambda update: seen.append(update))
    result = asyncio.run(a.run(request()))
    assert result.status == "completed"
    active = [i for i, r in enumerate(a.client.requests) if REMINDER in r["system"]]
    assert active == [6, 7, 8]
    assert len(updates(a)) == len(seen) == 1
    assert any(e["event"] == "lab.communication.hook.completed" for e in a.recorder.events)
    assert not any(e["event"] == "lab.communication.hook.expired" for e in a.recorder.events)
    assert REMINDER not in str(a.history) and PERMANENT not in str(a.history)
    assert "publish_progress" not in [s.name for s in a.tools.specs()]
    assert (a.recorder.current / "comunicacion/resumen.json").exists()


def test_failed_publication_expires_and_does_not_reset(tmp_path):
    turns = [query() for _ in range(8)] + [response(call=("publish_progress", {
        "message": "No respaldado", "evidence_refs": ["future"]})), response()]
    a = agent(tmp_path, turns, AgentLimits(max_llm_calls=20, max_tool_calls=30))
    attach(a)
    asyncio.run(a.run(request()))
    assert not updates(a)
    assert any(e["event"] == "lab.communication.hook.expired" for e in a.recorder.events)
    assert not any(e["event"] == "lab.communication.hook.completed" for e in a.recorder.events)


def test_hook_cooldown_and_spontaneous_reset():
    h = HookController()
    h.since_publication = 6
    assert h.before(6)
    h.retire(9)
    assert not h.before(13)
    assert h.before(14)
    h.since_publication = 0
    h.retire(14)
    assert not h.before(20)


def test_hook_expiry_and_reactivation(tmp_path):
    a = agent(tmp_path, [query() for _ in range(16)] + [response()],
              AgentLimits(max_llm_calls=25, max_tool_calls=30))
    attach(a)
    asyncio.run(a.run(request()))
    active = [i for i, r in enumerate(a.client.requests) if REMINDER in r["system"]]
    assert active == [6, 7, 8, 14, 15, 16]
    assert len([e for e in a.recorder.events if e["event"] == "lab.communication.hook.expired"]) == 2


def test_service_reference_cutoff_rate_and_callback_failure(tmp_path):
    a = agent(tmp_path, [])
    compose_policy(a, request())  # initialize recorder
    a.recorder.event("lab.tool.completed", artifact_ref="old")
    cutoff = len(a.recorder.events)
    a.recorder.event("lab.tool.completed", artifact_ref="future")
    def broken(update):
        assert updates(a)[-1]["id"] == update["id"]
        raise RuntimeError("display failed")
    service = PublicationService(a.recorder, "communicator", broken)
    with pytest.raises(ValueError):
        service.publish("Future", ["future"], cutoff)
    service.publish("Confirmed", ["old"], cutoff)
    assert len(updates(a)) == 1
    with pytest.raises(ValueError):
        service.publish("Too soon", [], cutoff)
    service.exchange = 5
    with pytest.raises(ValueError):
        service.publish("Confirmed", [], cutoff)
    assert any(e["event"] == "lab.communication.display_failed" for e in a.recorder.events)


def test_snapshot_bounded_and_frozen(tmp_path):
    a = agent(tmp_path, [])
    compose_policy(a, request())
    for i in range(200):
        a.recorder.event("lab.tool.completed", artifact_ref=f"ref-{i}", tool_name="read", detail="漢" * 600)
    service = PublicationService(a.recorder, "communicator")
    view = snapshot(service, "Pregunta" * 10000, "research")
    frozen = encoded(view)
    a.recorder.event("lab.tool.completed", artifact_ref="future", tool_name="read")
    assert encoded(view) == frozen and b"future" not in frozen
    assert len(frozen) < 32768 and view["omitted_events"] > 0 and view["request_truncated"]
    medium = snapshot(service, "x" * 20000, "research")
    assert medium["request"] == "x" * 20000 and not medium["request_truncated"]


def test_live_communicator_publishes_without_changing_investigator(tmp_path):
    a = agent(tmp_path, [query() for _ in range(8)] + [response()],
              AgentLimits(max_llm_calls=20, max_tool_calls=30))
    observer = ScriptedClient([text(json.dumps({"publish": True, "message": "He revisado los datos disponibles.", "evidence_refs": []}))])
    attach(a, "communicator", observer)
    a.workspace.write_file("indice.md", "Dato confirmado: periodo 2025.")
    before = a.workspace.snapshot()
    result = asyncio.run(a.run(request()))
    assert result.llm_calls == 9 and result.tool_calls == 8
    assert a.workspace.snapshot() == before
    assert len(updates(a)) == 1 and len(observer.requests) == 1
    assert not observer.requests[0]["tools"] and observer.requests[0]["allow_tools"] is False
    assert "publish_progress" not in str(a.client.requests)
    assert PERMANENT not in str(a.client.requests)
    assert "He revisado" not in str(a.history)
    view = json.loads(observer.requests[0]["input_items"][0].content)
    assert any("Dato confirmado" in str(item.get("result")) for item in view["activity"])
    summary = json.loads((a.recorder.current / "comunicacion/resumen.json").read_bytes())
    assert summary["llm_calls"] == 1 and summary["input_tokens"] is None


def test_slow_communicator_cancelled_without_blocking(tmp_path):
    class Slow:
        cancelled = False
        async def respond(self, **kwargs):
            try:
                await asyncio.Event().wait()
            finally:
                self.cancelled = True
    a = agent(tmp_path, [query() for _ in range(15)] + [response()],
              AgentLimits(max_llm_calls=25, max_tool_calls=30))
    observer = Slow()
    attach(a, "communicator", observer)
    async def run():
        return await asyncio.wait_for(a.run(request()), 5)
    result = asyncio.run(run())
    assert result.status == "completed" and observer.cancelled
    assert not updates(a)
    assert json.loads((a.recorder.current / "comunicacion/resumen.json").read_bytes())["llm_calls"] == 1


def test_communicator_budget_and_invalid_decisions(tmp_path):
    a = agent(tmp_path, [query() for _ in range(19)] + [response()],
              AgentLimits(max_llm_calls=30, max_tool_calls=30))
    observer = ScriptedClient([text('{"publish": "yes"}')])
    attach(a, "communicator", observer, max_calls=1)
    result = asyncio.run(a.run(request()))
    assert result.status == "completed" and len(observer.requests) == 1
    assert not updates(a)
    summary = json.loads((a.recorder.current / "comunicacion/resumen.json").read_bytes())
    assert summary["errors"] == summary["llm_calls"] == 1


def test_continuous_hook_excludes_auxiliary_calls_and_closing(tmp_path):
    a, req = make(tmp_path, [text() for _ in range(15)], config=ContinuousConfig(max_llm_calls=15))
    attach(a)
    result = asyncio.run(a.run(req))
    assert result.status != "failed"
    assert REMINDER not in str(a.history)
    assert all(REMINDER not in r["system"] for r in a.client.requests if not r["allow_tools"])
    assert len(a.client.review_requests) > 0


@pytest.mark.parametrize("continuous", [False, True])
@pytest.mark.parametrize("mode", ["hook", "communicator"])
def test_progress_composition_keeps_evaluators_isolated(tmp_path, continuous, mode):
    from support.progress import Client, objective
    from research_agent.contracts import AgentRequest
    if continuous:
        a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=12))
        req = replace(req, objective=objective(), progress_step_calls=1)
    else:
        a = agent(tmp_path, [], AgentLimits(max_llm_calls=12))
        req = AgentRequest("Explain", "w", "c", objective=objective(), progress_step_calls=1)
    a.client = Client()
    observer = ScriptedClient([])
    attach(a, mode, observer)
    result = asyncio.run(a.run(req))
    assert result.status == "completed" and result.stop_reason == "objective_sufficient"
    assert not observer.requests
    assert all(REMINDER not in r["system"] and PERMANENT not in r["system"]
               for r in a.client.requests if not r["allow_tools"])


def test_failed_persistence_is_not_publication(tmp_path, monkeypatch):
    import research_agent.extensions.communication.service as module
    a = agent(tmp_path, [])
    compose_policy(a, request())
    service = PublicationService(a.recorder, "hook")
    def fail(*args):
        raise OSError("disk")
    monkeypatch.setattr(module, "atomic_bytes", fail)
    with pytest.raises(OSError):
        service.publish("Intento", [], len(a.recorder.events))
    assert not service.updates and not updates(a) and service.last_exchange == -5


def test_runs_do_not_share_publication_state(tmp_path):
    publish = response(call=("publish_progress", {"message": "Voy a revisar los datos.", "evidence_refs": []}))
    a = agent(tmp_path, [publish, response(), publish, response()])
    attach(a)
    first = asyncio.run(a.run(request()))
    first_path = a.recorder.current
    second = asyncio.run(a.run(request()))
    assert len(updates(a)) == 1 and updates(a)[0]["run_id"] == second.run_id
    assert first.run_id != second.run_id
    assert json.loads((first_path / "comunicacion/publicaciones.jsonl").read_text())["run_id"] == first.run_id


def test_stale_phase_and_pending_snapshot_coalescing(tmp_path):
    async def run():
        a = agent(tmp_path, [])
        gate = asyncio.Event()
        started = asyncio.Event()
        class Observer:
            views = []
            async def respond(self, **kwargs):
                self.views.append(json.loads(kwargs["input_items"][0].content))
                started.set()
                await gate.wait()
                return text(json.dumps({"publish": True, "message": "Avance.", "evidence_refs": []}))
        observer = Observer()
        attach(a, "communicator", observer)
        policy = compose_policy(a, request())
        await policy.prepare()
        for _ in range(6):
            policy.complete_exchange()
        await asyncio.wait_for(started.wait(), 2)
        for _ in range(12):
            policy.complete_exchange()
        assert policy.pending["exchange"] == 18 and len(observer.views) == 1
        policy.phase_generation += 1
        gate.set()
        await policy.task
        assert [v["exchange"] for v in observer.views] == [6, 18]
        assert not updates(a)
        assert len([e for e in a.recorder.events if e["event"] == "lab.communication.discarded"]) == 2
        await policy.finalize(None)
    asyncio.run(run())


def test_cancellation_unregisters_hook_and_finalizes_before_terminal(tmp_path):
    a = agent(tmp_path, [asyncio.CancelledError()])
    attach(a)
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(a.run(request()))
    assert "publish_progress" not in [s.name for s in a.tools.specs()]
    assert (a.recorder.current / "comunicacion/resumen.json").exists()
    assert json.loads((a.recorder.current / "resultado.json").read_bytes())["status"] == "cancelled"


def test_observable_tokens_and_trace_identity_are_separate(tmp_path):
    import logging
    from runtime_contracts.execution import current_run_context
    class Observer:
        async def respond(self, **kwargs):
            assert current_run_context().component == "communicator"
            logging.getLogger("ingestion_service.llm_trace").info("usage", extra={"json_fields": {
                "event": "engine.llm_call", "input_tokens": 10, "output_tokens": 3}})
            return text(json.dumps({"publish": False, "message": None, "evidence_refs": []}))
    a = agent(tmp_path, [query() for _ in range(7)] + [response()], AgentLimits(max_llm_calls=20))
    attach(a, "communicator", Observer())
    result = asyncio.run(a.run(request()))
    summary = json.loads((a.recorder.current / "comunicacion/resumen.json").read_bytes())
    assert summary["input_tokens"] == 10 and summary["output_tokens"] == 3
    trace = a.recorder.current / "comunicacion/trazas-0001/events.jsonl"
    usage = json.loads(trace.read_text())
    assert usage["run_id"].startswith(result.run_id + ":communication:")
    parent = a.recorder.current / "trazas/events.jsonl"
    assert not parent.exists() or "communication:" not in parent.read_text()


def test_hook_counts_final_request_size(tmp_path):
    a = agent(tmp_path, [response()])
    attach(a)
    async def run():
        policy = compose_policy(a, request())
        await policy.prepare()
        a.limits = replace(a.limits, max_context_bytes=1024)
        # Exercise the decorator check, independently of the base policy's own check.
        from research_agent.core.execution import ModelCall
        from research_agent.core.context_budget import ContextConfigurationError
        with pytest.raises(ContextConfigurationError):
            policy.check_size(ModelCall("x" * 900 + PERMANENT + REMINDER, [], [], 1))
        await policy.finalize(None)
    asyncio.run(run())


def test_research_can_end_with_active_hook(tmp_path):
    a = agent(tmp_path, [query() for _ in range(7)] + [response()], AgentLimits(max_llm_calls=20))
    attach(a)
    result = asyncio.run(a.run(request()))
    assert result.status == "completed"
    assert any(e["event"] == "lab.communication.hook.cancelled" for e in a.recorder.events)
    assert not updates(a)


def test_renewal_does_not_accumulate_instructions(tmp_path):
    a, req = make(tmp_path, [text("avance " * 700) for _ in range(25)],
        config=ContinuousConfig(max_llm_calls=20, general_review=False,
                                max_context_bytes=200000, consolidation_threshold_bytes=50000))
    attach(a)
    result = asyncio.run(a.run(req))
    assert result.status != "failed"
    assert any(e["event"] == "lab.intervention.applied" and e.get("kind") == "renew" for e in a.recorder.events)
    assert REMINDER not in str(a.history)
    assert all(r["system"].count(REMINDER) <= 1 for r in a.client.requests)


@pytest.mark.parametrize("mode", ["off", "hook", "communicator"])
def test_cli_selects_mode_and_displays_only_confirmed_updates(tmp_path, monkeypatch, capsys, mode):
    from contextlib import asynccontextmanager
    from research_agent.agent import AgentA
    from research_agent.observability.recording import RunRecorder
    from research_agent.core.tools import ToolRegistry
    from research_agent.storage.workspace import Workspace
    from research_agent.capabilities.state.files import register_files
    from research_agent.cli.main import main
    options = []
    @asynccontextmanager
    async def build(workspace, runs, limits, **kwargs):
        options.append(kwargs)
        recorder = RunRecorder(runs, experiment=kwargs["experiment"], run_name=kwargs["run_name"])
        space = Workspace(workspace)
        registry = ToolRegistry(recorder)
        register_files(registry, space)
        if mode == "hook":
            turns = [response(call=("publish_progress", {"message": "Actualización confirmada.", "evidence_refs": []})), response()]
        else:
            turns = [query() for _ in range(7)] + [response()]
        a = AgentA(ScriptedClient(turns), registry, space, recorder, limits)
        if mode != "off":
            observer = ScriptedClient([text(json.dumps({"publish": True,
                "message": "Actualización confirmada.", "evidence_refs": []}))])
            a.communication = (kwargs["communication"], observer, kwargs["on_progress"])
        yield a
    monkeypatch.setattr("research_agent.cli.main.build_agent", build)
    assert main(["Investiga", "--new", "--run-name", "inicial", "--output", str(tmp_path / "out"),
                 "--communication", mode]) == 0
    captured = capsys.readouterr()
    assert ("Actualización confirmada." in captured.err) == (mode != "off")
    assert "Actualización confirmada." not in captured.out
    assert ("communication" in options[0]) == (mode != "off")


@pytest.mark.parametrize("mode", ["off", "hook", "communicator"])
def test_build_creates_distinct_client_only_for_communicator(tmp_path, monkeypatch, mode):
    from infra.llm_factory import LLMFactory
    from research_agent.composition.build import build_agent
    profiles = []
    clients = {}
    def conversation(factory, profile):
        profiles.append(profile)
        # Match the real factory's profile-keyed cache.
        if profile not in clients:
            clients[profile] = ScriptedClient([])
        return clients[profile]
    monkeypatch.setattr(LLMFactory, "conversation", conversation)
    async def run():
        async with build_agent(tmp_path / "state", tmp_path / "runs",
                               communication=CommunicationConfig(mode)) as a:
            if mode == "off":
                assert not hasattr(a, "communication")
            else:
                assert (a.communication[1] is not None) == (mode == "communicator")
                if mode == "communicator":
                    assert a.communication[1] is not a.client
    asyncio.run(run())
    assert len(profiles) == (2 if mode == "communicator" else 1)
    if mode == "communicator":
        assert profiles[0].model == profiles[1].model
        assert replace(profiles[0], name=profiles[1].name) == profiles[1]


@pytest.mark.parametrize("argv", [
    ["--communication", "hook", "--communication-max-calls", "2"],
    ["--communication-timeout-seconds", "2"],
    ["--communication", "communicator", "--communication-max-calls", "0"],
    ["--communication", "communicator", "--communication-timeout-seconds", "nan"],
])
def test_cli_rejects_invalid_options_before_clients(argv):
    from research_agent.cli.main import main
    with pytest.raises(SystemExit) as exc:
        main(["question", "--new", "--output", "unused", *argv])
    assert exc.value.code == 2
