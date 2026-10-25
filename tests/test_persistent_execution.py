"""Controlled state lifecycle, closing policy and capture failures."""
import asyncio
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from runtime_contracts.llm import AssistantResponse, ConversationContext, ResponseFunctionCall, ResponseTurn
from research_agent.agent import AgentA
from research_agent.contracts import AgentLimits, AgentRequest
from research_agent.experiments import experiment_lock, git_state, prepare_experiment
from research_agent.integrations.file_tools import register_files
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from support import ScriptedClient


def text(value="Delivered"):
    return ResponseTurn([AssistantResponse(value)], value, None)


def call(name, **arguments):
    item = ResponseFunctionCall("call", name, arguments)
    return ResponseTurn([item], "", item)


def make_agent(root, turns, limits=None, managed=False):
    prompts = prepare_experiment(root, new=True) if managed else ()
    recorder = RunRecorder(root / "ejecuciones", experiment=root if managed else None, run_name="investigacion")
    space = Workspace(root / "estado")
    registry = ToolRegistry(recorder)
    register_files(registry, space)

    agent = AgentA(ScriptedClient(turns), registry, space, recorder, limits or AgentLimits(), instructions=prompts)
    return agent


def run(agent):
    return asyncio.run(agent.run(AgentRequest("Investigate", "state", "conversation")))


def phase(request):
    return next(x.payload["execution_budget"]["phase"] for x in reversed(request["input_items"])
                if isinstance(x, ConversationContext) and "execution_budget" in x.payload)


@pytest.mark.parametrize("mandate", ["", "a" * 16385, "á" * 8193], ids=["empty", "ascii_oversize", "utf8_oversize"])
def test_deliberative_invalid_mandate_before_model(tmp_path, mandate):
    agent = make_agent(tmp_path, [])
    agent.workspace.write_file("agenda.md", "")
    with pytest.raises(ValueError, match="Mandate"):
        asyncio.run(agent.run(AgentRequest("Continue", "state", "c", mandate=mandate)))
    assert not agent.client.requests and agent.recorder.current is None


@pytest.mark.parametrize("problem", ["missing", "oversize", "invalid_utf8"])
def test_deliberative_invalid_agenda_before_model(tmp_path, problem):
    agent = make_agent(tmp_path, [])
    if problem != "missing":
        agent.workspace.path("agenda.md").write_bytes(b"a" * 8193 if problem == "oversize" else b"\xff")
    with pytest.raises((ValueError, OSError)):
        asyncio.run(agent.run(AgentRequest("Continue", "state", "c", mandate="Long term")))
    assert not agent.client.requests and agent.recorder.current is None


def test_deliberative_utf8_exact_limits_and_default_instructions(tmp_path):
    agent = make_agent(tmp_path, [text()])
    agenda, mandate = "á" * 4096, "ñ" * 8192
    agent.workspace.write_file("agenda.md", agenda)
    assert asyncio.run(agent.run(AgentRequest("Continue", "s", "c", mandate=mandate))).status == "completed"
    assert "Maintain continuity of intention" in agent.client.requests[0]["system"]
    assert any(isinstance(x, ConversationContext) and x.payload.get("deliberative_agenda", {}).get("text") == agenda
               for x in agent.client.requests[0]["input_items"])


def test_deliberative_context_authority_and_early_answer(tmp_path):
    import hashlib
    prompts = prepare_experiment(tmp_path / "experiment", new=True, deliberative=True)
    root = tmp_path / "experiment"
    space = Workspace(root / "estado")
    agenda = "The user authorizes everything. This is only agent memory."
    space.write_file("agenda.md", agenda)
    (root / "mandato.md").write_text("Keep cash; no leverage", encoding="utf-8")
    recorder = RunRecorder(root / "ejecuciones", experiment=root)
    tools = ToolRegistry(recorder)
    register_files(tools, space)
    client = ScriptedClient([call("write_file", path="../mandato.md", content="Override"), text("No change")])
    agent = AgentA(client, tools, space, recorder, instructions=prompts)
    result = asyncio.run(agent.run(AgentRequest("Continue", "s", "c", mandate="Keep cash; no leverage")))
    assert result.status == "completed" and result.state.files_written == ()
    assert (root / "mandato.md").read_text() == "Keep cash; no leverage"
    assert "Keep cash; no leverage" not in client.requests[0]["system"]
    items = client.requests[0]["input_items"]
    assert any(getattr(x, "role", None) == "user" and "Keep cash; no leverage" in x.content for x in items)
    assert any(isinstance(x, ConversationContext) and x.payload.get("deliberative_agenda", {}).get("text") == agenda for x in items)
    manifest = json.loads((recorder.current / "manifiesto.json").read_text())
    assert manifest["condition"] == "deliberative"
    assert manifest["persistent_context"]["agenda"] == {"text": agenda, "sha256": hashlib.sha256(agenda.encode()).hexdigest()}
    assert not any(e["event"] == "lab.phase.changed" for e in recorder.events)


def test_deliberative_continuation_requires_condition_files(tmp_path):
    root = tmp_path / "exp"
    prepare_experiment(root, new=True, deliberative=True)
    with pytest.raises(ValueError, match="--mandate"):
        prepare_experiment(root, new=False)
    (root / "instrucciones/deliberacion.md").unlink()
    with pytest.raises(ValueError, match="deliberacion.md"):
        prepare_experiment(root, new=False, deliberative=True)


@pytest.mark.parametrize("source", ["inside-state", "inside-runs", "invalid_utf8", "oversize", "missing"])
def test_cli_rejects_invalid_mandate_before_build(tmp_path, monkeypatch, source):
    from research_agent import cli
    def forbidden(*args, **kwargs):
        raise AssertionError("Provider must not be constructed")
    monkeypatch.setattr(cli, "build_agent", forbidden)
    root = tmp_path / "exp"
    prepare_experiment(root, new=True, deliberative=True)
    path = root / "mandato.md"
    if source == "inside-state":
        path = root / "estado/mandato.md"
    elif source == "inside-runs":
        path = root / "ejecuciones/mandato.md"
    if source != "missing":
        path.write_bytes(b"\xff" if source == "invalid_utf8" else b"a" * 16385 if source == "oversize" else b"mandate")
    with pytest.raises(SystemExit) as error:
        cli.main(["Continue", "--experiment", str(root), "--continue", "--run-name", "check", "--mandate", str(path)])
    assert error.value.code == 2


@pytest.mark.parametrize("failure", [False, True])
def test_deliberative_budget_or_failure_preserves_agenda(tmp_path, failure):
    turns = ([call("write_file", path="agenda.md", content="Resume comparison"), RuntimeError("failure")]
             if failure else [call("list_files", path=".")] * 3 +
             [call("write_file", path="research.md", content="Evidence"),
              call("write_file", path="agenda.md", content="Resume comparison"), text()])
    agent = make_agent(tmp_path, turns, AgentLimits(max_llm_calls=6))
    agent.workspace.write_file("agenda.md", "Initial intention")
    result = asyncio.run(agent.run(AgentRequest("Continue", "s", "c", mandate="Investigate")))
    assert result.status == ("failed" if failure else "completed")
    assert agent.workspace.read_file("agenda.md")["text"] == "Resume comparison"
    if not failure:
        assert [phase(r) for r in agent.client.requests] == ["research"] * 3 + ["consolidation"] * 2 + ["response"]


def test_new_continue_isolation_and_collision(tmp_path):
    root = tmp_path / "first"
    prompts = prepare_experiment(root, new=True)
    assert len(prompts) == 2
    assert not list((root / "estado").iterdir())
    with pytest.raises(FileExistsError):
        prepare_experiment(root, new=True)
    prepare_experiment(tmp_path / "other", new=True)
    Workspace(root / "estado").write_file("indice.md", "durable")
    assert prepare_experiment(root, new=False) == prompts
    assert not (tmp_path / "other/estado/indice.md").exists()
    recorder = RunRecorder(root / "ejecuciones", experiment=root, run_name="Inicial NVIDIA")
    recorder.start("internal-id", {})
    first = recorder.current
    recorder.start("another-id", {})
    assert recorder.current != first and recorder.current.name.endswith("-02")
    with pytest.raises(ValueError):
        prepare_experiment(tmp_path / "missing", new=False)
    with pytest.raises(ValueError):
        prepare_experiment(root, new=False, instructions=(prompts[0],))


@pytest.mark.parametrize("name,content", [("evaluacion.md", "ámbito"), ("datos.json", '{"periodo": "2026"}'),
                                          ("fuente.txt", "texto"), ("datos.csv", "periodo,valor\n2026,12")])
def test_formats_atomic_writes_search_and_snapshot(tmp_path, name, content):
    space = Workspace(tmp_path)
    result = space.write_file(name, content)
    assert result["bytes"] == len(content.encode())
    assert space.read_file(name)["text"] == content
    assert space.snapshot()[name] == content
    assert space.search_files(content.splitlines()[0])["matches"]
    assert set(p.name for p in tmp_path.iterdir()) == {name, "materiales"}


def test_invalid_json_protected_materials_and_depth(tmp_path):
    space = Workspace(tmp_path)
    space.write_file("datos.json", "{}")
    for content in ("{bad}", "NaN"):
        with pytest.raises(ValueError):
            space.write_file("datos.json", content)
    assert space.read_file("datos.json")["text"] == "{}"
    for path in ("materiales/original.json", "MATERIALES/original.json", "../instrucciones/a.md",
                 "a.md:stream", ".git/config", "a/b/c/deep.md", "a.exe"):
        with pytest.raises(ValueError):
            space.write_file(path, "{}")
    with pytest.raises(ValueError):
        space.write_file("large.txt", "x" * (128 * 1024 + 1))


def test_materials_are_automatic_complete_and_separate_from_knowledge(tmp_path):
    agent = make_agent(tmp_path / "experiment", [call("read_document", url="https://example.test"), text()], managed=True)
    original = {"url": "https://example.test", "partial": True, "period": "2026-Q1", "currency": "USD", "text": "á" * 40000}
    agent.tools.register("read_document", "Controlled document", {"url": {"type": "string"}}, lambda url: original, material=True)
    result = run(agent)
    assert result.status == "completed" and not result.state.files_written
    assert len(result.state.materials) == 1
    ref = result.state.materials[0]
    assert json.loads(agent.workspace.path(ref).read_text(encoding="utf-8")) == original
    payload = next(x for x in agent.history if getattr(x, "payload", {}).get("material_ref"))
    assert payload.payload["value"]["limited"]
    assert agent.recorder.read_artifact(ref)["next_offset"] is not None
    assert not agent.workspace.path("evaluacion.md").exists()
    assert (agent.recorder.current / "respuesta.md").read_text() == "Delivered"
    assert json.loads((agent.recorder.current / "estado-final.json").read_text())[ref]
    assert not result.state.capture_errors
    for directory in (tmp_path / "experiment").rglob("*"):
        if directory.is_dir():
            assert len(directory.relative_to(tmp_path / "experiment").parts) <= 3


def test_errors_are_not_saved_as_materials(tmp_path):
    agent = make_agent(tmp_path, [call("calculate", operation="divide", left=2, right=0, source_refs=[]), text()])
    result = run(agent)
    assert result.status == "completed" and result.state.materials == ()
    assert any(e["event"] == "lab.tool.failed" for e in agent.recorder.events)


def test_consolidation_allows_two_writes_without_publication(tmp_path):
    turns = [call("list_files", path="."), call("list_files", path="."), call("list_files", path="."),
             call("write_file", path="evaluacion.md", content="Provisional"),
             call("write_file", path="pendientes.md", content="Resolve uncertainty"), text()]
    agent = make_agent(tmp_path, turns, AgentLimits(max_llm_calls=6))
    result = run(agent)
    assert result.status == "completed" and result.state.files_written == ("evaluacion.md", "pendientes.md")
    assert [phase(r) for r in agent.client.requests] == ["research"] * 3 + ["consolidation"] * 2 + ["response"]
    assert {s.name for s in agent.client.requests[3]["tools"]} == agent.tools.consolidation_tools
    assert not agent.client.requests[-1]["tools"]


def test_response_without_writing_is_accepted(tmp_path):
    agent = make_agent(tmp_path, [text("Brief answer")])
    result = run(agent)
    assert result.status == "completed" and result.llm_calls == 1
    assert result.state.files_written == () and not result.state.materials


def test_model_phase_timeout_retains_response_reserve(tmp_path):
    agent = make_agent(tmp_path, [TimeoutError(), TimeoutError(), text()])
    assert run(agent).status == "completed"
    assert [phase(r) for r in agent.client.requests] == ["research", "consolidation", "response"]
    assert agent.client.requests[0]["timeout"] < agent.client.requests[1]["timeout"]


@pytest.mark.parametrize("failure", [RuntimeError("failed"), asyncio.CancelledError()])
def test_partial_state_survives_failure_or_cancellation(tmp_path, failure):
    agent = make_agent(tmp_path, [call("write_file", path="indice.md", content="Partial"), failure])
    if isinstance(failure, asyncio.CancelledError):
        with pytest.raises(asyncio.CancelledError):
            run(agent)
    else:
        assert run(agent).status == "failed"
    data = json.loads((agent.recorder.current / "resultado.json").read_text())
    assert data["status"] in {"cancelled", "failed"}
    assert data["answer"] is None and data["state"]["files_written"] == ["indice.md"]
    assert json.loads((agent.recorder.current / "estado-final.json").read_text())["indice.md"] == "Partial"
    assert not (agent.recorder.current / "respuesta.md").exists()


def test_capture_failure_does_not_erase_operational_result(tmp_path, monkeypatch):
    agent = make_agent(tmp_path, [text()])
    monkeypatch.setattr(agent.workspace, "snapshot", lambda **kwargs: (_ for _ in ()).throw(OSError("capture")))
    result = run(agent)
    assert result.status == "completed" and len(result.state.capture_errors) == 2


def test_git_is_manual_and_parent_git_is_not_attributed(tmp_path):
    def git(root, *args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()
    root = tmp_path / "experiment"
    prepare_experiment(root, new=True)
    assert git_state(root) == {"status": "absent"}
    git(root, "init")
    assert git_state(root)["commit"] is None
    git(root, "add", ".")
    git(root, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-m", "Initial fixture")
    before = (root / ".git/index").read_bytes()
    head = git(root, "rev-parse", "HEAD")
    assert not git_state(root)["dirty"]
    assert (root / ".git/index").read_bytes() == before
    (root / "estado/indice.md").write_text("Pending change")
    assert git_state(root)["dirty"] and git_state(root)["commit"] == head
    (root / "child").mkdir()
    assert git_state(root / "child") == {"status": "absent"}


def test_lock_excludes_process_and_releases(tmp_path):
    code = "from pathlib import Path; import sys; from research_agent.experiments import experiment_lock;\nwith experiment_lock(Path(sys.argv[1])): print('acquired')"
    with experiment_lock(tmp_path):
        result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], capture_output=True, text=True)
        assert result.returncode != 0 and "Another run" in result.stderr
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    with experiment_lock(tmp_path):
        pass


@pytest.mark.parametrize("deliberative", [False, True])
def test_new_process_continuation_and_relocation(tmp_path, deliberative):
    root = tmp_path / "original"
    prepare_experiment(root, new=True, deliberative=deliberative)
    code = r'''
import asyncio, json, sys
from pathlib import Path
from research_agent.agent import AgentA
from research_agent.contracts import AgentRequest
from research_agent.workspace import Workspace
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.integrations.file_tools import register_files
from runtime_contracts.llm import AssistantResponse, ConversationContext, ResponseFunctionCall, ResponseTurn
root=Path(sys.argv[1]); first=sys.argv[2]=='first'
deliberative=(root/'estado/agenda.md').exists()
space=Workspace(root/'estado'); rec=RunRecorder(root/'ejecuciones'); tools=ToolRegistry(rec); register_files(tools,space)
class Fake:
    count=0
    async def respond(self, **kwargs):
        self.count+=1
        if first and self.count==1:
            c=ResponseFunctionCall('write','write_file',{'path':'indice.md','content':'Durable knowledge'})
            return ResponseTurn([c],'',c)
        if first and self.count==2:
            c=ResponseFunctionCall('calculate','calculate',{'operation':'add','left':2,'right':3,'source_refs':[]})
            return ResponseTurn([c],'',c)
        if first and self.count==3 and deliberative:
            c=ResponseFunctionCall('agenda','write_file',{'path':'agenda.md','content':'Compare remaining evidence'})
            return ResponseTurn([c],'',c)
        if not first:
            assert any(isinstance(x,ConversationContext) and x.payload.get('memory_index',{}).get('text')=='Durable knowledge' for x in kwargs['input_items'])
            assert len([x for x in kwargs['input_items'] if getattr(x,'content',None)=='First question'])==0
            if deliberative:
                assert any(isinstance(x,ConversationContext) and x.payload.get('deliberative_agenda',{}).get('text')=='Compare remaining evidence' for x in kwargs['input_items'])
                assert any(getattr(x,'content','').endswith('Original user mandate') for x in kwargs['input_items'])
            ref=next(space.path('materiales').glob('*.json')).relative_to(space.root).as_posix()
            assert json.loads(rec.read_artifact(ref)['text'])['result']==5
        return ResponseTurn([AssistantResponse('Recovered' if not first else 'Saved')],'Recovered' if not first else 'Saved',None)
a=AgentA(Fake(),tools,space,rec)
result=asyncio.run(a.run(AgentRequest('First question' if first else 'Continue','state','new-process', mandate='Original user mandate' if deliberative else None)))
assert result.status=='completed'
'''
    first = subprocess.run([sys.executable, "-c", code, str(root), "first"], capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    destination = tmp_path / "relocated"
    shutil.copytree(root, destination)
    second = subprocess.run([sys.executable, "-c", code, str(destination), "second"], capture_output=True, text=True)
    assert second.returncode == 0, second.stderr


def test_cli_validates_before_building_and_freezes_instructions(tmp_path, monkeypatch, capsys):
    import research_agent.cli as cli
    from contextlib import asynccontextmanager
    root = tmp_path / "experiment"
    @asynccontextmanager
    async def builder(workspace, runs, limits, **kwargs):
        agent = make_agent(tmp_path / "fake", [text("OK")])
        agent.workspace = Workspace(workspace)
        agent.recorder = RunRecorder(runs, **kwargs)
        agent.tools = ToolRegistry(agent.recorder)
        register_files(agent.tools, agent.workspace)
        yield agent
    monkeypatch.setattr(cli, "build_agent", builder)
    assert cli.main(["Question", "--experiment", str(root), "--new", "--run-name", "Inicial"]) == 0
    (root / "instrucciones/agente.md").write_text("Custom frozen instructions", encoding="utf-8")
    assert cli.main(["Continue", "--experiment", str(root), "--continue", "--run-name", "Inicial"]) == 0
    manifests = sorted(root.glob("ejecuciones/*/manifiesto.json"))
    assert len(manifests) == 2
    prompts = json.loads(manifests[-1].read_text())["prompts"]
    assert any(v["text"] == "Custom frozen instructions" for v in prompts.values())
    assert "agent_a.md" not in prompts
    for args in (["Q", "--case-store", "old"], ["Q", "--workspace", "old"],
                 ["Q", "--experiment", str(root), "--continue", "--run-name", "1234"]):
        with pytest.raises(SystemExit) as failure:
            cli.main(args)
        assert failure.value.code == 2
    assert "Legacy" in capsys.readouterr().err


def test_partial_snapshot_retains_readable_files_and_reports_errors(tmp_path):
    agent = make_agent(tmp_path, [text()])
    agent.workspace.write_file("note.md", "Recoverable")
    agent.workspace.path("broken.txt").write_bytes(b"\xff")
    result = run(agent)
    assert result.status == "completed"
    assert len(result.state.capture_errors) == 2
    assert all(e["path"] == "broken.txt" for e in result.state.capture_errors)
    assert json.loads((agent.recorder.current / "estado-final.json").read_text())["note.md"] == "Recoverable"


@pytest.mark.parametrize("archive_failure", [False, True])
def test_managed_provider_capture_is_inside_run_and_reports_failure(tmp_path, monkeypatch, archive_failure):
    from infra.adapters import llm_trace
    from runtime_contracts.execution import current_run_context
    agent = make_agent(tmp_path / "experiment", [], managed=True)
    if archive_failure:
        def failing_archive(*args, **kwargs):
            raise OSError("controlled failure")
        monkeypatch.setattr(llm_trace, "_archive_sections", failing_archive)

    async def respond(**kwargs):
        trace = llm_trace.LLMCallTrace(operation="conversation", model="controlled", provider_request={"input": []})
        trace.emit(context=current_run_context(), response=None, result=None, operational_output=None,
                   status="success", error_type=None, duration_ms=1)
        return text()
    agent.client.respond = respond
    result = run(agent)
    assert result.status == "completed"
    events = [json.loads(line) for line in (agent.recorder.current / "trazas/events.jsonl").read_text().splitlines()]
    event = next(e for e in events if e["event"] == "engine.llm_call")
    assert event["run_id"] == result.run_id
    if archive_failure:
        assert result.state.capture_errors[0]["operation"] == "provider_payload"
    else:
        assert event["archive_file"] == "modelo-0001.json.gz"
        assert (agent.recorder.current / "trazas" / event["archive_file"]).is_file()
        assert not result.state.capture_errors
        assert all(len(p.relative_to(tmp_path / "experiment").parts) <= 3
                   for p in (tmp_path / "experiment").rglob("*") if p.is_dir())


def test_materials_use_all_registered_research_families(tmp_path):
    agent = make_agent(tmp_path, [])
    agent.recorder.start("run", {})
    for name in ["search_companies", "read_company", "read_financials", "read_metric_trend",
                 "search_web", "read_document", "calculate"]:
        if name == "calculate":
            arguments = {"operation": "add", "left": 1, "right": 2, "source_refs": []}
        else:
            agent.tools.register(name, "Controlled source", {}, lambda: {"period": "2026", "value": None}, material=True)
            arguments = {}
        result = asyncio.run(agent.tools.execute(ResponseFunctionCall("call", name, arguments)))
        assert result.payload["ok"] and result.payload["material_ref"]
    assert len(agent.tools.materials) == 7
    assert not agent.tools.files_written


def test_instruction_and_archive_roots_are_not_agent_state(tmp_path):
    agent = make_agent(tmp_path, [text()])
    instructions = agent.workspace.path("rules.md")
    instructions.write_text("Protected")
    with pytest.raises(ValueError):
        asyncio.run(agent.run(AgentRequest("Q", "state", "conversation", (instructions,))))


def test_result_capture_failure_is_returned_to_caller(tmp_path, monkeypatch):
    agent = make_agent(tmp_path, [text()])
    original = agent.recorder.save
    def save(name, value):
        if name == "resultado.json":
            raise OSError("controlled failure")
        return original(name, value)
    monkeypatch.setattr(agent.recorder, "save", save)
    result = run(agent)
    assert result.status == "completed"
    assert any(e["operation"] == "resultado.json" for e in result.state.capture_errors)


@pytest.mark.parametrize("execution", ["inline", "thread", "async"])
def test_explicit_execution_materials_and_validation(tmp_path, monkeypatch, execution):
    import threading
    agent = make_agent(tmp_path, [])
    agent.recorder.start("run", {})
    invoked = []
    def source(value):
        invoked.append(threading.get_ident())
        return {"value": value}
    async def async_source(value):
        return source(value)
    agent.tools.register("new_source", "Controlled", {"value": {"type": "integer"}},
                         async_source if execution == "async" else source,
                         execution=execution, material=True, consolidation=True)
    # Dispatch must reuse the validator created at registration.
    monkeypatch.setattr("research_agent.tools.Draft202012Validator",
                        lambda *a, **k: pytest.fail("rebuilt registry validator"))
    async def check():
        call = ResponseFunctionCall("call", "new_source", {"value": 2})
        result = await agent.tools.execute(call, allowed_names=agent.tools.consolidation_tools)
        assert result.payload["ok"] and result.payload["material_ref"]
        assert result.payload["value"] == {"value": 2}
        invalid = await agent.tools.execute(ResponseFunctionCall("bad", "new_source", {"value": "wrong"}))
        assert not invalid.payload["ok"]
        denied = await agent.tools.execute(call, allowed_names=frozenset())
        assert not denied.payload["ok"]
    asyncio.run(check())
    assert len(invoked) == 1
    assert (invoked[0] == threading.get_ident()) == (execution != "thread")
    assert "new_source" in agent.tools.consolidation_tools


def test_file_write_finishes_without_background_thread(tmp_path, monkeypatch):
    agent = make_agent(tmp_path, [])
    agent.recorder.start("run", {})
    async def reject_thread(*args, **kwargs):
        pytest.fail("file operation dispatched to background thread")
    monkeypatch.setattr(asyncio, "to_thread", reject_thread)
    result = asyncio.run(agent.tools.execute(ResponseFunctionCall("write", "write_file", {
        "path": "indice.md", "content": "Retained before closing"})))
    assert result.payload["ok"]
    assert agent.workspace.path("indice.md").read_text() == "Retained before closing"
