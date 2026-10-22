# A0 y A1 — primera observación longitudinal v2

Fecha de revisión: 2026-10-22. Evidencia local, no portable en Git:
`artifacts/benchmark/20261022T124506Z-6393f0d2` (A0) y
`artifacts/benchmark/20261022T144636Z-4053832b` (A1). Se revisaron respuestas,
trayectorias compactas, capturas inicial/final y SQLite en solo lectura.

## Observado

- Ambas campañas completaron 18 sesiones con captura íntegra. Coinciden código,
  dependencias, definiciones, modelo, esfuerzo y límites; A1 añade herramientas y
  prompt de expediente. Una tentativa por condición, sin evaluación ciega.
- ASML y NVIDIA de A1 terminaron con SQLite vacío. Ford conservó tres evidencias y
  una evaluación con revisiones 1 y 2; desde la tercera sesión continuó en Markdown.
- En Ford 02 la búsqueda por ID devolvió vacío; listar sin texto y knowledge_read
  sí recuperaron el registro. En Ford 03–06 volvió a buscar el ID o frases literales
  sin recuperarlo. La revisión 2 permanecía en la captura final.
- Ford 04 intentó crear el ID existente con expected_revision=0; knowledge_apply
  rechazó el lote por conflicto. No quedaron aplicadas sus evidencias parciales.
  La corrección posterior quedó en Markdown, con SQLite desactualizado.
- La búsqueda implementada comparaba el texto con el contenido JSON, sin incluir
  el ID. Las descripciones no explicitaban suficientemente el carácter literal.
- La fuente ASML decía «8 nuevos pedidos» sin importe, pero la rúbrica esperaba
  sumar 8 miles de millones EUR. Ambos agentes evitaron esa suma; el criterio
  cuantitativo estaba insuficientemente especificado y no se penaliza al agente.

Referencias de traza A1: Ford 02 secuencias 36/64/71 (búsqueda/listado/lectura),
Ford 04 secuencia 95 (lote rechazado); Ford 06 `conocimiento-final.json` conserva
las revisiones. Las secuencias identifican captura observable, no razonamiento privado.

## Interpretación e hipótesis

El almacenamiento y los controles mecánicos conservaron los datos examinados.
La adopción y recuperación del expediente no fueron fiables, y el tratamiento
argumentativo apenas se ejercitó. No demuestra inutilidad de SQLite ni una ventaja
de A1. La divergencia entre Markdown y SQLite es un fallo operativo relevante.

Hipótesis de reparación: hacer recuperables los IDs, explicar búsqueda y conflicto,
y pedir conservación de avances materiales con estructura mínima permitirá probar
el mecanismo antes de atribuirle beneficios semánticos. La siguiente comparación
necesita nuevas campañas con los mismos estímulos corregidos para ambas condiciones.
La [preparación v2.1](../longitudinal-v2-1/protocol.md) registra la intervención.
