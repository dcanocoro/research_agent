# Revisión de cartera ficticia — fecha simulada 2023-02-01

## Juicio vigente y decisión

**No enviar nuevas órdenes ni vender en esta revisión.** Mantener las cinco posiciones iniciales y los **50.000 USD** de efectivo disponible mientras no se pueda comparar una cotización de mercado real con beneficios/caja normalizados. Las herramientas solo dan precios ajustados normalizados, no cotizaciones accionables ni múltiplos fiables; la subida observada en un mes no demuestra infravaloración o mejora sostenible. Esto es una decisión de cartera bajo evidencia incompleta, no una orden para una cartera real.

Se conserva la postura anterior de inversión parcial: cinco empresas de actividades distintas, con concentración idiosincrática y estadounidense, no constituyen diversificación amplia. La ganancia observada no justifica aumentar exposición. El efectivo es opcionalidad pendiente de investigación, no un objetivo permanente.

## Estado operativo al 2023-02-01

La cartera simulada confirma que las cinco órdenes de compra de 10.000 USD fueron ejecutadas el **2023-01-03**; ya no están pendientes. La historia muestra cantidades normalizadas adquiridas y precio de ejecución en unidades ajustadas, no acciones/cotizaciones negociables. A 2023-02-01: efectivo 50.000 USD; valor de posiciones 53.796,60 USD; valor total simulado 103.796,60 USD; ninguna orden pendiente. Evidencia: `materiales/2026-10-24-activation-0002-attempt-0002-02-portfolio-history.json` y `materiales/2026-10-24-activation-0002-attempt-0002-01-portfolio-get.json`.

Valores de posición al cierre normalizado del 2023-02-01: AAPL 11.627,89; ABT 10.250,62; ACN 10.536,52; ADP 9.540,10; AXP 11.841,48 USD. La serie ajustada incorpora dividendos y splits; no volver a contabilizarlos. Las cantidades y valores no son los de una cuenta de corretaje.

El valor total excede los 100.000 USD iniciales en 3.796,60 USD, o 3,80% por cálculo sobre el valor de cuenta simulado (`materiales/2026-10-24-activation-0002-attempt-0002-08-calculate.json`, `...-09-calculate.json`). Es una variación marcada a mercado de la simulación entre enero y febrero, no una ganancia realizada, pronóstico ni evidencia suficiente para decidir valor intrínseco; la mitad inicial del capital sigue en efectivo.

## Revisión fundamental al corte

Los datos son USD y anuales. La herramienta aplica una convención experimental de disponibilidad estimada de 120 días; `published_at` es nulo. Por tanto, la fecha estimada de disponibilidad no verifica la publicación real, y los datos pueden ser revisados/restatados. No usar observaciones posteriores al 2023-02-01.

- **AAPL:** aparece ahora FY terminado 2022-09-30: ingresos 394.328 M USD, resultado operativo 119.437 M, FCF 111.443 M, deuda 120.069 M y efectivo/inversiones cortas 23.646 M. Frente a FY2021, ingresos +7,79% y FCF +19,89%, cálculos sobre datos anuales de Alpha Vantage preservados; razón resultado operativo/ingresos 30,29% frente a 29,78% (+0,51 puntos porcentuales). Esto apoya que el negocio siguió creciendo en ese ejercicio y tuvo leve expansión de margen operativo observado, no prueba de continuidad ni de precio atractivo. Referencias: `materiales/2026-10-24-activation-0002-attempt-0002-03-read-financials.json` y datos comparativos FY2021 en `materiales/2026-10-24-activation-0001-attempt-0001-07-read-financials.json`; cálculos: `...-10-calculate.json` a `...-16-calculate.json` en la sesión 0002. La revisión anterior señaló deuda material y exposición a productos/ecosistema; eso sigue siendo pertinente.
- **ADP:** el corte sigue mostrando FY2022-06-30: ingresos 16.498 M, resultado operativo 3.803 M, deuda 3.124 M, FCF 2.546 M USD. No hay nuevo período anual frente a la revisión inicial; permanece la observación de menor FCF que en FY2021 pese al alza de ingresos.
- **ACN:** FY2022-08-31 sin cambio de corte: ingresos 61.594 M, resultado operativo 9.367 M, FCF 8.823 M, deuda 763 M USD. La lectura previa de ingresos crecientes y margen operativo aproximadamente estable no cambia.
- **ABT:** sigue disponible FY2021-12-31, sin dato anual FY2022 conforme a esta convención. Sigue abierta la incertidumbre sobre normalización de demanda; no afirmar sostenibilidad a partir del aumento previo.
- **AXP:** sigue disponible FY2021-12-31, sin dato anual FY2022 conforme a esta convención. La recuperación de 2021 puede ser cíclica y la deuda de un emisor financiero no es directamente comparable con deuda corporativa industrial.

Referencias 2023-02-01: `materiales/2026-10-24-activation-0002-attempt-0002-04-read-financials.json` (ADP), `...-05-read-financials.json` (ACN), `...-06-read-financials.json` (ABT), `...-07-read-financials.json` (AXP). La evaluación inicial de 2023-01-01 conserva detalles y referencias anteriores: AAPL FY2020–21, riesgos empresariales y descripción de metodología/precio; no se sustituye por información actualizada donde no hubo cambio.

## Precio, límites y criterios de revisión

El precio de cartera es una serie ajustada histórica normalizada, con ancla 100 al 2022-12-30. Los cierres del 2023-02-01 (AAPL 111,93; ABT 102,31; ACN 106,72; ADP 94,92; AXP 117,91 USD por unidad ajustada) **no son cotizaciones**. No calcular P/E, rendimiento de flujo de caja a precio, ni valor intrínseco a partir de estos valores. No hay DCF disponible. Los fundamentales son datos de proveedor aceptados por una regla estimada; no equivalen a fuente contemporánea verificada.

Reconsiderar las 50.000 USD no comprometidas cuando se pueda valorar negocios con cotizaciones reales y datos públicos fechados verificablemente, además de analizar resultados/caja normalizados y exposición conjunta; evitar añadir concentración sin comprender riesgos. Debilitar posiciones si aparecen deterioros estructurales de ingresos, margen, caja, balance, ventaja competitiva o riesgos regulatorios/crediticios. Un avance mensual de precio por sí solo no activa compra ni venta.

## Historial de revisión

- **2023-01-01:** decisión inicial: cinco órdenes de compra de 10.000 USD (AAPL, ADP, ACN, ABT, AXP) y mantener unos 50.000 USD en efectivo, principalmente por límites de valoración; estaban pendientes al cierre de esa sesión. Véase la evaluación/fuentes originales arriba y materiales de la activación `2026-10-24-activation-0001-attempt-0001`.
- **2023-02-01:** nueva evidencia operativa confirma ejecución de las cinco órdenes el 2023-01-03 y avance marcado a mercado de la cartera simulada. AAPL FY2022 queda disponible solo bajo la convención estimada y apoya crecimiento anual, con leve mejora del margen operativo calculado. No cambian los fundamentos de valoración ni las incertidumbres sobre sostenibilidad, concentración y fechas reales de publicación: no se agregan posiciones ni se vende; se conserva 50% en efectivo y se prioriza una valoración basada en precios utilizables antes de comprometerlo.
