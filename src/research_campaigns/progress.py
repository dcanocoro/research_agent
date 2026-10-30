"""Offline V6 observations and explicit numerical checks; never directs the agent."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from research_agent.continuity import focus_context
from research_agent.recording import encoded
from research_agent.state_tools import headings, section_has_body, section_text
from research_agent.workspace import Workspace


def number(value: Any) -> Decimal:
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("Numerical checks require finite decimal values.")
    return result


def resolve_value(state: dict[str, str], reference: dict[str, Any]) -> Decimal:
    """Resolve an explicit JSON pointer in captured original evidence, not live data."""
    path, pointer = reference["path"], reference["pointer"]
    if not path.startswith("materiales/") or not path.endswith(".json"):
        raise ValueError("Numerical inputs must reference captured materiales/*.json.")
    value = json.loads(state[path], parse_float=Decimal, parse_int=Decimal)
    if pointer:
        if not pointer.startswith("/"):
            raise ValueError("Expected a JSON pointer.")
        for token in pointer[1:].split("/"):
            key = token.replace("~1", "/").replace("~0", "~")
            value = value[int(key)] if isinstance(value, list) else value[key]
    if isinstance(value, (bool, dict, list)) or value is None:
        raise ValueError("Pointer must select a numerical scalar.")
    return number(value)


def numerical_checks(state: dict[str, str], specification: dict[str, Any]) -> list[dict[str, Any]]:
    if specification.get("schema_version") != "numerical-checks-v1":
        raise ValueError("Expected numerical-checks-v1.")
    if not isinstance(specification.get("checks"), list) or not all(isinstance(c, dict) for c in specification["checks"]):
        raise ValueError("Expected a list of explicit numerical check objects.")
    results = []
    for check in specification["checks"]:
        result = {"document": check.get("document"), "quote": check.get("quote"),
                  "unit": check.get("unit"), "specification": check}
        try:
            quote = check["quote"]
            if not isinstance(quote, str) or not quote or quote not in state[check["document"]]:
                raise ValueError("Exact quoted assertion is absent from captured document.")
            reported = str(check["reported"])
            if not re.search(r"(?<![\d.])" + re.escape(reported) + r"(?![\d.])", quote.replace(",", ".")):
                raise ValueError("Reported value must occur literally in the quoted assertion (decimal dot/comma).")
            units = [check["unit"], check["left"]["unit"], check["right"]["unit"]]
            if not all(isinstance(unit, str) and unit.strip() for unit in units):
                raise ValueError("Explicit input and output units are required.")
            left, right = resolve_value(state, check["left"]), resolve_value(state, check["right"])
            operation = check["operation"]
            if operation in {"add", "subtract"} and check["left"]["unit"] != check["right"]["unit"]:
                raise ValueError("Addition/subtraction requires matching declared input units.")
            if operation == "add":
                expected = left + right
            elif operation == "subtract":
                expected = left - right
            elif operation == "multiply":
                expected = left * right
            elif operation == "divide":
                expected = left / right
            else:
                raise ValueError("Unsupported explicit numerical operation.")
            expected *= number(check["scale"])
            tolerance = number(check["tolerance"])
            if tolerance < 0:
                raise ValueError("Tolerance must be nonnegative.")
            difference = abs(number(reported) - expected)
            result.update(status="matches" if difference <= tolerance else "mismatch",
                          expected=str(expected), absolute_difference=str(difference))
        except (KeyError, ValueError, TypeError, IndexError, InvalidOperation, ArithmeticError) as exc:
            result.update(status="unobservable", reason=str(exc))
        results.append(result)
    return results


def inspect_documents(files: dict[str, Any]) -> dict[str, Any]:
    empty: list[str] = []
    duplicate: list[str] = []
    for path, value in files.items():
        if not path.startswith("empresas/") or not path.endswith(".md"):
            continue
        raw = value["text"].encode("utf-8")
        hs = headings(raw)
        ids = [h["id"] for h in hs if h["id"]]
        duplicate.extend(f"{path}#{key}" for key in sorted(set(ids)) if ids.count(key) > 1)
        empty.extend(f"{path}#{h['id']}" for h in hs
                     if h["id"] and not section_has_body(section_text(raw, h, hs)))
    return {"empty_ids": empty, "duplicate_ids": duplicate}


def evaluate_run(run: Path, checks: Path | None = None) -> dict[str, Any]:
    """Use native captures only; missing checkpoints remain explicitly unobservable."""
    run = run.absolute()
    Workspace._check_links(run)
    def read(name: str) -> Any:
        path = run / name
        Workspace._check_links(path)
        return json.loads(path.read_bytes())
    manifest = read("manifiesto.json")
    observations = []
    index_path = run / "continuidad/indice.json"
    Workspace._check_links(index_path)
    previous: dict[str, Any] = {}
    previous_complete = True
    if index_path.exists():
        for entry in read("continuidad/indice.json")["checkpoints"]:
            relative = Path(entry["reference"])
            if relative.is_absolute() or len(relative.parts) != 2 or relative.parts[0] != "continuidad" or ".." in relative.parts:
                raise ValueError("Checkpoint reference escapes native continuity capture.")
            checkpoint = read(entry["reference"])
            if checkpoint.get("schema_version") != "knowledge-checkpoint-v1":
                raise ValueError("Unknown checkpoint schema.")
            files = checkpoint["files"]
            for value in files.values():
                if hashlib.sha256(value["text"].encode("utf-8")).hexdigest() != value["sha256"]:
                    raise ValueError("Checkpoint content/hash mismatch.")
            changed = [p for p in sorted(files.keys() | previous.keys()) if files.get(p) != previous.get(p)]
            comparable = previous_complete and checkpoint["capture_complete"]
            observations.append({"reference": entry["reference"], "label": checkpoint["label"],
                                 "llm_calls_used": checkpoint.get("llm_calls_used"),
                                 "llm_calls_by_phase": checkpoint.get("llm_calls_by_phase"),
                                 "capture_complete": checkpoint["capture_complete"],
                                 "comparison_status": "available" if comparable else "unobservable",
                                 "changed_documents": changed if comparable else [],
                                 "focus": focus_context(files.get("agenda.md", {}).get("text", "")),
                                 **inspect_documents(files)})
            previous = files
            previous_complete = checkpoint["capture_complete"]
    writes = {"research": 0, "consolidation": 0, "review": 0, "external_review": 0, "unknown": 0}
    successful_reads = []
    context_number, phase = 0, "unknown"
    pending = {}
    events_path = run / "eventos.jsonl"
    Workspace._check_links(events_path)
    for line in events_path.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        name = event["event"]
        if name == "lab.model.started":
            phase = event["phase"]
        elif name == "lab.context.renewed":
            context_number = event["context_number"]
        elif name == "lab.file.written":
            writes[phase if phase in writes else "unknown"] += 1
        elif name == "lab.tool.started":
            pending[event["call_id"]] = event
        elif name == "lab.tool.completed":
            started = pending.get(event["call_id"], {})
            if started.get("tool_name") in {"read_company_document", "read_state", "read_file"}:
                successful_reads.append({"context_number": context_number, "phase": phase,
                                         "sequence": event["sequence"], "arguments": started["arguments"],
                                         "artifact_ref": event["artifact_ref"]})
    final = read("estado-final.json")
    numerical = []
    if checks is not None:
        Workspace._check_links(checks)
        numerical = numerical_checks(final, json.loads(checks.read_bytes()))
    return {"schema_version": "research-progress-v6", "run_id": manifest["run_id"],
            "observations": observations, "checkpoint_status": "available" if observations else "unobservable",
            "writes_by_phase": writes, "successful_read_events": successful_reads,
            "numerical_checks": numerical,
            "semantic_review": {dimension: {"status": "not_assessed", "question": question}
                                for dimension, question in {
                                    "progress": "What material question became clearer or was resolved? Cite before/after evidence, including justified lack of data.",
                                    "quality": "Are retained conclusions, numbers and uncertainties supported by original sources?",
                                    "utility": "What new comparison or evaluation does the knowledge permit?",
                                    "recovery": "After renewal, was the actual argument recovered faithfully without redundant investigation?"}.items()},
            "limits": "Mechanical observations are not semantic scores. Reads do not prove comprehension; closed tasks do not prove resolution. Numerical checks cover explicit assertions only; declared units, scale and chosen sources require review. No LLM, providers or feedback to researcher."}


def save_report(run: Path, output: Path, checks: Path | None = None) -> None:
    report = evaluate_run(run, checks)
    # Reports belong to audit, never inside editable estado/ or frozen campaign inputs.
    if output.absolute().parent != run.absolute():
        raise ValueError("Progress output must be a direct child of the native run directory.")
    if output.suffix != ".json" or output.name in {"manifiesto.json", "estado-inicial.json", "estado-final.json", "resultado.json", "conversacion.json", "git-final.json"}:
        raise ValueError("Choose a separate progress JSON report name.")
    Workspace._check_links(output)
    with output.open("xb") as stream:
        stream.write(encoded(report))
