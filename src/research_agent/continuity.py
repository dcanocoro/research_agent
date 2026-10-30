"""Compact work focus, derived from the agenda rather than a second memory."""
from __future__ import annotations

import hashlib
import re
import json
from typing import Any

from .state_tools import headings, section_text
from .workspace import Workspace


AGENDA_TEMPLATE = """# Agenda

## Prioridades generales
Pendiente de concretar a partir del mandato.

## Investigación activa
Sin investigación seleccionada todavía. Decide qué pregunta material abordar.
Al seleccionarla, conserva pregunta, relevancia, último avance, incertidumbre decisiva,
criterio de cierre, referencias y siguiente acción tentativa.

## Investigaciones aplazadas
Ninguna registrada.

## Decisiones y cambios de prioridad
Sin cambios registrados.
"""


def focus_context(agenda: str) -> dict[str, Any]:
    raw = agenda.encode("utf-8")
    hs = headings(raw)
    candidates = [h for h in hs if h["title"].casefold() == "investigación activa"]
    focus: dict[str, Any] = {"source": "agenda.md", "sha256": hashlib.sha256(raw).hexdigest(),
                             "available": len(candidates) == 1,
                             "instruction": "Reevalúa la investigación activa de la agenda ya incluida: qué intentabas resolver, último avance, incertidumbre y siguiente exploración. Recupera fundamentos selectivamente; no trates el plan previo como una orden."}
    if len(candidates) == 1:
        heading = candidates[0]
        text = section_text(raw, heading, hs)
        focus["selector"] = {"kind": "section", "start": heading["line"], "end": None}
        focus["end_line"] = heading["line"] + len(text.splitlines()) - 1
    else:
        focus["note"] = "No unique active section; interpret the existing agenda without inventing a focus or migrating it automatically."
    return focus


def utf8_excerpt(text: str, limit: int) -> str:
    return text.encode("utf-8")[:limit].decode("utf-8", errors="ignore")


def active_foundations(workspace: Workspace, agenda: str) -> list[dict[str, Any]]:
    hs = headings(agenda.encode("utf-8"))
    active = [h for h in hs if h["title"].casefold() == "investigación activa"]
    if len(active) != 1:
        return []
    text = section_text(agenda.encode("utf-8"), active[0], hs)
    refs = list(dict.fromkeys(re.findall(r"(?<![\w/])([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+){0,2}\.md(?:#[A-Za-z][A-Za-z0-9_-]*)?)", text)))[:2]
    result = []
    remaining = 8192
    for ref in refs:
        path, _, identifier = ref.partition("#")
        try:
            raw, version = workspace.read_version(path)
            content = raw.decode("utf-8")
            if identifier:
                headers = headings(raw)
                selected = [h for h in headers if h["id"] == identifier]
                if len(selected) != 1:
                    raise ValueError("missing_or_ambiguous_id")
                content = section_text(raw, selected[0], headers)
            excerpt = utf8_excerpt(content, remaining)
            remaining -= len(excerpt.encode("utf-8"))
            result.append({"reference": ref, "path": path, "sha256": version,
                           "text": excerpt, "partial": excerpt != content})
        except (OSError, ValueError) as exc:
            result.append({"reference": ref, "error": type(exc).__name__, "detail": str(exc)[:160]})
    # Include metadata and escaping in the protected-view budget too.
    for item in result:
        if 'reference' in item and len(item['reference'].encode('utf-8')) > 1024:
            item['reference'] = utf8_excerpt(item['reference'], 1024)
            item['reference_partial'] = True
    while len(json.dumps(result, ensure_ascii=False).encode('utf-8')) > 8192:
        excess = len(json.dumps(result, ensure_ascii=False).encode('utf-8')) - 8192
        shrink_item = next((item for item in reversed(result) if item.get('text')), None)
        if shrink_item is None:
            result.pop()
            continue
        shrink_item['text'] = utf8_excerpt(shrink_item['text'], max(0, len(shrink_item['text'].encode('utf-8')) - excess - 8))
        shrink_item['partial'] = True
    return result


class OperationalObserver:
    """Advisory signals only; no semantic inference or control permissions."""
    def __init__(self) -> None:
        self.seen: dict[str, str] = {}
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
