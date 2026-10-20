"""Deterministic, regenerable views of native evidence. No semantic scoring."""
from __future__ import annotations

from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

from .workspace import Workspace


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def brief(value: Any) -> str | None:
    if value is None:
        return None
    result = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    result = " ".join(result.split())
    return result if len(result) <= 240 else result[:237] + "..."


def inspect_run(campaign: Path, run: Path, case_id: str, session_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if (run / "ejecucion.json").exists():
        from .benchmark_archive import inspect_compact
        return inspect_compact(campaign, run, case_id, session_id)
    errors: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []

    def ref(path: Path) -> str:
        return path.relative_to(campaign).as_posix()

    def issue(path: Path, reason: str) -> None:
        errors.append({"file": ref(path), "error": reason})

    def read(path: Path, kind: type | None = dict) -> Any:
        try:
            Workspace._check_links(path)
            if path.suffix == ".gz":
                with gzip.open(path, "rt", encoding="utf-8") as stream:
                    value = json.load(stream)
            else:
                value = json.loads(path.read_text(encoding="utf-8"))
            if kind is not None and not isinstance(value, kind):
                raise ValueError("Unexpected JSON type")
            return value
        except (OSError, ValueError, UnicodeError, EOFError) as exc:
            issue(path, type(exc).__name__)
            return kind() if kind is not None else None

    manifest = read(run / "manifiesto.json")
    result = read(run / "resultado.json")
    read(run / "estado-inicial.json")
    read(run / "estado-final.json")
    read(run / "conversacion.json", list)
    run_id = manifest.get("run_id")
    if not run_id or result.get("run_id") != run_id:
        issue(run / "resultado.json", "Missing or inconsistent run_id")
    try:
        (run / "peticion.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        issue(run / "peticion.md", type(exc).__name__)
    state = result.get("state")
    if not isinstance(state, dict) or not isinstance(state.get("capture_errors"), list):
        issue(run / "resultado.json", "Missing state.capture_errors")
        state = {}
    errors.extend(state.get("capture_errors", []))

    def events(path: Path) -> list[tuple[int, dict[str, Any]]]:
        try:
            Workspace._check_links(path)
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, ValueError, UnicodeError) as exc:
            issue(path, type(exc).__name__)
            return []
        parsed = []
        for number, line in enumerate(lines, 1):
            try:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError("Expected event object")
                parsed.append((number, value))
            except ValueError:
                issue(path, f"Invalid event at line {number}")
        return parsed

    def row(action: str, path: Path, event: dict[str, Any], *, line: int | None = None,
            input_value: Any = None, output_value: Any = None, evidence: list[str] | None = None) -> None:
        rows.append({"case_id": case_id, "session_id": session_id, "run_id": run_id,
                     "action": action, "occurred_at": event.get("occurred_at"),
                     "llm_call_id": event.get("llm_call_id"), "call_id": event.get("call_id"),
                     "tool": event.get("tool_name"), "input": brief(input_value), "output": brief(output_value),
                     "source": ref(path), "line": line, "evidence": evidence or []})

    tool_payloads: dict[str, tuple[dict[str, Any], Path]] = {}
    for path in sorted((run / "trazas").glob("herramienta-*.json")):
        payload = read(path)
        call = payload.get("call") or {}
        call_id = call.get("call_id")
        if call_id:
            if call_id in tool_payloads:
                issue(path, "Duplicate tool call_id")
            tool_payloads[call_id] = (payload, path)

    native_path = run / "eventos.jsonl"
    native = events(native_path)
    terminal = [e for _, e in native if e.get("event") in {"lab.run.completed", "lab.run.failed", "lab.run.interrupted"}]
    if not terminal:
        issue(native_path, "Missing terminal event")
    starts = 0
    failed_document = False
    for line, event in native:
        name = event.get("event", "")
        if event.get("run_id") != run_id:
            issue(native_path, f"Inconsistent event run_id at line {line}")
        if name not in {"lab.tool.started", "lab.tool.completed", "lab.tool.failed", "lab.phase.timeout"}:
            continue
        input_value = event.get("arguments")
        output_value: Any = event.get("error_type")
        evidence = []
        if name == "lab.tool.started":
            starts += 1
        if name in {"lab.tool.completed", "lab.tool.failed"}:
            payload_entry = tool_payloads.get(event.get("call_id", ""))
            if payload_entry:
                payload, path = payload_entry
                input_value = (payload.get("call") or {}).get("arguments")
                output_value = payload.get("result")
                evidence.append(ref(path))
                reference = output_value.get("artifact_ref") if isinstance(output_value, dict) else None
                if isinstance(reference, str):
                    parts = reference.split("/")
                    try:
                        if len(parts) == 3 and parts[0] == "archivo" and parts[1] == run.name:
                            original = Workspace(run / "trazas", create=False).path(parts[2])
                        elif reference.startswith("materiales/"):
                            original = Workspace(run.parent.parent / "estado", create=False).path(reference)
                        else:
                            raise ValueError("Invalid original result reference")
                        read(original, None)
                        evidence.append(ref(original))
                    except ValueError:
                        issue(path, "Invalid original result reference")
            else:
                issue(native_path, f"Missing tool payload at line {line}")
            if name == "lab.tool.failed" and event.get("tool_name") == "read_document":
                failed_document = True
        row("tool_call" if name == "lab.tool.started" else "tool_result" if name == "lab.tool.completed" else "error",
            native_path, event, line=line, input_value=input_value, output_value=output_value, evidence=evidence)

    provider_path = run / "trazas/events.jsonl"
    provider = events(provider_path)
    seen_calls: set[str] = set()
    for line, event in provider:
        if event.get("event") != "engine.llm_call":
            continue
        if event.get("run_id") != run_id:
            issue(provider_path, f"Inconsistent provider run_id at line {line}")
        llm_id = event.get("llm_call_id")
        if not llm_id or llm_id in seen_calls:
            issue(provider_path, f"Missing or duplicate llm_call_id at line {line}")
            continue
        seen_calls.add(llm_id)
        payload = {}
        evidence = []
        archive = event.get("archive_file")
        if isinstance(archive, str) and Path(archive).name == archive and archive.endswith(".json.gz"):
            payload_path = run / "trazas" / archive
            payload = read(payload_path)
            evidence.append(ref(payload_path))
        else:
            issue(provider_path, f"Missing provider payload at line {line}")
        if event.get("capture_error") or event.get("archive_error"):
            issue(provider_path, f"Provider capture error at line {line}")
        row("model_call", provider_path, event, line=line,
            input_value=payload.get("provider_input"), output_value=payload.get("provider_output"), evidence=evidence)

    llm_calls = result.get("llm_calls")
    tool_calls = result.get("tool_calls")
    if not isinstance(llm_calls, int) or len(seen_calls) < llm_calls:
        issue(provider_path, "Missing model call captures")
    if not isinstance(tool_calls, int) or starts != tool_calls:
        issue(native_path, "Tool count does not match result")
    if sum(e.get("event") in {"lab.tool.completed", "lab.tool.failed"} for _, e in native) != starts:
        issue(native_path, "Missing tool completion events")
    if result.get("status") == "completed":
        answer_path = run / "respuesta.md"
        try:
            answer = answer_path.read_text(encoding="utf-8")
            if answer != result.get("answer"):
                issue(answer_path, "Answer differs from result")
            row("final_answer", answer_path, terminal[-1] if terminal else {}, output_value=answer)
        except (OSError, UnicodeError) as exc:
            issue(answer_path, type(exc).__name__)
    rows.sort(key=lambda r: (r["occurred_at"] or "", r["source"], r["line"] or 0))
    for order, item in enumerate(rows, 1):
        item["order"] = order
    duration = None
    try:
        duration = (datetime.fromisoformat(terminal[-1]["occurred_at"]) - datetime.fromisoformat(native[0][1]["occurred_at"])).total_seconds()
    except (ValueError, KeyError, IndexError, TypeError):
        pass
    return {"run_id": run_id, "run_directory": ref(run), "agent_status": result.get("status"),
            "stop_reason": result.get("stop_reason"), "llm_calls": llm_calls, "tool_calls": tool_calls,
            "duration_seconds": duration, "capture_errors": errors, "capture_complete": not errors,
            "document_tool_failure_observed": failed_document}, rows


def extract(campaign: Path) -> list[dict[str, Any]]:
    """Regenerate steps and capture diagnostics; never edit native/session evidence."""
    rows = []
    diagnostics = []
    paths = sorted((campaign / "sesiones").glob("*.json"))
    sessions = ([json.loads(path.read_text(encoding="utf-8")) for path in paths] if paths else
                json.loads((campaign / "resumen.json").read_text(encoding="utf-8"))["sessions"])
    for session in sessions:
        if session.get("run_directory"):
            run = campaign / session["run_directory"]
            if not run.resolve().is_relative_to(campaign.resolve()):
                raise ValueError("Run reference escapes campaign")
            details, steps = inspect_run(campaign, run, session["case_id"], session["session_id"])
            diagnostics.append({"case_id": session["case_id"], "session_id": session["session_id"],
                                "capture_complete": details["capture_complete"], "capture_errors": details["capture_errors"]})
            rows.extend(steps)
        else:
            diagnostics.append({"case_id": session["case_id"], "session_id": session["session_id"],
                                "capture_complete": False, "capture_errors": session.get("capture_errors", []),
                                "status": session["status"]})
    with (campaign / "pasos.jsonl").open("w", encoding="utf-8") as stream:
        for item in rows:
            stream.write(json.dumps(item, ensure_ascii=False) + "\n")
    save(campaign / "extraccion.json", {"sessions": diagnostics})
    return rows
