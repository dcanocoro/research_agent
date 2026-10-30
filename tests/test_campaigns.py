from __future__ import annotations

import gzip
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from research_campaigns.runner import launch
from research_campaigns.cli import main
from research_campaigns.suite import run_suite
from research_campaigns.catalog import load_suite
from research_campaigns.evidence import inspect_run
from research_campaigns.storage import save
from research_campaigns.report import report
from research_agent.workspace import Workspace


ROOT = Path(__file__).resolve().parents[1]


from support import catalog, fake_cli


def test_transaction_journal_directory_is_not_a_native_run(tmp_path):
    def worker(command, out, err):
        experiment = Path(command[command.index("--experiment") + 1])
        (experiment / "ejecuciones/transacciones").mkdir(exist_ok=True)
        return fake_cli(command, out, err)
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)),
                               tmp_path / "out", launcher=worker)
    assert code == 0
    session = json.loads((campaign / "campaign.json").read_bytes())["sessions"][0]
    assert session["capture_complete"] and session["run_directory"].endswith("s0")


def test_report_uses_frozen_runtime_of_each_attempt(tmp_path, monkeypatch):
    import importlib
    module = importlib.import_module("research_campaigns.report")
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)),
                               tmp_path / "out", launcher=fake_cli)
    assert code == 0
    record = json.loads((campaign / "campaign.json").read_bytes())
    record["runtime"] = {"profile": {"model": "later-profile"}}
    record["runtime_by_attempt"] = {record["sessions"][0]["id"]: {}}
    original = module.inspect_run
    observed = []
    def spy(root, run, runtime):
        observed.append(runtime)
        return original(root, run, runtime)
    monkeypatch.setattr(module, "inspect_run", spy)
    module.report(campaign, record)
    assert observed == [{}]


def test_validate_catalog_without_service_imports(tmp_path):
    fixture = catalog(tmp_path, cases=3, sessions=6)
    code = """
import sys
class Block:
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'infra','findata','engine','finmate','api'}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, Block())
from research_campaigns.cli import main
raise SystemExit(main(['validate', sys.argv[1]]))
"""
    result = subprocess.run([sys.executable, "-c", code, str(fixture)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "cases=3; sessions=18" in result.stdout


@pytest.mark.parametrize("package", ["research_agent", "research_campaigns"])
def test_campaign_output_cannot_overlap_either_source_package(tmp_path, package):
    from importlib.util import find_spec
    source = Path(find_spec(package).origin).parent
    output = source / "forbidden-campaign-output"
    with pytest.raises(ValueError):
        run_suite(load_suite(catalog(tmp_path)), output, launcher=fake_cli)
    assert not output.exists()


@pytest.mark.parametrize("change", ["duplicate_case", "duplicate_session", "missing", "escape", "overwrite", "device", "duplicate_yaml"])
def test_invalid_catalog(tmp_path, change):
    root = catalog(tmp_path)
    path = root / "C0/case.yaml"
    raw = yaml.safe_load(path.read_text())
    if change == "duplicate_case":
        suite = yaml.safe_load((root / "suite.yaml").read_text())
        suite["cases"].append(suite["cases"][0])
        (root / "suite.yaml").write_text(yaml.safe_dump(suite))
    elif change == "duplicate_yaml":
        path.write_text(path.read_text() + "\nid: another\n")
    else:
        if change == "duplicate_session":
            raw["sessions"][1]["id"] = raw["sessions"][0]["id"]
        elif change == "missing":
            raw["sessions"][0]["publish"]["entradas/initial.md"] = "absent.md"
        elif change == "escape":
            raw["rubric"] = "../C1/rubric.md"
        elif change == "overwrite":
            raw["sessions"][1]["publish"] = {"entradas/INITIAL.md": "future.md"}
        elif change == "device":
            raw["sessions"][1]["publish"] = {"entradas/con.md": "future.md"}
        path.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError):
        load_suite(root)


def test_isolation_publication_and_extraction(tmp_path):
    root = catalog(tmp_path)
    seen = []
    def worker(command, out, err):
        exp = Path(command[command.index("--experiment") + 1])
        session = command[command.index("--run-name") + 1]
        state = Workspace(exp / "estado", create=False)
        assert not list((exp / "estado").rglob("rubric.md"))
        with pytest.raises(ValueError):
            state.read_file("../../definiciones/C0/rubric.md")
        if session == "s0":
            assert not (state.root / "entradas/future.md").exists()
            state.write_file("indice.md", "AGENT INDEX")
            state.write_file("evaluation.md", "remembered")
        else:
            assert state.read_file("indice.md")["text"] == "AGENT INDEX"
            assert state.read_file("evaluation.md")["text"] == "remembered"
            assert state.read_file("entradas/future.md")["text"] == "future evidence"
        seen.append((exp, session))
        return fake_cli(command, out, err)
    campaign, code = run_suite(load_suite(root), tmp_path / "out", launcher=worker)
    assert code == 0 and len(seen) == 4
    summary = json.loads((campaign / "campaign.json").read_text())
    assert sum(s["status"] == "completed" for s in summary["sessions"]) == 4
    assert sum(s["llm_calls"] for s in summary["sessions"]) == 4
    assert len({exp for exp, _ in seen}) == 2
    original = (campaign / "campaign.json").read_bytes()
    report(campaign)
    assert (campaign / "campaign.json").read_bytes() == original
    assert len(list((campaign / "casos").glob("*/ejecuciones/*/respuesta.md"))) == 4
    second, code = run_suite(load_suite(root), tmp_path / "second", selected="C0", launcher=worker)
    assert code == 0 and second != campaign
    assert (campaign / "campaign.json").read_bytes() == original


@pytest.mark.parametrize("failure", ["operational", "missing_payload", "truncated_payload", "corrupt_event", "interruption", "no_run"])
def test_failures_preserve_evidence_and_skip_dependents(tmp_path, failure):
    root = catalog(tmp_path)
    attempted = []
    def worker(command, out, err):
        exp = Path(command[command.index("--experiment") + 1])
        session = command[command.index("--run-name") + 1]
        attempted.append((exp.name, session))
        if exp.name != "C0":
            return fake_cli(command, out, err)
        if failure == "no_run":
            out.write_text("partial")
            err.write_text("startup error")
            return 1
        code = fake_cli(command, out, err, status="failed" if failure == "operational" else "completed",
                        missing="trazas/modelo-0001.json.gz" if failure == "missing_payload" else None)
        if failure == "truncated_payload":
            path = exp / "ejecuciones" / session / "trazas/modelo-0001.json.gz"
            path.write_bytes(path.read_bytes()[:10])
        if failure == "corrupt_event":
            with (exp / "ejecuciones" / session / "eventos.jsonl").open("a") as stream:
                stream.write("\n{broken")
        if failure == "interruption":
            raise KeyboardInterrupt
        return code
    campaign, code = run_suite(load_suite(root), tmp_path / "out", launcher=worker)
    assert code == 1
    summary = json.loads((campaign / "campaign.json").read_text())
    assert summary["sessions"][1]["status"] == "not_executed"
    assert summary["sessions"][0]["status"] == ("interrupted" if failure == "interruption" else "failed")
    assert (campaign / summary["sessions"][0]["stdout"]).exists()
    assert len(attempted) == (1 if failure == "interruption" else 3)
    if failure not in {"operational", "interruption"}:
        assert summary["sessions"][0]["capture_errors"]


def test_publication_cannot_overwrite_agent_file(tmp_path):
    def worker(command, out, err):
        exp = Path(command[command.index("--experiment") + 1])
        (exp / "estado/entradas/future.md").write_text("agent content")
        return fake_cli(command, out, err)
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1)), tmp_path / "out", launcher=worker)
    summary = json.loads((campaign / "campaign.json").read_text())
    assert code == 1 and summary["sessions"][1]["error"] == "FileExistsError"
    assert (campaign / "casos/C0/estado/entradas/future.md").read_text() == "agent content"


def test_modified_stimulus_is_reported(tmp_path):
    def worker(command, out, err):
        exp = Path(command[command.index("--experiment") + 1])
        (exp / "estado/entradas/initial.md").write_text("modified")
        return fake_cli(command, out, err)
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out", launcher=worker)
    assert code == 0  # Data mutation is evidence for review, not an invented semantic verdict.
    session = json.loads((campaign / "campaign.json").read_text())["sessions"][0]
    assert session["input_modifications"][0]["path"] == "entradas/initial.md"


def test_longitudinal_suite_with_simulated_agent_and_no_providers(tmp_path):
    suite = load_suite(catalog(tmp_path, cases=3, sessions=6))
    attempted = []
    def worker(command, out, err):
        exp = Path(command[command.index("--experiment") + 1])
        session_id = command[command.index("--run-name") + 1]
        case = next(c for c in suite.cases if c.id == exp.name)
        index = next(i for i, session in enumerate(case.sessions) if session.id == session_id)
        expected = {p.target for session in case.sessions[:index + 1] for p in session.publish}
        actual = {p.relative_to(exp / "estado").as_posix() for p in (exp / "estado/entradas").rglob("*") if p.is_file()}
        assert actual == expected
        assert not any("rubric" in p.name for p in (exp / "estado").rglob("*"))
        attempted.append((exp.name, session_id))
        return fake_cli(command, out, err)
    campaign, code = run_suite(suite, tmp_path / "out", launcher=worker)
    assert code == 0
    assert attempted == [(case.id, session.id) for case in suite.cases for session in case.sessions]
    assert len(attempted) == 18
    sources = json.loads((campaign / "campaign.json").read_text())["runtime"]["source"]
    assert "agent.py" in sources["research_agent"] and "runner.py" in sources["research_campaigns"]


def test_regeneration_reports_missing_capture_without_changing_sessions(tmp_path):
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out", launcher=fake_cli)
    assert code == 0
    session_file = campaign / "campaign.json"
    before = session_file.read_bytes()
    session = json.loads(before)["sessions"][0]
    (campaign / session["run_directory"] / "trazas/modelo-0001.json.gz").unlink()
    report(campaign)
    assert "FileNotFoundError" in (campaign / "README.md").read_text(encoding="utf-8")
    assert session_file.read_bytes() == before


@pytest.mark.parametrize("breakdown", [None, {"research": 1, "consolidation": 0, "review": 0}])
def test_phase_breakdown_and_legacy_results_are_readable_in_report(tmp_path, breakdown):
    def worker(command, out, err):
        result = fake_cli(command, out, err)
        experiment = Path(command[command.index("--experiment") + 1])
        run_name = command[command.index("--run-name") + 1]
        path = experiment / "ejecuciones" / run_name / "resultado.json"
        value = json.loads(path.read_bytes())
        if breakdown is not None:
            value["llm_calls_by_phase"] = breakdown
            save(path, value)
        return result

    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out", launcher=worker)
    assert code == 0
    session = json.loads((campaign / "campaign.json").read_bytes())["sessions"][0]
    assert session["llm_calls_by_phase"] == (breakdown or {})
    view = (campaign / "README.md").read_text(encoding="utf-8")
    assert "LLM total / herramientas" in view
    assert ("1 / 0 / 0" if breakdown else "desconocido / desconocido / desconocido") in view


def test_real_subprocess_sessions_use_agent_cli_and_native_recorder(tmp_path):
    # The worker substitutes only the composition of external services in this test.
    # The runner, CLI, AgentA, file tools, recorder and scoped provider capture are real.
    worker = tmp_path / "worker.py"
    worker.write_text('''
import os
from contextlib import asynccontextmanager
from research_agent import cli
from research_agent.agent import AgentA
from research_agent.contracts import AgentLimits
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from research_agent.integrations.file_tools import register_files
from runtime_contracts.llm import AssistantResponse, ResponseTurn, ResponseFunctionCall
from runtime_contracts.execution import current_run_context
from infra.adapters.llm_trace import LLMCallTrace

@asynccontextmanager
async def builder(workspace, runs, limits=AgentLimits(), **kwargs):
    state_tools = kwargs.pop('state_tools', 'legacy')
    space = Workspace(workspace)
    recorder = RunRecorder(runs, **kwargs)
    tools = ToolRegistry(recorder)
    register_files(tools, space, state_tools=state_tools)
    class Client:
        n = 0
        async def respond(self, **request):
            self.n += 1
            if self.n == 1:
                item = ResponseFunctionCall('read', 'read_file', {'path':'indice.md','offset':0,'max_bytes':8192})
            elif self.n == 2:
                previous = (space.root/'remembered.md').read_text() if (space.root/'remembered.md').exists() else ''
                item = ResponseFunctionCall('write', 'write_file', {'path':'remembered.md','content':previous+str(os.getpid())+'\\n'})
            else:
                item = AssistantResponse('done')
            turn = ResponseTurn([item], 'done' if self.n == 3 else '', item if self.n < 3 else None)
            LLMCallTrace(operation='conversation', model='controlled', provider_request={'input':[]}).emit(
                context=current_run_context(), response={'output':[]}, result=turn, operational_output=None,
                status='success', error_type=None, duration_ms=1)
            return turn
    yield AgentA(Client(), tools, space, recorder, limits)
cli.build_agent = builder
raise SystemExit(cli.main())
''', encoding="utf-8")
    def subprocess_worker(command, out, err):
        return launch([sys.executable, str(worker), *command[3:]], out, err)
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1)), tmp_path / "out", launcher=subprocess_worker)
    assert code == 0, (campaign / "campaign.json").read_text()
    pids = (campaign / "casos/C0/estado/remembered.md").read_text().splitlines()
    assert len(pids) == 2 and pids[0] != pids[1]
    sessions = json.loads((campaign / "campaign.json").read_text())["sessions"]
    for session in sessions:
        run = campaign / session["run_directory"]
        capture = inspect_run(campaign, run)
        assert capture["capture_complete"] and capture["llm_calls"] == 3 and capture["tool_calls"] == 2
        assert (run / "respuesta.md").read_text() == "done"


def test_invalid_cli_is_exit_two_without_output(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["run", str(catalog(tmp_path)), "--case", "absent", "--output", str(tmp_path / "out")])
    assert exc.value.code == 2
    assert not (tmp_path / "out").exists()


def tool_fixture(command, out, err, *, limited=False):
    """Native tool success with both raw and delivered results plus historical state."""
    code = fake_cli(command, out, err)
    exp = Path(command[command.index("--experiment") + 1])
    session = command[command.index("--run-name") + 1]
    run = exp / "ejecuciones" / session
    raw = [{"text": "évidence " * (6000 if limited else 2)}]
    body = json.dumps(raw, ensure_ascii=False, sort_keys=True)
    material_path = exp / "estado/materiales/source.json"
    material_path.write_text(body, encoding="utf-8")
    call = {"call_id": "call-1", "name": "read_document", "arguments": {"url": "https://example.test"},
            "continuation": {"provider": "test", "opaque": [1, 2]}}
    delivered = {"ok": True, "artifact_ref": "materiales/source.json", "material_ref": "materiales/source.json",
                 "value": {"limited": True, "artifact_ref": "materiales/source.json"} if limited else raw}
    save(run / "trazas/resultado-herramienta-0001.json", raw)
    save(run / "trazas/herramienta-0004.json", {"call": call, "result": delivered})
    native = [json.loads(l) for l in (run / "eventos.jsonl").read_text().splitlines()]
    native[1:1] = [
        {"event": "lab.tool.started", "run_id": native[0]["run_id"], "call_id": "call-1", "tool_name": "read_document",
         "arguments": call["arguments"], "occurred_at": "2026-10-20T00:00:01.1+00:00"},
        {"event": "lab.tool.completed", "run_id": native[0]["run_id"], "call_id": "call-1", "tool_name": "read_document",
         "occurred_at": "2026-10-20T00:00:01.2+00:00"}]
    (run / "eventos.jsonl").write_text("\n".join(json.dumps(e) for e in native), encoding="utf-8")
    result = json.loads((run / "resultado.json").read_text())
    result["tool_calls"] = 1
    save(run / "resultado.json", result)
    save(run / "estado-final.json", {"materiales/source.json": body, "evaluation.md": "Preserved judgement"})
    return code


@pytest.mark.parametrize("limited", [False, True])
def test_native_evidence_and_artifact_pagination_preserved(tmp_path, limited):
    from research_campaigns.storage import digest
    from research_agent.recording import RunRecorder
    root, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out",
                           launcher=lambda c, o, e: tool_fixture(c, o, e, limited=limited))
    assert code == 0
    run = root / "casos/C0/ejecuciones/s0"
    before = {p.relative_to(root): digest(p) for p in root.rglob("*") if p.is_file()}
    report(root)
    assert before == {p.relative_to(root): digest(p) for p in root.rglob("*") if p.is_file()}
    tool = json.loads((run / "trazas/herramienta-0004.json").read_text(encoding="utf-8"))
    state = json.loads((run / "estado-final.json").read_text(encoding="utf-8"))
    original = json.loads((run / "trazas/resultado-herramienta-0001.json").read_text(encoding="utf-8"))
    assert original == json.loads(state["materiales/source.json"])
    assert tool["result"]["value"] == ({"limited": True, "artifact_ref": "materiales/source.json"} if limited else original)
    recorder = RunRecorder(run.parent)
    page = recorder.read_artifact("archivo/s0/resultado-herramienta-0001.json", max_bytes=31)
    assert page["next_offset"] is not None and page["text"]
    forbidden = {"pasos.jsonl", "steps.json", "extraccion.json", "resumen.json", "ejecucion.json", "trayectoria.jsonl.gz"}
    assert not any(p.name in forbidden for p in root.rglob("*"))
    assert not list((root / "casos").glob("*/ejecuciones/*.stdout.txt"))


@pytest.mark.parametrize("operation", ["extract", "compact", "longitudinal", "prepare", "check"])
def test_retired_commands_rejected(operation):
    with pytest.raises(SystemExit) as error:
        main([operation])
    assert error.value.code == 2


def test_definition_options_and_resume_rejected_without_execution(tmp_path):
    from research_campaigns.cli import definition
    root = catalog(tmp_path)
    (root / "scenario.json").write_text("{}")
    with pytest.raises(ValueError, match="exactly one"):
        definition(root)
    (root / "scenario.json").unlink()
    for option in (["--condition", "baseline"], ["--instructions-dir", str(root)], ["--data", str(root)]):
        with pytest.raises(SystemExit) as error:
            main(["run", str(root), "--output", str(tmp_path / "unused"), *option])
        assert error.value.code == 2 and not (tmp_path / "unused").exists()
    campaign, _ = run_suite(load_suite(root), tmp_path / "campaign", launcher=fake_cli)
    with pytest.raises(SystemExit) as error:
        main(["resume", str(campaign)])
    assert error.value.code == 2
    assert main(["report", str(campaign)]) == 0
    with pytest.raises(FileExistsError):
        run_suite(load_suite(root), campaign, launcher=fake_cli)


def test_atomic_record_preserves_previous_version_on_replace_failure(tmp_path, monkeypatch):
    from research_campaigns.storage import save
    target = tmp_path / "campaign.json"
    save(target, {"status": "prepared"})
    original = Path.replace
    def fail(source, destination):
        if destination == target:
            raise OSError("controlled replace failure")
        return original(source, destination)
    monkeypatch.setattr(Path, "replace", fail)
    with pytest.raises(OSError):
        save(target, {"status": "running"})
    assert json.loads(target.read_text()) == {"status": "prepared"}
    assert list(tmp_path.iterdir()) == [target]
