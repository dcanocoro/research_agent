"""Compact work focus, derived from the agenda rather than a second memory."""
from __future__ import annotations

import hashlib
from typing import Any

from .state_tools import headings, section_text


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
