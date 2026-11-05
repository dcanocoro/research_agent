"""Compact work focus, derived from the agenda rather than a second memory."""
from __future__ import annotations

import hashlib
import re
import json
from typing import Any

from research_agent.capabilities.state.operations import headings
from research_agent.capabilities.state.operations import section_text
from research_agent.storage.workspace import Workspace


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
