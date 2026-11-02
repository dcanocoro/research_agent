"""E2 contracts and interventions exercised without external services."""
import asyncio
from dataclasses import replace
import json

import pytest
from runtime_contracts.llm import ToolResult

from research_agent.context_management import reconstruct
from research_agent.context_budget import ContextConfigurationError
from research_agent.runtime_control import (RuntimeState, evaluation_policy, reconciliation_policy,
    register_report, recover_state, validate_runtime)
from research_agent.experiments import prepare_experiment
from test_continuous import make, execute, text, call, events
from support import ScriptedClient, save_turn, save_current


def report_args(refs=(), **changes):
    return dict(kind="reconciliation", references=list(refs), disposition="pending",
                documents=[], reason="Resultado pendiente", **changes)


def test_report_is_optional_scoped_and_total_budget_includes_final(tmp_path):
    agent, req = make(tmp_path, [text()] * 30)
    req = replace(req, continuous=replace(req.continuous, max_llm_calls=25))
    result = execute(agent, req)
    assert result.llm_calls == sum(result.llm_calls_by_phase.values()) == 25
    assert result.llm_calls_by_phase == {"researcher": 23, "checkpoint": 0, "evaluator": 2}
    assert not events(agent, "lab.phase.changed") and not events(agent, "lab.review.completed")
    assert all("report_work" in {t.name for t in r["tools"]} and r["allow_tools"] for r in agent.client.requests)
    assert "report_work" not in {t.name for t in agent.tools.specs()}
    assert len([e for e in events(agent, "lab.intervention.delivered") if e["reason"] == "evaluation_feedback"]) <= 1


def test_single_call_skips_evaluation_and_preserves_answer(tmp_path):
    agent, req = make(tmp_path, [text("respuesta")])
    result = execute(agent, replace(req, continuous=replace(req.continuous, max_llm_calls=1)))
    assert result.llm_calls == 1 and result.answer == "respuesta"
    assert result.llm_calls_by_phase["evaluator"] == 0
    assert events(agent, "lab.evaluation.skipped")


def test_report_validates_refs_versions_and_never_writes_knowledge(tmp_path):
    agent, _ = make(tmp_path, [])
    agent.recorder.start("fixture", {"run_id": "fixture"})
    state = RuntimeState()
    register_report(agent.tools, state, agent.workspace)
    ref = agent.recorder.artifact({"new_evidence": True})
    agent.workspace.write_file("evaluation.md", "Provisional")
    sha = agent.workspace.read_version("evaluation.md")[1]

    def send(**updates):
        args = report_args([ref])
        args.update(updates)
        return asyncio.run(agent.tools.execute(call("report_work", **args).function_call)).payload

    before = agent.workspace.snapshot()
    assert not send(references=["archivo/missing/no.json"])["ok"]
    assert not send(disposition="integrated")["ok"]
    assert not send(disposition="integrated", documents=[{"path": "evaluation.md", "sha256": "old"}])["ok"]
    result = send(disposition="integrated", documents=[{"path": "evaluation.md", "sha256": sha}])
    assert result["ok"] and not result["value"]["semantic_validity_assessed"]
    assert state.pending() == [] and agent.workspace.snapshot() == before
    agent.workspace.write_file("evaluation.md", "Nueva conclusión")
    state.refresh(agent.workspace)
    assert state.pending()[0]["disposition"] == "unknown"
    new_sha = agent.workspace.read_version("evaluation.md")[1]
    assert send(disposition="integrated", documents=[{"path": "evaluation.md", "sha256": new_sha}])["ok"]
    state.refresh(agent.workspace)
    assert state.pending() == []  # Old stale declarations cannot invalidate newer ones.


def test_report_capture_failure_does_not_claim_success(tmp_path, monkeypatch):
    agent, _ = make(tmp_path, [])
    agent.recorder.start("fixture", {"run_id": "fixture"})
    state = RuntimeState()
    register_report(agent.tools, state, agent.workspace)
    monkeypatch.setattr(agent.recorder, "artifact", lambda value: (_ for _ in ()).throw(OSError("disk")))
    result = asyncio.run(agent.tools.execute(call("report_work", **report_args()).function_call))
    assert not result.payload["ok"] and state.declarations == []


def test_pending_survives_unrelated_write_renewal_and_resume(tmp_path):
    agent, req = make(tmp_path, [call("source"), save_turn("other.md", "Otro avance"), text()] * 3)
    agent.tools.register("source", "Synthetic source", {}, lambda: {"text": "evidence"}, execution="inline", material=True)
    req = replace(req, continuous=replace(req.continuous, max_llm_calls=4))
    execute(agent, req)
    saved = json.loads((agent.recorder.current / "runtime/estado.json").read_bytes())
    assert sum(ref.startswith("materiales/") for ref in saved["references"]) == 1
    assert next(iter(saved["references"].values()))["disposition"] == "unknown"
    prior = agent.recorder.current
    agent.client = ScriptedClient([text("retomado")])
    execute(agent, replace(req, continuous=replace(req.continuous, max_llm_calls=1)))
    assert agent.recorder.current != prior
    assert "pending_count" in str(agent.client.requests[0]["input_items"])
    data = json.loads((agent.recorder.current / "runtime/estado.json").read_bytes())
    assert all(data["references"][ref] == value for ref, value in saved["references"].items())
    text_refs = [ref for ref, value in saved["references"].items() if value.get("source") == "researcher_text"]
    assert text_refs and "text" in agent.recorder.read_artifact(text_refs[0])["text"]


def test_evaluation_events_group_and_backstop_and_removal(tmp_path, monkeypatch):
    agent, _ = make(tmp_path, [])
    state = RuntimeState()
    agent.workspace.write_file("evaluation.md", "v1")
    assert not evaluation_policy(state, agent.workspace, "evaluation.md")
    state.researcher_calls = 5
    assert evaluation_policy(state, agent.workspace, "evaluation.md")[0].reason == "event"
    state.last_evaluation_call = 5
    state.evaluation_requested = False
    state.researcher_calls = 24
    assert not evaluation_policy(state, agent.workspace, "evaluation.md")
    state.researcher_calls = 25
    assert evaluation_policy(state, agent.workspace, "evaluation.md")[0].reason == "backstop"
    import research_agent.runtime_control as control
    monkeypatch.setattr(control, "POLICIES", ())
    assert control.inspect_policies(state, agent.workspace, "evaluation.md") == []
    runner, req = make(tmp_path / "removed", [text()] * 25)
    result = execute(runner, replace(req, continuous=replace(req.continuous, max_llm_calls=23)))
    assert result.llm_calls_by_phase["evaluator"] == 1  # Final review remains a closing guarantee.


def test_reconciliation_marks_only_observed_version_change(tmp_path):
    agent, _ = make(tmp_path, [])
    agent.workspace.write_file("evaluation.md", "v1")
    state = RuntimeState(evaluated_versions={"evaluation.md": agent.workspace.read_version("evaluation.md")[1]})
    assert not reconciliation_policy(state, agent.workspace, None)
    agent.workspace.write_file("evaluation.md", "v2")
    proposal = reconciliation_policy(state, agent.workspace, None)[0]
    assert proposal.reason == "review_outdated"
    assert "economic" not in proposal.payload


def test_checkpoint_max_two_calls_full_tools_and_no_required_write(tmp_path):
    agent, req = make(tmp_path, [text("avance " * 6000), call("list_files", path=""),
                              call("list_files", path=""), text("continuar"), text()])
    req = replace(req, continuous=replace(req.continuous, max_llm_calls=6,
        max_context_bytes=120000, consolidation_threshold_bytes=30000))
    result = execute(agent, req)
    assert result.stop_reason == "call_limit"
    assert result.llm_calls_by_phase["checkpoint"] == 2
    assert events(agent, "lab.context.renewed")
    assert not result.state.files_written
    assert all("calculate" in {t.name for t in r["tools"]} for r in agent.client.requests)
    assert all(not e["continuity_verified"] for e in events(agent, "lab.context.renewed"))


def test_reconstruct_keeps_whole_exchange_and_rejects_oversized_seed():
    measure = lambda items: {"budgeted_bytes": sum(len(x) for x in items)}
    history, retained = reconstruct(["seed"], [["old", "result"], ["call", "answer"]], measure, 18, 30)
    assert history == ["seed", "call", "answer"] and retained == [["call", "answer"]]
    with pytest.raises(ContextConfigurationError):
        reconstruct(["protected"], [], measure, 5, 30)
    with pytest.raises(ContextConfigurationError):
        reconstruct(["seed"], [["x" * 40]], measure, 18, 30)


def test_runtime_identity_and_alias_conflict_before_clients(tmp_path, monkeypatch):
    root = tmp_path / "experiment"
    prepare_experiment(root, new=True, deliberative=True)
    validate_runtime(root)
    (root / "runtime.json").unlink()
    with pytest.raises(ValueError, match="migration"):
        validate_runtime(root)
    from research_agent.cli import main
    monkeypatch.setattr("research_agent.cli.build_agent", lambda *a, **k: pytest.fail("client built"))
    with pytest.raises(SystemExit) as error:
        main(["m", "--experiment", str(root), "--continue", "--run-name", "test",
              "--renewal-bytes", "30000", "--consolidation-bytes", "40000"])
    assert error.value.code == 2
