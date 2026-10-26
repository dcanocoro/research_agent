# Cartera simulada — razonamiento de asignación

Mandato: inversión ficticia a largo plazo, capital inicial $100.000, efectivo permitido. Estado operativo autoritativo: herramientas de cartera; este archivo conserva el razonamiento.

## C1 — Inicio prudente; posiciones ejecutadas
Decisión inicial 2023-01-01: enviar compras de AAPL $15.000 y ADP $10.000, mantener el resto sin reservar. La lógica fue exposición inicial limitada a dos modelos de negocio, con 75% de capital conservado por falta de valoración/precio compatibles y escasa comparación sectorial; no se afirmó infravaloración. Referencias iniciales: `empresas/AAPL/evaluacion.md#E1`, `empresas/ADP/evaluacion.md#E1`, `oportunidades.md#O1`.

### Estado y revisión al 2023-02-01
La consulta de cartera y el historial confirman que ambas órdenes **se ejecutaron el 2023-01-03**: AAPL $15.000 a 96.259548 unidades de precio ajustado normalizado, 155.828697 unidades simuladas; ADP $10.000 a 99.497608, 100.504928 unidades. No hay órdenes pendientes ni canceladas. Fuente: `materiales/2026-10-25-activation-0002-attempt-0002-02-portfolio-history.json`.

A 2023-02-01, efectivo/disponible $75.000; valor marcado AAPL $17.441,83; ADP $9.540,10; equity $101.981,93. Pesos sobre equity: AAPL 17,10%, ADP 9,35%, efectivo 73,54% (cálculos `materiales/2026-10-25-activation-0002-attempt-0002-23-calculate.json`, `materiales/2026-10-25-activation-0002-attempt-0002-24-calculate.json`, `materiales/2026-10-25-activation-0002-attempt-0002-25-calculate.json`). Cambio marcado respecto de capital inicial: +$1.981,93 / +1,98%, cálculos `materiales/2026-10-25-activation-0002-attempt-0002-28-calculate.json`, `materiales/2026-10-25-activation-0002-attempt-0002-29-calculate.json`. Es rendimiento interno del simulador sobre series históricas normalizadas ajustadas, no cotización/acción negociada ni evidencia de valor razonable. La serie integra dividendos y splits; no abonarlos o aplicarlos otra vez. No se contabiliza retorno por intereses del efectivo.

No cambia la tesis por el movimiento de precio marcado; faltan datos nominales de mercado comparables y valoración por escenarios para AAPL y ADP (`empresas/AAPL/valoracion.md#V1`, `empresas/ADP/valoracion.md#V1`). AMGN sigue en investigación, no posición (`empresas/AMGN/evaluacion.md#E1`). Mantener el efectivo por ahora; no enviar órdenes por desempeño reciente ni por ausencia de oportunidades ya valoradas.

## Asignación y siguientes revisiones
La exposición continúa concentrada en dos compañías y más de 70% en efectivo: prudente ante valoración no resuelta pero con coste de oportunidad. No se ha completado cribado homogéneo de las 50 firmas. Antes de ampliar, resolver o reformular valoraciones de AAPL/ADP, analizar AMGN (balance, productos/patentes y adquisición de Horizon) y escoger alternativas sectoriales comparables. Revisar liquidez, disponibilidad de precio/capitalización/acciones compatibles y nuevas fuentes fechadas. No considerar el efectivo automáticamente óptimo a largo plazo.
