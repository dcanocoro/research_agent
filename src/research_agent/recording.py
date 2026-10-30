from __future__ import annotations
"""Per-run evidence; editable knowledge and original materials live in Workspace."""
import json
import hashlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any
from .contracts import serializable
from .experiments import git_state, human_name
from .workspace import Workspace


def encoded(value: Any) -> bytes:
    return json.dumps(serializable(value), ensure_ascii=False, sort_keys=True).encode("utf-8")


class RunRecorder:
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
        self.contract_changes: list[str] = []
        self.checkpoints: list[dict[str, Any]] = []

    def start(self, run_id: str, metadata: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        contracts = metadata.get("state_contracts", {})
        for contract in contracts.values():
            contract["sha256"] = hashlib.sha256(contract["text"].encode("utf-8")).hexdigest()
        previous = None
        for candidate in sorted(self.root.glob("*/manifiesto.json"), key=lambda p: p.stat().st_mtime_ns, reverse=True):
            Workspace._check_links(candidate)
            value = json.loads(candidate.read_bytes())
            if value.get("workspace_fingerprint") == metadata.get("workspace_fingerprint"):
                previous = value.get("state_contracts", {})
                break
        self.contract_changes = ([] if previous is None else sorted(
            name for name in contracts.keys() | previous.keys()
            if contracts.get(name, {}).get("sha256") != previous.get(name, {}).get("sha256")))
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
        self.checkpoints = []
        self.workspace_fingerprint = metadata.get("workspace_fingerprint")
        self.save("manifiesto.json", {**metadata, "run_directory": current.name,
                                    "state_contract_changes": self.contract_changes,
                                    "git_initial": git_state(self.experiment)})

    def save(self, name: str, value: Any) -> str:
        if self.current is None:
            raise RuntimeError("No active recording.")
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
        (self.current / name).write_text(content, encoding="utf-8")

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
        bounded.path(f"{parts[1]}/trazas/{parts[2]}")
        manifest = run / "manifiesto.json"
        Workspace._check_links(manifest)
        metadata = json.loads(manifest.read_bytes())
        if metadata.get("workspace_fingerprint") != self.workspace_fingerprint:
            raise FileNotFoundError("Artifact belongs to another workspace.")
        return {"reference": reference, **Workspace(run / "trazas", create=False).read_file(parts[2], offset, max_bytes)}

    def snapshot(self, workspace: Workspace) -> dict[str, Any]:
        try:
            return workspace.snapshot(errors=self.capture_errors)
        except Exception as exc:
            issue = {"operation": "state_snapshot", "error_type": type(exc).__name__}
            self.capture_errors.append(issue)
            return {"capture_error": issue}

    def checkpoint(self, workspace: Workspace, label: str, **metadata: Any) -> None:
        """Offline evidence only; never injected as memory or used to control research."""
        start_errors = len(self.capture_errors)
        try:
            paths = self.snapshot(workspace)
            contents = {}
            for path in sorted(paths):
                if path == "capture_error" or Path(path).parts[0].casefold() == "materiales":
                    continue
                try:
                    raw, version = workspace.read_version(path)
                    contents[path] = {"text": raw.decode("utf-8"), "sha256": version}
                except (OSError, ValueError) as exc:
                    self.capture_errors.append({"operation": "knowledge_checkpoint", "path": path,
                                                "error_type": type(exc).__name__})
            reference = f"continuidad/estado-{len(self.checkpoints):04d}.json"
            item = {"schema_version": "knowledge-checkpoint-v1", "label": label, **metadata,
                    "capture_complete": len(self.capture_errors) == start_errors,
                    "files": contents, "capture_errors": self.capture_errors[start_errors:]}
            self.save(reference, item)
            entry = {"reference": reference, "label": label, **metadata,
                     "capture_complete": item["capture_complete"]}
            self.checkpoints.append(entry)
            self.save("continuidad/indice.json", {"schema_version": "knowledge-checkpoints-v1",
                                                  "checkpoints": self.checkpoints})
            self.event("lab.knowledge.checkpoint", **entry)
        except Exception as exc:
            self.capture_errors.append({"operation": "knowledge_checkpoint", "error_type": type(exc).__name__})

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
            with (self.current / "eventos.jsonl").open("ab") as stream:
                stream.write(encoded(event) + b"\n")
