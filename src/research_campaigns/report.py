"""Deterministic, regenerable human entry point. Never changes native evidence."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote

from research_agent.workspace import Workspace
from research_agent.simulation.state import read
from .storage import load, save
from .evidence import inspect_run


def report(root: Path, record: dict[str, Any] | None = None) -> None:
    root = root.absolute()
    record = load(root) if record is None else record

    def link(name: str, label: str | None = None) -> str:
        path = root / name
        Workspace._check_links(path)
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("Campaign reference escapes its directory.")
        return f"[{label or name}]({quote(name, safe='/')})" if path.exists() else f"{label or name} (ausente)"

    def cell(value: Any) -> str:
        text = str(value if value is not None else "desconocido")
        labels = {"suite": "casos con documentos", "historical": "histórica", "continuous": "continua",
                  "prepared": "preparada", "running": "en ejecución", "completed": "completada",
                  "failed": "fallida", "interrupted": "interrumpida", "not_executed": "sin ejecutar",
                  "blocked": "bloqueada", "all_sessions_completed": "todas las sesiones completadas",
                  "all_activations_completed": "calendario completado", "incomplete_sessions": "sesiones incompletas",
                  "answered": "respuesta entregada", "call_limit": "límite de llamadas", "True": "correcta", "False": "fallida"}
        return labels.get(text, text).replace("|", "\\|").replace("\n", " ")

    lines = [f"# Campaña {record['id']}", "", f"Modalidad: **{cell(record['mode'])}**. Estado: **{cell(record['status'])}**.", "",
             f"Motivo de cierre: {cell(record.get('stop_reason'))}.", "",
             "## Definición y condiciones", "", link("campaign.json", "Registro de campaña"), "",
             f"Condición: {cell(record.get('condition'))}. Límites: `{record.get('limits', {})}`.", "",
             f"Configuración técnica: `campaign.json → runtime`. Comprobación de datos: {cell(record.get('preflight', {}).get('ready'))}.", ""]
    profile = record.get("runtime", {}).get("profile", {})
    lines += [f"Modelo: {cell(profile.get('model'))}. Proveedor: {cell(profile.get('provider'))}.", ""]
    if record.get("review_policy"):
        lines += ["El límite de llamadas cubre investigación y consolidación; las revisiones periódicas son adicionales. "
                  "Comparten los límites de tiempo y contexto. Política efectiva: `campaign.json → review_policy`.", ""]
    if (root / "definicion/peticion.md").is_file():
        lines += ["### Petición inicial", "", (root / "definicion/peticion.md").read_text(encoding="utf-8"), ""]
    for day, message in record.get("config", {}).get("messages", {}).items():
        lines += [f"### Mensaje del {day}", "", message, ""]
    for path in sorted((root / "definicion").rglob("*")):
        if path.is_file():
            lines.append(f"- {link(path.relative_to(root).as_posix())}")
    lines += ["", "## Sesiones e intentos", "",
              "| Sesión / intento | Fecha | Petición | Estado / cierre | LLM total / herramientas | LLM investigación / consolidación / revisión | Segundos | Evidencia |",
              "|---|---|---|---|---|---|---|---|"]
    diagnostics = []
    for session in record["sessions"]:
        activation = session.get("activation", {})
        details = dict(session)
        refs = []
        if session.get("run_directory"):
            name = session["run_directory"]
            link(name)  # Validate before reading any capture.
            capture = inspect_run(root, root / name, record["runtime"])
            details.update(capture)
            details["capture_errors"] = [*session.get("capture_errors", []), *[e for e in capture["capture_errors"] if e not in session.get("capture_errors", [])]]
            refs = [link(f"{name}/{file}", label) for file, label in
                    (("respuesta.md", "Respuesta"), ("manifiesto.json", "Configuración"), ("estado-inicial.json", "Estado inicial"),
                     ("estado-final.json", "Estado final"), ("eventos.jsonl", "Eventos"), ("trazas", "Trazas"))]
        else:
            details.setdefault("capture_errors", [{"error": "Sin captura de ejecución"}])
        for key in ("stdout", "stderr"):
            if session.get(key):
                refs.append(link(session[key], key))
        for error in details.get("capture_errors", []):
            diagnostics.append(f"- {cell(session['id'])}: {cell(error)}")
        if session.get("error") or session.get("input_modifications"):
            diagnostics.append(f"- {cell(session['id'])}: {cell(session.get('error') or session['input_modifications'])}")
        phases = details.get("llm_calls_by_phase") or {}
        lines.append("| " + " | ".join([cell(session['id']), cell(activation.get("date")),
            cell(session.get("message", activation.get("message"))),
            cell(session["status"]) + " / " + cell(details.get("stop_reason", session.get("reason"))),
            f"{cell(details.get('llm_calls'))} / {cell(details.get('tool_calls'))}",
            " / ".join(cell(phases.get(p)) for p in ("research", "consolidation", "review")),
            cell(session.get("elapsed_seconds", details.get("duration_seconds"))), " · ".join(refs)]) + " |")
    lines += ["", "## Diagnósticos", "", *(diagnostics or ["Sin errores de captura observados."]),
              "", "## Instrucciones y conocimiento vigente", ""]
    experiments = [root] if record["mode"] != "suite" else sorted((root / "casos").glob("*"))
    for experiment in experiments:
        for folder in ("instrucciones", "estado"):
            for path in sorted((experiment / folder).rglob("*")):
                if path.is_file() and (folder != "estado" or not path.relative_to(experiment / folder).as_posix().startswith("materiales/")):
                    lines.append(f"- {link(path.relative_to(root).as_posix())}")
        materials = experiment / "estado/materiales"
        if materials.exists():
            lines.append(f"- {link(materials.relative_to(root).as_posix(), 'Materiales originales')}")
    if (root / "simulador/state.json").exists():
        state = read(root / "simulador/state.json")
        lines += ["", "## Simulación", "", f"Fecha: {state['date']}. Efectivo: {state['cash']}.", "",
                  link("simulador/state.json", "Posiciones, órdenes y comunicaciones"), "",
                  link("simulador/data.json", "Dataset congelado")]
    lines += ["", "El estado operativo y la captura no acreditan calidad semántica ni resultados de inversión.", ""]
    Workspace._check_links(root / "README.md")
    (root / "README.md").write_text("\n".join(lines), encoding="utf-8")


def persist(root: Path, record: dict[str, Any]) -> None:
    save(root / "campaign.json", record)
    report(root, record)
