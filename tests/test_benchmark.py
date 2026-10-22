from __future__ import annotations

import gzip
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from research_agent.benchmark import launch, main, run_suite
from research_agent.benchmark_catalog import load_suite
from research_agent.benchmark_evidence import extract, save
from research_agent.workspace import Workspace


ROOT = Path(__file__).resolve().parents[1]


def catalog(tmp_path, cases=2, sessions=2):
    root = tmp_path / "suite"
    root.mkdir()
    paths = []
    for n in range(cases):
        case = root / f"C{n}"
        case.mkdir()
        (case / "source.md").write_text("initial evidence", encoding="utf-8")
        (case / "future.md").write_text("future evidence", encoding="utf-8")
        (case / "rubric.md").write_text("EVALUATOR ONLY", encoding="utf-8")
        value = {"id": f"C{n}", "title": "Test", "context": "Company", "competencies": ["memory"],
                 "difficulty": "Requires recovery", "rubric": "rubric.md", "sessions": [
                     {"id": f"s{i}", "message": f"Question {i}",
                      "publish": {"entradas/initial.md": "source.md"} if i == 0 else
                                 {"entradas/future.md": "future.md"} if i == 1 else {}}
                     for i in range(sessions)]}
        (case / "case.yaml").write_text(yaml.safe_dump(value), encoding="utf-8")
        paths.append(f"C{n}/case.yaml")
    (root / "suite.yaml").write_text(yaml.safe_dump({"schema_version": "benchmark-v1", "id": "test", "cases": paths}), encoding="utf-8")
    return root


def fake_cli(command, out, err, *, status="completed", missing=None):
    """Small native-format fixture, not a replacement used by the product runner."""
    experiment = Path(command[command.index("--experiment") + 1])
    session = command[command.index("--run-name") + 1]
    run = experiment / "ejecuciones" / session
    run.mkdir()
    (run / "trazas").mkdir()
    out.write_text("arbitrary output; never parsed", encoding="utf-8")
    err.write_text("diagnostic", encoding="utf-8")
    run_id = f"run-{experiment.name}-{session}"
    save(run / "manifiesto.json", {"run_id": run_id})
    save(run / "resultado.json", {"run_id": run_id, "status": status, "stop_reason": "answered", "answer": "done",
                                 "llm_calls": 1, "tool_calls": 0, "state": {"capture_errors": []}})
    save(run / "estado-inicial.json", {})
    save(run / "estado-final.json", {})
    save(run / "conversacion.json", [])
    (run / "peticion.md").write_text(command[3], encoding="utf-8")
    (run / "respuesta.md").write_text("done", encoding="utf-8")
    native = [{"run_id": run_id, "event": "lab.run.started", "occurred_at": "2026-10-20T00:00:00+00:00"},
              {"run_id": run_id, "event": f"lab.run.{status}", "occurred_at": "2026-10-20T00:00:02+00:00"}]
    (run / "eventos.jsonl").write_text("\n".join(json.dumps(e) for e in native), encoding="utf-8")
    event = {"run_id": run_id, "event": "engine.llm_call", "llm_call_id": run_id + "-llm",
             "occurred_at": "2026-10-20T00:00:01+00:00", "archive_file": "modelo-0001.json.gz"}
    (run / "trazas/events.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    with gzip.open(run / "trazas/modelo-0001.json.gz", "wt", encoding="utf-8") as stream:
        json.dump({"provider_input": {"input": ["question"]}, "provider_output": {"text": "done"}}, stream)
    if missing:
        (run / missing).unlink()
    return 0 if status == "completed" else 1


def test_validate_catalog_without_service_imports():
    code = """
import sys
class Block:
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'infra','findata','engine','finmate','api'}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, Block())
from research_agent.benchmark import main
raise SystemExit(main(['validate', 'benchmarks/longitudinal-v1']))
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "cases=3; sessions=18" in result.stdout


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
    campaign, code = run_suite(load_suite(root), tmp_path / "out", launcher=worker, compact=False)
    assert code == 0 and len(seen) == 4
    summary = json.loads((campaign / "resumen.json").read_text())
    assert summary["sessions_completed"] == 4 and summary["llm_calls"] == 4
    assert len({exp for exp, _ in seen}) == 2
    original = (campaign / "pasos.jsonl").read_bytes()
    rows = extract(campaign)
    assert (campaign / "pasos.jsonl").read_bytes() == original
    assert len(rows) == 8
    assert all((campaign / r["source"]).exists() for r in rows)
    assert all((campaign / p).exists() for r in rows for p in r["evidence"])
    second, code = run_suite(load_suite(root), tmp_path / "out", selected="C0", launcher=worker, compact=False)
    assert code == 0 and second != campaign
    assert (campaign / "pasos.jsonl").read_bytes() == original


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
    campaign, code = run_suite(load_suite(root), tmp_path / "out", launcher=worker, compact=False)
    assert code == 1
    summary = json.loads((campaign / "resumen.json").read_text())
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
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1)), tmp_path / "out", launcher=worker, compact=False)
    summary = json.loads((campaign / "resumen.json").read_text())
    assert code == 1 and summary["sessions"][1]["error"] == "FileExistsError"
    assert (campaign / "casos/C0/estado/entradas/future.md").read_text() == "agent content"


def test_modified_stimulus_is_reported(tmp_path):
    def worker(command, out, err):
        exp = Path(command[command.index("--experiment") + 1])
        (exp / "estado/entradas/initial.md").write_text("modified")
        return fake_cli(command, out, err)
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out", launcher=worker, compact=False)
    assert code == 0  # Data mutation is evidence for review, not an invented semantic verdict.
    session = json.loads((campaign / "sesiones/C0-s0.json").read_text())
    assert session["input_modifications"][0]["path"] == "entradas/initial.md"


def test_all_longitudinal_cases_with_simulated_agent_and_no_providers(tmp_path):
    attempted = []
    def worker(command, out, err):
        exp = Path(command[command.index("--experiment") + 1])
        session = command[command.index("--run-name") + 1]
        attempted.append((exp.name, session))
        state = exp / "estado"
        assert not any("rubric" in p.name for p in state.rglob("*"))
        if exp.name == "S1":
            assert (state / "entradas/catalogo.md").exists() == (session >= "sesion-03")
            assert (state / "entradas/precio.md").exists() == (session >= "sesion-05")
        if exp.name == "S2":
            assert (state / "entradas/hipotesis.md").exists() == (session >= "sesion-03")
        return fake_cli(command, out, err)
    campaign, code = run_suite(load_suite(ROOT / "benchmarks/longitudinal-v1"), tmp_path / "out", launcher=worker, compact=False)
    assert code == 0 and len(attempted) == 18
    assert [c for c, _ in attempted] == ["S1"]*6 + ["S2"]*6 + ["S3"]*6


def test_regeneration_reports_missing_capture_without_changing_sessions(tmp_path):
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out", launcher=fake_cli, compact=False)
    assert code == 0
    session_file = campaign / "sesiones/C0-s0.json"
    before = session_file.read_bytes()
    session = json.loads(before)
    (campaign / session["run_directory"] / "trazas/modelo-0001.json.gz").unlink()
    extract(campaign)
    diagnostic = json.loads((campaign / "extraccion.json").read_text())["sessions"][0]
    assert not diagnostic["capture_complete"] and diagnostic["capture_errors"]
    assert session_file.read_bytes() == before


@pytest.mark.parametrize("compact", [False, True])
def test_real_subprocess_sessions_use_agent_cli_and_native_recorder(tmp_path, compact):
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
    space = Workspace(workspace)
    recorder = RunRecorder(runs, **kwargs)
    tools = ToolRegistry(recorder)
    register_files(tools, space)
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
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1)), tmp_path / "out", launcher=subprocess_worker, compact=compact)
    assert code == 0, (campaign / "resumen.json").read_text()
    pids = (campaign / "casos/C0/estado/remembered.md").read_text().splitlines()
    assert len(pids) == 2 and pids[0] != pids[1]
    rows = extract(campaign)
    assert sum(r["action"] == "model_call" for r in rows) == 6
    if compact:
        assert sum(r["action"] == "tool_execution" for r in rows) == 4
    else:
        assert sum(r["action"] == "tool_call" for r in rows) == 4
        assert sum(r["action"] == "tool_result" for r in rows) == 4
    assert sum(r["action"] == "final_answer" for r in rows) == 2


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
def test_compact_export_is_lossless_and_source_is_unchanged(tmp_path, limited):
    from research_agent.benchmark_archive import export_campaign, records, delivered_result, full_result, restore_snapshot
    from research_agent.benchmark_evidence import digest, inspect_run
    def worker(command, out, err):
        return tool_fixture(command, out, err, limited=limited)
    source, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out", launcher=worker, compact=False)
    assert code == 0
    native = source / "casos/C0/ejecuciones/s0"
    source_hashes = {p.relative_to(source): digest(p) for p in source.rglob("*") if p.is_file()}
    original_tool = json.loads((native / "trazas/herramienta-0004.json").read_text(encoding="utf-8"))
    original_state = json.loads((native / "estado-final.json").read_text(encoding="utf-8"))
    with gzip.open(native / "trazas/modelo-0001.json.gz", "rt", encoding="utf-8") as stream:
        original_model = json.load(stream)
    destination = export_campaign(source, tmp_path / "compact")
    run = destination / native.relative_to(source)
    assert len([p for p in run.rglob("*") if p.is_file()]) == 5
    assert {p.relative_to(source): digest(p) for p in source.rglob("*") if p.is_file()} == source_hashes
    trace = records(run)
    tool = next(e for e in trace if e["kind"] == "tool")
    assert tool["call"] == original_tool["call"]
    assert delivered_result(destination, tool) == original_tool["result"]
    assert full_result(destination, tool) == original_state_to_raw(original_state)
    assert next(e for e in trace if e["kind"] == "model")["payload"] == original_model
    assert restore_snapshot(destination, json.loads((run / "estado-final.json").read_text(encoding="utf-8"))) == original_state
    details, _ = inspect_run(destination, run, "C0", "s0")
    assert details["capture_complete"], details
    assert (destination / "LEEME.md").exists()
    assert not list((destination / "sesiones").glob("*.json"))
    assert not list((destination / "sesiones").glob("*.stdout.txt"))
    # Existing citations remain readable, including byte pagination and opaque calls.
    from research_agent.recording import RunRecorder
    recorder = RunRecorder(run.parent)
    recorder.workspace_fingerprint = None  # Fixture manifests have no fingerprint.
    page = recorder.read_artifact("archivo/s0/resultado-herramienta-0001.json", max_bytes=31)
    assert page["next_offset"] is not None
    assert page["text"]
    recorder.workspace_fingerprint = "unrelated-workspace"
    with pytest.raises(FileNotFoundError):
        recorder.read_artifact("archivo/s0/resultado-herramienta-0001.json")
    with pytest.raises(ValueError):
        export_campaign(source, source / "nested")


def original_state_to_raw(state):
    return json.loads(state["materiales/source.json"])


def test_default_compact_and_corruption_diagnostics(tmp_path):
    from research_agent.benchmark_evidence import inspect_run
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out", launcher=tool_fixture)
    assert code == 0
    summary = json.loads((campaign / "resumen.json").read_text())
    assert summary["recording_format"] == "benchmark-compact-v1"
    run = campaign / summary["sessions"][0]["run_directory"]
    (run / "respuesta.md").write_text("changed")
    details, _ = inspect_run(campaign, run, "C0", "s0")
    assert not details["capture_complete"]
    assert "hash mismatch" in details["capture_errors"][0]["error"]


def test_incomplete_native_capture_is_retained(tmp_path):
    def worker(command, out, err):
        return fake_cli(command, out, err, missing="trazas/modelo-0001.json.gz")
    campaign, code = run_suite(load_suite(catalog(tmp_path, cases=1, sessions=1)), tmp_path / "out", launcher=worker)
    assert code == 1
    session = json.loads((campaign / "resumen.json").read_text())["sessions"][0]
    run = campaign / session["run_directory"]
    assert session["recording_format"] == "native-incomplete"
    assert (run / "conversacion.json").exists()
    assert not (run / "ejecucion.json").exists()
    assert (campaign / session["stdout"]).exists()
