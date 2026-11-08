# Piloto y lanzamiento paralelo — 2026-11-08

Actualización posterior: [resultados de la tanda completa](findings.md).

El usuario autorizó lanzar las campañas paralelizando V0, V1 y V2. Se ejecutó primero
el piloto de S2/O4 y después se lanzó la tanda completa. Este registro acredita el
piloto y el lanzamiento; no acredita la finalización ni la evaluación de la tanda.

## Condiciones efectivas

Perfil común: OpenAI `gpt-6-luna`, razonamiento `medium`, salida principal de hasta
16000 tokens; timeout del perfil30 segundos, presupuesto interno45 segundos y hasta3
intentos del transporte. Se conservan los límites y las instrucciones del protocolo.
El checkpoint conserva el mismo modelo y limita la salida a1500 tokens.

Tres procesos, uno por condición, cada uno secuencial dentro de su propia carpeta.
El bloqueo del runner impide varios escritores sobre una campaña: se derivaron tres
planes independientes de la misma preparación congelada, filtrando los trabajos por
condición. Cada `campaign.json` registra origen, condición, etapa y concurrencia.
No se modificaron fuentes, prompts ni configuración mientras se ejecutaban.

Este paralelismo sustituye la ejecución secuencial prevista originalmente, por
petición del usuario. Se mantienen entradas, memoria aislada y presupuesto por trabajo;
tiempo y fallos pueden verse afectados por contención o límites compartidos del
proveedor. No comparar latencias con una ejecución secuencial como si fueran iguales.
La selección aleatoria de casos/repeticiones se conserva dentro de cada cola;
el orden relativo de las condiciones pasa a depender de sus duraciones.

## Piloto observado

Seis ejecuciones completadas, motivos de cierre diferenciados, sin `capture_errors`.
Se verificaron perfil/código comunes y lectura de todos los archivos gzip referidos
por los eventos LLM. El número de registros del proveedor coincide con las llamadas
gestionadas en estos seis trabajos. Se comprobó exposición efectiva al checkpoint.

| Condición | S2: llamadas/cierre | O4: llamadas/cierre | Total llamadas | Suma de segundos de los dos trabajos |
|---|---|---|---:|---:|
| V0 | 5 / voluntario | 15 / voluntario | 20 | 63,34 |
| V1 | 5 / voluntario | 15 / voluntario | 20 | 55,67 |
| V2 | 5 / voluntario | 8 / checkpoint | 13 | 47,88 |

Las ocho llamadas de O4-V2 incluyen siete de A y una del evaluador. Tras la sexta
llamada, el evaluador devolvió REQUEST_FINISH en11,09 segundos. La siguiente llamada
produjo respuesta sin herramientas. S2 terminó antes del primer checkpoint en las
tres condiciones. El piloto no se incorpora a las108 observaciones de la tanda.

La lectura operativa de las respuestas confirmó entregas sobre la petición, sin
asignar puntuaciones ni hacer revisión ciega. Las tres respuestas S2 dan25 %.
En O4, V2 conserva corrección auditada, caja no recurrente y juicio provisional,
pero omite parte del detalle numérico presente en V0/V1. La revisión independiente
debe decidir si esa reducción pierde contenido necesario. Menos llamadas no demuestra
equivalencia semántica ni mejora consistente. Tokens y coste monetario no se agregaron.

## Tanda lanzada y procedencia

La tanda se lanzó después de revisar el piloto:36 trabajos por condición,108 en total,
12 casos por3 repeticiones, con los mismos hashes y perfil. Hay tres procesos independientes;
el supervisor local conserva PID, comandos, códigos de salida y horas UTC en
`full/launch.json`. El supervisor no evalúa respuestas ni envía notificaciones.

Raíz local: `artifacts/terminacion-paralelo-20261108-204413/`.
Piloto: `pilot/V0`, `pilot/V1`, `pilot/V2`, más `pilot-summary.json`.
Tanda: `full/V0`, `full/V1`, `full/V2`; cada una tiene informe y capturas nativas.
El lanzador operativo local queda en `artifacts/termination-setup/parallel_launch.py`.
No hay reintento automático ni modificación del runner de A. Los planes originales
`terminacion-react-piloto` y `terminacion-react-tanda` permanecen como origen sin ejecutar.

Las capturas y el lanzador son locales e ignorados; su ruta identifica procedencia,
no evidencia portable. Conservar la raíz completa para una auditoría posterior.
Cuando termine la tanda, registrar su estado y revisión por separado, incluyendo
fallos e interrupciones. No se ha hecho commit, push ni cambio en FinMate.
