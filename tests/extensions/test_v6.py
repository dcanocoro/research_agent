"""V6 regression cases and offline observations; scripted behavior is not semantic acceptance."""
import asyncio
import hashlib
import json

import pytest
from support import review_turn, create_doc, edit_doc, save_arguments
from runtime_contracts.llm import AssistantResponse, ConversationContext, ResponseFunctionCall, ResponseTurn

from research_agent.agent import AgentA
from research_agent.extensions.deliberation.agenda import AGENDA_TEMPLATE
from research_agent.extensions.deliberation.agenda import focus_context
from research_agent.contracts import AgentRequest
from research_agent.contracts import ContinuousConfig
from research_agent.experiments.store import prepare_experiment
from research_agent.capabilities.state.files import register_files
from research_agent.observability.recording import RunRecorder
from research_agent.observability.recording import encoded
from research_agent.capabilities.state.operations import StateOperations
from research_agent.core.tools import ToolRegistry
from research_agent.storage.workspace import Workspace
from research_campaigns.cli import main
from research_campaigns.reporting.progress import evaluate_run
from research_campaigns.reporting.progress import numerical_checks
from support import ScriptedClient


@pytest.fixture
def ops(tmp_path):
    return StateOperations(Workspace(tmp_path / "estado"))


def test_aapl_populated_hypothesis_cannot_be_moved_under_evidence(ops):
    path = "empresas/AAPL/modelo.md"
    original = "### H1 — Caja\r\nHipótesis provisional.\r\n### E3 — Evidencia\r\nDato observado.\r\n"
    created = create_doc(ops, path, original, "Conservar")
    broken = "### H1 — Caja\r\n\r\n### E3 — Evidencia\r\nHipótesis provisional.\r\nDato observado.\r\n"
    changes = [{"kind": "replace", "target": original, "content": broken}]
    with pytest.raises(ValueError, match="empty_section"):
        edit_doc(ops, path, created["sha256"], changes, "Revisar")
    assert ops.workspace.path(path).read_bytes() == original.encode()


def test_header_hierarchy_loss_rejected_but_no_financial_template_imposed(ops):
    path = "empresas/AAPL/modelo.md"
    original = "## H1\n### Detalle\nArgumento provisional\n"
    create_doc(ops, path, original, "Conservar")
    with pytest.raises(ValueError, match="empty_section"):
        ops.workspace.write_file(path, original.replace("### Detalle", "## E3"))
    assert create_doc(ops, "nota.md", "## H1\n", "Nota")["applied"]
    # An ID that was already empty may be repaired without filling unrelated fields.
    value = create_doc(ops, "empresas/ADP/modelo.md", "### H1\n\n### E1\nDatos.\n", "Inicializar")
    assert value["validation"]["empty_ids"] == ["H1"]


def test_duplicate_create_and_alias_bypass_rejected(ops):
    path = "empresas/AAPL/modelo.md"
    with pytest.raises(ValueError, match="duplicate_ids"):
        create_doc(ops, path, "### H1\nUno\n### H1\nDos\n", "Crear")
    assert not ops.workspace.path(path).exists()
    create_doc(ops, path, "### H1\nUno\n", "Crear")
    with pytest.raises(ValueError, match="id_changed"):
        ops.workspace.write_file(path, "### H2\nOtro\n")
    with pytest.raises(FileExistsError):
        create_doc(ops, path, "sin ID", "Crear")


def test_external_duplicate_repair_and_preexisting_empty_id(ops):
    path = ops.workspace.path("empresas/AAPL/modelo.md")
    path.parent.mkdir(parents=True)
    path.write_bytes(b"### H1\nOne\n### H1\nTwo\n### E1\n\n")
    value = ops.workspace.write_file("empresas/AAPL/modelo.md", "### H1\nOne and two\n### E1\n\n")
    assert value["validation"]["duplicate_ids"] == []
    assert value["validation"]["empty_ids"] == ["E1"]


def test_adp_revised_pending_and_literal_future_reference(ops):
    original = "### H1\nPendiente: recuperar ratios.\n### E2\nSin comparación.\n"
    created = create_doc(ops, "empresas/ADP/modelo.md", original, "Guardar")
    changes = [{"kind": "replace", "target": "Pendiente: recuperar ratios.",
                "content": "Comparación cuantificada en #E2. Pendiente: explicar persistencia económica."},
               {"kind": "replace", "target": "Sin comparación.",
                "content": "Comparación modera #H1. Afecta empresas/ADP/valoracion.md#V1 (futura)."}]
    value = edit_doc(ops, "empresas/ADP/modelo.md", created["sha256"], changes, "Nuevo cálculo")
    assert value["changed_ids"] == ["H1", "E2"]
    assert value["validation"]["unresolved_references"] == [
        {"reference": "empresas/ADP/valoracion.md#V1", "status": "unavailable_document"}]
    for section in value["recovered_sections"]:
        recovered = ops.read_company_document("ADP", "modelo", "Comprobar", None,
                                              section["identifier"], value["sha256"], None)
        assert recovered["text"] == section["text"]
        assert "Pendiente: recuperar ratios" not in recovered["text"]
    assert not ops.workspace.path("empresas/ADP/valoracion.md").exists()


def test_large_recovered_views_remain_bounded_and_have_recovery(tmp_path):
    space = Workspace(tmp_path / "estado")
    recorder = RunRecorder(tmp_path / "runs")
    registry = ToolRegistry(recorder)
    register_files(registry, space)
    recorder.start("fixture", {"run_id": "fixture"})
    text = "".join(f"### H{i}\n" + '😀\\"' * 400 + "\n" for i in range(20))
    call = ResponseFunctionCall("c", "record_research_advance", save_arguments("empresas/X/modelo.md", text))
    payload = asyncio.run(registry.execute(call)).payload
    assert payload["ok"] and len(encoded(payload)) <= 32768
    value = payload["value"]["files"][0]
    assert value["recovered_sections_omitted"] > 0 or any(s["partial"] for s in value["recovered_sections"])
    assert value["recovery"]


def test_new_agenda_and_legacy_continuation_not_overwritten(tmp_path):
    root = tmp_path / "experiment"
    prepare_experiment(root, new=True, deliberative=True)
    agenda = root / "estado/agenda.md"
    assert agenda.read_text(encoding="utf-8") == AGENDA_TEMPLATE
    agenda.write_text("Agenda anterior personalizada", encoding="utf-8")
    prepare_experiment(root, new=False, deliberative=True)
    assert agenda.read_text(encoding="utf-8") == "Agenda anterior personalizada"
    assert not focus_context("Agenda anterior personalizada")["available"]
    assert focus_context(AGENDA_TEMPLATE)["available"]
    assert not focus_context(AGENDA_TEMPLATE + "\n## Investigación activa\nOtra\n")["available"]


def text(value="avance"):
    return ResponseTurn([AssistantResponse(value)], value, None)


def test_continuous_checkpoints_and_progress_are_offline_and_not_extra_calls(tmp_path):
    space = Workspace(tmp_path / "estado")
    space.write_file("agenda.md", AGENDA_TEMPLATE)
    recorder = RunRecorder(tmp_path / "runs")
    registry = ToolRegistry(recorder)
    register_files(registry, space)
    function = ResponseFunctionCall("w", "record_research_advance", save_arguments("empresas/X/modelo.md", "### H1\nProvisional\n"))
    turns = [ResponseTurn([function], "", function)] + [text()] * 9 + [text("Revisar incertidumbre"), text()]
    client = ScriptedClient(turns)
    agent = AgentA(client, registry, space, recorder,
                   configuration={"provider": "openai", "model": "test", "max_output_tokens": 128})
    request = AgentRequest("Investiga", "state", "chat", mandate="Compara fundamentos",
                           continuous=ContinuousConfig(max_llm_calls=11))
    result = asyncio.run(agent.run(request))
    assert result.llm_calls == 11 and len(client.requests) == 10
    report = evaluate_run(recorder.current)
    assert report["writes_by_phase"] == {"researcher": 1, "checkpoint": 0, "evaluator": 0, "unknown": 0}
    assert [item["label"] for item in report["observations"]] == ["initial", "evaluation", "final"]
    assert "empresas/X/modelo.md" in report["observations"][1]["changed_documents"]
    assert all(v["status"] == "not_assessed" for v in report["semantic_review"].values())
    context = next(x.payload for x in client.requests[0]["input_items"]
                   if isinstance(x, ConversationContext) and "work_focus" in x.payload)
    assert context["work_focus"]["available"] and not context["memory_index"]["exists"]
    assert "continuidad/indice.json" in result.artifact_refs
    before = space.snapshot()
    assert main(["progress", str(recorder.current)]) == 0
    assert space.snapshot() == before and len(client.requests) == 10
    with pytest.raises(SystemExit):
        main(["progress", str(recorder.current)])  # Cannot overwrite prior review evidence.


def test_checkpoint_hashes_crlf_and_capture_failure_is_explicit(tmp_path, monkeypatch):
    space = Workspace(tmp_path / "estado")
    raw = "## Investigación activa\r\nPregunta á\r\n".encode()
    space.path("agenda.md").write_bytes(raw)
    recorder = RunRecorder(tmp_path / "runs")
    recorder.start("fixture", {"run_id": "fixture"})
    recorder.checkpoint(space, "review", llm_calls_used=10)
    checkpoint = json.loads((recorder.current / recorder.checkpoints[0]["reference"]).read_bytes())
    assert checkpoint["files"]["agenda.md"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert checkpoint["files"]["agenda.md"]["text"].encode() == raw
    monkeypatch.setattr(recorder, "save", lambda *a: (_ for _ in ()).throw(OSError("disk")))
    recorder.checkpoint(space, "final")
    assert recorder.capture_errors[-1]["operation"] == "knowledge_checkpoint"
    assert space.path("agenda.md").read_bytes() == raw


def aon_check():
    return {"schema_version": "numerical-checks-v1", "checks": [{
        "document": "empresas/AON/modelo.md", "quote": "caída de 8,99 puntos", "reported": "8.99",
        "operation": "subtract", "left": {"path": "materiales/calculo.json", "pointer": "/margin/0", "unit": "fraction"},
        "right": {"path": "materiales/calculo.json", "pointer": "/margin/1", "unit": "fraction"},
        "scale": "100", "unit": "percentage_points", "tolerance": "0.005"}]}


def test_aon_explicit_claim_checked_against_original_calculation():
    state = {"empresas/AON/modelo.md": "El margen sufrió una caída de 8,99 puntos.",
             "materiales/calculo.json": '{"margin":["0.25131","0.17141"]}'}
    result = numerical_checks(state, aon_check())[0]
    assert result["status"] == "mismatch" and result["expected"] == "7.99000"
    check = aon_check()
    check["checks"][0].update(quote="caída de 7,99 puntos", reported="7.99")
    state["empresas/AON/modelo.md"] = "caída de 7,99 puntos"
    assert numerical_checks(state, check)[0]["status"] == "matches"
    check["checks"][0]["right"]["unit"] = "percent"
    assert numerical_checks(state, check)[0]["status"] == "unobservable"


def test_numerical_check_does_not_invent_evidence_or_match_substring():
    state = {"empresas/AON/modelo.md": "caída de 18,99 puntos"}
    spec = aon_check()
    spec["checks"][0]["quote"] = "caída de 18,99 puntos"
    assert numerical_checks(state, spec)[0]["status"] == "unobservable"


def test_offline_report_does_not_invent_checkpoints_and_detects_tampering(tmp_path):
    space = Workspace(tmp_path / "estado")
    space.write_file("agenda.md", AGENDA_TEMPLATE)
    recorder = RunRecorder(tmp_path / "runs")
    recorder.start("fixture", {"run_id": "fixture"})
    recorder.event("lab.run.started")
    recorder.save("estado-final.json", space.snapshot())
    assert evaluate_run(recorder.current)["checkpoint_status"] == "unobservable"
    recorder.checkpoint(space, "final")
    path = recorder.current / recorder.checkpoints[0]["reference"]
    checkpoint = json.loads(path.read_bytes())
    checkpoint["files"]["agenda.md"]["text"] += "Alteración"
    path.write_bytes(encoded(checkpoint))
    with pytest.raises(ValueError, match="hash mismatch"):
        evaluate_run(recorder.current)


def test_checkpoint_marks_partial_state_without_concealing_capture_errors(tmp_path, monkeypatch):
    space = Workspace(tmp_path / "estado")
    space.write_file("agenda.md", AGENDA_TEMPLATE)
    recorder = RunRecorder(tmp_path / "runs")
    recorder.start("fixture", {"run_id": "fixture"})
    def fail(path):
        raise OSError("Cannot read this knowledge file")
    monkeypatch.setattr(space, "read_version", fail)
    recorder.checkpoint(space, "review")
    snapshot = json.loads((recorder.current / recorder.checkpoints[0]["reference"]).read_bytes())
    assert snapshot["files"] == {} and not snapshot["capture_complete"]
    assert snapshot["capture_errors"][0]["path"] == "agenda.md"
