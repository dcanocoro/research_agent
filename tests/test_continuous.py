"""Local continuous-loop checks: no provider or database calls."""
import asyncio
import json
from dataclasses import replace

import pytest
from runtime_contracts.llm import (AssistantResponse, ConversationContext, ConversationMessage,
    ProviderContinuation, ResponseFunctionCall, ResponseTurn, ToolResult)

from research_agent.agent import AgentA
from research_agent.context_budget import TokenCounter
from research_agent.contracts import AgentLimits, AgentRequest, ContinuousConfig
from research_agent.integrations.file_tools import register_files
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from support import ScriptedClient


def text(value="avance"):
    return ResponseTurn([AssistantResponse(value)], value, None)


def call(name, **arguments):
    item = ResponseFunctionCall("call", name, arguments)
    return ResponseTurn([item], "", item)


def make(tmp_path, turns, *, config=None, profile=None):
    space = Workspace(tmp_path / "estado")
    space.write_file("agenda.md", "Investigar la pregunta pendiente.")
    recorder = RunRecorder(tmp_path / "ejecuciones")
    registry = ToolRegistry(recorder)
    register_files(registry, space)
    agent = AgentA(ScriptedClient(turns), registry, space, recorder, AgentLimits(),
                   configuration=profile or {"provider": "openai", "model": "gpt-4o", "max_output_tokens": 128})
    request = AgentRequest("Comparar alternativas conservando los fundamentos.", "state", "conversation",
                           mandate="Gestiona una cartera ficticia sin apalancamiento.",
                           continuous=config or ContinuousConfig(max_llm_calls=3))
    return agent, request


def execute(agent, request):
    return asyncio.run(agent.run(request))


def events(agent, name):
    return [e for e in agent.recorder.events if e["event"] == name]


def test_text_continues_and_budget_is_a_pause(tmp_path):
    agent, request = make(tmp_path, [text("uno"), text("dos"), text("tres")])
    result = execute(agent, request)
    assert result.status == "interrupted" and result.stop_reason == "call_limit"
    assert result.llm_calls == 3 and result.answer == "tres"
    assert len(events(agent, "lab.continuous.response")) == 3
    transcript = (agent.recorder.current / "conversacion-completa.jsonl").read_text(encoding="utf-8")
    assert all(value in transcript for value in ("uno", "dos", "tres"))
    assert "conversacion-completa.jsonl" in result.artifact_refs
    manifest = json.loads((agent.recorder.current / "manifiesto.json").read_bytes())
    assert manifest["continuous"]["max_llm_calls"] == 3 and manifest["closing_policy"] is None


def test_three_reconstructions_recover_saved_state_and_preserve_mandate(tmp_path):
    class Client:
        def __init__(self):
            self.requests = []
            self.phases = {}

        async def respond(self, **kwargs):
            self.requests.append(kwargs)
            budget = next(x.payload["execution_budget"] for x in reversed(kwargs["input_items"])
                          if isinstance(x, ConversationContext) and "execution_budget" in x.payload)
            n = budget["context_number"]
            # Detect by offered tools rather than stale budget inserted before phase transition.
            consolidation = not any(t.name == "calculate" for t in kwargs["tools"])
            if consolidation:
                if self.phases.get(n) != "written":
                    self.phases[n] = "written"
                    return call("write_file", path="agenda.md", content=f"Pregunta pendiente {n + 1}")
                return text("Avances conservados")
            if n < 3:
                return text("novedad material " * 2500)
            contexts = [x.payload for x in kwargs["input_items"] if isinstance(x, ConversationContext)]
            assert any("Pregunta pendiente 3" in str(c.get("deliberative_agenda", "")) for c in contexts)
            return call("read_file", path="agenda.md", offset=0, max_bytes=1024)

    config = ContinuousConfig(max_context_tokens=18000, consolidation_threshold=6500, max_llm_calls=10)
    agent, request = make(tmp_path, [], config=config)
    agent.client = client = Client()
    result = execute(agent, request)
    assert result.stop_reason == "call_limit", result
    renewals = events(agent, "lab.context.renewed")
    assert len(renewals) == 3
    assert all("agenda.md" in e["changed_files"] for e in renewals)
    assert [e["llm_calls_used"] for e in renewals] == [3, 6, 9]
    for entry in client.requests:
        messages = [i.content for i in entry["input_items"] if isinstance(i, ConversationMessage)]
        assert request.message in messages
        assert any(request.mandate in msg for msg in messages)
    counter = TokenCounter("openai", "gpt-4o")
    for entry in client.requests:
        assert counter.measure(entry["system"], entry["input_items"], entry["tools"], entry["max_tokens"])["budgeted_tokens"] <= config.max_context_tokens
    assert all(e["budgeted_tokens"] <= config.max_context_tokens for e in events(agent, "lab.context.budget"))
    assert "Pregunta pendiente 3" in agent.workspace.read_file("agenda.md")["text"]


@pytest.mark.parametrize("profile", [
    {"provider": "gemini", "model": "gemini-test", "max_output_tokens": 128},
    {"provider": "openai", "model": "unknown-model", "max_output_tokens": 128},
    {"provider": "openai", "model": "gpt-4o", "max_output_tokens": 0},
])
def test_incompatible_profile_fails_before_call_with_evidence(tmp_path, profile):
    agent, request = make(tmp_path, [], profile=profile)
    result = execute(agent, request)
    assert result.status == "failed" and not agent.client.requests
    assert (agent.recorder.current / "resultado.json").exists()


def test_large_initial_context_rejected_without_truncation(tmp_path):
    agent, request = make(tmp_path, [], config=ContinuousConfig(max_context_tokens=2000, consolidation_threshold=100))
    result = execute(agent, request)
    assert result.status == "failed" and not agent.client.requests
    assert request.message in str(agent.history)
    assert "Pregunta" not in agent.workspace.read_file("agenda.md")["text"]


def test_large_tool_result_is_archived_and_readable(tmp_path):
    agent, request = make(tmp_path, [call("large"), text()], config=ContinuousConfig(max_llm_calls=2))
    original = {"text": "á漢🙂<|endoftext|>" * 2000}
    agent.tools.register("large", "Large result", {}, lambda: original, execution="inline")
    result = execute(agent, request)
    assert result.stop_reason == "call_limit"
    delivered = next(i for i in agent.client.requests[1]["input_items"] if isinstance(i, ToolResult))
    reference = delivered.payload["artifact_ref"]
    assert original["text"][:20] in agent.recorder.read_artifact(reference, 0, 512)["text"]
    assert original["text"] in (agent.recorder.current / "trazas" / reference.split("/")[-1]).read_text(encoding="utf-8")


def test_token_specific_tool_delivery_under_byte_limit(tmp_path):
    config = ContinuousConfig(max_context_tokens=18000, consolidation_threshold=6500, max_llm_calls=2)
    agent, request = make(tmp_path, [call("large"), text("guardado")], config=config)
    original = {"text": "漢" * 9000}  # <32 KiB but many tokens
    agent.tools.register("large", "Large result", {}, lambda: original, execution="inline")
    result = execute(agent, request)
    assert result.stop_reason == "call_limit"
    delivered = next(i for i in agent.client.requests[1]["input_items"] if isinstance(i, ToolResult))
    assert delivered.payload["limited"]
    raw = agent.recorder.read_artifact(delivered.payload["artifact_ref"], 0, 32768)["text"]
    assert "漢" * 100 in raw


def test_provider_continuation_is_unchanged_and_counted(tmp_path):
    continuation = ProviderContinuation("openai", "gpt-4o", [{"type": "reasoning", "encrypted_content": "opaque" * 50}])
    item = AssistantResponse("avance", continuation)
    agent, request = make(tmp_path, [ResponseTurn([item], "avance", None), text()], config=ContinuousConfig(max_llm_calls=2))
    result = execute(agent, request)
    assert result.llm_calls == 2
    replay = next(i for i in agent.client.requests[1]["input_items"] if isinstance(i, AssistantResponse))
    assert replay.continuation == continuation
    counter = TokenCounter("openai", "gpt-4o")
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
    agent, request = make(tmp_path, [call("write_file", path="avance.md", content="guardado")],
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
    for kwargs in ({"max_llm_calls": 0}, {"timeout_seconds": float("inf")}, {"consolidation_threshold": 32000}):
        with pytest.raises(ValueError):
            ContinuousConfig(**kwargs)


def test_cli_rejects_missing_mandate_and_misplaced_options():
    from research_agent.cli import main
    for flags in (["--continuous"], ["--max-calls", "3"]):
        with pytest.raises(SystemExit) as caught:
            main(["Investiga", "--experiment", "unused", "--new", "--run-name", "test", *flags])
        assert caught.value.code == 2


def test_consolidation_failure_preserves_active_history(tmp_path):
    agent, request = make(tmp_path, [text("novedad " * 6000),
        call("read_file", path="missing.md", offset=0, max_bytes=100)],
        config=ContinuousConfig(max_context_tokens=18000, consolidation_threshold=6500, max_llm_calls=8))
    result = execute(agent, request)
    assert result.stop_reason == "consolidation_failed"
    assert not events(agent, "lab.context.renewed")
    assert any(isinstance(i, AssistantResponse) and "novedad" in i.text for i in agent.history)


def test_oversized_exchange_pauses_without_sending_or_trimming_continuation(tmp_path):
    opaque = ProviderContinuation("openai", "gpt-4o", [{"encrypted_content": "漢" * 30000}])
    item = AssistantResponse("avance", opaque)
    agent, request = make(tmp_path, [ResponseTurn([item], "avance", None)],
        config=ContinuousConfig(max_context_tokens=12000, consolidation_threshold=6500, max_llm_calls=4))
    result = execute(agent, request)
    assert result.stop_reason == "context_exchange_too_large"
    assert len(agent.client.requests) == 1
    assert next(i for i in agent.history if isinstance(i, AssistantResponse)).continuation == opaque


def test_four_consolidation_calls_then_renew_without_required_writes(tmp_path):
    turns = [text("novedad " * 6000)] + [call("list_files", path="") for _ in range(4)] + [text()]
    agent, request = make(tmp_path, turns,
        config=ContinuousConfig(max_context_tokens=18000, consolidation_threshold=6500, max_llm_calls=6))
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and result.llm_calls == 6
    renewals = events(agent, "lab.context.renewed")
    assert len(renewals) == 1 and renewals[0]["changed_files"] == []


def test_global_time_limit_and_finite_operation_timeout(tmp_path, monkeypatch):
    class Clock:
        now = 0

        def __call__(self):
            return self.now

    clock = Clock()
    monkeypatch.setattr("research_agent.continuous.monotonic", clock)
    agent, request = make(tmp_path, [], config=ContinuousConfig(timeout_seconds=5))

    class Client:
        async def respond(self, **kwargs):
            assert kwargs["timeout"] == 5
            clock.now = 6
            return text()

    agent.client = Client()
    result = execute(agent, request)
    assert result.stop_reason == "time_limit" and result.llm_calls == 1


def test_fixed_simulated_date_and_order_not_repeated_on_resume(tmp_path):
    from research_agent.simulation.state import Simulator
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
            assert 0 < kwargs["timeout"] <= 300
            raise asyncio.CancelledError()

    agent.client = Client()
    with pytest.raises(asyncio.CancelledError):
        execute(agent, request)
    assert json.loads((agent.recorder.current / "resultado.json").read_bytes())["status"] == "cancelled"


def test_cli_creates_and_resumes_with_controlled_client(tmp_path, monkeypatch, capsys):
    from contextlib import asynccontextmanager
    from research_agent.cli import main

    @asynccontextmanager
    async def build(workspace, runs, limits, *, experiment, run_name, **kwargs):
        recorder = RunRecorder(runs, experiment=experiment, run_name=run_name)
        registry = ToolRegistry(recorder)
        register_files(registry, Workspace(workspace))
        yield AgentA(ScriptedClient([text("uno"), text("dos")]), registry, registry.workspace,
                     recorder, limits, configuration={"provider": "openai", "model": "gpt-4o", "max_output_tokens": 128})

    monkeypatch.setattr("research_agent.cli.build_agent", build)
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
