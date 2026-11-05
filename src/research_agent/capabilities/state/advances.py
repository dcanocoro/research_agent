from pathlib import Path
from typing import Any
from collections.abc import Callable
from research_agent.storage.workspace import Workspace
from research_agent.storage.transactions import record_advance

def register_advance(registry: Any, workspace: Workspace, *, journal_root: Path | None = None,
                     write_guard: Callable[[list[dict[str, Any]]], None] | None = None) -> None:
    string = {"type": "string"}
    nullable = {"type": ["string", "null"]}
    operation = {"type": "object", "properties": {
        "kind": {"type": "string", "enum": ["replace", "insert_before", "insert_after"]},
        "target": {"type": "string"}, "content": string},
        "required": ["kind", "target", "content"], "additionalProperties": False}
    change = {"type": "object", "properties": {"path": string,
        "action": {"type": "string", "enum": ["create", "edit"]},
        "content": nullable, "expected_sha256": nullable,
        "operations": {"type": ["array", "null"], "minItems": 1, "items": operation}},
        "required": ["path", "action", "content", "expected_sha256", "operations"],
        "additionalProperties": False}
    def apply(changes: list[dict[str, Any]], reason: str, source_refs: list[str]) -> dict[str, Any]:
        if write_guard is not None:
            write_guard(changes)
        return record_advance(workspace, journal_root if journal_root is not None else registry.recorder.root, changes, reason, source_refs)
    registry.register("record_research_advance", "Save one coherent advance across 1-5 files; versions and structural integrity checked; recoverable batch, no semantic certification.",
        {"changes": {"type": "array", "minItems": 1, "maxItems": 5, "items": change},
         "reason": {"type": "string", "minLength": 1}, "source_refs": {"type": "array", "items": string}},
        apply, execution="inline", consolidation=True, mutation=True, bounded=True)
    registry.contracts["record_research_advance"] = {"version": "state-tools-e1",
        "text": "Create: content supplied, operations and expected_sha256 null. Edit: content null, exact operations and current expected_sha256 supplied; empty target only matches an empty file. All changes validate before publishing; recovery journal outside state. Readers/editors external to this process are not isolated. No deletions. Evidence references are not semantically validated."}
