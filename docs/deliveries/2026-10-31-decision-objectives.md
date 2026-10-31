# Dirección hacia una evaluación útil para decidir

Fecha: 2026-10-31. Encargo aceptado: orientar el trabajo a una evaluación, hacer
visibles impedimentos materiales, comprobar adaptaciones y evitar agendas publicadas
que no puedan recuperarse. Incluye campaña real posterior con la pregunta literal
del usuario; [protocolo y condiciones](../experiments/evaluacion-msft-v1/protocol.md).

## Cambios

- `Objective.assessment_path` opcional, validado y congelado; definiciones anteriores
  conservan hash. Vista de evaluación versionada hasta 4 KiB, inicial, tras cambio
  y tras renovación; sin creación automática ni edición por el controlador.
- Dirección explícita en cada llamada con objetivo y guía financiera hacia juicio
  provisional, fundamentos, escenarios, precio, riesgos y bloqueos concretos.
- Evaluador con `decision_review`: utilidad para decidir, impedimentos por tipo e
  impacto, IDs resueltos y revisión de adaptación. Para objetivos con documento activo
  se exige ese contrato; capturas V8 previas siguen legibles. Distancia como auxiliar.
- Agenda máxima 8 KiB UTF-8, rechazo previo en operaciones individuales y conjuntas;
  semilla con margen de 16 KiB para objetivos con documento activo. Sin migración de
  estado anterior ni cambios al wheel compartido.
- Lectores de campaña muestran utilidad según el evaluador, diferenciada de aceptación
  financiera independiente. Una evaluación positiva no determina éxito por sí sola.

## Verificación local

Las pruebas específicas de dirección decisoria y V8 finalizaron con 45 aprobadas.
Tipado correcto en 42 archivos y dependencias sin incompatibilidades. Incluyen
rechazo conjunto sin publicar, UTF-8, referencias seguras, juicio actualizado tras
escritura y renovación, contrato/feedback y regresión de objetivos anteriores.

La primera pasada detectó serialización de `FrozenDict` al comparar versiones de
la vista; se corrigió antes de llamar a proveedores. La regresión general también
detectó sensibilidad a tamaño en fixtures continuos al ampliar la guía común de
deliberación; esa guía se conservó y la dirección nueva se inyecta solo con objetivo.
Regresión específica posterior de dirección/V8/estado/V7: 101 aprobadas (22,29 s).
La pasada general dejó 372 aprobadas y cinco fallos de fixtures continuos sensibles
al texto añadido a la guía común (307,25 s). Tras conservar esa guía y ubicar la
dirección solo en objetivos, los cinco casos vuelven a pasar (7,21 s). No quedan
fallos conocidos; no se presenta la pasada original como íntegramente verde.
Mypy final correcto en 42 archivos; `pip check` y `git diff --check` correctos.
El comprobador documental conserva 270 incidencias históricas (82 Markdown,
790 enlaces locales); las nuevas referencias resuelven a archivos existentes.

## Campaña y correcciones posteriores

Los [hallazgos](../experiments/evaluacion-msft-v1/findings.md) conservan 100 llamadas
ordinarias, 108 totales, evaluación provisional y cierre por presupuesto sin fallo
operativo. La pregunta literal del usuario se verificó en definición y captura.
Tras cerrar se corrigió la pérdida de revisiones parciales como antecedente: se
separan última revisión estructuralmente válida y última distancia completa, también
ante fallos y continuaciones. La evaluación activa puede ocupar hasta 16 KiB en el
paquete evaluador, dentro de 64 KiB totales, sin ampliar su vista de contexto de 4 KiB.
No se repitió el proveedor ni se sustituyó la evidencia original por un resultado hipotético.

Regresión posterior continuo/V7/V8/estado/dirección: **150 aprobadas**, 32,95 s;
mypy correcto en 42 archivos. Fuentes de arranque y corregidas conservadas por separado.

## Límites

No se atribuye utilidad semántica a estos checks. La campaña debe observar si existe
una evaluación decisoria y qué ajustes resolvieron impedimentos, con fuentes y cifras
escogidas verificadas aparte. No se hace commit ni se elige arquitectura de FinMate.
