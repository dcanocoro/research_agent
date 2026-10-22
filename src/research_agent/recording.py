from __future__ import annotations
"""Per-run evidence; editable knowledge and original materials live in Workspace."""
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any
from .contracts import serializable
from .experiments import git_state, human_name
from .workspace import Workspace
from .knowledge import KnowledgeStore


def encoded(value: Any) -> bytes:
    return json.dumps(serializable(value), ensure_ascii=False, sort_keys=True).encode("utf-8")


class RunRecorder:
    names = {"manifest.json": "manifiesto.json", "result.json": "resultado.json",
             "transcript.json": "conversacion.json", "events.jsonl": "eventos.jsonl",
             "workspace_before.json": "estado-inicial.json", "workspace_after.json": "estado-final.json",
             "answer.md": "respuesta.md"}

    def __init__(self, root: Path, *, experiment: Path | None = None, run_name: str = "intervencion") -> None:
        self.root = root.absolute()
        Workspace._check_links(self.root)
        self.experiment, self.run_name = experiment, human_name(run_name)
        self.events: list[dict[str, Any]] = []
        self.current: Path | None = None
        self.workspace: Workspace | None = None
        self.workspace_fingerprint: str | None = None
        self.sequence = 0
        self.capture_errors: list[dict[str, str]] = []
        self.knowledge: KnowledgeStore | None = None
        self.knowledge_snapshot_count = 0

    def filename(self, name: str) -> str:
        return self.names.get(name, name) if self.experiment is not None else name

    def start(self, run_id: str, metadata: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        stem = f"{datetime.now(ZoneInfo('Europe/Madrid')):%Y-%m-%d}-{self.run_name}"
        for i in range(1, 100000):
            current = self.root / (stem if i == 1 else f"{stem}-{i:02d}")
            try:
                current.mkdir(exist_ok=False)
                break
            except FileExistsError:
                continue
        else:
            raise ValueError("Run name exhausted.")
        self.current = current
        self.events, self.capture_errors, self.sequence = [], [], 0
        self.knowledge_snapshot_count = 0
        self.workspace_fingerprint = metadata.get("workspace_fingerprint")
        self.save("manifest.json", {**metadata, "run_directory": current.name,
                                    "git_initial": git_state(self.experiment)})

    def save(self, name: str, value: Any) -> str:
        if self.current is None:
            raise RuntimeError("No active recording.")
        name = self.filename(name)
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or len(relative.parts) > 2:
            raise ValueError("Invalid recording path.")
        path = self.current / name
        Workspace._check_links(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encoded(value))
        return name

    def text(self, name: str, content: str) -> None:
        assert self.current is not None
        (self.current / self.filename(name)).write_text(content, encoding="utf-8")

    def artifact(self, value: Any) -> str:
        assert self.current is not None
        self.sequence += 1
        name = f"trazas/resultado-herramienta-{self.sequence:04d}.json"
        self.save(name, value)
        return f"archivo/{self.current.name}/{Path(name).name}"

    def read_artifact(self, reference: str, offset: int = 0, max_bytes: int = 32768) -> dict[str, Any]:
        if reference.startswith("materiales/") and self.workspace is not None:
            return {"reference": reference, **self.workspace.read_file(reference, offset, max_bytes)}
        parts = reference.split("/")
        if len(parts) != 3 or parts[0] != "archivo" or any(p in {"", ".", ".."} or ":" in p or "\\" in p for p in parts):
            raise ValueError("Invalid artifact reference.")
        bounded = Workspace(self.root, create=False)
        run = bounded.path(parts[1])
        if (run / "ejecucion.json").exists():
            from .benchmark_archive import read_json, records, full_result
            metadata = read_json(run / "ejecucion.json")["manifest"]
            if metadata.get("workspace_fingerprint") != self.workspace_fingerprint:
                raise FileNotFoundError("Artifact belongs to another workspace.")
            entry = next((e for e in records(run) if e["kind"] == "tool" and e.get("artifact_name") == parts[2]), None)
            if entry is None:
                raise FileNotFoundError("Unknown archived tool result")
            value = encoded(full_result(run.parents[3], entry))
            if offset < 0 or not 1 <= max_bytes <= 32768:
                raise ValueError("Invalid read window.")
            end = min(offset + max_bytes, len(value))
            for trim in range(4):
                try:
                    text = value[offset:max(offset, end - trim)].decode("utf-8")
                    end = max(offset, end - trim)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("File is not UTF-8, or offset is not a character boundary.")
            return {"reference": reference, "path": parts[2], "offset": offset, "text": text,
                    "next_offset": end if end < len(value) else None}
        bounded.path(f"{parts[1]}/trazas/{parts[2]}")
        manifest = run / self.filename("manifest.json")
        Workspace._check_links(manifest)
        metadata = json.loads(manifest.read_bytes())
        if metadata.get("workspace_fingerprint") != self.workspace_fingerprint:
            raise FileNotFoundError("Artifact belongs to another workspace.")
        return {"reference": reference, **Workspace(run / "trazas", create=False).read_file(parts[2], offset, max_bytes)}

    def snapshot(self, workspace: Workspace) -> dict[str, Any]:
        try:
            if self.knowledge is not None:
                assert self.current is not None
                phase = "inicial" if self.knowledge_snapshot_count == 0 else "final"
                self.knowledge_snapshot_count += 1
                hashes = self.knowledge.capture(self.current, phase)
                self.save(f"conocimiento-{phase}-hashes.json", hashes)
            return workspace.snapshot(errors=self.capture_errors)
        except Exception as exc:
            issue = {"operation": "state_snapshot", "error_type": type(exc).__name__}
            self.capture_errors.append(issue)
            return {"capture_error": issue}

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
            with (self.current / self.filename("events.jsonl")).open("ab") as stream:
                stream.write(encoded(event) + b"\n")
