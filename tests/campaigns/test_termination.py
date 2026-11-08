import asyncio
import json
from pathlib import Path

import pytest
from research_agent.contracts import AgentRequest
from research_agent.core.execution import execute
from research_campaigns.termination.policy import TerminationPolicy
from research_campaigns.termination.runner import prepare, verify, main, run_job
from support import ScriptedClient
from support.bounded import agent, request, response

DEFINITION = Path(__file__).resolve().parents[2] / "campaigns/terminacion"


def read():
    return response(call=("list_files", {}))


def checkpoint(decision="REQUEST_FINISH"):
    return response(json.dumps({"decision": decision, "reason": "Suficiente con lo obtenido"}))


def test_natural_answer_never_calls_checkpoint(tmp_path):
    a = agent(tmp_path, [response("respuesta")])
    judge = ScriptedClient([])
    result = asyncio.run(execute(TerminationPolicy(a, request(), evaluator=judge)))
    assert result.stop_reason == "answered"
    assert result.llm_calls == 1
    assert not judge.requests


def test_checkpoint_finishes_after_complete_exchange_without_tools(tmp_path):
    a = agent(tmp_path, [*[read() for _ in range(6)], response("final")])
    judge = ScriptedClient([checkpoint()])
    policy = TerminationPolicy(a, request(), evaluator=judge, evaluator_prompt="check")
    result = asyncio.run(execute(policy))
    assert result.stop_reason == "checkpoint_requested_finish"
    assert result.llm_calls == 8  # Seven A, one checkpoint.
    assert result.tool_calls == 6
    assert a.client.requests[-1]["tools"] == []
    assert a.client.requests[-1]["allow_tools"] is False
    assert judge.requests[0]["tools"] == []
    packet = json.loads(judge.requests[0]["input_items"][0].content)
    assert packet["agent_calls"] == 6
    assert packet["conversation"][-1]["call_id"] == "call"
    assert result.llm_calls_by_phase == {"research": 6, "response": 1, "checkpoint": 1}
    saved = json.loads((a.recorder.current / "resultado.json").read_bytes())
    assert saved["llm_calls"] == 8


def test_checkpoint_cancellation_preserves_terminal_cause(tmp_path):
    a = agent(tmp_path, [read() for _ in range(6)])
    judge = ScriptedClient([asyncio.CancelledError()])
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(execute(TerminationPolicy(a, request(), evaluator=judge)))
    saved = json.loads((a.recorder.current / "resultado.json").read_bytes())
    assert saved["status"] == "cancelled" and saved["stop_reason"] == "cancelled"
    assert saved["llm_calls"] == 7


@pytest.mark.parametrize("bad", [response("invalid"), response('{"decision":"REQUEST_FINISH"}'),
                                 TimeoutError(), response('{"decision":"X","reason":"a"}')])
def test_invalid_or_failed_checkpoint_continues_without_retry(tmp_path, bad):
    a = agent(tmp_path, [*[read() for _ in range(6)], response("voluntario")])
    judge = ScriptedClient([bad])
    result = asyncio.run(execute(TerminationPolicy(a, request(), evaluator=judge)))
    assert result.stop_reason == "answered"
    assert result.llm_calls == 8
    assert len(judge.requests) == 1
    assert a.client.requests[-1]["allow_tools"] is True
    report = json.loads((a.recorder.current / "terminacion/checkpoint-06.json").read_bytes())
    assert report["outcome"] == "failed"


def test_two_checkpoints_and_normal_reserves(tmp_path):
    a = agent(tmp_path, [*[read() for _ in range(17)], response("cierre")])
    judge = ScriptedClient([checkpoint("CONTINUE"), checkpoint("CONTINUE")])
    result = asyncio.run(execute(TerminationPolicy(a, request(), evaluator=judge)))
    assert result.llm_calls == 20
    assert result.stop_reason == "budget"
    assert result.llm_calls_by_phase == {"research": 15, "consolidation": 2, "response": 1, "checkpoint": 2}
    assert a.client.requests[-1]["tools"] == []


def test_reject_other_extensions(tmp_path):
    a = agent(tmp_path, [])
    with pytest.raises(ValueError):
        TerminationPolicy(a, AgentRequest("x", "s", "c", progress=True))


def test_v0_preserves_native_bounded_behavior(tmp_path, monkeypatch):
    from research_agent.regimes.bounded.policy import BoundedPolicy
    from research_campaigns.termination.tracing import capture
    # Compare execution behavior with the same trace adapter. The new wheel removed
    # the private archive global used by A's historical tracer; never patch at runtime.
    monkeypatch.setattr("research_agent.regimes.bounded.policy.capture_traces", lambda root, **kw: capture(root))
    results = []
    for label, policy in (("native", BoundedPolicy), ("experimental", TerminationPolicy)):
        a = agent(tmp_path / label, [read(), response("respuesta")])
        results.append(asyncio.run(execute(policy(a, request()))))
    assert [(r.status, r.stop_reason, r.answer, r.llm_calls, r.tool_calls) for r in results] == [
        ("completed", "answered", "respuesta", 2, 1)] * 2


def test_corpus_cannot_be_modified_with_agent_tools(tmp_path):
    from support import save_arguments
    a = agent(tmp_path, [response(call=("record_research_advance",
        save_arguments("materiales/corpus.md", "inventado", "original"))), response("fin")])
    a.workspace.path("materiales/corpus.md").write_text("original", encoding="utf-8")
    asyncio.run(execute(TerminationPolicy(a, request())))
    assert a.workspace.path("materiales/corpus.md").read_text(encoding="utf-8") == "original"
    assert any(e["event"] == "lab.tool.failed" for e in a.recorder.events)


def test_prepare_offline_freezes_balanced_plan_and_refuses_changes(tmp_path):
    output = tmp_path / "campaign"
    prepare(DEFINITION, output, 3)
    campaign = verify(output)
    assert len(campaign["jobs"]) == 108
    assert len({j["id"] for j in campaign["jobs"]}) == 108
    assert campaign["profile"] is None
    assert not (output / "jobs").exists()
    with pytest.raises(FileExistsError):
        prepare(DEFINITION, output, 3)
    (output / "definition/self-control.md").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="definition changed"):
        verify(output)


def test_real_local_job_has_readonly_corpus_and_private_rubric(tmp_path):
    from dataclasses import dataclass

    @dataclass
    class Profile:
        name: str = "fixture"

    class Factory:
        def __init__(self):
            self.clients = []

        def conversation(self, profile):
            client = ScriptedClient([response("240 millones EUR, 2025, A1")])
            self.clients.append(client)
            return client

    output = tmp_path / "campaign"
    prepare(DEFINITION, output, 1)
    campaign = verify(output)
    case = json.loads((DEFINITION / "cases.json").read_bytes())[0]
    job = next(j for j in campaign["jobs"] if j["case"] == "S1" and j["condition"] == "V1")
    factory = Factory()
    asyncio.run(run_job(output, campaign, job, case, factory, Profile()))
    root = output / "jobs" / job["id"]
    record = json.loads((root / "job.json").read_bytes())
    assert record["status"] == "completed"
    manifest = json.loads((root / record["run"] / "manifiesto.json").read_bytes())
    assert manifest["continuous"] is None and manifest["objective"] is None
    system = factory.clients[0].requests[0]["system"]
    assert "Suficiencia del encargo" in system
    assert case["rubric"] not in system
    assert "checkpoint.md" not in manifest["prompts"]
    assert not any(t["name"] in {"search_web", "query_findata"} for t in manifest["tools"])
    from research_campaigns.termination.runner import report
    report(output)
    packet = next((output / "review/answers").glob("*.json"))
    private = json.loads(packet.read_bytes())
    assert "condition" not in private and private["rubric"] == case["rubric"]


def test_validate_command_without_output():
    assert main(["validate", "--definition", str(DEFINITION)]) == 0


def test_shared_trace_archive_capture_without_provider(tmp_path):
    import gzip
    from infra.adapters.llm_trace import LLMCallTrace
    from research_campaigns.termination.tracing import capture
    with capture(tmp_path, metadata=lambda: {"experiment_role": "checkpoint"}) as events:
        trace = LLMCallTrace(operation="test", model="fixture", provider_request={"input": "synthetic"})
        trace.emit(context=None, response={"id": "fixture", "text": "done"}, result=None,
                   operational_output=None, status="success", error_type=None, duration_ms=1)
    assert len(events) == 1 and events[0]["experiment_role"] == "checkpoint"
    with gzip.open(tmp_path / events[0]["archive_file"], "rt", encoding="utf-8") as stream:
        payload = json.load(stream)
    assert payload["provider_input"]["input"] == "synthetic"
    assert (tmp_path / "events.jsonl").exists()
