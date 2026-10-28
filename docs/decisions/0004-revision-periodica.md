# ADR-0004 — Revisión periódica permanente en el ciclo continuo

Estado: Aceptada
Fecha: 2026-10-27

## Contexto

El análisis v3 aportado por el usuario describe progreso parcial, recuperación
repetida y conservación concentrada en consolidaciones técnicas. Esa observación
motiva una oportunidad explícita de reconsiderar el trabajo; no demuestra que la
ausencia de revisión periódica sea su causa. El usuario aprobó el plan de implementación.

## Decisión y alternativas

Integrar permanentemente en el ciclo continuo una llamada sin herramientas cada diez
llamadas de investigación, con el mismo modelo y contexto. El modelo elige el enfoque;
el harness fija la ocasión de revisarlo. La consolidación tiene prioridad y el contador
se conserva entre ventanas. No añadir un interruptor, otro agente ni archivos de reflexión.

El límite de llamadas ordinarias cubre investigación y consolidación; las revisiones
son adicionales, con tiempo y contexto compartidos. Conservar el total real y añadir
desglose por fase. El ciclo acotado mantiene su comportamiento.

Se consideraron un aviso dentro de la siguiente acción ordinaria, un techo compartido
de llamadas y extenderlo al ciclo acotado. El usuario eligió llamada aparte, presupuesto
adicional y alcance continuo. La [arquitectura](../architecture.md#revisión-periódica-permanente--2026-10-27)
define el contrato y el [protocolo](../experiments/contexto-continuo-v1/protocol.md#v4--revisión-periódica-permanente)
define la observación futura.

## Justificación

La intervención se resuelve en el bucle existente y permite separar su coste de las
oportunidades ordinarias. La elección permanente está aceptada por el usuario;
su eficacia intelectual no está validada por los checks locales.

## Consecuencias

Cambian las unidades presupuestarias de `--max-calls` solo en continuo. Se añade
consumo y latencia; el contexto de revisión puede adelantar una consolidación.
No se garantiza un cambio de enfoque, conservación útil ni mejor análisis financiero.
Reconsiderar frecuencia o mecanismo si la observación muestra reflexión ritual sin
acciones útiles o coste desproporcionado. No se ejecuta v4 en esta entrega.
