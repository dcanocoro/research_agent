"""V5 integrity and scripted integration; no providers or financial-quality claims."""
import asyncio
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from importlib.resources import files

import pytest
from support import review_turn, create_doc, edit_doc, save_arguments
from runtime_contracts.llm import AssistantResponse, ConversationContext, ResponseFunctionCall, ResponseTurn, ToolResult

from research_agent.agent import AgentA
from research_agent.contracts import AgentLimits, AgentRequest, ContinuousConfig
from research_agent.experiments import prepare_experiment
from research_agent.integrations.file_tools import register_files
from research_agent.recording import RunRecorder, encoded
from research_agent.state_configuration import validate_state_configuration, CONFIGURATION
from research_agent.state_tools import StateOperations, headings
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace


@pytest.fixture
def ops(tmp_path):
    return StateOperations(Workspace(tmp_path / "estado"))


def edit(target, content, kind="replace"):
    return {"kind": kind, "target": target, "content": content}


def select(kind="lines", start=1, end=None):
    return {"kind": kind, "start": start, "end": end}


def registry(tmp_path):
    recorder = RunRecorder(tmp_path / "runs")
    tools = ToolRegistry(recorder)
    space = Workspace(tmp_path / "state")
    register_files(tools, space)
    recorder.start("test", {"workspace_fingerprint": "same", "state_contracts": tools.contracts})
    return tools


def invoke(tools, name, **args):
    return asyncio.run(tools.execute(ResponseFunctionCall("call", name, args))).payload


def test_exact_edit_preserves_utf8_crlf_and_rejects_partial_batch(ops):
    raw = "# Modelo\r\ná😀 pendiente\r\nOtro contenido\r\n".encode()
    ops.workspace.path("a.md").write_bytes(raw)
    before = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="ambiguous_target"):
        edit_doc(ops, "a.md", before, [edit("pendiente", "confirmado"), edit("ausente", "x")], "Revisar")
    assert ops.workspace.path("a.md").read_bytes() == raw
    value = edit_doc(ops, "a.md", before, [edit("pendiente", "revisión pendiente")], "Precisar")
    assert ops.workspace.path("a.md").read_bytes() == raw.replace(b"pendiente", "revisión pendiente".encode())
    assert value["previous_sha256"] == before and value["applied"]
    with pytest.raises(ValueError, match="version_conflict"):
        edit_doc(ops, "a.md", before, [edit("Otro", "Más")], "Revisar")


@pytest.mark.parametrize("target,text", [("a", "aaa"), ("aa", "aaa"), ("", "text"), ("missing", "text")])
def test_ambiguous_and_missing_anchors(ops, target, text):
    created = create_doc(ops, "a.txt", text, "Guardar")
    with pytest.raises(ValueError, match="ambiguous_target"):
        edit_doc(ops, "a.txt", created["sha256"], [edit(target, "x")], "Revisar")
    assert ops.workspace.read_version("a.txt")[0] == text.encode()


def test_insertions_and_json_validation_before_write(ops):
    created = create_doc(ops, "a.json", '{"x":1}', "Guardar")
    with pytest.raises(ValueError, match="Invalid JSON"):
        edit_doc(ops, "a.json", created["sha256"], [edit("1", "NaN")], "Revisar")
    assert ops.workspace.read_version("a.json")[1] == created["sha256"]
    value = edit_doc(ops, "a.json", created["sha256"], [edit('"x":1', '"y":2,', "insert_before")], "Añadir")
    assert json.loads(ops.workspace.read_version("a.json")[0]) == {"y": 2, "x": 1}
    assert value["applied"]


def test_cooperating_creators_and_editors_share_lock(ops):
    other = StateOperations(Workspace(ops.workspace.root))
    def create(candidate):
        try:
            return create_doc(candidate, "shared.md", "original", "Crear")
        except FileExistsError:
            return None
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(create, [ops, other]))
    assert sum(x is not None for x in results) == 1
    version = ops.workspace.read_version("shared.md")[1]
    def update(candidate):
        try:
            return edit_doc(candidate, "shared.md", version, [edit("original", "revisado")], "Revisar")
        except ValueError:
            return None
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(update, [ops, other]))
    assert sum(x is not None for x in results) == 1


@pytest.mark.parametrize("path", ["../escape.md", "materiales/x.md", "MATERIALES/x.md", "con.md", "a/b/c/d.md", "x.exe"])
def test_creation_boundaries(ops, path):
    with pytest.raises((ValueError, OSError)):
        create_doc(ops, path, "x", "Guardar")


def test_size_and_purpose(ops):
    with pytest.raises(ValueError, match="write limit"):
        create_doc(ops, "a.md", "x" * (128 * 1024 + 1), "Guardar")
    with pytest.raises(ValueError, match="Supply a reason"):
        create_doc(ops, "a.md", "x", " \n")
    assert not ops.workspace.path("a.md").exists()


def test_heading_map_and_sections(ops):
    text = "# Modelo\n### H1 — Uno\nReserva negativa\n#### Detalle\nNo confirmado\n```md\n### F1 falso\n```\n### H2 — Dos\n~~~\n# F2\n~~~\nSetext\n======\n"
    version = create_doc(ops, "a.md", text, "Guardar")["sha256"]
    assert [h["id"] for h in headings(text.encode())] == [None, "H1", None, "H2"]
    value = ops.read_state("a.md", "Recuperar H1", select("section", 2), version, None)
    assert "No confirmado" in value["text"] and "### H2" not in value["text"]
    assert value["heading"]["id"] == "H1"
    mapped = ops.inspect_state("a.md", "Orientar", None)
    assert mapped["items"][0]["sha256"] == version


def test_read_long_lines_serialized_budget_and_continuation(ops, tmp_path):
    tools = registry(tmp_path)
    text = "# Título\n" + '😀\\"\x00' * 10000 + "\nAdvertencia: no demostrado."
    created = create_doc(ops, "long.md", text, "Guardar")
    # Exercise the actual registry envelope as well as all page boundaries.
    tools.workspace = ops.workspace
    register = StateOperations(ops.workspace)
    tools._tools["read_state"] = tools._tools["read_state"].__class__(
        tools._tools["read_state"].spec, register.read_state, tools._tools["read_state"].validator,
        "inline", False, True, False, True)
    cursor = None
    chunks = []
    while True:
        payload = invoke(tools, "read_state", path="long.md", purpose="Recuperar reservas",
                         selector=select(), expected_sha256=created["sha256"], cursor=cursor)
        assert payload["ok"] and len(encoded(payload)) <= 32768
        chunks.append(payload["value"]["text"])
        cursor = payload["value"]["continuation"]
        if cursor is None:
            break
    assert "".join(chunks) == text


def test_version_and_selector_bound_continuations(ops):
    created = create_doc(ops, "a.md", "x" * 30000, "Guardar")
    value = ops.read_state("a.md", "Leer", select(), None, None)
    with pytest.raises(ValueError, match="version_required"):
        ops.read_state("a.md", "Leer", select(), None, value["continuation"])
    with pytest.raises(ValueError, match="continuation_changed"):
        ops.read_state("a.md", "Leer", select("bytes", 0), created["sha256"], value["continuation"])
    ops.workspace.write_file("a.md", "changed")
    with pytest.raises(ValueError, match="version_conflict"):
        ops.read_state("a.md", "Leer", select(), created["sha256"], value["continuation"])


def test_search_file_directory_context_and_version_changes(ops):
    create_doc(ops, "a.md", "No confirmado\nH1\nNo extrapolar\n" * 60, "Guardar")
    first = ops.search_state("a.md", "h1", "Localizar", 2, None)
    assert first["items"][0]["line"] == 2 and "No confirmado" in first["items"][0]["text"]
    assert first["limited"] and len(first["items"]) <= 50
    rest = ops.search_state("a.md", "h1", "Localizar", 2, first["continuation"])
    assert rest["items"][0]["line"] > first["items"][-1]["line"]
    directory = ops.search_state(".", "H1", "Localizar", 2, None)
    create_doc(ops, "b.md", "sin coincidencias", "Guardar")
    with pytest.raises(ValueError, match="continuation_changed"):
        ops.search_state(".", "H1", "Localizar", 2, directory["continuation"])


def test_inventory_and_heading_map_pagination(ops):
    create_doc(ops, "a.md", "".join(f"### H{i} — Tema\n" for i in range(130)), "Guardar")
    first = ops.inspect_state("a.md", "Orientar", None)
    second = ops.inspect_state("a.md", "Orientar", first["continuation"])
    assert first["limited"] and first["items"][-1] != second["items"][0]
    ops.workspace.write_file("a.md", "changed")
    with pytest.raises(ValueError, match="continuation_changed"):
        ops.inspect_state("a.md", "Orientar", first["continuation"])


def test_long_search_excerpt_contains_match_and_marks_partial(ops):
    create_doc(ops, "long.md", "x" * 10000 + " STRASSE pendiente de contraste " + "y" * 10000, "Guardar")
    item = ops.search_state("long.md", "straße", "Localizar contradicción", 2, None)["items"][0]
    assert "STRASSE" in item["text"] and item["text_partial"] and item["excerpt_offset"] > 0


def test_full_edit_is_in_transaction_journal_and_delivery_is_bounded(tmp_path):
    tools = registry(tmp_path)
    tools.workspace.write_file("a.md", "a" * 20000)
    value = invoke(tools, "record_research_advance", **save_arguments("a.md", "b" * 20000, "a" * 20000))
    assert value["ok"] and value["value"]["files"][0]["partial"] and len(encoded(value)) <= 32768
    journal = json.loads(next((tools.recorder.root / "transacciones").glob("*.json")).read_bytes())
    assert journal["changes"][0]["before"] == "a" * 20000
    assert journal["changes"][0]["after"] == "b" * 20000


@pytest.mark.parametrize("symbol", ["../X", "A/B", "Ñ", "CON", "a..b", "A-", ".A"])
def test_invalid_company_symbols(ops, symbol):
    with pytest.raises(ValueError):
        ops.inspect_company(symbol, "Orientar", None)


def test_company_absence_ids_and_preservation(ops):
    absent = ops.inspect_company("BRK.B", "Orientar", None)
    assert all(not i["exists"] for i in absent["items"])
    assert not ops.workspace.path("empresas").exists()
    created = create_doc(ops, "empresas/BRK.B/modelo.md", "### H1 — Hipótesis\nProvisional\n", "Inicio")
    with pytest.raises(ValueError, match="company_case_collision"):
        ops.inspect_company("brk.b", "Orientar", None)
    with pytest.raises(ValueError, match="id_changed"):
        edit_doc(ops, "empresas/BRK.B/modelo.md", created["sha256"], [edit("H1", "H2")], "No válido")
    # Simulate externally corrupted state; every composed writer now rejects duplicates.
    ops.workspace.path("empresas/BRK.B/modelo.md").write_bytes("### H1\nUno\n### H1\nDos\n".encode())
    mapped = ops.inspect_company("BRK.B", "Orientar", None)
    assert mapped["items"][0]["duplicate_ids"] == ["H1"]
    with pytest.raises(ValueError, match="ambiguous_id"):
        ops.read_company_document("BRK.B", "modelo", "Leer", None, "H1", None, None)
    view = ops.read_company_document("BRK.B", "modelo", "Leer", select("lines", 1, 2), None, None, None)
    assert view["text"] == "### H1\nUno\n"
    assert not ops.workspace.path("empresas/BRK.B/valoracion.md").exists()


@pytest.mark.parametrize("failure_at", ["artifact", "event", "save"])
def test_applied_mutation_survives_capture_failure(tmp_path, monkeypatch, failure_at):
    tools = registry(tmp_path)
    if failure_at == "event":
        original = tools.recorder.event
        def failing(name, **fields):
            if name == "lab.file.written":
                raise OSError("disk")
            return original(name, **fields)
        monkeypatch.setattr(tools.recorder, "event", failing)
    else:
        monkeypatch.setattr(tools.recorder, failure_at, lambda *a, **k: (_ for _ in ()).throw(OSError("disk")))
    payload = invoke(tools, "record_research_advance", **save_arguments("a.md", "conserved"))
    assert payload["applied"] is True
    assert payload["mutation"]["files"][0]["sha256"] == tools.workspace.read_version("a.md")[1]
    assert tools.summary().files_written == ("a.md",) and tools.summary().capture_errors


def test_schemas_contracts_and_phase_restrictions(tmp_path):
    tools = registry(tmp_path)
    def strict(value):
        if isinstance(value, dict):
            if value.get("properties") is not None:
                assert value["additionalProperties"] is False
                assert set(value["required"]) == set(value["properties"])
            for child in value.values():
                strict(child)
        elif isinstance(value, list):
            for child in value:
                strict(child)
    for spec in tools.specs():
        strict(spec.parameters)
    assert set(tools.contracts) <= tools.consolidation_tools
    payload = invoke(tools, "describe_state_tools", tool="read_state")
    assert payload["ok"] and "state-tools-e1" in payload["value"]["text"]
    denied = asyncio.run(tools.execute(ResponseFunctionCall("c", "describe_state_tools", {"tool": "read_state"}),
                                      allowed_names=frozenset({"describe_state_tools"})))
    assert not denied.payload["ok"]
    denied = asyncio.run(tools.execute(ResponseFunctionCall("c", "create_state", {"path": "a.md", "content": "x", "purpose": "Guardar"}), allowed_names=frozenset()))
    assert not denied.payload["ok"] and not tools.workspace.path("a.md").exists()


@pytest.mark.parametrize("group", ["state", "company"])
def test_packaged_examples_execute(ops, group):
    text = files("research_agent").joinpath(f"state_contracts/{group}.md").read_text(encoding="utf-8")
    code = re.search(r"```python\n(.*?)```", text, re.S)[1]
    exec(compile(code, f"{group}.md", "exec"), {"workspace": ops.workspace, "runs": ops.workspace.root.parent / "runs"})


def test_single_interface_freezes_guide_and_captures_contract_changes(tmp_path):
    root = tmp_path / "exp"
    original = prepare_experiment(root, new=True)
    validate_state_configuration(root)
    assert json.loads((root / "herramientas.json").read_bytes()) == CONFIGURATION
    contents = {p: p.read_bytes() for p in original}
    assert prepare_experiment(root, new=False) == original
    assert all(p.read_bytes() == text for p, text in contents.items())
    tools = registry(tmp_path / "capture")
    manifest = json.loads((tools.recorder.current / "manifiesto.json").read_bytes())
    assert manifest["state_contracts"]["read_state"]["sha256"] == hashlib.sha256(tools.contracts["read_state"]["text"].encode()).hexdigest()
    tools.contracts["read_state"]["text"] += "\nchanged"
    tools.recorder.start("second", {"workspace_fingerprint": "same", "state_contracts": tools.contracts})
    assert tools.recorder.contract_changes == ["read_state"]


@pytest.mark.parametrize("config", [None, {"schema_version": "state-tools-profile-v1", "profile": "legacy"},
                                    {"schema_version": "state-tools-profile-v1", "profile": "v5"}])
def test_old_continuation_rejected_before_clients_and_without_migration(tmp_path, monkeypatch, config, capsys):
    from research_agent import cli
    root = tmp_path / "old"
    prepare_experiment(root, new=True)
    path = root / "herramientas.json"
    if config is None:
        path.unlink()
    else:
        path.write_text(json.dumps(config), encoding="utf-8")
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    monkeypatch.setattr(cli, "build_agent", lambda *a, **k: pytest.fail("client constructed"))
    with pytest.raises(SystemExit):
        cli.main(["Continúa", "--experiment", str(root), "--continue", "--run-name", "continuacion"])
    assert "Incompatible state tools contract" in capsys.readouterr().err
    assert {p: p.read_bytes() for p in root.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("flag", [["--state-tools", "v5"], ["--adopt-state-tools-v5"]])
def test_removed_profile_flags_rejected_before_creation(tmp_path, flag):
    from research_agent import cli
    root = tmp_path / "new"
    with pytest.raises(SystemExit):
        cli.main(["Pregunta", "--experiment", str(root), "--new", "--run-name", "inicial", *flag])
    assert not root.exists()


@pytest.mark.parametrize("kind", ["replace", "insert_before", "insert_after"])
def test_empty_anchor_initializes_only_an_empty_versioned_file(tmp_path, kind):
    tools = registry(tmp_path)
    created = invoke(tools, "record_research_advance", **save_arguments("empty.md", ""))
    assert created["ok"]
    args = save_arguments("empty.md", "Initialized", "")
    args["changes"][0]["operations"][0]["kind"] = kind
    initialized = invoke(tools, "record_research_advance", **args)
    assert initialized["ok"] and tools.workspace.read_version("empty.md")[0] == b"Initialized"
    args["changes"][0]["expected_sha256"] = initialized["value"]["files"][0]["sha256"]
    rejected = invoke(tools, "record_research_advance", **args)
    assert not rejected["ok"] and "ambiguous_target" in rejected["message"]
    assert tools.workspace.read_version("empty.md")[0] == b"Initialized"


def test_one_writer_and_removed_calls_never_apply(tmp_path):
    tools = registry(tmp_path)
    writers = {spec.name for spec in tools.specs() if tools.is_mutation(spec.name)}
    assert writers == {"record_research_advance"}
    assert writers <= tools.consolidation_tools
    for name in ("write_file", "write_markdown", "create_state", "edit_state", "update_company_document"):
        assert name not in tools.contracts
        assert not invoke(tools, name, path="forbidden.md", content="bad")["ok"]
    assert not tools.workspace.path("forbidden.md").exists()


def test_byte_selectors_reject_split_codepoints(ops):
    created = create_doc(ops, "a.txt", "á😀\r\nAviso", "Guardar")
    value = ops.read_state("a.txt", "Leer", select("bytes", 0, 2), created["sha256"], None)
    assert value["text"] == "á"
    with pytest.raises(ValueError, match="UTF-8"):
        ops.read_state("a.txt", "Leer", select("bytes", 1, 2), None, None)
    with pytest.raises(ValueError, match="UTF-8"):
        ops.read_state("a.txt", "Leer", select("bytes", 0, 3), None, None)


def test_large_company_result_keeps_receipt_and_full_artifact(tmp_path):
    tools = registry(tmp_path)
    refs = ["fixture:" + "a" * 2000] * 30
    value = invoke(tools, "record_research_advance", **save_arguments("empresas/ACME/modelo.md", "### H1\nProvisional", source_refs=refs))
    assert value["ok"] and value["value"]["limited"] and len(encoded(value)) <= 32768
    assert value["value"]["mutation"]["files"][0]["applied"]
    full = json.loads((tools.recorder.current / "trazas" / value["artifact_ref"].split("/")[-1]).read_bytes())
    assert full["source_refs"] == refs


def test_company_h1_v1_recovered_after_context_renewal(tmp_path):
    space = Workspace(tmp_path / "state")
    space.write_file("agenda.md", "# Agenda\n## Investigación activa\nRevisar consecuencias de H1.\nÚltimo avance: hipótesis pendiente de contraste.\n## Investigaciones aplazadas\nNinguna.\n")
    space.write_file("empresas/ACME/modelo.md", "### H1 — Márgenes\nSupuesto 20 %.\n")
    space.write_file("empresas/ACME/valoracion.md", "### V1\nDepende de empresas/ACME/modelo.md#H1\nCifra provisional.\n")
    space.write_file("empresas/ACME/evaluacion.md", "Depende de empresas/ACME/valoracion.md#V1; pendiente.\n")
    recorder = RunRecorder(tmp_path / "runs")
    tools = ToolRegistry(recorder)
    register_files(tools, space)
    def call(name, **args):
        item = ResponseFunctionCall("c", name, args)
        return ResponseTurn([item], "", item)
    def text(value):
        return ResponseTurn([AssistantResponse(value)], value, None)
    class Client:
        def __init__(self):
            self.step = 0
            self.recovered = False
        async def respond(self, **kwargs):
            if any("review_packet" in getattr(x, "payload", {}) for x in kwargs["input_items"]):
                return review_turn()
            budget = next(x.payload["execution_budget"] for x in reversed(kwargs["input_items"])
                          if isinstance(x, ConversationContext) and "execution_budget" in x.payload)
            if budget["purpose"] == "checkpoint":
                return text("Conservado; V1 pendiente.")
            n, self.step = self.step, self.step + 1
            results = [x for x in kwargs["input_items"] if isinstance(x, ToolResult)]
            if results:
                assert results[-1].payload["ok"]
            if n == 0:
                return call("inspect_company", symbol="ACME", purpose="Orientar", cursor=None)
            if n == 1:
                return call("read_company_document", symbol="ACME", dimension="modelo", purpose="Recuperar H1", selector=None, identifier="H1", expected_sha256=None, cursor=None)
            if n == 2:
                return call("record_research_advance", changes=[dict(path="empresas/ACME/modelo.md", action="edit", content=None, expected_sha256=results[-1].payload["value"]["sha256"], operations=[edit('20 %', '10 %')])], reason='Evidencia sintética contradictoria', source_refs=["fixture:update"])
            if n == 3:
                assert "10 %" in results[-1].payload["value"]["files"][0]["recovered_sections"][0]["text"]
                return call("search_state", path=".", query="empresas/ACME/modelo.md#H1", purpose="Localizar consecuencias", context_lines=2, cursor=None)
            if n == 4:
                return call("read_company_document", symbol="ACME", dimension="valoracion", purpose="Recuperar V1", selector=None, identifier="V1", expected_sha256=None, cursor=None)
            if n == 5:
                return call("record_research_advance", changes=[dict(path="empresas/ACME/valoracion.md", action="edit", content=None, expected_sha256=results[-1].payload["value"]["sha256"], operations=[edit('Cifra provisional.', 'Revisión pendiente por cambio H1; cifra anterior no confirmada.')])], reason='Falta recálculo', source_refs=["empresas/ACME/modelo.md#H1"])
            if n == 6:
                return text("Contexto sintético para forzar renovación. " * 2400)
            if n == 7:
                assert any(e["event"] == "lab.context.renewed" for e in recorder.events)
                seed = next(x.payload for x in kwargs["input_items"]
                            if isinstance(x, ConversationContext) and "work_focus" in x.payload)
                assert seed["work_focus"]["available"] and not seed["memory_index"]["exists"]
                assert "Revisar consecuencias de H1" in seed["deliberative_agenda"]["text"]
                return call("read_company_document", symbol="ACME", dimension="valoracion", purpose="Recuperar pendiente tras renovar", selector=None, identifier="V1", expected_sha256=None, cursor=None)
            assert "Revisión pendiente" in results[-1].payload["value"]["text"]
            self.recovered = True
            return text("V1 sigue pendiente; no afirmar evaluación resuelta.")
    client = Client()
    agent = AgentA(client, tools, space, recorder, AgentLimits(),
                   configuration={"provider": "openai", "model": "fake", "max_output_tokens": 128})
    request = AgentRequest("Revisar H1 y sus consecuencias", "state", "conversation", mandate="Investiga con datos sintéticos.",
                           continuous=ContinuousConfig(max_context_bytes=240000, consolidation_threshold_bytes=90000, max_llm_calls=12))
    result = asyncio.run(agent.run(request))
    assert result.stop_reason == "call_limit" and client.recovered, result
    assert "10 %" in space.read_version("empresas/ACME/modelo.md")[0].decode()
    assert len(list(space.path("empresas/ACME").iterdir())) == 3
    renewal = next(c for c in recorder.checkpoints if c["label"] == "renewal")
    snapshot = json.loads((recorder.current / renewal["reference"]).read_bytes())
    assert "10 %" in snapshot["files"]["empresas/ACME/modelo.md"]["text"]
    assert "Revisión pendiente" in snapshot["files"]["empresas/ACME/valoracion.md"]["text"]
