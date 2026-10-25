# ADR-0003 — Condición experimental de intención persistente

Estado: Aceptada
Fecha: 2026-10-24

## Contexto

El usuario aprobó implementar el plan de mandato persistente, agenda automática y
disciplina de continuidad, preparando un piloto sin proveedores reales. La campaña
anterior mostró recuperación de archivos y pérdida parcial del encargo inicial según
su análisis local; la asociación con la estrechez investigadora no identifica causalidad.

## Decisión y alternativas

Mantener A y activar explícitamente la condición mediante un mandato auténtico
externo al estado editable. Cargar también la agenda y registrar el contexto entregado.
El controlador conserva mensajes por fecha y congela la condición. Sin mandato se
mantiene el comportamiento baseline. Reutilizar herramientas y reserva de cierre.

Dejar el mandato únicamente en la memoria del modelo mantiene el riesgo de pérdida;
un planificador, otra base de memoria o un workflow no son necesarios para este contraste.
El [protocolo](../experiments/intencion-persistente-v1/protocol.md) fija interfaces,
comparación, presupuestos y límites. No se elige la arquitectura final de FinMate.

## Justificación

Elección experimental aceptada explícitamente por el usuario; su utilidad todavía
debe observarse. Permite comprobar entrega del encargo y continuidad de intenciones
sin programar la selección de empresas ni la secuencia de investigación.

## Consecuencias

Se añade contexto y mantenimiento de agenda, cuyo coste debe medirse. El mandato no
puede ampliarse por escrituras del agente. No hay resumen automático, transacción
multiarchivo ni garantía de guardar lo que permanecía solo en contexto. Se reconsiderará
el mecanismo si el piloto muestra mantenimiento sin progreso o pérdida de continuidad.
La ejecución posterior y sus límites se registran en los
[hallazgos de la ampliación](../experiments/intencion-persistente-v1/findings-amplio.md);
no convierten esta elección experimental en aceptación semántica.
