# Cartera simulada — razonamiento de asignación

Mandato: inversión ficticia a largo plazo, capital inicial $100.000, efectivo permitido. Estado operativo autoritativo: herramientas de cartera; este archivo conserva razonamiento.

## C1 — Inicio prudente; posiciones iniciales ejecutadas
Decisión inicial 2023-01-01: enviar compras AAPL $15.000 y ADP $10.000, conservar el resto. Exposición limitada a dos modelos, con 75% en efectivo ante falta de precio/valoración comparables y comparación sectorial insuficiente; no se afirmó infravaloración. Referencias: `empresas/AAPL/evaluacion.md#E1`, `empresas/ADP/evaluacion.md#E1`, `oportunidades.md#O1`.

La consulta de historial confirmó ambas órdenes ejecutadas 2023-01-03: AAPL $15.000 a 96.259548 unidades de precio ajustado normalizado, 155.828697 unidades simuladas; ADP $10.000 a 99.497608, 100.504928 unidades. No hubo órdenes pendientes/canceladas en el historial consultado. `materiales/2026-10-25-activation-0002-attempt-0002-02-portfolio-history.json`.

### Revisiones sin nueva orden: 2023-02-01 y 2023-03-01
Al 2023-02-01 efectivo $75.000; marcas AAPL $17.441,83 y ADP $9.540,10; equity $101.981,93. Cálculos de pesos/rendimiento en `materiales/2026-10-25-activation-0002-attempt-0002-23-calculate.json` a `...-29-calculate.json`. Al 2023-03-01 efectivo $75.000; AAPL $17.454,05; ADP $9.238,41; equity $101.692,46; sin órdenes pendientes (`materiales/2026-10-25-activation-0003-attempt-0003-01-portfolio-get.json`). No se operó porque el movimiento de la serie no resolvió valoración.

Las marcas son una serie de precios ajustados y normalizados, no cotizaciones nominales ni participaciones de acciones reales; dividendos y splits están incorporados y no se deben volver a abonar/aplicar. El rendimiento de marca no es evidencia de valor fundamental.

## C2 — Revisión al 2023-04-01: conservar cartera, sin nuevas órdenes
Consulta al 2023-04-01 (marcas de cierre 2023-03-31): efectivo y disponible $75.000; AAPL 155.828697 unidades simuladas, valor $19.807,12; ADP 100.504928 unidades, valor $9.420,63; equity $104.227,75; ninguna orden pendiente (`materiales/2026-10-25-activation-0004-attempt-0004-01-portfolio-get.json`, historial `...-02-portfolio-history.json`). Pesos calculados: AAPL 19,00%, ADP 9,04%, efectivo 71,96% (`...-20-calculate.json`, `...-21-calculate.json`, `...-22-calculate.json`).

Desde el costo simulado de $15.000 AAPL marca +$4.807,12 (+32,05%); ADP, desde $10.000, -$579,37 (-5,79%). Equity marca +$4.227,75 frente al capital inicial, aproximadamente +4,23% (`...-10-calculate.json` a `...-15-calculate.json`). Son resultados del simulador sobre precios históricos ajustados normalizados, dividendos/splits embebidos; no precios reales de ejecución ni evidencia de infravaloración. No se contabiliza interés de caja. Fuentes de valores: `materiales/2026-10-25-activation-0004-attempt-0004-01-portfolio-get.json`; cálculos referidos en cada línea.

Cambio fundamental que afecta la postura: el 10-Q de AAPL para el trimestre terminado 2022-12-31 informa ventas -5% interanual y debilidad de iPhone/Mac, parcialmente compensada por Services/iPad (`empresas/AAPL/modelo.md#E2`). Reduce confianza en el impulso reciente, pero una observación trimestral no demuestra ruptura de la tesis de largo plazo; sin FCF trimestral comparable no hay recálculo de valor sostenible. La evaluación AAPL queda “mantener, no ampliar ni vender” con V1 pendiente (`empresas/AAPL/evaluacion.md#E1`, `empresas/AAPL/valoracion.md#V1`). ADP permanece sin nueva evidencia primaria verificada y con conversión/valoración pendientes; la caída de la marca no justifica vender (`empresas/ADP/evaluacion.md#E1`, `empresas/ADP/valoracion.md#V1`). AMGN continúa sin posición y no está suficientemente valorada para sustituir efectivo (`empresas/AMGN/evaluacion.md#E1`).

**Decisión:** conservar exactamente las posiciones y $75.000 de efectivo; no se envía orden nueva. La liquidez sigue siendo alta y tiene coste de oportunidad; su mantenimiento es una decisión provisional por incertidumbre de valoración/comparación, no afirmación de que el efectivo sea óptimo. No vender por rentabilidad marcada ni ampliar por el rendimiento de AAPL. Reconsiderar tras próximas cifras de Apple, aclaración del FCF de ADP, actualización del efecto Horizon y valoración comparable.
