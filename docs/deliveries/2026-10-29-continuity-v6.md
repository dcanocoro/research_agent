# Continuidad V6

Fecha: 2026-10-29. Base: árbol local con V5 y corrección de consolidación previas,
conservadas sin commit. Encargo: implementar conjuntamente la primera propuesta V6;
sin los supervisores LLM de la propuesta posterior. El
[protocolo](../experiments/continuidad-v6/protocol.md) conserva hipótesis y límites.

## Cambio

- Agenda inicial compacta con foco activo, aplazadas y cambios. Copias anteriores
  intactas. Prompts concretos de persistencia ordinaria, revisión y fidelidad numérica.
- Contexto reconstruido con localizador del foco y ausencia de índice explícita,
  sin nueva memoria paralela ni carga automática de expedientes.
- Validación de expedientes antes de publicar, por herramientas específicas y generales
  en composición V5: IDs únicos/conservados y rechazo al vaciar cuerpos antes poblados.
  Recibos con secciones recuperables y advertencias literales, dentro del presupuesto.
- Revisión existente enfocada en cambios de comprensión, sin herramientas ni llamadas
  nuevas. Consolidación orientada a pendientes de persistencia y continuidad suficiente.
- Checkpoints de conocimiento fuera del estado editable, con contenido, hashes,
  fase, contadores y errores de captura, al iniciar, revisar, renovar y terminar.
- Comando offline `research_campaigns progress`: comparación de estados, escrituras
  por fase, lecturas y comprobaciones numéricas explícitas sobre materiales capturados.
  Las dimensiones semánticas quedan pendientes de revisión humana, sin puntuación.
- Definición V6 con mismo dataset, mandato, petición, modelo y límites V5; preparada,
  sin campaña ejecutada. Se mantiene el selector `v5` para la familia de herramientas;
  los contratos efectivos pasan a `state-tools-v6.1` y se capturan por run.

## Verificación local

- Suite completa: **315 pruebas aprobadas** en 279,16 s, sin proveedores ni bases remotas.
- 16 casos V6: protección por todas las vías de escritura, jerarquía ATX, duplicados,
  cuerpo vacío, pendientes, referencias futuras, Unicode/presupuesto, agenda heredada,
  capturas, errores, contenido/hash, observación offline y comprobaciones numéricas.
- Integración H1/V1: tras renovación se recuperan el foco, la hipótesis revisada y el
  pendiente conservado. Cliente controlado; no demuestra iniciativa semántica autónoma.
- Mypy: aprobado sobre 38 archivos de agente/campañas. `pip check`: sin incompatibilidades.
- Validación offline de la definición V6: aprobada. Comparación con V5: mismo escenario
  salvo ID de campaña, mandato y petición idénticos byte a byte; rúbrica V6 propia.
- `git diff --check`: aprobado.
- Comprobador documental: 723 enlaces locales en 63 Markdown; conserva los mismos
  270 errores previos por referencias históricas y al repositorio hermano ausentes.
  Comparación antes/después: ningún enlace roto añadido; no se declara aprobado el
  comprobador global. Logs locales en `artifacts/v6-local-validation/`, ignorados.

La primera pasada completa detectó cuatro fallos de fixtures: dos umbrales de contexto
demasiado ajustados a los prompts anteriores y dos lecturas de agenda sin UTF-8 en el
proveedor simulado de Windows. Se ajustó la ventana sintética, sin cambiar los límites
reales, y la codificación del fixture; la repetición completa pasó. Las expectativas
anteriores de agenda vacía y corrupción mediante alias se actualizaron a los contratos
V6, manteniendo la prueba de corrupción externa y recuperación por líneas.

## Límites

Los checks estructurales no detectan todos los traslados de significado, pendientes
obsoletos o errores numéricos en prosa. La comparación ADP es una transición programada,
no una corrección autónoma observada. El comprobador numérico requiere seleccionar
cita, operandos, unidades, escala y tolerancia: no es un auditor financiero universal.
Los informes no dirigen a A ni confirman progreso por contar documentos o escrituras.

Capturas intermedias no equivalen a versionado de cada edición ni aislamiento frente
a editores externos. El coste de capturar estados existe aunque no añada llamadas al
modelo. Los prompts nuevos no modifican copias de instrucciones existentes; tampoco
se migran campañas congeladas. Se conservan los artefactos V5 originales.

La utilidad semántica de V6 requiere campaña y revisión autorizadas posteriormente.
La intervención conjunta permite evaluar el paquete, no atribuir causalidad a cada
pieza. No cambia FinMate, datos financieros, wheel compartido, motor Python ni ReAct.
