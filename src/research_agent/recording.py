from __future__ import annotations
"""Immutable per-run artifacts, plus a structured event journal."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .contracts import serializable


def encoded(value: Any) -> bytes:
    return json.dumps(serializable(value), ensure_ascii=False, sort_keys=True).encode("utf-8")


class RunRecorder:
    def __init__(self, root: Path) -> None:
        self.root = root.absolute()
        self.events: list[dict[str, Any]] = []
        self.current: Path | None = None
        self.workspace_fingerprint: str | None = None

    def start(self, run_id: str, metadata: dict[str, Any]) -> None:
        self.current = self.root / run_id
        self.current.mkdir(parents=True, exist_ok=False)
        self.events = []
        self.workspace_fingerprint = metadata.get("workspace_fingerprint")
        self.save("manifest.json", metadata)

    def save(self, name: str, value: Any) -> str:
        if self.current is None:
            raise RuntimeError("No active recording.")
        path = self.current / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encoded(value))
        return name

    def artifact(self, value: Any) -> str:
        data = encoded(value)
        name = f"artifacts/{hashlib.sha256(data).hexdigest()}.json"
        self.save(name, value)
        return name

    def read_artifact(self, reference: str, offset: int = 0, max_bytes: int = 32768) -> dict[str, Any]:
        if (self.current is None or not reference.startswith("artifacts/")
                or len(reference.split("/")) != 2 or not reference.endswith(".json")
                or not 1 <= max_bytes <= 32768 or offset < 0):
            raise ValueError("Invalid artifact read.")
        name = reference.split("/")[1][:-5]
        if len(name) != 64 or any(c not in "0123456789abcdef" for c in name):
            raise ValueError("Invalid artifact identity.")
        source = self.current / reference
        if not source.is_file() and self.workspace_fingerprint:
            for manifest in sorted(self.root.glob("*/manifest.json")):
                try:
                    matching = json.loads(manifest.read_bytes()).get("workspace_fingerprint") == self.workspace_fingerprint
                except (OSError, ValueError):
                    continue
                candidate = manifest.parent / reference
                if matching and candidate.is_file():
                    source = candidate
                    break
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != name:
            raise ValueError("Artifact hash mismatch.")
        chunk = data[offset:offset + max_bytes]
        for trim in range(4):
            try:
                selected = chunk[:len(chunk)-trim] if trim else chunk
                text = selected.decode("utf-8")
                break
            except UnicodeDecodeError:
                if trim == 3:
                    raise ValueError("Offset is not a UTF-8 character boundary.") from None
        else:
            text = ""
        end = offset + len(selected)
        return {"reference": reference, "text": text, "next_offset": end if end < len(data) else None}

    def event(self, name: str, **fields: Any) -> None:
        from observability_context import current_interaction_context
        from runtime_contracts.execution import current_run_context
        interaction, run = current_interaction_context(), current_run_context()
        event = {"event": name, "occurred_at": datetime.now(timezone.utc).isoformat(),
                 "run_id": run.run_id if run else None,
                 "conversation_id": interaction.conversation_id if interaction else None,
                 "interaction_id": interaction.interaction_id if interaction else None,
                 "sequence": len(self.events) + 1, **fields}
        self.events.append(event)
        if self.current is not None:
            with (self.current / "events.jsonl").open("ab") as stream:
                stream.write(encoded(event) + b"\n")
