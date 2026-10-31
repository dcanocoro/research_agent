# Tres casos fijos con lanzamiento paralelo

Fecha: 2026-10-31. Base Git: `b9a0792`. Implementación del plan aprobado, sin campañas reales ni cambios
en el comportamiento de A o las modalidades de `research_campaigns`.

Se añaden los prompts estables de analista abierto, Microsoft e infraestructura de
IA, con mandato común, según el [protocolo](../experiments/casos-fijos/protocol.md).
El script lanza tres procesos de la CLI nativa, con 100 llamadas ordinarias cada uno,
revisiones adicionales, directorios nuevos y separados y conservación de entradas y
logs. No añade objetivos JSON, simulador, reintentos ni informes agregados.

Se rechazan destinos existentes antes de lanzar; un fallo no detiene los demás casos.
La cancelación detiene y recoge los procesos. El cierre por `call_limit` se presenta
como presupuesto agotado y no acredita cumplimiento. La [guía](../campaigns.md#tres-casos-fijos-en-paralelo)
documenta el único comando y los resultados nativos.

Verificación local: 12 pruebas del lanzador aprobadas, incluida una barrera de tres
procesos Python locales que comprueba solapamiento sin ejecutar A ni consultar servicios.
Se comprueban parámetros, entradas UTF-8, aislamiento, logs, rechazo de destinos,
fallos, cancelación y recogida forzada, y lectura de capturas parciales.
Tipado del script correcto; 72 enlaces locales y dos anclas comprobados, y `git diff --check`
sin errores. La suite completa se bloquea durante recopilación porque el test
preexistente `tests/test_price_review.py` requiere `scripts/review_historical_prices.py`,
ausente en el checkout de base. No se restaura ese script ajeno al alcance.
Al excluir únicamente ese archivo para poder recopilar el resto, la regresión
termina con 354 pruebas aprobadas, 9 fallidas y 22 errores: faltan definiciones y
bundles históricos como `campaigns/contexto-continuo-v3` y
`campaigns/analisis-financiero-v1/control`. No se restauran esas entradas retiradas.
La calidad semántica y el comportamiento integrado con proveedores siguen sin evaluarse.
