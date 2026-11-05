# Entrega — ablación E1 del agente actual

Fecha: 2026-10-31. Base Git: `493952fa01d5a2839110ff1379488147bbc69102`.
Implementación y preparación solicitadas. Después se ejecutaron las tres campañas E1
autorizadas, con proveedores y acceso de lectura a las fuentes habilitadas por el
laboratorio. Sin cambios en FinMate, commit ni push.

## Cambio

El mismo agente conserva una sola composición y un único escritor,
`record_research_advance`. Se retiraron cinco escritores alternativos, sus adaptadores,
métodos sin consumidores y la selección legacy/v5 en CLI y APIs internas.
Las primitivas internas de Workspace siguen sirviendo publicación y preparación local.

Conserva las lecturas, herramientas de investigación/cálculo, Python opcional,
restricciones por fase, validación de documentos de empresa, versiones, límites,
diarios y recuperación. Una edición con target vacío solo funciona sobre archivo
vacío y con versión vigente, para no perder la capacidad de inicializarlo.

Las instrucciones se condensaron por responsabilidad: generales (rigor y conservación),
deliberación (prioridad/agenda/cierre), financieras (método/documentos/dependencias) y
guía técnica (recuperación y escritura). Se conservaron procedencia, fechas, unidades,
fuentes, cálculos verificables, incertidumbre y límites de autorización.
No cambiaron los tres encargos ni el mandato de casos fijos.

| Texto | Palabras antes | Después |
|---|---:|---:|
| General | 1385 | 609 |
| Deliberación | 1158 | 433 |
| Financiero | 2369 | 938 |
| Guía de estado | 552 | 364 |
| Total | 5464 | 2344 |

Conteo por separación en espacios sobre los textos, comparado con la base Git.
Es descripción del tratamiento, sin equivalencia automática con tokens ni calidad.

Los experimentos nuevos congelan la guía y la identidad del contrato en
`herramientas.json`. Los anteriores se rechazan antes de crear clientes, sin editar
sus instrucciones, estado o capturas; requieren código anterior o migración autorizada.
El lanzador fijo usa la única composición. Los timeouts de 180 segundos siguen
siendo variables explícitas del proceso, sin modificación permanente de .env.

## Verificación

Comprobaciones locales, sin servicios externos:

- Pasada ampliada: `python -m pytest -q tests --ignore=tests/campaigns/test_price_review.py --tb=short --show-capture=no`: 386 passed y tres fallos en fixtures.
  Dos fixtures confundían revisión sin herramientas con consolidación tras ampliar su
  presupuesto sintético; el tercero no preparaba el contrato de una sesión gestionada.
  Corregidos y repetidos: 2 passed y 1 passed, respectivamente.
- Regresión focalizada posterior sobre agente, metodología y estado: 78 passed.
  Los 389 casos disponibles quedan cubiertos entre la pasada ampliada y las repeticiones;
  no se hizo otra pasada integral después de corregir los fixtures.
- Mypy sobre `research_agent` y `research_campaigns`: sin errores en 42 archivos.
- `pip check`: sin requisitos rotos.
- Comprobador documental histórico ejecutado en memoria contra la raíz actual:
  83 Markdown, 702 enlaces locales, cero errores internos. Se registran aparte 241
  referencias externas a archivos ausentes del checkout hermano de FinMate; el
  chequeo global sin separar esas referencias devuelve error, no un passed global.
- `git diff --check`: sin errores.

La primera pasada ampliada detectó además fixtures que dependían de recetas retiradas
antes de E1; se sustituyeron por entradas sintéticas temporales para verificar los
contratos actuales sin restaurar campañas.

Las pruebas se adaptaron al contrato real, sin traducción de herramientas retiradas
en el agente. Se añadieron comprobaciones de escritor único, rechazo de contratos
antiguos sin mutación y anclas vacías versionadas. Las pruebas de instrucciones y
piloto usan fixtures sintéticos temporales en lugar de recetas históricas retiradas;
no reconstruyen ni validan resultados de aquellas campañas.

La primera colección completa está bloqueada por `tests/campaigns/test_price_review.py`:
importa `scripts/review_historical_prices.py`, ausente ya en la base Git.
No se restaura ese script ni se oculta el bloqueo mediante un cambio al test histórico.
Se comprueba el resto de la suite por separado. La primera pasada ampliada y el detalle del chequeo de enlaces quedan en
`artifacts/`, ignorado y no portable; este registro conserva los resultados y límites.

## Interpretación y siguiente paso

El [protocolo E1](../experiments/e1-simplificacion/protocol.md) fija intervención
conjunta, tres casos, condiciones y rúbrica. Las tres ejecuciones llegaron a 100
llamadas ordinarias y terminaron `interrupted: call_limit`; no se interpreta como
resolución de los encargos. Hubo 4, 4 y 9 eventos `lab.tool.failed` en analista,
Microsoft y sector IA; las capturas no registran errores de captura. Microsoft dejó
una referencia de precio en la respuesta final sin propagarla a la agenda/evaluación.
Los detalles, clasificaciones y límites están en los [hallazgos E1](../experiments/e1-simplificacion/findings.md).

La comparación con octubre será descriptiva; no hay control equivalente ni separación
de efectos entre retiradas. Esta ejecución no demuestra que la simplificación mejore o
empeore calidad o eficacia.

Los checks acreditan funcionamiento local, no selección útil de acciones, calidad
financiera o resultados de inversión. La campaña de esta entrega ya se ejecutó; los
hallazgos no autorizan ni implican una campaña posterior.
