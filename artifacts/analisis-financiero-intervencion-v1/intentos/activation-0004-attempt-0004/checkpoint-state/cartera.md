# Cartera simulada — razonamiento de asignación

Mandato: inversión ficticia a largo plazo, capital inicial $100.000, efectivo permitido. Estado operativo autoritativo: herramientas de cartera; este archivo conserva razonamiento.

## C1 — Inicio prudente; posiciones ejecutadas
Decisión inicial 2023-01-01: enviar compras AAPL $15.000 y ADP $10.000, conservar el resto. Exposición limitada a dos modelos, con 75% mantenido en efectivo ante falta de precio/valoración comparables y escasa comparación sectorial; no se afirmó infravaloración. Referencias: `empresas/AAPL/evaluacion.md#E1`, `empresas/ADP/evaluacion.md#E1`, `oportunidades.md#O1`.

### Estado confirmado al 2023-02-01
La consulta de historial confirmó ambas órdenes ejecutadas 2023-01-03: AAPL $15.000 a 96.259548 unidades de precio ajustado normalizado, 155.828697 unidades simuladas; ADP $10.000 a 99.497608, 100.504928 unidades. No hubo órdenes pendientes/canceladas. `materiales/2026-10-25-activation-0002-attempt-0002-02-portfolio-history.json`.

Al 2023-02-01 efectivo $75.000; marcas AAPL $17.441,83 y ADP $9.540,10; equity $101.981,93. Pesos/cambio calculados en `materiales/2026-10-25-activation-0002-attempt-0002-23-calculate.json` a `...-29-calculate.json`. Rendimiento del simulador sobre series normalizadas ajustadas, no cotización/acción negociada ni evidencia de valor razonable. Dividendos y splits incluidos en la serie; no abonarlos/aplicarlos otra vez. Sin retorno por intereses contabilizado.

### Revisión temporal 2023-03-01 — sin órdenes nuevas
Consulta: efectivo y disponible $75.000; AAPL 155.828697 unidades simuladas, marca $17.454,05; ADP 100.504928 unidades, marca $9.238,41; equity $101.692,46; sin órdenes pendientes. Fuente de cartera y convención: `materiales/2026-10-25-activation-0003-attempt-0003-01-portfolio-get.json`. Efectivo / equity = 73,75% (cálculo `materiales/2026-10-25-activation-0003-attempt-0003-13-calculate.json`). Las marcas son precios por unidad ajustada normalizada, no cotizaciones nominales ni participaciones de acciones reales; el cambio desde febrero no es razón suficiente para operar. Posición AAPL y ADP siguen sin valoración relativa completa (`empresas/AAPL/valoracion.md#V1`, `empresas/ADP/valoracion.md#V1`). AMGN continúa candidata sin posición (`empresas/AMGN/evaluacion.md#E1`). Se conserva asignación sin cambio; no se ejecutó una transacción nueva.

## Asignación y revisiones siguientes
Exposición en dos empresas y más de 70% de efectivo: reduce riesgo de asignar capital sin valoración, pero mantiene coste de oportunidad y concentración de nombres. Cribado homogéneo de otras empresas pendiente. Antes de ampliar/reducir, resolver o reformular valoraciones de AAPL/ADP, avanzar análisis AMGN (mezcla de productos, expiraciones/pipeline y adquisición Horizon) y buscar alternativas comparables con precios/datos compatibles. No considerar efectivo óptimo automáticamente ni usar marcas normalizadas para rendimiento fundamental.
