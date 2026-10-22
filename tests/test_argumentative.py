"""Offline contracts for structured knowledge, closed corpus and portable capture."""
import asyncio
from contextlib import closing
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

import pytest
from runtime_contracts.llm import AssistantResponse, ResponseFunctionCall, ResponseTurn, ConversationContext

from research_agent.agent import AgentA
from research_agent.benchmark import run_suite
from research_agent.benchmark_catalog import load_suite
from research_agent.contracts import AgentLimits, AgentRequest
from research_agent.experiments import prepare_experiment
from research_agent.integrations.file_tools import register_files
from research_agent.knowledge import KnowledgeStore, register_knowledge, verify_capture
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace

ROOT = Path(__file__).resolve().parents[1]


def ref(id, revision=1):
    return {"id": id, "revision": revision}


def change(id, kind="hypothesis", revision=0, retired=False, **data):
    return {"id": id, "kind": kind, "expected_revision": revision, "retired": retired, "reason": "Nueva evidencia",
            "data": data or {"proposition": id, "status": "open", "references": []}}


def make_store(tmp_path):
    space = Workspace(tmp_path / "estado")
    space.write_file("entradas/base.md", "# Fuente\nIngresos 10 EUR; guía, no resultado.")
    return KnowledgeStore(tmp_path / "conocimiento/expediente.sqlite", space)


def foundations():
    return [change("E", "evidence", observation="Guía ingresos 10", source="entradas/base.md#L2", date="2030-01-01",
                   period="2030", currency="EUR", units="miles de millones"), change("H"),
            change("A", "argument", premises=[ref("E")], inference="Guía sostiene expectativa", conclusion=ref("H")),
            change("J", "assessment", judgment="Condicionado", scope="Negocio, no precio", references=[ref("H")]),
            change("U")]


def test_atomic_history_impact_and_retirement(tmp_path):
    store = make_store(tmp_path)
    store.apply(foundations(), "primero")
    assert store.impact("E")["affected"] == ["A", "H", "J"]
    revised = change("E", "evidence", 1, observation="Guía revisada a 8", source="entradas/base.md#L2",
                     date="2030-02-01", period="2030", currency="EUR", units="miles de millones")
    result = store.apply([revised], "segundo")
    assert result["pending_review"] == ["A", "H", "J"]
    assert store.read("H")["data"]["status"] == "open"
    assert any(r["cause"] == "E" and r["cause_revision"] == 2 for r in store.read("H")["pending_review"])
    assert not store.read("U")["pending_review"]
    assert store.read("E", 1)["data"]["observation"] == "Guía ingresos 10"
    assert store.history("E", limit=1)["next_offset"] == 1
    store.apply([change("H", revision=1)], "revision-local")
    assert not store.read("H")["pending_review"]
    assert store.read("J")["pending_review"]
    store.apply([change("U", revision=1, retired=True)], "retiro")
    assert store.read("U")["retired"]
    assert "U" not in [r["id"] for r in store.query()["items"]]
    assert len(KnowledgeStore(store.path, store.workspace).history("U")["items"]) == 2
    with closing(sqlite3.connect(store.path)) as db, pytest.raises(sqlite3.IntegrityError):
        db.execute("DELETE FROM revisions")


@pytest.mark.parametrize("problem", ["stale", "missing", "wrong_kind", "cycle", "source", "duplicate", "retired"])
def test_invalid_batches_rollback_everything(tmp_path, problem):
    store = make_store(tmp_path)
    store.apply(foundations(), "initial")
    before = store.export()
    bad = change("V", references=[ref("absent")], proposition="V", status="open")
    if problem == "stale":
        bad = change("H", revision=0)
    elif problem == "wrong_kind":
        bad = change("W", "argument", premises=[ref("H")], inference="wrong", conclusion=ref("E"))
    elif problem == "cycle":
        bad = change("C", "relation", source=ref("E"), target=ref("J"), relation="depends_on")
    elif problem == "source":
        bad = change("X", "evidence", observation="x", source="../private.md#L1", date=None,
                     period=None, currency=None, units=None)
    elif problem == "duplicate":
        bad = change("new")
    elif problem == "retired":
        bad = change("Z", retired=True)
    with pytest.raises(ValueError):
        store.apply([change("new"), bad], "invalid")
    assert store.export() == before


def test_support_objection_and_relation_history(tmp_path):
    store = make_store(tmp_path)
    store.apply(foundations(), "initial")
    store.apply([change("S", "relation", source=ref("U"), target=ref("H"), relation="supports"),
                 change("O", "relation", source=ref("U"), target=ref("H"), relation="objects")], "debate")
    assert {"H", "J"} <= set(store.impact("U")["affected"])
    assert store.read("H")["data"]["status"] == "open"
    store.apply([change("S", "relation", 1, True, source=ref("U"), target=ref("H"), relation="supports")], "retire")
    assert len(store.history("S")["items"]) == 2
    assert store.read("O")["retired"] is False


def test_relation_pin_review_does_not_reinvalidate_reviewed_judgment(tmp_path):
    store = make_store(tmp_path)
    store.apply([change("E"), change("H"), change("S", "relation", source=ref("E"), target=ref("H"), relation="supports")], "initial")
    store.apply([change("E", revision=1)], "new-evidence")
    assert store.read("H")["pending_review"]
    store.apply([change("H", revision=1)], "review-judgment")
    store.apply([change("S", "relation", 1, source=ref("E", 2), target=ref("H", 2), relation="supports")], "review-link")
    assert not store.read("H")["pending_review"]
    assert not store.read("S")["pending_review"]


def test_retirement_cannot_rewrite_content_or_remove_unknown_reference(tmp_path):
    store = make_store(tmp_path)
    store.apply([change("E"), change("H"), change("S", "relation", source=ref("E"), target=ref("H"), relation="supports")], "initial")
    before = store.export()
    with pytest.raises(ValueError, match="preserve"):
        store.apply([change("S", "relation", 1, True, source=ref("E"), target=ref("unknown"), relation="supports")], "retire")
    assert store.export() == before


def test_relation_metadata_does_not_create_a_foundation_cycle(tmp_path):
    store = make_store(tmp_path)
    store.apply([change("E"), change("H", proposition="H", status="open", references=[ref("S")]),
                 change("S", "relation", source=ref("E"), target=ref("H"), relation="supports")], "initial")
    assert store.read("H")["data"]["references"] == [ref("S")]
    with pytest.raises(ValueError, match="#locator"):
        store.apply([change("V", "evidence", observation="x", source="entradas/base.md#", date=None,
                            period=None, currency=None, units=None)], "invalid")


def test_cross_process_recovery_and_capture_relocation(tmp_path):
    store = make_store(tmp_path)
    store.apply(foundations(), "initial")
    code = '''
from pathlib import Path
import sys
from research_agent.knowledge import KnowledgeStore
from research_agent.workspace import Workspace
root=Path(sys.argv[1])
s=KnowledgeStore(root/'conocimiento/expediente.sqlite', Workspace(root/'estado'))
assert s.read('A')['data']['conclusion']['id']=='H'
assert s.history('E')['items'][0]['run']=='initial'
'''
    subprocess.run([sys.executable, "-c", code, str(tmp_path)], check=True, capture_output=True)
    captured = tmp_path / "run"
    captured.mkdir()
    for phase in ("inicial", "final"):
        hashes = store.capture(captured, phase)
        (captured / f"conocimiento-{phase}-hashes.json").write_text(json.dumps(hashes), encoding="utf-8")
    relocated = tmp_path / "relocated"
    shutil.copytree(captured, relocated)
    verify_capture(relocated)
    recovered = KnowledgeStore(relocated / "conocimiento-final.sqlite", store.workspace)
    assert recovered.export() == store.export()
    (relocated / "conocimiento-final.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_capture(relocated)


def test_closed_corpus_budget_blocks_search_bypasses(tmp_path):
    writer = Workspace(tmp_path)
    for name in ("a", "b", "c"):
        writer.write_file(f"entradas/{name}.md", "Sensitive content " + name)
    writer.write_file("entradas/catalogo.md", "a,b,c")
    space = Workspace(tmp_path, closed_corpus=True, document_paths=tuple(f"entradas/{n}.md" for n in "abc"), document_limit=2)
    space.read_file("entradas/catalogo.md")
    assert not space.documents_read
    with pytest.raises(ValueError, match="consultation limit"):
        space.search_files("Sensitive")
    assert not space.documents_read
    assert space.search_files("Sensitive", "entradas/a.md")["matches"]
    space.read_file("entradas/A.md")  # Windows case-insensitive aliases do not spend another consultation.
    space.read_file("entradas/b.md")
    with pytest.raises(ValueError):
        space.read_file("entradas/c.md", max_bytes=4)
    for path in ("entradas/a.md", "ENTRADAS/new.md"):
        with pytest.raises(ValueError, match="read-only"):
            space.write_file(path, "changed")
    assert len(space.documents_read) == 2


def test_fixed_mode_and_default_compatibility(tmp_path):
    root = tmp_path / "exp"
    prompts = prepare_experiment(root, new=True, knowledge_mode="argumentative", tool_profile="closed-corpus")
    assert len(prompts) == 3
    assert prepare_experiment(root, new=False) == prompts
    for config in ({"knowledge_mode": "markdown"}, {"tool_profile": "live"}):
        with pytest.raises(ValueError, match="Continuation"):
            prepare_experiment(root, new=False, **config)
    (root / "experimento.json").unlink()
    with pytest.raises(ValueError, match="configuration is missing"):
        prepare_experiment(root, new=False)
    default = tmp_path / "default"
    assert len(prepare_experiment(default, new=True)) == 2
    (default / "experimento.json").unlink()  # historical experiment
    assert len(prepare_experiment(default, new=False)) == 2
    with pytest.raises(ValueError):
        prepare_experiment(default, new=False, knowledge_mode="argumentative")


def test_literal_id_retrieval_filters_pagination_and_retirement(tmp_path):
    store = make_store(tmp_path)
    store.apply([change("ford_refinancing_risk_2030_31", proposition="Liquidez condicionada", status="open", references=[]),
                 change("ford_second", proposition="Información distinta", status="open", references=[]),
                 change("other", "assessment", judgment="Ford requiere más evidencia", scope="Prueba", references=[])], "initial")
    result = store.query(kind="hypothesis", text="FORD_REFINANCING_RISK_2030_31")
    assert [r["id"] for r in result["items"]] == ["ford_refinancing_risk_2030_31"]
    assert store.query(kind="assessment", text="ford_refinancing_risk_2030_31")["items"] == []
    assert len(store.query(text="Ford")["items"]) == 3
    assert store.query(text="ford refinancing risk 2030 2031")["items"] == []  # Not semantic/token search.
    first = store.query(kind="hypothesis", text="ford", limit=1)
    second = store.query(kind="hypothesis", text="ford", offset=first["next_offset"], limit=1)
    assert first["items"][0]["id"] != second["items"][0]["id"] and second["next_offset"] is None
    row = store.read("ford_refinancing_risk_2030_31")
    store.apply([change(row["id"], revision=1, retired=True, **row["data"])], "retire")
    assert not store.query(text=row["id"])["items"]
    assert store.read(row["id"], 1)["data"] == row["data"]


def test_recovery_conflict_retry_and_history_across_fresh_processes(tmp_path):
    """Use the real tool boundary; every step loses Python/chat state."""
    make_store(tmp_path)
    script = r'''
import asyncio, json, sys
from pathlib import Path
from research_agent.workspace import Workspace
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.integrations.file_tools import register_files
from research_agent.knowledge import KnowledgeStore, register_knowledge
from runtime_contracts.llm import ResponseFunctionCall
from runtime_contracts.json import thaw_json
root=Path(sys.argv[1]); phase=int(sys.argv[2]); space=Workspace(root/'estado')
rec=RunRecorder(root/'ejecuciones',experiment=root,run_name=f'paso-{phase}')
reg=ToolRegistry(rec); register_files(reg,space)
store=KnowledgeStore(root/'conocimiento/expediente.sqlite',space); register_knowledge(reg,store)
rec.start(str(phase),{}); rec.snapshot(space)
def change(id,revision,value):
    return {'id':id,'kind':'hypothesis','expected_revision':revision,'retired':False,'reason':'Correction' if revision else 'Initial',
            'data':{'proposition':value,'status':'conditional','references':[]}}
async def execute():
    results=[]
    async def call(name,args):
        result=await reg.execute(ResponseFunctionCall(str(len(results)),name,args)); results.append(thaw_json(result.payload));return result.payload
    id='ford_refinancing_risk_2030_31'
    if phase==1:
        await call('knowledge_apply',{'changes':[change(id,0,'Caja no restringida 13; vencimientos 10')]})
    elif phase==2:
        await call('knowledge_query',{'kind':'hypothesis','text':id,'offset':0,'limit':20})
        await call('knowledge_read',{'id':id,'revision':0})
    elif phase==3:
        await call('knowledge_apply',{'changes':[change('must_rollback',0,'Temporary'),change(id,0,'Caja 11')]})
        current=await call('knowledge_read',{'id':id,'revision':0})
        await call('knowledge_apply',{'changes':[change(id,current['value']['revision'],'Caja no restringida 11; vencimientos 10')]})
    else:
        await call('knowledge_read',{'id':id,'revision':1})
        await call('knowledge_read',{'id':id,'revision':0})
        await call('knowledge_history',{'id':id,'offset':0,'limit':20})
        await call('knowledge_query',{'kind':'','text':'must_rollback','offset':0,'limit':20})
    rec.snapshot(space)
    print(json.dumps(results,ensure_ascii=False))
asyncio.run(execute())
'''
    results = []
    for phase in range(1, 5):
        proc = subprocess.run([sys.executable, "-X", "utf8", "-c", script, str(tmp_path), str(phase)],
                              capture_output=True, text=True, encoding="utf-8")
        assert proc.returncode == 0, proc.stderr
        results.append(json.loads(proc.stdout))
    assert results[0][0]["ok"]
    assert results[1][0]["value"]["items"][0]["id"] == "ford_refinancing_risk_2030_31"
    assert results[1][1]["value"]["revision"] == 1
    conflict, recovered, updated = results[2]
    assert not conflict["ok"] and "knowledge_read" in conflict["message"] and "current 1" in conflict["message"]
    assert recovered["value"]["revision"] == 1 and updated["ok"]
    old, current, history, rollback = results[3]
    assert "13" in old["value"]["data"]["proposition"] and "11" in current["value"]["data"]["proposition"]
    assert [r["revision"] for r in history["value"]["items"]] == [1, 2]
    assert not rollback["value"]["items"]
    for run in (tmp_path / "ejecuciones").iterdir():
        verify_capture(run)


def test_corrected_catalog_preserves_original_and_short_probe(tmp_path):
    original = load_suite(ROOT / "benchmarks/longitudinal-v2")
    corrected = load_suite(ROOT / "benchmarks/longitudinal-v2-1")
    assert corrected.id == "longitudinal-v2-1" and len(corrected.cases) == 3
    assert all(len(c.sessions) == 6 for c in corrected.cases)
    # No other stimulus, rubric or budget changed in the new version.
    for path in original.files():
        relative = path.relative_to(original.root)
        if relative.as_posix() not in {"suite.yaml", "S1/inputs/cartera.md"}:
            assert path.read_bytes() == (corrected.root / relative).read_bytes()
    assert corrected.execution == original.execution
    probe = load_suite(ROOT / "benchmarks/argumentative-continuity-v1")
    assert len(probe.cases) == 1 and len(probe.cases[0].sessions) == 4
    assert probe.execution == corrected.execution


def test_new_operating_instructions_are_copied_without_updating_old_experiments(tmp_path):
    old_root = tmp_path / "old"
    prepare_experiment(old_root, new=True, knowledge_mode="argumentative")
    old_copy = old_root / "instrucciones/expediente.md"
    old_copy.write_text("Frozen prior instructions", encoding="utf-8")
    prepare_experiment(old_root, new=False)
    assert old_copy.read_text(encoding="utf-8") == "Frozen prior instructions"
    new_root = tmp_path / "new"
    prepare_experiment(new_root, new=True, knowledge_mode="argumentative")
    assert (new_root / "instrucciones/expediente.md").read_text(encoding="utf-8") == (ROOT / "src/research_agent/prompts/argumentative.md").read_text(encoding="utf-8")


def make_agent(root, turns, limits=None):
    prompts = prepare_experiment(root, new=True, knowledge_mode="argumentative", tool_profile="closed-corpus")
    space = Workspace(root / "estado", closed_corpus=True)
    recorder = RunRecorder(root / "ejecuciones", experiment=root)
    tools = ToolRegistry(recorder)
    register_files(tools, space)
    store = KnowledgeStore(root / "conocimiento/expediente.sqlite", space)
    register_knowledge(tools, store)

    class Client:
        def __init__(self):
            self.turns = iter(turns)
            self.requests = []

        async def respond(self, **kwargs):
            self.requests.append(kwargs)
            value = next(self.turns)
            if isinstance(value, BaseException):
                raise value
            return value

    return AgentA(Client(), tools, space, recorder, limits or AgentLimits(),
                  configuration={"state_mode": "argumentative"}, instructions=prompts), store


def turn(name, **kwargs):
    call = ResponseFunctionCall("test", name, kwargs)
    return ResponseTurn([call], "", call)


def test_structured_writes_during_consolidation_and_final_capture(tmp_path):
    done = ResponseTurn([AssistantResponse("Entregado")], "Entregado", None)
    agent, store = make_agent(tmp_path / "exp", [turn("knowledge_apply", changes=[change("H")]),
                            turn("knowledge_read", id="H", revision=0), done], AgentLimits(max_llm_calls=4))
    result = asyncio.run(agent.run(AgentRequest("Pregunta", "exp", "conv")))
    assert result.status == "completed" and not result.state.capture_errors
    assert store.read("H")["revision"] == 1
    phases = [x.payload["execution_budget"]["phase"] for request in agent.client.requests for x in request["input_items"]
              if isinstance(x, ConversationContext) and "execution_budget" in x.payload]
    assert "consolidation" in phases
    assert "knowledge_apply" in {s.name for s in agent.client.requests[1]["tools"]}
    verify_capture(agent.recorder.current)
    assert store.export()["revisions"][0]["run"] == agent.recorder.current.name


def test_cancellation_does_not_schedule_late_sqlite_writer(tmp_path):
    agent, store = make_agent(tmp_path / "exp", [turn("knowledge_apply", changes=[change("H")]), asyncio.CancelledError()])
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(agent.run(AgentRequest("Pregunta", "exp", "conv")))
    before = store.export()
    assert len(before["revisions"]) == 1
    assert store.export() == before
    verify_capture(agent.recorder.current)


def test_final_phase_refuses_knowledge_mutation(tmp_path):
    agent, store = make_agent(tmp_path / "exp", [turn("knowledge_apply", changes=[change("H")])], AgentLimits(max_llm_calls=1))
    result = asyncio.run(agent.run(AgentRequest("Pregunta", "exp", "conv")))
    assert result.status == "interrupted"
    assert not store.export()["revisions"]
    assert not agent.client.requests[0]["tools"]


def test_closed_bootstrap_never_builds_remote_tools(tmp_path, monkeypatch):
    import infra.llm_factory as factory_module
    import sqlalchemy
    from research_agent.bootstrap import build_agent
    from infra.llm_profiles import LLMProfile

    class Factory:
        def __init__(self, settings):
            pass

        def conversation(self, profile):
            return object()

        async def aclose(self):
            pass

    monkeypatch.setattr(factory_module, "LLMFactory", Factory)
    monkeypatch.setattr(factory_module, "configured_profile", lambda *args: LLMProfile("lab", "openai", "simulated"))
    monkeypatch.setattr(sqlalchemy, "create_engine", lambda *args, **kwargs: pytest.fail("Database construction"))

    async def check():
        root = tmp_path / "exp"
        prepare_experiment(root, new=True, knowledge_mode="argumentative", tool_profile="closed-corpus")
        async with build_agent(root / "estado", root / "ejecuciones", experiment=root,
                               knowledge_mode="argumentative", tool_profile="closed-corpus") as agent:
            names = {s.name for s in agent.tools.specs()}
            assert names == {"list_files", "read_file", "search_files", "write_file", "write_markdown", "read_artifact",
                             "calculate", "knowledge_query", "knowledge_read", "knowledge_history", "knowledge_apply", "knowledge_impact"}
        with pytest.raises(ValueError, match="fixed experiment"):
            async with build_agent(root / "estado", root / "ejecuciones", experiment=root):
                pass
        monkeypatch.setattr(factory_module, "configured_profile", lambda *args: pytest.fail("Read environment profile"))
        async with build_agent(root / "estado", root / "ejecuciones", experiment=root,
                               knowledge_mode="argumentative", tool_profile="closed-corpus",
                               profile_overrides={"provider": "openai", "model": "controlled", "reasoning_effort": "medium", "max_output_tokens": 4000}) as agent:
            assert agent.configuration["model"] == "controlled"

    asyncio.run(check())


def test_v2_controls_and_budget_survive_runner(tmp_path):
    from test_benchmark import fake_cli
    suite = load_suite(ROOT / "benchmarks/longitudinal-v2")
    assert len(suite.cases) == 3 and all(len(c.sessions) == 6 for c in suite.cases)
    with pytest.raises(ValueError, match="explicit"):
        run_suite(suite, tmp_path / "missing")
    assert not (tmp_path / "missing").exists()
    profile = {"provider": "openai", "model": "simulated", "reasoning_effort": "medium", "max_output_tokens": 4000}
    calls = []

    def worker(command, out, err):
        runtime = json.loads(Path(command[command.index("--runtime-config")+1]).read_text(encoding="utf-8"))
        assert runtime["limits"] == asdict(AgentLimits())
        assert runtime["profile"] == profile
        exp = Path(command[command.index("--experiment")+1])
        assert json.loads((exp / "experimento.json").read_text())["tool_profile"] == "closed-corpus"
        assert not list((exp / "estado").rglob("rubric.md"))
        calls.append(runtime)
        return fake_cli(command, out, err)

    campaign, code = run_suite(suite, tmp_path / "out", selected="S1", launcher=worker, compact=False, profile=profile)
    assert code == 0
    assert calls[2]["document_limit"] == 2 and len(calls[2]["document_paths"]) == 6
    manifest = json.loads((campaign / "manifiesto.json").read_text())
    assert manifest["condition"] == "A0" and manifest["profile"] == profile
    assert all((campaign / key).exists() for key in manifest["definitions_sha256"])


def test_knowledge_roundtrip_compact_and_corruption(tmp_path):
    from test_benchmark import catalog, fake_cli
    from research_agent.benchmark_evidence import save
    from research_agent.benchmark_archive import export_campaign, inspect_compact

    def worker(command, out, err):
        code = fake_cli(command, out, err)
        exp = Path(command[command.index("--experiment")+1])
        session = command[command.index("--run-name")+1]
        run = exp / "ejecuciones" / session
        manifest = json.loads((run / "manifiesto.json").read_text())
        manifest["configuration"] = {"state_mode": "argumentative"}
        save(run / "manifiesto.json", manifest)
        store = KnowledgeStore(exp / "conocimiento/expediente.sqlite", Workspace(exp / "estado"))
        for phase in ("inicial", "final"):
            if phase == "final":
                store.apply([change("H", revision=0 if session == "s0" else 1)], session)
            save(run / f"conocimiento-{phase}-hashes.json", store.capture(run, phase))
        return code

    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1)), tmp_path / "out", condition="A1", launcher=worker)
    assert code == 0
    exported = export_campaign(campaign, tmp_path / "export")
    summary = json.loads((exported / "resumen.json").read_text())
    session = summary["sessions"][-1]
    run = exported / session["run_directory"]
    verify_capture(run)
    assert inspect_compact(exported, run, "C0", "s1")[0]["capture_complete"]
    (run / "conocimiento-final.sqlite").write_bytes(b"broken")
    assert not inspect_compact(exported, run, "C0", "s1")[0]["capture_complete"]


def test_argumentative_cli_in_fresh_processes_with_simulated_llm(tmp_path):
    from test_benchmark import catalog
    from research_agent.benchmark import launch
    from research_agent.benchmark_archive import records
    worker = tmp_path / "worker.py"
    worker.write_text('''
import sys
from research_agent import cli
import infra.llm_factory as factory
from infra.llm_profiles import LLMProfile
from runtime_contracts.llm import AssistantResponse, ResponseFunctionCall, ResponseTurn
from runtime_contracts.execution import current_run_context
from infra.adapters.llm_trace import LLMCallTrace

class Client:
    n=0
    async def respond(self, **request):
        self.n+=1
        session=sys.argv[sys.argv.index('--run-name')+1]
        if self.n==1:
            item=ResponseFunctionCall('query','knowledge_query',{'kind':'hypothesis','text':'','offset':0,'limit':20})
        elif self.n==2:
            change={'id':'H','kind':'hypothesis','expected_revision':0 if session=='s0' else 1,
                    'retired':False,'reason':'New session','data':{'proposition':'Continuity', 'status':'open','references':[]}}
            item=ResponseFunctionCall('save','knowledge_apply',{'changes':[change]})
        else:
            item=AssistantResponse('done')
        turn=ResponseTurn([item], 'done' if self.n==3 else '', item if self.n<3 else None)
        LLMCallTrace(operation='conversation',model='simulated',provider_request={'input':[]}).emit(
            context=current_run_context(),response={'output':[]},result=turn,operational_output=None,
            status='success',error_type=None,duration_ms=1)
        return turn

class Factory:
    def __init__(self, settings): pass
    def conversation(self, profile): return Client()
    async def aclose(self): pass
factory.LLMFactory=Factory
factory.configured_profile=lambda *args: LLMProfile('lab','openai','simulated')
raise SystemExit(cli.main())
''', encoding="utf-8")
    suite = load_suite(catalog(tmp_path, cases=1))
    # Add closed-corpus controls without mutating the source fixture.
    from dataclasses import replace
    suite = replace(suite, execution={"tool_profile": "closed-corpus", "limits": asdict(AgentLimits())})
    # Persist definition: run_suite deliberately reloads frozen definitions.
    import yaml
    path = suite.root / "suite.yaml"
    raw = yaml.safe_load(path.read_text())
    raw["execution"] = suite.execution
    path.write_text(yaml.safe_dump(raw))
    profile = {"provider": "openai", "model": "simulated", "reasoning_effort": "medium", "max_output_tokens": 4000}

    def worker_launch(command, out, err):
        return launch([sys.executable, str(worker), *command[3:]], out, err)

    campaign, code = run_suite(load_suite(suite.root), tmp_path / "out", condition="A1", profile=profile, launcher=worker_launch)
    assert code == 0, (campaign / "resumen.json").read_text()
    summary = json.loads((campaign / "resumen.json").read_text())
    for session in summary["sessions"]:
        run = campaign / session["run_directory"]
        verify_capture(run)
        trace = records(run)
        query = next(r for r in trace if r["kind"] == "tool" and r["call"]["name"] == "knowledge_query")
        from research_agent.benchmark_archive import delivered_result
        items = delivered_result(campaign, query)["value"]["items"]
        assert len(items) == (0 if session["session_id"] == "s0" else 1)
    state = KnowledgeStore(campaign / "casos/C0/conocimiento/expediente.sqlite", Workspace(campaign / "casos/C0/estado"))
    assert state.read("H")["revision"] == 2
