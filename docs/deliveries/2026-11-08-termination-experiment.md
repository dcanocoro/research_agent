# Experimento aislado de terminación del ReAct

Fecha: 2026-11-08. Base Research Agent: `cf0cf0e779c1bd7b06c1bb8ef213993f39873a54`.
Encargo: dejar montado el contraste acordado, sin ejecutar la campaña ni contaminar A.

## Cambio

[Protocolo](../experiments/terminacion-react/protocol.md) y
[definición/lanzamiento](../../campaigns/terminacion/README.md):12 casos sintéticos,
V0 acotado actual, V1 instrucciones de suficiencia, V2 checkpoint tras6 y12.
Presupuesto común de18 llamadas de A, reservas actuales y hasta2 revisiones adicionales.
Sin continuo, Progress, nota, B, mandato ni datos remotos. Archivos y aritmética locales.

`research_campaigns/termination` compone y ejecuta el contraste sobre el motor actual.
No se modifica ningún archivo de `src/research_agent`, su CLI ni prompts estándar.
La preparación congela entradas/hashes, el lanzamiento fija perfil, cada trabajo
tiene estado nuevo y captura nativa. Las respuestas se exportan sin condición para
revisión ciega. No hay juez automático ni resultados semánticos. Los fallos se conservan
y no se reintentan; `run` posterior solo ejecuta trabajos aún no intentados.

Hay un adaptador de captura limitado al experimento. El wheel disponible actualmente
expone `local_trace_capture`, mientras el tracer de A espera `configure_local_archive`
y `_archive_directory`. La primera prueba falló también con la política nativa por
esta incompatibilidad. No se modificó A ni se parcheó el wheel: la política experimental
prepara el mismo contexto acotado con captura local compatible, común a V0/V1/V2.
Se verificaron equivalencia de comportamiento, archivo gzip y eventos sin proveedor.
Esto no certifica que el resto de la CLI de A funcione con este nuevo entorno.

## Entorno recuperado

La `.venv` local estaba vacía (solo pip), sin pytest ni wheel compartido. Se construyó
e instaló `findata==0.1.0` desde el checkout hermano, base
`44d67278ff33030e539cf79fe6686445d47aa08f`, con cambios ajenos presentes que no se editaron.
El SHA-256 del wheel efectivamente instalado es
`185eb2324e1cb936bc68311e2dfbbd22c4a199e1f4e6903d2ecbe09b6a4a510e`.
No se puede reproducir ese wheel solo con el commit si no se conserva su archivo;
los fingerprints de paquetes congelados identifican las bibliotecas realmente usadas.

Se instaló el laboratorio editable sin reinstalar sus dependencias y se resolvieron
las dependencias del wheel y pytest. No se aplicó `constraints.txt` histórico: este
entorno es nuevo, no una reproducción del corte anterior. Python3.12.10, pytest9.2.0,
OpenAI3.46.0. Wheel y lista efectiva de versiones se conservan localmente en
`artifacts/termination-setup/`; no son evidencia portable ni se versionan.
No se mostró ni modificó `.env`, ni se llamaron proveedores o bases remotas.

## Verificación

Pruebas del experimento con clientes controlados y regresiones estáticas del motor
único/fronteras:17 pasadas (15 específicas y2 de arquitectura;6 no seleccionadas).
Incluyen cierre natural, checkpoints, fallos, cancelación, reservas, recuento total,
protección del corpus, separación de rúbrica, preparación congelada y captura local
real de un payload sintético. La comparación con la política nativa usa en test el
mismo adaptador de captura; no enmascara una integración real con proveedor.

Validación de definición, preparación de planes, `pip check`, compilación Python,
enlaces locales afectados y `git diff --check`. Sin campaña LLM, Findata, Tavily,
aceptación semántica, commit o push. Las ejecuciones preparadas siguen pendientes.

Planes finales locales: `artifacts/terminacion-react-piloto` (36 trabajos posibles;
el piloto propuesto selecciona S2/O4, seis) y `artifacts/terminacion-react-tanda`
(108 trabajos). La preparación no crea `jobs/` ni consume llamadas. Las primeras
preparaciones de comprobación con nombre `terminacion-react-v1-*` quedaron superadas
por cambios posteriores de fingerprint, sin trabajos lanzados; no deben ejecutarse.

Siguiente paso: ejecutar solo el piloto con los comandos de la definición, revisar
captura y exposición al checkpoint antes de lanzar la tanda. La evaluación independiente
de respuestas y trayectorias sigue siendo trabajo posterior. La retirada del experimento
está descrita en el protocolo y no requiere revertir código de A.
