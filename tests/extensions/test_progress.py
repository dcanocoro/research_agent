"""Commitment control, using the real runtime and local clients only."""

import asyncio
import json
from dataclasses import replace

import pytest

from research_agent.contracts import AgentRequest
from research_agent.contracts import AgentLimits
from research_agent.contracts import ContinuousConfig
from research_agent.extensions.progress.objective import Objective
import research_agent.extensions.progress.evaluator as evaluator
from support.bounded import agent as bounded_agent, response
from support.continuous import make, execute, text
from support import save_arguments
from support.progress import objective, report, Client








@pytest.mark.parametrize("continuous", [False, True])
def test_commitment_success_uses_one_runtime_and_total_budget(tmp_path, continuous):
    if continuous:
        a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=12))
        req = replace(req, objective=objective(), progress_step_calls=1)
    else:
        a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=12))
        req = AgentRequest("Explain", "w", "c", objective=objective(), progress_step_calls=1)
    a.client = Client()
    result = execute(a, req)
    assert result.status == "completed" and result.stop_reason == "objective_sufficient"
    assert result.llm_calls == 4 and result.tool_calls == 1
    assert result.llm_calls_by_phase == {"objective_generation": 0, "evaluator": 2, "researcher": 1, "closing": 1}
    saved = json.loads((a.recorder.current / "progreso/estado.json").read_bytes())
    assert saved["history"][0]["result"]["kind"] == "progress"
    assert saved["latest"]["outcome"] == "sufficient"
    manifest = json.loads((a.recorder.current / "manifiesto.json").read_bytes())
    assert manifest["extensions"]["progress"] == "commitments-v1"
    assert manifest["external_review_policy"] is None
    terminal = [e for e in a.recorder.events if e["event"].startswith("lab.run.")][-1]
    assert terminal["stop_reason"] == result.stop_reason


def test_generate_once_and_recover_on_continuation(tmp_path):
    a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=6))
    a.client = Client(final="blocked", research=lambda n: text("No usable data"))
    req = AgentRequest("Explain", "w", "c", progress=True)
    first = execute(a, req)
    assert first.stop_reason == "objective_blocked" and a.client.generations == 1
    b = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=6))
    b.client = Client(final="blocked")
    second = execute(b, req)
    assert b.client.generations == 0 and second.stop_reason == "objective_blocked"


@pytest.mark.parametrize("calls", [1, 2, 3, 4, 8])
def test_total_budget_and_segment_limits(tmp_path, calls):
    a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=calls))
    a.client = Client(final="continue", research=lambda n: text("Activity is not progress"))
    result = execute(a, AgentRequest("Explain", "w", "c", objective=objective(), progress_step_calls=2))
    assert result.llm_calls <= calls
    assert sum(result.llm_calls_by_phase.values()) == result.llm_calls
    assert result.status == "interrupted" and result.stop_reason == "call_limit"
    assert a.client.evaluations == 0 or a.client.requests[-1]["allow_tools"] is False


@pytest.mark.parametrize("bad", ["{}", "not JSON", TimeoutError(), asyncio.CancelledError()])
def test_invalid_failure_and_cancellation_are_captured(tmp_path, bad):
    a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=6))
    a.client = Client(fail=bad)
    req = AgentRequest("Explain", "w", "c", objective=objective())
    if isinstance(bad, asyncio.CancelledError):
        with pytest.raises(asyncio.CancelledError):
            execute(a, req)
        result = json.loads((a.recorder.current / "resultado.json").read_bytes())
        assert result["status"] == "cancelled"
    else:
        result = execute(a, req)
        assert result.status != "completed"
    assert a.client.research_calls == 0
    assert list((a.recorder.current / "progreso").glob("*-evaluator-input.json"))
    assert list((a.recorder.current / "progreso").glob("*-evaluator.json"))


def test_evaluator_rejects_missing_stale_and_unchanged_progress(tmp_path):
    a = bounded_agent(tmp_path, [])
    a.workspace.write_file("result.md", "Saved result")
    view = evaluator.packet(a.workspace, objective(), None, None, {})
    good = report(view, outcome="sufficient", kind="progress")
    assert evaluator.parse(json.dumps(good), objective(), view)
    good["criteria"][0]["references"][0]["sha256"] = "wrong"
    with pytest.raises(ValueError, match="stale"):
        evaluator.parse(json.dumps(good), objective(), view)
    good["criteria"][0]["references"] = [{"path": "missing.md", "sha256": None}]
    with pytest.raises(ValueError, match="Missing"):
        evaluator.parse(json.dumps(good), objective(), view)
    same = evaluator.packet(a.workspace, objective(), None, None, evaluator.versions(view))
    with pytest.raises(ValueError, match="changed persisted"):
        evaluator.parse(json.dumps(report(same, outcome="sufficient", kind="progress")), objective(), same)


def test_failed_attempt_requires_reconsideration(tmp_path):
    a = bounded_agent(tmp_path, [])
    view = evaluator.packet(a.workspace, objective(), None, {"id": "attempt"}, {})
    with pytest.raises(ValueError, match="reconsideration"):
        evaluator.parse(json.dumps(report(view, kind="stagnant")), objective(), view)


def test_explicit_objective_revision_resets_comparison(tmp_path):
    a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=6))
    a.client = Client(final="blocked", research=lambda n: text("blocked"))
    execute(a, AgentRequest("Explain", "w", "c", objective=objective()))
    b = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=3))
    b.client = Client()
    revised = replace(objective(), id="revised")
    execute(b, AgentRequest("Explain", "w", "c", objective=revised))
    assert any(e["event"] == "lab.progress.objective_revised" for e in b.recorder.events)
    inputs = list((b.recorder.current / "progreso").glob("*-evaluator-input.json"))
    assert json.loads(inputs[0].read_bytes())["previous"] is None


def test_progress_rejects_b_before_run(tmp_path):
    a = bounded_agent(tmp_path, [])
    a.knowledge = object()
    with pytest.raises(ValueError, match="knowledge agent"):
        execute(a, AgentRequest("Explain", "w", "c", progress=True))
    assert a.recorder.current is None


def test_renewal_preserves_commitment_without_extra_evaluator(tmp_path):
    from support.continuous import call
    a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=14, max_context_bytes=100000,
                                                       consolidation_threshold_bytes=30000))
    a.tools.register("large", "Large result", {}, lambda: {"text": "漢" * 9000}, execution="inline")
    a.client = Client(final="continue", research=lambda n: call("large"))
    result = execute(a, replace(req, objective=objective(), progress_step_calls=8))
    assert result.stop_reason == "call_limit" and result.llm_calls <= 14
    renewals = [e for e in a.recorder.events if e["event"] == "lab.context.renewed"]
    assert renewals
    after = a.client.requests[renewals[0]["llm_calls_used"]]
    assert any(getattr(i, "payload", {}).get("progress", {}).get("commitment") for i in after["input_items"])
    assert not any(e["event"] == "lab.external_review.failed" for e in a.recorder.events)
    assert all(not e["event"].startswith("lab.objective.") for e in a.recorder.events)


def test_packet_declares_omissions_and_partial_views(tmp_path):
    a = bounded_agent(tmp_path, [])
    for n in range(8):
        a.workspace.write_file(f"document-{n}.md", "é" * 15000)
    view = evaluator.packet(a.workspace, objective(), None, None, {}, max_bytes=24000)
    assert view["omitted"] and any(d["partial"] for d in view["documents"])
    assert len(json.dumps(view, ensure_ascii=False).encode()) <= 24000


def test_tool_limit_verifies_result_and_returns_distinct_stop(tmp_path):
    a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=9, max_tool_calls=1))
    a.client = Client(final="continue")
    result = execute(a, AgentRequest("Explain", "w", "c", objective=objective()))
    assert result.stop_reason == "tool_limit" and result.tool_calls == 1
    assert a.client.evaluations == 2 and result.status == "interrupted"


def test_native_campaign_reader_reports_commitments_without_distance(tmp_path):
    from research_campaigns.reporting.evidence import inspect_run
    a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=8))
    a.client = Client()
    execute(a, AgentRequest("Explain", "w", "c", objective=objective(), progress_step_calls=1))
    summary = inspect_run(tmp_path, a.recorder.current)["objective_summary"]
    assert summary["outcome"] == "sufficient" and summary["commitments"] == 1
    assert "distance" not in summary and summary["failures"] == 0


@pytest.mark.parametrize("named", [False, True])
def test_cli_progress_create_and_continue(tmp_path, monkeypatch, named):
    from contextlib import asynccontextmanager
    from research_agent.agent import AgentA
    from research_agent.observability.recording import RunRecorder
    from research_agent.core.tools import ToolRegistry
    from research_agent.storage.workspace import Workspace
    from research_agent.capabilities.state.files import register_files
    from research_agent.cli.main import main
    clients = []

    @asynccontextmanager
    async def build(workspace, runs, limits, **kwargs):
        recorder = RunRecorder(runs, experiment=kwargs["experiment"], run_name=kwargs["run_name"])
        space = Workspace(workspace)
        tools = ToolRegistry(recorder)
        register_files(tools, space)
        client = Client()
        clients.append(client)
        yield AgentA(client, tools, space, recorder, limits, configuration={"max_output_tokens": 128})

    monkeypatch.setattr("research_agent.cli.main.build_agent", build)
    output = tmp_path / "out"
    selection = ["--name", "progreso", "--continuous"] if named else ["Explain", "--progress", "--run-name", "test"]
    for operation in ("--new", "--continue"):
        assert main([*selection, "--output", str(output), operation, "--progress-step-calls", "1"]) == 0
    assert clients[0].generations == (0 if named else 1)
    assert clients[1].generations == 0
    assert len(list((output / "ejecuciones").glob("*/progreso/estado.json"))) == 2


def test_failed_evaluation_preserves_last_valid_state_for_continuation(tmp_path):
    class FailSecond(Client):
        async def respond(self, **kwargs):
            if kwargs["system"] == evaluator.SYSTEM and self.evaluations == 1:
                self.evaluations += 1
                return text("invalid")
            return await super().respond(**kwargs)

    a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=8))
    a.client = FailSecond()
    req = AgentRequest("Explain", "w", "c", objective=objective(), progress_step_calls=1)
    result = execute(a, req)
    assert result.stop_reason == "progress_evaluation_invalid"
    state = json.loads((a.recorder.current / "progreso/estado.json").read_bytes())
    assert state["latest"]["outcome"] == "continue" and state["commitment"]
    b = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=8))
    b.client = Client(final="blocked")
    resumed = execute(b, req)
    assert resumed.stop_reason == "objective_blocked"
    view = b.client.requests[0]["input_items"][0].payload
    from research_agent.observability.recording import encoded
    assert json.loads(encoded(view["previous"])) == state["latest"]
    assert json.loads(encoded(view["commitment"])) == state["commitment"]


def test_bounded_context_limit_verifies_and_closes_in_a_small_context(tmp_path):
    from research_agent.observability.recording import encoded
    a = bounded_agent(tmp_path, [], AgentLimits(max_llm_calls=12, max_context_bytes=30000))
    a.configuration["max_output_tokens"] = 128
    a.tools.register("large", "Large result", {}, lambda: {"text": "漢" * 9000}, execution="inline")
    a.client = Client(final="continue", research=lambda n: response(call=("large", {})))
    result = execute(a, AgentRequest("Explain", "w", "c", objective=objective()))
    assert result.stop_reason == "context_limit" and result.status == "interrupted"
    assert a.client.evaluations == 2 and result.answer
    assert all(len(encoded({"system": r["system"], "input": r["input_items"], "tools": r["tools"]})) <= 30000
               for r in a.client.requests)

