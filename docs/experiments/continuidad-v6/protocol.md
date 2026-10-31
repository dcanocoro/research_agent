# V6: foco, conocimiento recuperable y evaluación longitudinal

Fecha: 2026-10-29. Estado: implementación local verificada; campaña real ejecutada
con [hallazgos](findings.md). Encargo del usuario: implementar conjuntamente la primera propuesta V6,
excluyendo la propuesta posterior de supervisores LLM.

## Base, observación e hipótesis

Los [hallazgos V5](../herramientas-estado-v5/findings.md) documentan 19 escrituras
concentradas en consolidación, H1 de AAPL vacío, pendientes parcialmente obsoletos de
ADP, acumulación de intenciones y una cifra incorrecta en el texto de AON. Son fallos
observados; no prueban que una única causa explique todos.

Las instrucciones V5 ya pedían persistencia ordinaria, depuración y consolidación
ligera. La hipótesis V6 es que agenda explícita, mejores recibos de escritura y
protecciones de recuperabilidad ayuden a cumplir esa disciplina. Los nuevos prompts
por sí solos no constituyen evidencia de mejora.

## Intervención conjunta

- Un único investigador y el mismo bucle ReAct. Sin supervisores LLM, planificador,
  propagación económica ni nuevas llamadas de revisión.
- Agenda Markdown con prioridades generales, investigación activa, aplazadas y cambios.
  La parte activa conserva pregunta, materialidad, último avance, incertidumbre,
  criterio de cierre, referencias y acción tentativa; el modelo puede cambiar el foco.
- Contexto reconstruido con agenda completa y localizador de su sección activa,
  sin otra memoria duplicada ni carga automática de expedientes. Índice ausente explícito.
- Escrituras de empresa validadas antes de publicar, también por herramientas generales
  de la composición V5: IDs únicos y conservados; rechazo al vaciar cuerpos previamente
  poblados. Recibo con secciones recuperables y advertencias literales acotadas.
- Escritura incremental y revisión de pendientes por el investigador. Consolidación
  orientada a lo aún no guardado. Revisión cada diez llamadas de investigación, sin
  herramientas; los cambios de archivos se realizan en la continuación ordinaria.
- Capturas intermedias fuera del estado editable y evaluación offline sin feedback.
  Números contrastables mediante afirmaciones explícitas y operandos en materiales.

No se convierte una sección en entidad financiera, ni se certifica causalidad,
coherencia semántica, unidades en prosa o calidad de inversión mediante validadores.
Una sección nueva vacía genera advertencia; no se exige completar una plantilla.
Referencias futuras ausentes no bloquean una escritura legítima.

## Configuración y reproducción futura

La definición V6 (`campaigns/contexto-continuo-v6/scenario.json`; referencia local histórica) conserva
universo, fecha fija 2023-01-01, dataset SHA-256
`4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`, mandato,
petición, modelo `gpt-6-luna`, razonamiento medium, salida máxima 16000 y límites V5.
Se mantienen 100 llamadas ordinarias, 150 herramientas, 1200 segundos y umbrales
262144/524288 bytes. Las revisiones adicionales conservan su contabilización.
La rúbrica (`campaigns/contexto-continuo-v6/rubrica.md`; referencia local histórica) está fuera de las
instrucciones del agente.

Usar un destino nuevo, perfil de herramientas `v5` y prompts V6 actuales. `v5` sigue
nombrando la familia de herramientas; los contratos efectivos son `state-tools-v6.1`.
No existe un nuevo selector de perfil V6. Nuevos experimentos reciben la agenda y
prompts actuales; continuaciones conservan sus copias. Cambiar instrucciones requiere
adopción explícita, no una migración silenciosa. Runtime y contratos cambiados quedan
capturados; las campañas preparadas conservan sus bloqueos de deriva.

La implementación no autorizaba una campaña real. Posteriormente, el 2026-10-29, el
usuario autorizó expresamente ejecutar una campaña igual a la repetición V5 con V6.
Destino nuevo: `artifacts/contexto-continuo-v6/piloto-100-llamadas`. El lanzador local
`artifacts/contexto-continuo-v6/ejecutar.py` comprueba además perfil completo, código
compartido, configuración Python, límites, dataset, mandato y petición frente a V5;
recalcula el presupuesto inicial con Python habilitado. No modifica el runtime
durante la campaña. Preparación y ejecución habituales en la
[guía de campañas](../../campaigns.md); sin web ni BD remota. El dataset no se copia al Git.

## Evaluación offline

`python -m research_campaigns progress RUTA_DEL_RUN` genera `progreso-v6.json` nuevo
dentro del run. No sobrescribe un informe existente; `--output` permite otro nombre
JSON en ese mismo directorio. No se escribe en estado ni se devuelve feedback a A.

El informe conserva cambios entre snapshots, foco, IDs vacíos/duplicados, escrituras
por fase y lecturas exitosas con referencias. Una lectura exitosa no prueba comprensión;
un documento modificado no demuestra progreso. Las cuatro dimensiones semánticas
(progreso, calidad, utilidad y recuperación) quedan `not_assessed` hasta revisión con
la rúbrica. No se infiere cierre real de preguntas por marcas de texto.

`--checks ARCHIVO.json` aplica el contrato ilustrado en
[numerical-checks-example.json](numerical-checks-example.json): cita exacta y valor
escrito, operación, operandos por JSON pointer en materiales capturados, unidades,
escala y tolerancia. Usa Decimal sobre `estado-final.json`, no datos vivos. Devuelve
matches, mismatch o unobservable. No extrae automáticamente todas las afirmaciones:
selección de fuentes, unidades declaradas, escala y materialidad siguen requiriendo
revisión humana. El ejemplo es sintético, no un resultado de la campaña.

Las capturas guardan bytes UTF-8 decodificados sin normalizar CRLF y SHA-256 por
archivo de conocimiento. Materiales originales permanecen en la captura nativa.
Se guardan al inicio, revisión, renovación y cierre, con fase y contadores; no cada
edición. Los errores de captura se registran y marcan incompletitud. No constituyen
un almacén universal de versiones ni una transacción frente a editores externos.

## Aceptación local y alcance de conclusiones

Pruebas de regresión: traslado H1/E3 rechazado sin escritura parcial, protección por
aliases, reparación de duplicados externos, vista recuperable con Unicode/CRLF y
presupuesto, revisión explícita de pendiente ADP, discrepancia 8,99/7,99 de AON,
agenda heredada intacta, continuidad y snapshots sin llamadas adicionales.

Comparar V5 congelada con V6 como paquete, con mismos datos/modelo/presupuestos y
estados nuevos; idealmente repetir. Implementación conjunta no permite aislar efectos
de cada mecanismo. Separar mecánica, integración, aceptación semántica e inversión.
La comparación con las capturas V5 ya conservadas es descriptiva. Repetir un control
V5 exige disponer de su runtime e instrucciones originales y comprobar fingerprints;
ejecutar `campaigns/contexto-continuo-v5` con el runtime V6 no reproduce V5.
La [entrega](../../deliveries/2026-10-29-continuity-v6.md) registra las comprobaciones.
