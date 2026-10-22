"""Read compact run evidence without importing campaign orchestration."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

from .workspace import Workspace


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


FORMAT = "benchmark-compact-v1"


def reference(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def resolve(root: Path, name: str) -> Path:
    if not isinstance(name, str) or "\\" in name or ":" in name or Path(name).is_absolute() or ".." in name.split("/"):
        raise ValueError("Evidence reference escapes campaign")
    path = root / name
    Workspace._check_links(path)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Evidence reference escapes campaign")
    return path


def read_json(path: Path) -> Any:
    Workspace._check_links(path)
    return json.loads(path.read_text(encoding="utf-8"))


def records(run: Path) -> list[dict[str, Any]]:
    Workspace._check_links(run / "trayectoria.jsonl.gz")
    with gzip.open(run / "trayectoria.jsonl.gz", "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def material(root: Path, ref: dict[str, Any]) -> Any:
    path = resolve(root, ref["ref"])
    if digest(path) != ref["sha256"]:
        raise ValueError(f"Material hash mismatch: {ref['ref']}")
    return read_json(path)


def full_result(root: Path, record: dict[str, Any]) -> Any:
    value = record["full_result"]
    return material(root, value) if record.get("full_result_is_reference") else value


def delivered_result(root: Path, record: dict[str, Any]) -> Any:
    if record.get("delivered_value_is_full_result"):
        return {**record["delivered"], "value": full_result(root, record)}
    return record["delivered"]


def restore_snapshot(root: Path, value: dict[str, Any]) -> dict[str, Any]:
    if value.get("schema_version") != FORMAT:
        return value
    result = {}
    for name, entry in value["files"].items():
        if isinstance(entry, dict) and "ref" in entry:
            path = resolve(root, entry["ref"])
            if digest(path) != entry["sha256"]:
                raise ValueError(f"Snapshot material hash mismatch: {name}")
            result[name] = path.read_text(encoding="utf-8")
        else:
            result[name] = entry
    return result


