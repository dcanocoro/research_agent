# E001 — Expediente y continuación de NVIDIA

Estado del protocolo: fijado antes de ejecutar. Fecha: 2026-10-17.
El estado y los resultados de ejecución se registrarán en `findings.md`, después de ejecutar.

## Pregunta e hipótesis

¿Puede A construir conocimiento útil en un expediente Markdown versionado y recuperar
sus fundamentos en un proceso nuevo? La hipótesis exploratoria es que identidad,
historia y referencias recuperables permiten continuar sin reconstruir el chat.
No hay condición de control ni demostración de superioridad respecto de vanilla.

El candidato es el [modo cases](../../architecture.md#modo-experimental-de-expedientes).
Procede del plan aceptado por el usuario y de las preguntas de identidad, revisión y
recuperación de la [arqueología](../../finmate-concept-model/modelo-conocimiento-actual.md).
No supone aceptar este modelo como arquitectura final de FinMate.

## Entradas, secuencia y controles

Dos procesos CLI separados, mismo workspace, almacén y archivo, inicialmente nuevos:

1. Mensaje exacto: `Investiga NVIDIA`.
2. Mensaje exacto: `Continúa la investigación de NVIDIA a partir de lo que conservaste. Explica qué evaluación recuperas, qué sigue pendiente y decide cómo continuar.`

Modo `cases`, prompts general, financiero y de expediente incluidos, sin instrucciones
adicionales. Modelo y configuración del perfil `lab` derivados del planificador vigente.
Límites por intervención: 18 llamadas lógicas, 30 herramientas, 300 segundos,
45 segundos de ventana de cierre y 256 KiB de contexto serializado. No ampliarlos.

Findata se consulta en transacciones de solo lectura. Tavily y el modelo son reales;
la web y PostgreSQL no están congelados. Los resultados exactos se conservarán como
artefactos, con las fechas y metadatos disponibles. No hay simulación retrospectiva.
Se comprobará configuración y una lectura PostgreSQL antes del primer proceso;
un bloqueo se registrará sin ingestas, migraciones o reparación del producto.

No reintentar una intervención para mejorar su resultado. Los reintentos de transporte
propios del cliente compartido no equivalen a nuevas decisiones del agente. Una
ejecución posterior, si se autoriza, será un intento adicional identificado.
Si no se guarda expediente en el primer proceso, conservar esa ausencia y ejecutar
la continuación sin introducir resúmenes, IDs o material manual adicional.

## Captura y reproducibilidad

Conservar bajo `artifacts/E001-nvidia-casefile/<intento>/` workspace, cases, runs,
salidas CLI, preflight y manifiesto de entorno. Antes de ejecutar, registrar SHA-256
del protocolo, archivos locales de código/prompts, diff contra HEAD, revisión Git,
dependencias instaladas y huellas de archivos del wheel instalado. Si no se localiza
el wheel original, declarar su hash desconocido: no sustituirlo por la versión.
Los manifiestos por run capturan textos efectivos, schemas, límites y configuración.
Los snapshots `state_before.json`/`state_after.json` conservan punteros y restos no
publicados; eventos `lab.case.*` identifican expedientes consultados y modificados.

La CLI y la captura guardan respuesta, transcript, errores y cierres. Conservar todo
intento parcial. Los artefactos son locales ignorados y no evidencia portable por sí
solos. Publicar solo un resumen sin credenciales ni payloads privados. La revisión
semántica la realiza el mismo agente desarrollador; no es evaluación independiente.

## Guía de revisión fijada antes de ejecutar

Usar `observado`, `parcial`, `fallo` o `N/O`, con referencia a la captura; evitar un
score agregado. `N/O` indica ausencia de evidencia para evaluar esa dimensión.

| Dimensión | Pregunta de revisión |
|---|---|
| Alcance y materialidad | ¿Concreta la investigación y explica mecanismos económicos relevantes? |
| Fundamento | ¿Distingue observación, interpretación y supuesto, con material recuperable? |
| Fidelidad numérica | ¿Respeta periodo, moneda, unidades y fórmula; permite comprobar cifras utilizadas? |
| Expediente | ¿Conserva evaluación, fundamentos y límites suficientes para continuar? |
| Continuidad | ¿Lee lo conservado sin historial anterior y recupera correctamente pendientes y evaluación? |
| Revisión | ¿Explica cambios o mantenimiento del juicio según evidencia, sin borrar incertidumbres? |
| Operación y coste | ¿Entrega, guarda cuando procede y explica límites; cuánto consume? |

La existencia y hash de una referencia no validan la inferencia. Una revisión guardada
no prueba calidad; un `completed` puede cerrar por presupuesto. No exigir compra,
venta, DCF ni cambio de opinión. La ausencia de evidencia nueva puede impedir evaluar
corrección ante contradicción, incluso si la continuidad técnica funciona.

## Criterio para el siguiente experimento

Recomendar nueva estructura solo ante una pérdida concreta: cuestiones olvidadas,
dependencias no revisadas, mezcla de preguntas o referencias irrecuperables. Si el
fallo es presupuesto, proveedor o selección de contexto, diagnosticar esa capa antes
de atribuirlo al modelo conceptual. Cualquier recomendación será una hipótesis que
requiere contraste posterior, no un ADR aceptado por completar estas dos intervenciones.
