"""Compact evaluation evidence, retaining exact model/tool payloads and legacy aliases.

Compaction happens after the case has finished. It never changes agent execution.
Old campaigns are exported to a new directory; native captures with errors are retained.
"""
from __future__ import annotations

from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

from .evidence import brief, save
from research_agent.archive import (FORMAT, digest, reference, resolve, read_json, records,
                                    material, full_result, delivered_result, restore_snapshot)
from research_agent.workspace import Workspace


def _pack_snapshot(root: Path, experiment: Path, value: dict[str, Any]) -> dict[str, Any]:
    files = {}
    for name, content in value.items():
        if not name.startswith("materiales/") or not isinstance(content, str):
            files[name] = content
            continue
        candidate = Workspace(experiment / "estado", create=False).path(name)
        if not candidate.exists() or candidate.read_text(encoding="utf-8") != content:
            # Preserve historical material content if the current workspace was altered.
            raw = content.encode("utf-8")
            candidate = root / "fuentes" / (hashlib.sha256(raw).hexdigest() + ".json")
            candidate.parent.mkdir(exist_ok=True)
            if not candidate.exists():
                candidate.write_bytes(raw)
        files[name] = {"ref": reference(root, candidate), "sha256": digest(candidate)}
    return {"schema_version": FORMAT, "files": files}


def compact_run(root: Path, run: Path, case_id: str, session_id: str) -> bool:
    from .evidence import inspect_run
    if (run / "ejecucion.json").exists():
        details, _ = inspect_compact(root, run, case_id, session_id)
        if not details["capture_complete"]:
            raise ValueError("Existing compact evidence is incomplete or corrupt")
        return True
    details, _ = inspect_run(root, run, case_id, session_id)
    if not details["capture_complete"]:
        return False  # Keep all diagnostic evidence when a native capture is incomplete.
    manifest = read_json(run / "manifiesto.json")
    outcome = read_json(run / "resultado.json")
    request = (run / "peticion.md").read_text(encoding="utf-8")
    original_snapshots = {n: read_json(run / n) for n in ("estado-inicial.json", "estado-final.json")}
    native = [json.loads(l) for l in (run / "eventos.jsonl").read_text(encoding="utf-8").splitlines()]
    provider = [json.loads(l) for l in (run / "trazas/events.jsonl").read_text(encoding="utf-8").splitlines()]
    referenced_payloads = {e["archive_file"] for e in provider if e.get("archive_file")}
    if {p.name for p in (run / "trazas").glob("modelo-*.json.gz")} != referenced_payloads:
        raise ValueError("Unreferenced provider payloads; retain native capture")
    trajectory: list[dict[str, Any]] = [{"kind": "event", "event": e, "occurred_at": e.get("occurred_at")} for e in native]
    for event in provider:
        event = deepcopy(event)
        entry: dict[str, Any] = {"kind": "model" if event.get("event") == "engine.llm_call" else "provider_event",
                                 "occurred_at": event.get("occurred_at"), "event": event}
        archive = event.get("archive_file")
        if archive:
            path = resolve(run / "trazas", archive)
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                entry["payload"] = json.load(stream)
            # Log sections are references to the same payload, not additional data.
            for name in ("provider_input", "provider_output", "application_result"):
                if event.get(name) == {"archived": archive}:
                    event.pop(name)
            event.pop("archive_file", None)
        trajectory.append(entry)
    success_index = 0
    for path in sorted((run / "trazas").glob("herramienta-*.json")):
        value = read_json(path)
        call, delivered = value["call"], value["result"]
        matching: dict[str, Any] = next((e for e in native if e.get("call_id") == call["call_id"]
                         and e["event"] in {"lab.tool.completed", "lab.tool.failed"}), {})
        entry = {"kind": "tool", "call": call, "delivered": delivered,
                 "occurred_at": matching.get("occurred_at"), "full_result": None,
                 "full_result_present": False, "artifact_name": None}
        ref = delivered.get("artifact_ref")
        if delivered.get("ok"):
            success_index += 1
            raw_path = run / "trazas" / f"resultado-herramienta-{success_index:04d}.json"
            original_raw = read_json(raw_path)
            entry["artifact_name"] = raw_path.name
            if isinstance(ref, str) and ref.startswith("materiales/"):
                original = Workspace(run.parent.parent / "estado", create=False).path(ref)
                entry["full_result"] = {"ref": reference(root, original), "sha256": digest(original)}
                entry["full_result_is_reference"] = True
                raw_value = read_json(original)
            elif isinstance(ref, str) and ref.startswith(f"archivo/{run.name}/"):
                original = Workspace(run / "trazas", create=False).path(ref.split("/")[-1])
                raw_value = read_json(original)
                entry["full_result"] = raw_value
                entry["artifact_name"] = original.name
            else:
                raise ValueError("Successful tool result without an original reference")
            if raw_value != original_raw:
                raise ValueError("Original tool result differs from material")
            entry["full_result_present"] = True
            if delivered.get("value") == raw_value:
                entry["delivered"] = {k: v for k, v in delivered.items() if k != "value"}
                entry["delivered_value_is_full_result"] = True
        trajectory.append(entry)
    if len(list((run / "trazas").glob("resultado-herramienta-*.json"))) != success_index:
        raise ValueError("Unreferenced tool results; retain native capture")
    trajectory.sort(key=lambda e: e.get("occurred_at") or "")
    for n, entry in enumerate(trajectory, 1):
        entry["sequence"] = n
    temporary = run / "trayectoria.tmp.gz"
    with gzip.open(temporary, "wt", encoding="utf-8") as stream:
        for entry in trajectory:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    temporary.replace(run / "trayectoria.jsonl.gz")
    # Verify exact payload round trips before removing any native file.
    recovered = records(run)
    if recovered != trajectory:
        raise ValueError("Trajectory round-trip mismatch")
    for entry in recovered:
        if entry["kind"] == "tool":
            source = next(read_json(p) for p in (run / "trazas").glob("herramienta-*.json")
                          if read_json(p)["call"]["call_id"] == entry["call"]["call_id"])
            if delivered_result(root, entry) != source["result"]:
                raise ValueError("Delivered tool result mismatch")
    packed = {name: _pack_snapshot(root, run.parent.parent, value) for name, value in original_snapshots.items()}
    if any(restore_snapshot(root, packed[n]) != original_snapshots[n] for n in packed):
        raise ValueError("Snapshot round-trip mismatch")
    prompt_refs = {}
    for name, prompt in manifest.get("prompts", {}).items():
        body = prompt["text"]
        if hashlib.sha256(body.encode()).hexdigest() != prompt["sha256"]:
            raise ValueError("Source instruction hash mismatch")
        target = root / "definiciones" / "instrucciones" / (hashlib.sha256(body.encode()).hexdigest() + ".md")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(body, encoding="utf-8")
        prompt_refs[name] = {"ref": reference(root, target), "sha256": digest(target)}
    manifest["prompts"] = prompt_refs
    # Answer remains human-readable, once, outside the technical metadata.
    answer = outcome.pop("answer", None)
    if answer is not None and (run / "respuesta.md").read_text(encoding="utf-8") != answer:
        raise ValueError("Final answer mismatch")
    metadata = {"schema_version": FORMAT, "case_id": case_id, "session_id": session_id,
                "manifest": manifest, "result": outcome, "request": request,
                "git_final": read_json(run / "git-final.json") if (run / "git-final.json").exists() else None,
                "source_validation": details,
                "answer_file": "respuesta.md" if answer is not None else None}
    metadata["legacy_artifact_refs"] = outcome.get("artifact_refs", [])
    outcome["artifact_refs"] = ["ejecucion.json", "trayectoria.jsonl.gz", "estado-inicial.json", "estado-final.json"] + (["respuesta.md"] if answer is not None else [])
    for name, value in packed.items():
        save(run / name, value)
    metadata["files_sha256"] = {name: digest(run / name) for name in
                               ("trayectoria.jsonl.gz", "estado-inicial.json", "estado-final.json", "respuesta.md")
                               if (run / name).exists()}
    save(run / "ejecucion.json", metadata)
    # Only known native files in this run are removed, never arbitrary campaign paths.
    for name in ("manifiesto.json", "resultado.json", "peticion.md", "conversacion.json", "eventos.jsonl", "git-final.json"):
        (run / name).unlink(missing_ok=True)
    for path in list((run / "trazas").iterdir()):
        if path.is_file() and (path.name in {"events.jsonl"} or path.name.startswith(("modelo-", "herramienta-", "resultado-herramienta-"))):
            path.unlink()
    if not any((run / "trazas").iterdir()):
        (run / "trazas").rmdir()
    return True


def inspect_compact(root: Path, run: Path, case_id: str, session_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    rows = []
    try:
        meta = read_json(run / "ejecucion.json")
        for name, expected in meta["files_sha256"].items():
            if digest(resolve(run, name)) != expected:
                raise ValueError(f"Evidence hash mismatch: {name}")
        trace = records(run)
        for name in ("estado-inicial.json", "estado-final.json"):
            restore_snapshot(root, read_json(run / name))
        for ref in meta["manifest"].get("prompts", {}).values():
            path = resolve(root, ref["ref"])
            if digest(path) != ref["sha256"]:
                raise ValueError("Instruction hash mismatch")
        for entry in trace:
            kind = entry["kind"]
            event = entry.get("event", {})
            input_value = output_value = None
            if kind == "model":
                if "payload" not in entry:
                    raise ValueError("Model payload missing")
                input_value, output_value = entry["payload"].get("provider_input"), entry["payload"].get("provider_output")
            elif kind == "tool":
                input_value, output_value = entry["call"]["arguments"], delivered_result(root, entry)
                if entry["full_result_present"]:
                    full_result(root, entry)
                event = entry["call"]
            else:
                continue
            rows.append({"case_id": case_id, "session_id": session_id, "run_id": meta["manifest"]["run_id"],
                         "action": "model_call" if kind == "model" else "tool_execution",
                         "order": entry["sequence"], "occurred_at": entry.get("occurred_at"),
                         "llm_call_id": event.get("llm_call_id"), "call_id": event.get("call_id"),
                         "tool": event.get("tool_name", event.get("name")), "input": brief(input_value),
                         "output": brief(output_value), "source": reference(root, run / "trayectoria.jsonl.gz"),
                         "line": entry["sequence"], "evidence": []})
        outcome = meta["result"]
        if len([e for e in trace if e["kind"] == "model"]) < outcome["llm_calls"]:
            raise ValueError("Missing model records")
        if len([e for e in trace if e["kind"] == "tool"]) != outcome["tool_calls"]:
            raise ValueError("Missing tool records")
        if meta["answer_file"]:
            answer_path = run / meta["answer_file"]
            answer = answer_path.read_text(encoding="utf-8")
            rows.append({"case_id": case_id, "session_id": session_id, "run_id": meta["manifest"]["run_id"],
                         "action": "final_answer", "order": len(trace) + 1, "occurred_at": None,
                         "llm_call_id": None, "call_id": None, "tool": None, "input": None, "output": brief(answer),
                         "source": reference(root, answer_path), "line": None, "evidence": []})
        details = {**meta["source_validation"], "run_directory": reference(root, run)}
    except (OSError, ValueError, KeyError, TypeError, EOFError) as exc:
        errors.append({"file": reference(root, run), "error": f"{type(exc).__name__}: {exc}"})
        details = {"run_directory": reference(root, run), "run_id": None}
    details["capture_errors"] = list(details.get("capture_errors", [])) + errors
    details["capture_complete"] = not details["capture_errors"]
    return details, rows


def review_index(root: Path) -> None:
    summary = read_json(root / "resumen.json")
    lines = ["# Revisión de la campaña", "", "Empieza por resumen.json y las rúbricas en definiciones/.", "",
             "| Caso | Sesión | Estado | Respuesta | Evidencia |", "|---|---|---|---|---|"]
    for session in summary["sessions"]:
        run = session.get("run_directory")
        lines.append(f"| {session['case_id']} | {session['session_id']} | {session['status']} | "
                     + (f"[Respuesta]({run}/respuesta.md) | [Sesión]({run}/ejecucion.json) |" if run and (root/run/'ejecucion.json').exists()
                        else f"— | {session.get('reason', 'Captura nativa/incompleta')} |"))
    lines += ["", "## Cómo evaluar", "",
              "Para cada juicio cita el caso, sesión y sequence de trayectoria.jsonl.gz o el archivo de estado.",
              "Examina objetivo, autonomía, evidencia/cálculo, memoria/adaptación y recursos/robustez.",
              "Distingue lo pedido, lo disponible, lo leído, lo respondido y lo conservado.",
              "Contrasta estado-inicial y estado-final; comprueba la recuperación en sesiones posteriores.",
              "Separa fallos del agente, herramientas, ejecutor y diseño del caso. Usa N/O si falta evidencia.",
              "No premies volumen, compras ni cambios de opinión. No infieras razonamiento privado.",
              "Las fuentes pueden ser parciales; captura completa no significa documento completo.",
              "Entrega: hallazgo, evidencia, consecuencia y siguiente cambio que merezca contrastarse.",
              "No atribuyas mejora causal ni rentabilidad a esta campaña exploratoria.", "",
              "## Lectura técnica", "",
              "Usa research_agent.archive.records(run) para leer la trayectoria comprimida.",
              "delivered_result(campaign, record) y full_result(campaign, record) recuperan ambos resultados de herramientas.",
              "restore_snapshot(campaign, snapshot) recupera el estado completo verificando los materiales.",
              "Los eventos conservan el orden del productor; sequence ordena la captura, no infiere causalidad."]
    (root / "LEEME.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def compact_campaign(root: Path) -> None:
    summary = read_json(root / "resumen.json")
    for session in summary["sessions"]:
        if session.get("run_directory"):
            run = resolve(root, session["run_directory"])
            try:
                compacted = compact_run(root, run, session["case_id"], session["session_id"])
                session["recording_format"] = FORMAT if compacted else "native-incomplete"
            except (OSError, ValueError, KeyError, EOFError) as exc:
                session["archive_error"] = type(exc).__name__
                session["recording_format"] = "native-retained"
                session["status"] = "failed"
                summary["operational_complete"] = False
        # Preserve diagnostics for failures; successful stdout duplicates structured evidence.
        for key in ("stdout", "stderr"):
            if session.get(key):
                path = resolve(root, session[key])
                if path.exists() and (path.stat().st_size == 0 or (key == "stdout" and session["status"] == "completed")):
                    path.unlink()
                    session.pop(key)
    summary["recording_format"] = FORMAT
    save(root / "resumen.json", summary)
    manifest = read_json(root / "manifiesto.json")
    manifest["recording_format"] = FORMAT
    manifest["configuration_source"] = "Per-run ejecucion.json: manifest contains effective profile and verified frozen prompt references."
    save(root / "manifiesto.json", manifest)
    for path in (root / "sesiones").glob("*.json"):
        path.unlink()  # Session metadata is retained exactly once in resumen.json.
    for path in (root / "casos").glob("*/instrucciones-efectivas.json"):
        if all(s.get("recording_format") == FORMAT for s in summary["sessions"] if s["case_id"] == path.parent.name):
            path.unlink()  # Effective per-run prompts are now frozen by hash.
    review_index(root)


def export_campaign(source: Path, destination: Path) -> Path:
    source, destination = source.absolute(), destination.absolute()
    Workspace._check_links(source)
    Workspace._check_links(destination)
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Export must be separate from the source campaign")
    # Refuse links anywhere before copying private evidence, and never replace a destination.
    for path in source.rglob("*"):
        Workspace._check_links(path)
    shutil.copytree(source, destination)
    compact_campaign(destination)
    from .evidence import extract
    extract(destination)
    return destination
