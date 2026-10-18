# ADR-0001 — Estado de archivos por experimento

Estado: Aceptada
Fecha: 2026-10-18

## Contexto

El usuario ha aprobado implementar un estado accesible mediante herramientas, separado
de instrucciones, respuesta final y trazas, con nombres humanos y hasta tres niveles
de carpetas. E001/E002 son antecedentes del candidato anterior, no validaciones de
esta representación ni autorización para elegir la arquitectura definitiva de FinMate.

## Decisión y alternativas

Sustituir workspace Markdown y almacén de expedientes por un único estado Markdown,
JSON, TXT y CSV por experimento. Permitir empezar vacío o continuar, conservar materiales
automáticamente y ofrecer consolidación sin imponer escritura ni publicación.
Git manual conserva las versiones elegidas por la persona; el sistema registra su
situación y captura los extremos de cada run. No hay commits automáticos ni copia
de estados entre experimentos en esta versión.

La alternativa de conservar ambos almacenes mantiene dos interfaces de conocimiento;
la de versionar cada edición desde el runtime duplica una responsabilidad que se deja
a Git y añade estructura que no se necesita para este encargo.

## Justificación

La elección procede del plan explícitamente aceptado por el usuario. Permite localizar
qué se conserva, ejecutar pruebas aisladas y continuarlas sin navegar el archivo técnico.
La implementación y límites se describen en [arquitectura](../architecture.md);
las comprobaciones, en la [entrega](../deliveries/2026-10-18-experiment-state.md).

## Consecuencias

Se retira el protocolo de publicación con revisiones esperadas, puntero vigente y
referencias validadas de `CaseStore`. El bloqueo protege runs de un mismo experimento,
pero no ofrece transacciones multiarchivo ni aislamiento de editores externos.
Git manual no garantiza una revisión por run; los snapshots no conservan cada edición
intermedia. Material preservado no equivale a conocimiento consolidado.
Los experimentos históricos permanecen sin migrar. Reconsiderar estas elecciones si
una campaña muestra pérdida material de continuidad, historia o procedencia; no se
ha establecido todavía aceptación semántica con proveedores reales para este mecanismo.
