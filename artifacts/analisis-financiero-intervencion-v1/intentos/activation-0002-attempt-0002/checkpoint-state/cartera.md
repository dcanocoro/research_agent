# Cartera simulada — razonamiento de asignación

Fecha de corte: 2023-01-01. Estado operativo autoritativo: herramienta de cartera, no este archivo.

## C1 — Inicio prudente con órdenes pendientes
Mandato: inversión ficticia a largo plazo, $100.000 iniciales; se permite efectivo. Se enviaron órdenes de compra a siguiente cierre disponible: AAPL $15.000 (order-000001) y ADP $10.000 (order-000002). Total reservado $25.000, 25% del capital (cálculos `materiales/2026-10-25-activation-0001-attempt-0001-36-calculate.json`, `...-37-calculate.json`). No se habían ejecutado a fecha 2023-01-01: cartera sin posiciones, efectivo $100.000, disponible $75.000, las dos órdenes pendientes, equity $100.000 (`materiales/2026-10-25-activation-0001-attempt-0001-30-portfolio-get.json`). Por lo tanto, la exposición de mercado ejecutada sigue siendo cero en ese corte; no confundir efectivo disponible con efectivo neto de órdenes reservadas.

Razonamiento: iniciar participaciones limitadas en dos negocios con mecanismos de ingresos distintos y generación de caja observada; mantener 75% sin reservar porque no se consiguió precio/capitalización/acciones compatible con las unidades financieras y no hay valor intrínseco ni margen de seguridad calculados. No se concluye que ambas acciones estén baratas. Concentración sectorial y falta de diversificación permanecen; no añadir una tercera empresa sin comparar fundamentos y precio.

El precio de cartera es una serie ajustada normalizada (100 al ancla), no cotización ni cantidad nominal de acciones; dividendos y splits ya están en serie; no sumar dividendos ni multiplicar unidades de nuevo. Referencia de posición/precio y límites: `materiales/2026-10-25-activation-0001-attempt-0001-05-read-company.json`, `...-11-read-company.json`; convención también indicada por la activación.

Siguiente revisión: verificar órdenes/ejecuciones; valorar AAPL y ADP en unidades compatibles; evaluar otras industrias (salud/consumo/finanzas/industriales) y rendimiento del efectivo; revaluar tamaños tras comparación. Referencias: `empresas/AAPL/evaluacion.md#E1`, `empresas/ADP/evaluacion.md#E1`, `oportunidades.md#O1`.
