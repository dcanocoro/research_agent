# Prueba corta con datos históricos reales

Fecha de ejecución: 2026-10-24. Estado: tres activaciones completadas con captura íntegra. Es aceptación de integración y continuidad; no una evaluación de decisiones financieras ni de alfa.

## Condición ejecutada

Universo completo de 50 empresas, cartera ficticia de 100.000 USD y máximo de diez posiciones. Fechas simuladas: 2024-06-01, 2024-07-01 y 2024-08-01; liquidación del escenario al 2024-08-31. Se usan fundamentales reales de Findata con disponibilidad real/estimada y las [series reales ajustadas revisadas](price-review.md). No se fabrican cifras ni precios.

Las participaciones son unidades normalizadas de los cierres ajustados, no acciones negociables ni sus cotizaciones históricas. No se abonaron dividendos ni se aplicaron splits otra vez. Los dos instrumentos elegidos atraviesan splits efectivos durante el intervalo, APH en junio y AVGO en julio.

Configuración efectiva: OpenAI `gpt-6-luna`, razonamiento `medium`, salida máxima 16.000 tokens. Se conservaron los límites de 18 llamadas, 30 herramientas y 300 segundos por activación. Los prompts base son los vigentes. El mensaje inicial solicita compras pequeñas y el final su cierre para comprobar infraestructura; no constituyen decisiones autónomas de inversión.

La definición y datos de entrada están en `artifacts/historical-smoke-real-v1/scenario.yaml` y `data.json`. La campaña está en `artifacts/historical-smoke-real-v1/campaign/`; `verification.json` conserva la comprobación determinista posterior. Son artefactos locales e ignorados. Para trasladarlos, conservar también `artifacts/price-review-adjusted-v3/`, que contiene las respuestas y su procedencia.

## Ejecuciones observadas

| Fecha simulada | Activación | Llamadas LLM | Herramientas | Motivo de cierre | Captura |
|---|---|---:|---:|---|---|
| 2024-06-01 | usuario | 18 | 17 | budget | íntegra |
| 2024-07-01 | temporal | 14 | 13 | answered | íntegra |
| 2024-08-01 | usuario | 16 | 15 | answered | íntegra |

En total: 48 llamadas LLM y 45 herramientas. No se registraron errores de herramienta ni de captura en esta campaña. La primera sesión llegó al límite de llamadas (`budget`), entregó respuesta y conservó las dos órdenes y la nota; no debe describirse como investigación exhaustiva ni como cierre libre de presupuesto. Las otras dos terminaron por respuesta.

## Continuidad demostrada

1. Junio: A consultó la cartera y hechos financieros de APH/AVGO, hizo búsquedas web, solicitó ambas compras y escribió `continuidad-historica-real-v1.md` e `indice.md`. Las órdenes estaban pendientes al responder.
2. Julio: sin nuevo mensaje humano, leyó `indice.md` y la nota inicial, consultó cartera/historial y calculó variaciones con herramientas. Actualizó la nota, creó `revision-cartera-2024-07-01.md` y actualizó el índice. No emitió otra orden ni `notify_user`; su cierre quedó interno.
3. Agosto: leyó el índice, la nota inicial y la revisión de julio; consultó de nuevo hechos financieros y cartera, solicitó los dos cierres y guardó `revision-cartera-2024-08-01.md`. Diferenció las ventas pendientes de su ejecución posterior.

Estas lecturas aparecen en las llamadas de herramientas y sus resultados, seguidas por escrituras posteriores y snapshots. No se infiere continuidad solo de que el texto resulte coherente. Las cantidades de unidades presentes al inicio de julio y agosto son iguales a las compradas; no se multiplicaron por los splits ya incorporados en la serie.

El volumen completo de tres respuestas financieras se entregó mediante referencia paginada. Los originales completos están en materiales; no debe suponerse que todo su contenido entró al modelo. La comprobación temporal posterior examinó 336 observaciones en los resultados completos, incluyendo repeticiones entre consultas, y cuatro valoraciones de cartera.

## Operaciones y valoración

| Símbolo | Operación | Solicitud | Ejecución | Importe USD |
|---|---|---|---|---:|
| APH | buy | 2024-06-01 | 2024-06-03 | 100.00000000 |
| AVGO | buy | 2024-06-01 | 2024-06-03 | 100.00000000 |
| APH | sell | 2024-08-01 | 2024-08-02 | 89.88342733 |
| AVGO | sell | 2024-08-01 | 2024-08-02 | 109.14342837 |

Las compras se ejecutaron el lunes 3 de junio, primera sesión posterior al sábado 1 de junio. Las ventas solicitadas el 1 de agosto se ejecutaron al cierre observado del 2 de agosto. Se verificaron fechas, cantidades e importes contra el dataset congelado mediante aritmética Decimal independiente de la decisión del modelo.

En julio el patrimonio observado fue 100.027,16 USD; tras los cierres y al final quedaron **99.999,02685570135600194317908233347 USD**, sin posiciones ni órdenes pendientes. La caja final concilia con `100000 - 100 - 100 + 89,88342732997222362528584410180909 + 109,1434283713837783178932382316617`. Es el resultado mecánico de una prueba de 200 USD sobre participaciones normalizadas, no una estimación de rentabilidad invertible.

## Comprobaciones y límites

- Las cuatro ejecuciones utilizan el primer cierre disponible estrictamente posterior a la solicitud y coinciden con sus precios congelados.
- Las cuatro valoraciones observadas coinciden con caja más unidades por último cierre disponible, sin usar precios posteriores al corte.
- Los hechos financieros devueltos cumplen `period <= as_of` y `available_on <= as_of`. Estimar disponibilidad no demuestra publicación efectiva ni recupera versiones contables anteriores.
- Los diez resultados web devueltos tienen fecha detectable dentro del límite impuesto. Eso no certifica que los fragmentos no hayan sido actualizados después ni elimina conocimiento futuro del entrenamiento.
- Los archivos de respuesta y de memoria son diferentes: la memoria se conservó mediante herramientas, no automáticamente desde las respuestas.
- No se ejecutó aquí la campaña de dos años ni se introdujeron evaluador, nuevos mecanismos cognitivos, escrituras financieras remotas, commits o cambios del wheel.

El SHA-256 del archivo de entrada es `2b65121feae3ae0f2784584f53af6649856d988997eda6eb402f0a71f2b58745`; el JSON congelado por el simulador es `4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`. Se comprobó igualdad de los objetos JSON: la diferencia de bytes corresponde a serialización/saltos de línea. Cada identidad queda conservada en sus archivos y manifiestos; no se reescribieron las capturas.

## Evidencia local

Cada sesión conserva `manifiesto.json`, `resultado.json`, `eventos.jsonl`, snapshots, `respuesta.md` y trazas del proveedor bajo la ruta indicada:

- 2024-06-01: `artifacts/historical-smoke-real-v1/campaign/agente/ejecuciones/2026-10-24-activation-0001-attempt-0001`; run `6ea2dd1e-8730-4223-82c1-a6d917ef21b4`.
- 2024-07-01: `artifacts/historical-smoke-real-v1/campaign/agente/ejecuciones/2026-10-24-activation-0002-attempt-0002`; run `c0a56ddf-7d73-439c-91d2-7d9a387ea46a`.
- 2024-08-01: `artifacts/historical-smoke-real-v1/campaign/agente/ejecuciones/2026-10-24-activation-0003-attempt-0003`; run `081c0a8d-e99e-426d-be70-9229e1f65b5e`.

Las comprobaciones por intento están en `intentos/*/capture.json` y `steps.json`; los estados económicos en `simulator-before.json` y `simulator-after.json`. La caja e historial finales están en `portfolio-final.json` y `history-final.json`.

Checks de código tras el cambio: 109 pruebas locales pasadas; mypy sin errores en 26 archivos. Las nuevas pruebas comprueban normalización, cancelación de factores futuros comunes, no duplicación de splits, rechazo de granularidad/moneda/identidad incorrectas, ausencia de cierres ajustados y regla ex-dividendo del fallback. La observación semántica de esta prueba es parcial y no compara variantes.
