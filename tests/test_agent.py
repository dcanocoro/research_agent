import asyncio
import json
import subprocess
import sys
from pathlib import Path
import pytest
from runtime_contracts.llm import AssistantResponse, ResponseTurn, ResponseFunctionCall, ProviderContinuation, ToolResult
from research_agent.agent import AgentA
from research_agent.contracts import AgentRequest, AgentLimits
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from research_agent.integrations.file_tools import register_files


from support import ScriptedClient


def response(text="done", call=None, provider=None):
    continuation = ProviderContinuation(provider, "test", {"opaque": [1, 2]}) if provider else None
    item = ResponseFunctionCall("call", call[0], call[1], continuation) if call else AssistantResponse(text, continuation)
    return ResponseTurn([item], text if not call else "", item if call else None)


def agent(tmp_path, turns, limits=None):
    recorder = RunRecorder(tmp_path / "runs")
    registry = ToolRegistry(recorder)
    space = Workspace(tmp_path / "workspace")
    register_files(registry, space)
    return AgentA(ScriptedClient(turns), registry, space, recorder, limits or AgentLimits())


def request(message="Investigate", conversation="test"):
    return AgentRequest(message, "space", conversation)


@pytest.mark.parametrize("provider", ["openai", "gemini"])
def test_tools_preserve_replay_and_persist_memory(tmp_path, provider):
    a = agent(tmp_path, [response(call=("write_markdown", {"path": "memory/index.md", "content": "Remember the limit"}), provider=provider), response("saved"), response("revised")])
    first = asyncio.run(a.run(request()))
    assert first.status == "completed" and first.tool_calls == 1
    history = a.client.requests[1]["input_items"]
    assert any(isinstance(item, ResponseFunctionCall) and item.continuation.provider == provider for item in history)
    assert any(isinstance(item, ToolResult) and item.call_id == "call" for item in history)
    second = asyncio.run(a.run(request("Revisit")))
    assert second.run_id != first.run_id
    assert "Remember the limit" in (a.recorder.current / "estado-inicial.json").read_text()
    assert json.loads((a.recorder.current / "conversacion.json").read_text())


def test_reserved_finalization_disables_tools(tmp_path):
    a = agent(tmp_path, [response(call=("list_files", {"path": "."})), response("partial with limitations")], AgentLimits(max_llm_calls=2))
    result = asyncio.run(a.run(request()))
    assert result.status == "completed" and result.stop_reason == "budget"
    assert a.client.requests[-1]["allow_tools"] is False


@pytest.mark.parametrize("call", [("unknown", {}), ("write_markdown", {"path": "../escape.md", "content": "x"}), ("read_file", {})])
def test_invalid_tools_are_returned_and_recorded(tmp_path, call):
    a = agent(tmp_path, [response(call=call), response("explained")])
    result = asyncio.run(a.run(request()))
    assert result.status == "completed"
    assert any(e["event"] == "lab.tool.failed" for e in a.recorder.events)
    assert not list(tmp_path.glob("escape.md"))


@pytest.mark.parametrize("error", [RuntimeError("secret"), TimeoutError()])
def test_failure_preserves_partial_run(tmp_path, error):
    a = agent(tmp_path, [response(call=("write_markdown", {"path": "notes/prior.md", "content": "confirmed"})), error])
    result = asyncio.run(a.run(request()))
    assert result.status in {"failed", "interrupted"}
    assert (a.recorder.current / "resultado.json").exists()
    assert "confirmed" in (a.recorder.current / "estado-final.json").read_text()
    assert "secret" not in (a.recorder.current / "resultado.json").read_text()


def test_cancel_is_propagated_and_archived(tmp_path):
    a = agent(tmp_path, [asyncio.CancelledError()])
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(a.run(request()))
    assert json.loads((a.recorder.current / "resultado.json").read_text())["status"] == "cancelled"


def test_context_limit_does_not_silently_trim(tmp_path):
    a = agent(tmp_path, [], AgentLimits(max_context_bytes=1024))
    result = asyncio.run(a.run(request("x" * 4096)))
    assert result.stop_reason == "context_limit" and result.llm_calls == 0
    assert "x" * 4096 in (a.recorder.current / "conversacion.json").read_text()


def test_large_result_can_be_read_without_recursion(tmp_path):
    a = agent(tmp_path, [])
    a.recorder.start("test", {})
    a.tools.register("large", "Large result", {}, lambda: {"value": "a" * 40000})
    result = asyncio.run(a.tools.execute(ResponseFunctionCall("../unsafe", "large", {})))
    reference = result.payload["artifact_ref"]
    assert result.payload["value"]["limited"]
    read = a.recorder.read_artifact(reference)
    assert read["next_offset"] == 32768
    assert len(list((a.recorder.current / "trazas").glob("herramienta-*.json"))) == 1


def test_workspace_utf8_pagination_and_restrictions(tmp_path):
    space = Workspace(tmp_path / "workspace")
    space.write_markdown("memory/index.md", "á" * 5000)
    first = space.read_file("memory/index.md", max_bytes=8191)
    rest = space.read_file("memory/index.md", offset=first["next_offset"])
    assert first["text"] + rest["text"] == "á" * 5000
    for path in ("../outside.md", "C:/outside.md", "notes/a.exe", "file.md:stream"):
        with pytest.raises(ValueError):
            space.write_markdown(path, "bad")
    assert space.search_files("á")["matches"]


def test_workspace_rejects_links(tmp_path):
    space = Workspace(tmp_path / "workspace")
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (space.root / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Host does not permit symlinks.")
    with pytest.raises(ValueError):
        space.write_markdown("link/escape.md", "bad")


def test_findata_tools_are_readonly_and_rollback(monkeypatch):
    from research_agent.integrations.findata_tools import FindataTools
    import findata.read.case_financials as financials
    statements = []
    class Session:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def get_bind(self):
            from types import SimpleNamespace
            return SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))
        def execute(self, statement): statements.append(str(statement))
        def rollback(self): statements.append("rollback")
    expected = [{"value": None, "currency": "USD", "period": "2025", "source_ref": "original"}]
    monkeypatch.setattr(financials, "observations", lambda session, symbol: expected)
    assert FindataTools(Session).read_financials("TEST") == expected
    assert statements[0] == "SET TRANSACTION READ ONLY" and statements[-1] == "rollback"


def test_import_boundary_in_clean_subprocess(tmp_path):
    code = r'''
import sys, importlib.abc, tempfile, asyncio
from pathlib import Path
class Reject(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'finmate','engine','api','experience_audit','research_benchmarks'}:
            raise RuntimeError('Forbidden import: '+fullname)
sys.meta_path.insert(0, Reject())
from research_agent.bootstrap import build_agent
from research_agent.cli import main
from infra.llm_factory import LLMFactory
from research_agent.contracts import AgentRequest
from runtime_contracts.llm import ResponseTurn, AssistantResponse
async def check():
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder)
        async with build_agent(root/'workspace',root/'runs') as agent:
            class Fake:
                async def respond(self,**kwargs):
                    return ResponseTurn([AssistantResponse('done')],'done',None)
            agent.client=Fake()
            assert (await agent.run(AgentRequest('hello','space','conversation'))).status=='completed'
            assert 'save_case' not in {s.name for s in agent.tools.specs()}
            assert agent.instructions == ()
asyncio.run(check())
assert not any(n.split('.')[0] in {'finmate','engine','api','experience_audit','research_benchmarks'} for n in sys.modules)
'''
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr




def test_deterministic_calculator_and_source_references():
    from research_agent.integrations.file_tools import calculate
    assert calculate("divide", 20, 100, ["sources/test.md"])["result"] == .2
    with pytest.raises(ValueError):
        calculate("divide", 20, 0, [])
    with pytest.raises(ValueError):
        calculate("multiply", float("inf"), 1, [])


def test_static_import_boundary():
    import ast
    import importlib.util
    paths = [Path(importlib.util.find_spec("research_agent").origin).parent,
             Path(importlib.util.find_spec("runtime_contracts").origin).parent]
    for root in paths:
        for path in root.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                forbidden = {"finmate", "engine", "api"}
                if root.name == "research_agent":
                    forbidden |= {"experience_audit", "research_benchmarks"}
                assert not {n.split(".")[0] for n in names} & forbidden, path


def test_native_llm_capture_has_correlation_and_payload(tmp_path):
    from research_agent.tracing import capture_traces
    from runtime_contracts.execution import RunContext, bind_run_context
    from observability_context import interaction_context_for, bind_interaction_context
    from infra.adapters.llm_trace import LLMCallTrace
    with capture_traces(tmp_path / "capture") as events:
        context = RunContext("run")
        with bind_run_context(context), bind_interaction_context(interaction_context_for(
                interaction_id="interaction", conversation_id="conversation")):
            trace = LLMCallTrace(operation="conversation", model="test", provider_request={"input": [], "tools": []})
            trace.emit(context=context, response=None, result=None, operational_output=None,
                       status="success", error_type=None, duration_ms=1)
    calls = [e for e in events if e["event"] == "engine.llm_call"]
    assert len(calls) == 1
    assert calls[0]["interaction_id"] == "interaction" and calls[0]["run_id"] == "run"
    assert calls[0]["usage_known"] is False and calls[0]["occurred_at"]
    assert (tmp_path / "capture" / "llm" / calls[0]["archive_file"]).exists()


def test_prior_artifacts_are_readable_only_in_the_same_workspace(tmp_path):
    recorder = RunRecorder(tmp_path / "runs")
    recorder.start("first", {"workspace_fingerprint": "one"})
    reference = recorder.artifact({"original": "source"})
    recorder.start("second", {"workspace_fingerprint": "one"})
    assert "source" in recorder.read_artifact(reference)["text"]
    recorder.start("third", {"workspace_fingerprint": "other"})
    with pytest.raises(FileNotFoundError):
        recorder.read_artifact(reference)


def test_legacy_native_artifact_is_still_readable(tmp_path):
    recorder = RunRecorder(tmp_path / "runs")
    recorder.start("old", {"workspace_fingerprint": "same"})
    reference = recorder.artifact({"original": "historical"})
    (recorder.current / "manifiesto.json").rename(recorder.current / "manifest.json")
    recorder.start("new", {"workspace_fingerprint": "same"})
    assert "historical" in recorder.read_artifact(reference)["text"]
