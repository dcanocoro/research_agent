# ADR-0005 — Núcleo ReAct común y extensiones explícitas

Estado: Aceptada
Fecha: 2026-11-02

## Contexto

La [auditoría del código](../deliveries/2026-11-02-runtime-audit.md) identifica dos
bucles y políticas de B, evaluación y continuidad mezcladas con la infraestructura.
El usuario eligió unificar ambos bucles y solicitó implementar el plan revisado.
La aceptación corresponde a esta organización, no a la eficacia de los mecanismos.

## Decisión y alternativas

Un solo motor de interacción para acotado, continuo y B. Una política pequeña
prepara la sesión, decide el siguiente paso, recibe el resultado y finaliza.
Llamadas, herramientas, timeouts y captura utilizan servicios comunes. Las
revisiones aisladas pasan por el mismo transporte, sin herramientas.

Composición selecciona las implementaciones: acotado predeterminado, régimen E2
con progreso general o por objetivos, y B preparado opcional. Multiagente,
progreso y regímenes tienen ubicaciones propias. Los formatos, prompts congelados,
identidades y comandos existentes se conservan mediante adaptadores. No se añade
un sistema genérico de plugins ni nuevos comportamientos seleccionables.

La alternativa de extraer solo el transporte y conservar los dos bucles se
presentó durante la planificación; el usuario eligió la unificación en esta entrega.

## Justificación

Permite comprobar el motor y sus fronteras sin activar los mecanismos experimentales,
conservar un único lugar de interacción y localizar reservas y cierres específicos.
La separación responde a dependencias observadas; no demuestra mejor investigación.

## Consecuencias

La fachada y los imports anteriores siguen disponibles. El estado E2 que cruza
responsabilidades conserva su representación para no imponer una migración.
Los fingerprints cambian y las campañas preparadas que exigen identidad exacta
requieren una preparación nueva; no se desactiva esa comprobación.

Los regímenes actualmente admitidos conservan sus colaboraciones: E2 incluye
revisión y B preparado exige ese continuo de 100 llamadas. No se prometen nuevas
combinaciones ni una política financiera nueva. La selección vive en composición;
el motor no importa implementaciones experimentales.

La [entrega](../deliveries/2026-11-02-runtime-refactor.md) recoge checks y límites.
La reutilización en FinMate requerirá adaptar contratos y permisos en otro encargo.
