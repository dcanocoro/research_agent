# Benchmark piloto v1

Estado: implementado y verificado localmente con servicios simulados; campaña con
proveedores reales no ejecutada. Encargo: cuatro casos, herramientas reales y archivo
de evidencia, sin Excel, jueces LLM ni puntuación automática. Fecha: 2026-10-20.

Este protocolo es histórico: `benchmarks/pilot-v1/` fue retirado del árbol.
Sus archivos pueden consultarse sin restaurarlos con
`git show f6b4d0d8ff26cf0b5633abadddd6561156d05f29^:benchmarks/pilot-v1/suite.yaml`
y la misma revisión para cada caso/rúbrica. El controlador sigue disponible; los
catálogos actuales están en el [registro](../README.md).

## Pregunta y alcance

¿Qué acciones observables realiza A ante contradicción, continuidad, ruido y fuentes
fallidas cuando el usuario no le indica un procedimiento? Este piloto caracteriza
comportamientos; no compara condiciones ni demuestra mejora causal o rentabilidad.
La [metodología](../../experiments.md) distingue operación y aceptación semántica.

| Caso | Definición | Sesiones | Referencia del revisor |
|---|---|---|---|
| B1 | Fuentes contradictorias (`benchmarks/pilot-v1/B1/case.yaml`, histórico) | 1 | Rúbrica (`benchmarks/pilot-v1/B1/rubric.md`, histórico) |
| E2 | Continuidad (`benchmarks/pilot-v1/E2/case.yaml`, histórico) | 4 | Rúbrica (`benchmarks/pilot-v1/E2/rubric.md`, histórico) |
| F3 | Información irrelevante (`benchmarks/pilot-v1/F3/case.yaml`, histórico) | 2 | Rúbrica (`benchmarks/pilot-v1/F3/rubric.md`, histórico) |
| G2 | Fuentes fallidas (`benchmarks/pilot-v1/G2/case.yaml`, histórico) | 1 | Rúbrica (`benchmarks/pilot-v1/G2/rubric.md`, histórico) |

La suite (`benchmarks/pilot-v1/suite.yaml`, histórico) fija este orden. Las dificultades
dependen de incertidumbre, compatibilidad de datos y recuperación, no del número de
mensajes. Los documentos incluyen procedencia, fecha y carácter sintético/hipotético;
no convertirlos en datos actuales de una empresa real.

## Definición y ejecución

`suite.yaml` declara `schema_version: benchmark-v1`, `id` y una lista `cases` de rutas
relativas a YAML. Cada caso declara `id`, `title`, `context`, `competencies`,
`difficulty`, `rubric` y `sessions`. Cada sesión contiene `id`, `message` y `publish`:
un mapa de destinos `entradas/archivo.md` a fuentes relativas al directorio del caso.
Un mapa vacío no publica nada. No hay condiciones dinámicas, reintentos de sesión,
agenda temporal, clonación ni paralelismo. Los YAML rechazan campos o claves ambiguos.

El controlador valida todo el catálogo, congela únicamente los archivos referenciados
y prepara un experimento por caso con los prompts predeterminados. El índice inicial
contiene `context` y los caminos de las primeras entradas, sin rúbrica ni conclusiones.
Después solo publica archivos nuevos; no modifica el índice o la memoria del agente.
Cada sesión invoca la CLI existente en un proceso nuevo con `--continue`: conserva
archivos e instrucciones, no el chat. No se utilizan snapshots anteriores como
contexto suplente. Rúbricas y entradas futuras están fuera del alcance de las
herramientas de archivos. Las entradas publicadas siguen siendo editables: se conserva
el original congelado y se informa de cambios de hash después de cada sesión.

Las herramientas reales permanecen disponibles. El modelo, web y PostgreSQL no están
congelados; anotar fechas, fuentes y ausencias observadas. G2 no garantiza un fallo:
si el agente evita el enlace inaccesible, recuperación ante fallos queda no observada.
El campo mecánico solo detecta errores de `read_document`; la rúbrica requiere revisar
argumentos, contenido y alternativas. No hay intervención oculta sobre el transporte.

Se usa una tentativa, límites predeterminados y ejecución secuencial. Un fallo o captura
incompleta bloquea las siguientes sesiones del caso, pero no otros casos. Ctrl+C detiene
la campaña y conserva lo disponible. Las nuevas invocaciones crean campañas nuevas;
no existe resume. La [operación](../../development.md#benchmark-piloto) documenta comandos.

## Evidencia y aceptación

El manifiesto conserva revisión/cambios Git, intérprete, hashes del código local y
dependencias identificables y de las definiciones. Los prompts efectivos quedan en
el experimento y en los manifiestos nativos de cada run, junto al perfil efectivo.
No se vuelcan variables de entorno, `.env` ni credenciales.

La captura nativa se consolida al cerrar la campaña. `ejecucion.json` conserva petición,
configuración, resultado y hashes; `trayectoria.jsonl.gz` reúne eventos, payloads del
modelo y herramientas. La respuesta y los dos snapshots siguen siendo archivos legibles;
los materiales se conservan una vez y se referencian por hash. El resultado original de
una herramienta y el entregado al modelo permanecen distinguibles y reconstruibles.
Se retienen las escrituras intermedias en los argumentos de herramientas. No se necesita
una copia adicional de la conversación para evaluar qué recibió cada llamada al modelo.

`resumen.json` conserva comandos, tiempos, estados y errores de las sesiones. Los
diagnósticos no vacíos o de fallos permanecen en `sesiones/`; stdout redundante y stderr
vacío se omiten. Capturas incompletas permanecen nativas. `LEEME.md` orienta a Codex/humanos
para evaluar objetivo, autonomía, evidencia, memoria/adaptación y recursos, siempre con
referencias y N/O ante ausencia de observación. No es una evaluación automática.

`pasos.jsonl` es una vista determinista regenerable de llamadas al modelo, ejecuciones
de herramientas y respuestas finales. La trayectoria conserva además los errores y fases.
Los fragmentos se acotan a 240 caracteres, sin interpretación LLM. Los identificadores
solo se enlazan cuando existen; no representa razonamiento privado. Su orden utiliza
timestamps y referencias como desempate, no reconstruye causalidad ausente.
`extraccion.json` informa problemas de captura detectados al regenerar la vista,
conservando las evidencias originales de cada sesión. El extractor lee también las
campañas nativas anteriores. Su exportación compacta siempre crea otra carpeta; no
reescribe campañas históricas ni modifica el ciclo del agente.

`resumen.json` informa recursos observables, sesiones realizadas y errores, sin nota
financiera. `completed` con captura completa acredita entrega operativa, no corrección.
La revisión humana permanece pendiente; cada juicio deberá apuntar a su evidencia y
usar N/O cuando falte. No premiar más herramientas, escrituras o cambios de opinión.

Aceptación de ingeniería: validación offline, aislamiento y publicación temporal,
reinicio real entre sesiones, continuidad de archivos, errores conservados y extracción
regenerable comprobados con servicios simulados. La campaña real requiere ejecutar
explícitamente `run`; no se inicia en tests, instalación o validación.

`artifacts/` es local e ignorado. Su contenido no es evidencia portable; antes de
compartirlo revisar datos privados y disponibilidad de materiales. No crear hallazgos
de calidad financiera hasta disponer de ejecuciones y revisión humana.
