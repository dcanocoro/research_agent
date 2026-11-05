# Nota de continuidad opcional — 2026-11-04

## Cambio

Base Git: `6061cd4`, con cambios previos sin commit, incluidos Progress y sus pruebas.

Implementación del plan autorizado de renovación sencilla. `--context-note` requiere
continuo y habilita una nota aislada de A, sin herramientas, tras el checkpoint y
las integraciones pendientes. El tamaño dispara la renovación en el umbral actual;
un compromiso sucesor de Progress la permite desde el 60 % de ese umbral. El evento
no depende de textos ni de IDs globalmente únicos y se consume una sola vez.

La semilla se relee y se reconstruye con intercambios completos recientes. La nota
es operativa, provisional y reemplazable, no un documento de conocimiento. Fallos
recuperables, respuestas inválidas y falta de recursos permiten reconstruir sin
ella; cancelaciones y fallos terminales no se ocultan. Hay cinco llamadas y tiempo
de finalización protegidos; no consume reservas de B ni llamadas del compromiso.
No se cambia la identidad histórica E2 ni se migra estado. Sin la opción permanece
el comportamiento anterior. Se preservan los cambios previos del checkout.

## Verificación

Pruebas con clientes simulados: límites de triggers, consumo único del evento,
referencias actualizadas, notas válidas/inválidas/excesivas, falta de recursos,
fallos recuperables/terminales, cancelación, reconstrucción sin espacio para nota,
renovaciones sucesivas, captura y contabilidad de Progress. Regresiones locales
de continuo, E2 y B; análisis de tipos y comprobación documental.

Resultado de la tanda dirigida: 129 tests aprobados, incluidos 25 específicos de
la nota y regresiones de continuo, Progress, E2, B, arquitectura y CLI por carpetas.
`mypy` no encuentra errores en los 70 archivos de fuentes comprobados. Enlaces
locales y anclas de las cuatro referencias documentales afectadas comprobados;
`git diff --check` sin errores. Las dos referencias externas al checkout hermano
de FinMate no forman parte de la comprobación de enlaces internos.

La suite completa tiene un impedimento previo de colección:
`tests/campaigns/test_price_review.py` intenta cargar `scripts/review_historical_prices.py`,
ausente en el checkout. Se comprueban por separado los tests disponibles, sin
restaurar archivos ajenos a esta entrega.

La tanda ampliada, excluyendo ese archivo, terminó con 452 aprobados y dos fallos
en versiones iniciales de fixtures nuevos cargadas antes de su corrección: faltaba
soporte persistido para declarar suficiencia y el resultado grande se paginaba antes
de alcanzar el umbral pretendido. Ambos casos pasan con sus fixtures corregidos en
la tanda posterior de 129 tests. No se repitió íntegra la tanda ampliada tras esos
ajustes de pruebas; el código de ejecución no cambió durante esa corrección.

## Límites

La implementación inicial se verificó sin campaña ni servicios remotos. Los
checks deterministas no demuestran retención semántica ni mejora financiera. La
[arquitectura](../architecture.md#nota-de-continuidad-opcional) y la
[operación](../development.md#renovación-con-nota-de-continuidad) describen el contrato.

## Seguimiento real autorizado

El usuario autorizó después una prueba abierta de 100 llamadas. Sus
[hallazgos](../experiments/context-note-general-100/findings.md) conservan el fallo
de la cuarta nota por `LLMTruncated`, la corrección local de su fallback y la
continuación de 68 llamadas, sin exceder las 100 conjuntas. Se mantuvo el límite
de 1024 tokens y se comprobó el caso real con un nuevo test; 32 tests de notas y
arquitectura aprobados y mypy sin errores en 70 archivos. La continuación soportó
seis truncamientos de nota y terminó por `call_limit`. No hay commit ni publicación.

## Ajuste posterior solicitado: margen y uso de la nota

Tras revisar la campaña, el usuario pidió ampliar la salida a 5000 tokens y mejorar
el prompt según lo observado. Se pasa de 1024 a 5000 tokens y de 8192 a 40000 bytes
UTF-8 aceptados, evitando conservar un límite de texto incongruente con el margen
nuevo. El contador reserva la salida de 5000 tokens; no se alteran umbrales ni
presupuestos de llamadas. El fallback por truncamiento sigue disponible.

El prompt conserva cuatro apartados, pero concreta lo guardado frente a lo pendiente,
la procedencia de cifras no integradas, intentos fallidos y qué justificaría otro
intento. Pide rutas exactas sin inventar hashes y separa workspace de auditoría.
La instrucción del investigador con `--context-note` orienta a usar la nota para
recuperar selectivamente, persistir lo pendiente y replantear métodos improductivos.
No cambia el mandato financiero ni las instrucciones del modo sin notas. No se
editan entradas ni capturas de la campaña anterior ni se lanza una nueva ejecución.

Verificación de este ajuste: 86 tests locales de notas, continuo, Progress y
arquitectura aprobados, incluida la aceptación de una nota mayor de 8 KiB y la
salida configurada de 5000 tokens. Mypy sin errores en 70 archivos; enlaces locales
y `git diff --check` comprobados. No demuestra todavía una menor tasa de truncado
ni menos repeticiones en ejecución real.
