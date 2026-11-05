"""Local continuous-loop checks: no provider or database calls.

Small budgets leave room for the bundled prompts before testing threshold crossings.
"""
from support import save_turn, save_arguments, save_current
import asyncio
import json
from dataclasses import replace

import pytest
from support import review_turn
from runtime_contracts.llm import (AssistantResponse, ConversationContext, ConversationMessage,
    ProviderContinuation, ResponseFunctionCall, ResponseTurn, ToolResult)

from research_agent.agent import AgentA
from research_agent.core.context_budget import ByteCounter
from research_agent.contracts import AgentLimits
from research_agent.contracts import AgentRequest
from research_agent.contracts import ContinuousConfig
from research_agent.capabilities.state.files import register_files
from research_agent.observability.recording import RunRecorder
from research_agent.core.tools import ToolRegistry
from research_agent.storage.workspace import Workspace
from support import ScriptedClient
from support.continuous import text, call, make, execute, events












def test_text_continues_and_budget_is_a_pause(tmp_path):
    agent, request = make(tmp_path, [text("uno"), text("dos"), text("tres")])
    result = execute(agent, request)
    assert result.status == "interrupted" and result.stop_reason == "call_limit"
    assert (result.llm_calls - result.llm_calls_by_phase["evaluator"]) == 2 and result.answer == "dos"
    assert len(events(agent, "lab.continuous.response")) == 2
    transcript = (agent.recorder.current / "conversacion-completa.jsonl").read_text(encoding="utf-8")
    assert all(value in transcript for value in ("uno", "dos"))
    assert "conversacion-completa.jsonl" in result.artifact_refs
    manifest = json.loads((agent.recorder.current / "manifiesto.json").read_bytes())
    assert manifest["continuous"]["max_llm_calls"] == 3 and manifest["closing_policy"] is None




@pytest.mark.parametrize("output", [0, -1, None, True])
def test_invalid_output_reserve_fails_before_call_with_evidence(tmp_path, output):
    agent, request = make(tmp_path, [], profile={"provider": "openai", "model": "gpt-6-luna", "max_output_tokens": output})
    result = execute(agent, request)
    assert result.status == "failed" and not agent.client.requests
    assert (agent.recorder.current / "resultado.json").exists()


@pytest.mark.parametrize("provider,model", [("openai", "gpt-6-luna"), ("gemini", "unknown-model")])
def test_byte_budget_needs_no_tokenizer_mapping(tmp_path, provider, model):
    agent, request = make(tmp_path, [text()], profile={"provider": provider, "model": model, "max_output_tokens": 16000},
                          config=ContinuousConfig(max_llm_calls=1))
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and (result.llm_calls - result.llm_calls_by_phase["evaluator"]) == 1
    assert events(agent, "lab.context.counter")[0]["unit"] == "bytes"


def test_counter_counts_serialized_utf8_and_reserves_output():
    from research_agent.observability.recording import encoded
    counter = ByteCounter()
    value = "á漢🙂"
    assert counter.count(value) == len(encoded(value)) > len(value)
    measured = counter.measure(value, [], [], 16000)
    assert measured["reserved_output_bytes"] == 128000
    assert measured["budgeted_bytes"] == (measured["input_bytes"] * 11 + 9) // 10 + 128000


def test_large_initial_context_rejected_without_truncation(tmp_path):
    agent, request = make(tmp_path, [], config=ContinuousConfig(max_context_bytes=2000, consolidation_threshold_bytes=100))
    result = execute(agent, request)
    assert result.status == "failed" and not agent.client.requests
    assert request.message in str(agent.history)
    assert "Pregunta" not in agent.workspace.read_file("agenda.md")["text"]


def test_large_tool_result_is_archived_and_readable(tmp_path):
    agent, request = make(tmp_path, [call("large"), text()], config=ContinuousConfig(max_llm_calls=3))
    original = {"text": "á漢🙂<|endoftext|>" * 2000}
    agent.tools.register("large", "Large result", {}, lambda: original, execution="inline")
    result = execute(agent, request)
    assert result.stop_reason == "call_limit"
    delivered = next(i for i in agent.client.requests[1]["input_items"] if isinstance(i, ToolResult))
    reference = delivered.payload["artifact_ref"]
    assert original["text"][:20] in agent.recorder.read_artifact(reference, 0, 512)["text"]
    assert original["text"] in (agent.recorder.current / "trazas" / reference.split("/")[-1]).read_text(encoding="utf-8")


@pytest.mark.parametrize("maximum, limited", [(100000, False), (35000, True)])
def test_result_crossing_threshold_is_delivered_unless_hard_cap_exceeded(tmp_path, maximum, limited):
    config = ContinuousConfig(max_context_bytes=maximum, consolidation_threshold_bytes=30000, max_llm_calls=3)
    agent, request = make(tmp_path, [call("large"), text("guardado")], config=config)
    original = {"text": "漢" * 9000}  # Below the registry cap, above the renewal threshold.
    agent.tools.register("large", "Large result", {}, lambda: original, execution="inline")
    result = execute(agent, request)
    assert result.stop_reason == "call_limit"
    delivered = next(i for i in agent.client.requests[1]["input_items"] if isinstance(i, ToolResult))
    assert bool(delivered.payload.get("limited")) is limited
    if limited:
        raw = agent.recorder.read_artifact(delivered.payload["artifact_ref"], 0, 32768)["text"]
        assert "漢" * 100 in raw
    else:
        assert delivered.payload["value"] == original
        assert not events(agent, "lab.phase.changed")
        assert "calculate" in {tool.name for tool in agent.client.requests[1]["tools"]}
    assert all(e["budgeted_bytes"] <= maximum for e in events(agent, "lab.context.budget"))


def test_paginated_document_is_read_completely_across_consolidation_threshold(tmp_path):
    agent, request = make(tmp_path, [
        call("read_file", path="source.md", offset=0, max_bytes=32768),
        call("read_file", path="source.md", offset=32768, max_bytes=32768), text("Conservado")],
        config=ContinuousConfig(max_context_bytes=100000, consolidation_threshold_bytes=30000, max_llm_calls=4))
    original = "x" * 32843
    agent.workspace.write_file("source.md", original)
    result = execute(agent, request)
    assert result.stop_reason == "call_limit"
    delivered = list({item.payload["artifact_ref"]: item for entry in agent.client.requests for item in entry["input_items"] if isinstance(item, ToolResult)}.values())
    assert len(delivered) == 2
    assert all(not item.payload.get("limited") for item in delivered)
    assert "".join(item.payload["value"]["text"] for item in delivered) == original
    assert delivered[0].payload["value"]["next_offset"] == 32768
    assert delivered[1].payload["value"]["next_offset"] is None
    assert events(agent, "lab.context.renewed")


def test_provider_continuation_is_unchanged_and_counted(tmp_path):
    continuation = ProviderContinuation("openai", "gpt-4o", [{"type": "reasoning", "encrypted_content": "opaque" * 50}])
    item = AssistantResponse("avance", continuation)
    agent, request = make(tmp_path, [ResponseTurn([item], "avance", None), text()], config=ContinuousConfig(max_llm_calls=3))
    result = execute(agent, request)
    assert (result.llm_calls - result.llm_calls_by_phase["evaluator"]) == 2
    replay = next(i for i in agent.client.requests[1]["input_items"] if isinstance(i, AssistantResponse))
    assert replay.continuation == continuation
    counter = ByteCounter()
    assert counter.count(item) > counter.count(AssistantResponse("avance"))


@pytest.mark.parametrize("failure", [TimeoutError(), RuntimeError("failure"), asyncio.CancelledError()])
def test_failure_and_cancellation_preserve_capture(tmp_path, failure):
    agent, request = make(tmp_path, [text(), failure])
    if isinstance(failure, asyncio.CancelledError):
        with pytest.raises(asyncio.CancelledError):
            execute(agent, request)
    else:
        assert execute(agent, request).status != "completed"
    saved = json.loads((agent.recorder.current / "resultado.json").read_bytes())
    assert saved["llm_calls"] == 2
    assert (agent.recorder.current / "conversacion-completa.jsonl").exists()


def test_tool_limit_and_explicit_resume_do_not_replay_operation(tmp_path):
    agent, request = make(tmp_path, [save_turn(path="avance.md", content="guardado")],
                          config=ContinuousConfig(max_tool_calls=1))
    result = execute(agent, request)
    assert result.stop_reason == "tool_limit" and result.tool_calls == 1
    agent.client = ScriptedClient([text("retomado")])
    resumed = execute(agent, replace(request, continuous=ContinuousConfig(max_llm_calls=1)))
    assert resumed.tool_calls == 0
    assert agent.workspace.read_file("avance.md")["text"] == "guardado"


def test_requires_mandate_and_valid_configuration(tmp_path):
    agent, request = make(tmp_path, [])
    with pytest.raises(ValueError, match="mandate"):
        execute(agent, replace(request, mandate=None))
    for kwargs in ({"max_llm_calls": 0}, {"timeout_seconds": float("inf")}, {"consolidation_threshold_bytes": 524288}):
        with pytest.raises(ValueError):
            ContinuousConfig(**kwargs)


def test_cli_rejects_missing_mandate_and_misplaced_options():
    from research_agent.cli.main import main
    for flags in (["--continuous"], ["--max-calls", "3"]):
        with pytest.raises(SystemExit) as caught:
            main(["Investiga", "--experiment", "unused", "--new", "--run-name", "test", *flags])
        assert caught.value.code == 2


def test_checkpoint_tool_error_is_delivered_and_model_can_correct(tmp_path):
    agent, request = make(tmp_path, [text("novedad " * 6000),
        call("read_file", path="missing.md", offset=0, max_bytes=100),
        save_turn(path="agenda.md", content="Fundamentos conservados", previous="Investigar la pregunta pendiente."),
        text("Consolidado"), text("Continuación")],
        config=ContinuousConfig(max_context_bytes=100000, consolidation_threshold_bytes=30000, max_llm_calls=6))
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and (result.llm_calls - result.llm_calls_by_phase["evaluator"]) == 5
    correction_input = agent.client.requests[2]["input_items"]
    error = next(i for i in correction_input if isinstance(i, ToolResult))
    assert not error.payload["ok"] and error.payload["error_type"] == "FileNotFoundError"
    assert any(isinstance(i, AssistantResponse) and "novedad" in i.text for i in correction_input)
    assert len(events(agent, "lab.context.renewed")) == 1
    assert agent.workspace.read_file("agenda.md")["text"] == "Fundamentos conservados"
    assert result.llm_calls_by_phase["checkpoint"] == 2
    assert not result.state.capture_errors


def test_empty_agenda_rejection_can_be_corrected_in_checkpoint(tmp_path):
    import hashlib
    agent, request = make(tmp_path, [text("novedad " * 13000),
        call("record_research_advance", changes=[dict(path="agenda.md", action="edit", content=None, expected_sha256=hashlib.sha256(b"").hexdigest(),
             operations=[{"kind": "replace", "target": "\u0000", "content": "Fundamentos conservados"}])], reason="Conservar", source_refs=[]),
        save_turn(path="agenda.md", content="Fundamentos conservados", previous=""),
        text("Consolidado"), text("Continuación")],
        config=ContinuousConfig(max_context_bytes=240000, consolidation_threshold_bytes=90000, max_llm_calls=6))
    agent.workspace.write_file("agenda.md", "")
    agent.tools = ToolRegistry(agent.recorder)
    register_files(agent.tools, agent.workspace)
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and (result.llm_calls - result.llm_calls_by_phase["evaluator"]) == 5
    error = next(i for i in agent.client.requests[2]["input_items"] if isinstance(i, ToolResult))
    assert not error.payload["ok"] and "ambiguous_target" in error.payload["message"]
    assert agent.workspace.read_file("agenda.md")["text"] == "Fundamentos conservados"
    assert len(events(agent, "lab.context.renewed")) == 1
    assert len(events(agent, "lab.tool.failed")) == 1
    assert result.tool_calls == 2 and not result.state.capture_errors




def test_applied_write_with_capture_error_is_delivered_without_automatic_replay(tmp_path, monkeypatch):
    agent, request = make(tmp_path, [text("novedad " * 6000),
        save_turn(path="avance.md", content="Guardado una vez"),
        call("read_file", path="avance.md", offset=0, max_bytes=100),
        text("Consolidado"), text("Continuación")],
        config=ContinuousConfig(max_context_bytes=100000, consolidation_threshold_bytes=30000, max_llm_calls=6))
    original_artifact = agent.recorder.artifact
    def fail_write_capture(value):
        if isinstance(value, dict) and any(f.get("path") == "avance.md" for f in value.get("files", [])):
            raise OSError("Synthetic capture failure after applying the write")
        return original_artifact(value)
    monkeypatch.setattr(agent.recorder, "artifact", fail_write_capture)
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and result.tool_calls == 2
    error = next(i for i in agent.client.requests[2]["input_items"] if isinstance(i, ToolResult))
    assert not error.payload["ok"] and error.payload["applied"] is True
    assert error.payload["mutation"]["files"][0]["path"] == "avance.md"
    assert agent.workspace.read_file("avance.md")["text"] == "Guardado una vez"
    assert len(events(agent, "lab.file.written")) == 1
    assert len(events(agent, "lab.context.renewed")) == 1
    assert result.state.files_written == ("avance.md",)
    assert result.state.capture_errors == ({"operation": "tool_capture", "error_type": "OSError"},)




def test_oversized_exchange_pauses_without_sending_or_trimming_continuation(tmp_path):
    opaque = ProviderContinuation("openai", "gpt-4o", [{"encrypted_content": "漢" * 30000}])
    item = AssistantResponse("avance", opaque)
    agent, request = make(tmp_path, [ResponseTurn([item], "avance", None)],
        config=ContinuousConfig(max_context_bytes=40000, consolidation_threshold_bytes=30000, max_llm_calls=4))
    result = execute(agent, request)
    assert result.stop_reason == "context_exchange_too_large"
    assert len(agent.client.requests) == 1
    assert next(i for i in agent.history if isinstance(i, AssistantResponse)).continuation == opaque




def test_global_time_limit_and_finite_operation_timeout(tmp_path, monkeypatch):
    class Clock:
        now = 0

        def __call__(self):
            return self.now

    clock = Clock()
    monkeypatch.setattr("research_agent.regimes.continuous.policy.monotonic", clock)
    agent, request = make(tmp_path, [], config=ContinuousConfig(timeout_seconds=5))

    class Client:
        async def respond(self, **kwargs):
            if any("review_packet" in getattr(x, "payload", {}) for x in kwargs["input_items"]):
                return review_turn()
            assert kwargs["timeout"] == 5
            clock.now = 6
            return text()

    agent.client = Client()
    result = execute(agent, request)
    assert result.stop_reason == "time_limit" and (result.llm_calls - result.llm_calls_by_phase["evaluator"]) == 1


def test_fixed_simulated_date_and_order_not_repeated_on_resume(tmp_path):
    from research_agent.capabilities.simulation.state import Simulator
    simulator = Simulator.create(tmp_path / "sim", {
        "start": "2023-01-01", "end": "2023-02-01", "initial_cash": "100000",
        "universe": [{"symbol": "TEST", "name": "Synthetic"}], "max_positions": 1,
    }, {"prices": [{"symbol": "TEST", "date": "2023-01-02", "close": "10"}]})
    agent, request = make(tmp_path / "experiment", [call("portfolio_buy", symbol="TEST", amount="100")],
                          config=ContinuousConfig(max_tool_calls=1))
    agent.tools.register("portfolio_buy", "Synthetic simulated order", {
        "symbol": {"type": "string"}, "amount": {"type": "string"}}, simulator.buy, execution="inline", material=True)
    request = replace(request, metadata={"simulated_date": "2023-01-01"})
    first = execute(agent, request)
    assert first.tool_calls == 1
    agent.client = ScriptedClient([text()])
    execute(agent, replace(request, continuous=ContinuousConfig(max_llm_calls=1)))
    assert simulator.state["date"] == "2023-01-01"
    assert len(simulator.pending()) == 1 and simulator.state["positions"] == {}
    assert simulator.state["cash"] == "100000"


def test_no_global_limits_still_uses_finite_operation_timeout(tmp_path):
    agent, request = make(tmp_path, [], config=ContinuousConfig())

    class Client:
        async def respond(self, **kwargs):
            if any("review_packet" in getattr(x, "payload", {}) for x in kwargs["input_items"]):
                return review_turn()
            assert 0 < kwargs["timeout"] <= 300
            raise asyncio.CancelledError()

    agent.client = Client()
    with pytest.raises(asyncio.CancelledError):
        execute(agent, request)
    assert json.loads((agent.recorder.current / "resultado.json").read_bytes())["status"] == "cancelled"


def test_cli_creates_and_resumes_with_controlled_client(tmp_path, monkeypatch, capsys):
    from contextlib import asynccontextmanager
    from research_agent.cli.main import main

    @asynccontextmanager
    async def build(workspace, runs, limits, *, experiment, run_name, **kwargs):
        recorder = RunRecorder(runs, experiment=experiment, run_name=run_name)
        registry = ToolRegistry(recorder)
        register_files(registry, Workspace(workspace))
        yield AgentA(ScriptedClient([text("uno"), text("dos")]), registry, registry.workspace,
                     recorder, limits, configuration={"provider": "openai", "model": "gpt-4o", "max_output_tokens": 128})

    monkeypatch.setattr("research_agent.cli.main.build_agent", build)
    mandate = tmp_path / "mandato.md"
    mandate.write_text("Investiga y conserva fundamentos.", encoding="utf-8")
    experiment = tmp_path / "experiment"
    for operation, name in (("--new", "primero"), ("--continue", "segundo")):
        assert main(["Investiga", "--experiment", str(experiment), operation, "--run-name", name,
                     "--continuous", "--mandate", str(mandate), "--max-calls", "2"]) == 0
    assert capsys.readouterr().out.count("continuous=interrupted: call_limit") == 2
    runs = list((experiment / "ejecuciones").iterdir())
    assert len(runs) == 2
    assert all((r / "conversacion-completa.jsonl").exists() for r in runs)










def test_provider_captures_include_phase_and_index_for_each_attempt(tmp_path):
    from infra.adapters.llm_trace import LLMCallTrace

    agent, request = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=11))

    class Client:
        async def respond(self, **kwargs):
            if any("review_packet" in getattr(x, "payload", {}) for x in kwargs["input_items"]):
                return review_turn()
            # Simulate an adapter retry inside a single respond invocation.
            for status in ("error", "success"):
                trace = LLMCallTrace(operation="conversation", model="test", provider_request={"input": [], "tools": []})
                trace.emit(context=None, response=None, result=None, operational_output=None,
                           status=status, error_type=None, duration_ms=1)
            return text("decisión" if not kwargs["allow_tools"] else "avance")

    agent.client = Client()
    result = execute(agent, request)
    provider = [json.loads(line) for line in (agent.recorder.current / "trazas/events.jsonl").read_text(encoding="utf-8").splitlines()]
    calls = [e for e in provider if e["event"] == "engine.llm_call"]
    assert len(calls) == 2 * (result.llm_calls - result.llm_calls_by_phase["evaluator"])
    reviews = [e for e in calls if e["phase"] == "evaluator"]
    assert not reviews  # E2 has no periodic tools-disabled investigator call.
    assert all(e["usage_known"] is False for e in calls)
    assert all((agent.recorder.current / "trazas" / e["archive_file"]).exists() for e in calls)

