"""Existing advisory research observations, isolated from context mechanics."""
from __future__ import annotations
import json
from typing import Any
from research_agent.storage.workspace import Workspace

class OperationalObserver:
    """Advisory signals only; no semantic inference or control permissions."""
    def __init__(self) -> None:
        self.seen: dict[str, str] = {}
        self.repetitions: dict[str, int] = {}
        self.notified: set[str] = set()
        self.conflicts: dict[str, int] = {}
        self.last_conflict_path: str | None = None
        self.since_write = 0
        self.persistence_notified = False
        self.pending: list[dict[str, Any]] = []

    def research_call(self) -> None:
        self.since_write += 1

    def observe(self, tool: str, arguments: dict[str, Any], payload: dict[str, Any],
                material: bool, workspace: Workspace, mutation: bool = False) -> None:
        value = payload.get("value", {})
        if payload.get("applied") or (payload.get("ok") and mutation):
            self.since_write = 0
            self.persistence_notified = False
        if material and payload.get("ok"):
            key = json.dumps([tool, arguments], sort_keys=True, ensure_ascii=False)
            if key in self.seen and key not in self.notified:
                self.pending.append({"kind": "repeated_query", "tool": tool, "reference": self.seen[key],
                                     "note": "Consulta ya satisfecha; valora reutilizar su resultado. No se bloquea."})
                self.notified.add(key)
            if key in self.seen:
                self.repetitions[key] = self.repetitions.get(key, 0) + 1
                persistent = "persistent:" + key
                if self.repetitions[key] >= 2 and persistent not in self.notified:
                    self.pending.append({"kind": "repeated_query_persistent", "tool": tool,
                                         "reference": self.seen[key], "note": "Repetition after advisory; consider another approach."})
                    self.notified.add(persistent)
            self.seen[key] = payload.get("material_ref", payload.get("artifact_ref", ""))
        path = arguments.get("path")
        if not path and arguments.get("changes") and "version_conflict: " in payload.get("message", ""):
            path = payload["message"].split("version_conflict: ", 1)[1]
        if not path and arguments.get("symbol") and arguments.get("dimension"):
            path = f"empresas/{arguments['symbol']}/{arguments['dimension']}.md"
        if not payload.get("ok") and "version_conflict" in payload.get("message", "") and path:
            self.conflicts[path] = self.conflicts.get(path, 0) + 1 if self.last_conflict_path == path else 1
            self.last_conflict_path = path
            if self.conflicts[path] >= 2:
                try:
                    version = workspace.read_version(path)[1]
                    key = "version:" + path + version
                    if key not in self.notified:
                        self.pending.append({"kind": "version_conflict", "path": path, "sha256": version,
                                             "note": "Relee el archivo vigente antes de editar; no se reintenta automáticamente."})
                        self.notified.add(key)
                except (OSError, ValueError):
                    pass
        else:
            self.last_conflict_path = None

    def drain(self) -> list[dict[str, Any]]:
        if self.since_write >= 10 and not self.persistence_notified:
            self.pending.append({"kind": "persistence_interval", "research_calls": self.since_write,
                                 "note": "Valora si hay avances materiales que conservar. No implica ausencia de progreso ni obliga a escribir."})
            self.persistence_notified = True
        result: list[dict[str, Any]] = []
        while self.pending:
            item = self.pending.pop(0)
            if len(json.dumps([*result, item], ensure_ascii=False).encode("utf-8")) <= 4096:
                result.append(item)
        return result
