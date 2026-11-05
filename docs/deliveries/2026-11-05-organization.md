# Reorganización y retirada de V8 — 2026-11-05

## Base y alcance

Base Git: `6061cd4`, rama `experiment/fileAgent`, más cambios locales previos, incluidos
Progress y nota de continuidad. El encargo aprobó reorganizar, retirar V8 y aliases,
conservar extensiones y hacer opcional la revisión general, activada por defecto.
Se conservó una referencia local del diff inicial; no se reescribieron experimentos,
estados ni instrucciones congeladas. No hubo commit, publicación ni campaña real.

## Cambio

El [mapa de módulos](../modules.md) describe núcleo, persistencia, captura, composición,
regímenes, extensiones y capacidades. Campañas sigue siendo paquete hermano, organizado
en definiciones, ejecución e informes. Las pruebas reflejan áreas y comparten fábricas
en soporte, sin imports entre tests.

Se retiraron el evaluador V8, cobertura/distancia, recuperación asociada y ramas de
continuo. Objective conserva entradas, definición y hashes; assessment_path es un dato
histórico admitido, sin disparar revisión decisoria. Los lectores de informes de campañas
pueden seguir mostrando métricas ya capturadas: no las calculan ni ejecutan V8.

La revisión general vive con el continuo. ContinuousConfig.general_review=True y
--general-review on/off seleccionan su ejecución; Progress mantiene su propio evaluador
y desactiva el general. Apagarlo elimina revisiones y feedback previo, conserva trabajo,
checkpoints y límites, y permite una respuesta textual de cierre en el presupuesto.
Los selectores también se transmiten desde escenarios continuos de campañas.

Se eliminaron aliases internos tras actualizar consumidores. Se conservan AgentA,
petición, resultado, nombres de copias congeladas y comandos públicos. La entrada de
consola apunta ahora a research_agent.cli.main:main; actualizar la instalación editable
local regenera esa entrada; se realizó sin dependencias ni acceso a índices. Los prompts
y contratos viajan con sus componentes en el wheel.
Los ejemplos Python de contratos de estado usan los imports nuevos; sus hashes de texto
cambian y se notifican por el mecanismo existente, sin cambiar schemas de herramientas.
La [ADR-0006](../decisions/0006-organizacion-y-revision-opcional.md) modifica las decisiones
históricas sobre obligatoriedad de revisión y compatibilidad de imports.

## Verificación y límites

La ejecución de la suite completa, tanto inicial como final, encuentra un error previo
de recopilación: test_price_review necesita scripts/review_historical_prices.py, ausente
antes del cambio. Se conserva esa prueba sin inventar su implementación ni ocultarla
con un skip. La verificación ejecutable excluye explícitamente solo ese archivo.

- Pasada amplia: `python -m pytest -q tests --ignore=tests/campaigns/test_price_review.py`,
  445 pruebas correctas. Tras los últimos ajustes, 33 pruebas de E2 y revisión general
  y 19 de objetivos, congelación de campañas y atomicidad de agenda pasaron por separado.
  Estas últimas incluyen 12 casos de contratos vigentes recuperados de los archivos V8.
- Mypy comprobó 87 archivos sin incidencias; `pip check` no encontró requisitos rotos.
- Wheel local construido sin índice: 87 archivos Python y recursos verificados, sin
  módulos retirados. Ayudas de las CLI y entrada de consola instalada comprobadas.
- `git diff --check` y enlaces y anclas internos correctos.

Las comprobaciones usan clientes y datasets sintéticos; no certifican calidad financiera
ni continuidad semántica. No hubo llamadas a proveedores o Findata remota.

runtime.json conserva la identidad histórica byte a byte; los fingerprints de código
cambian y las campañas incompatibles siguen rechazándose. No hay migración ni promesa
de continuar campañas preparadas con otra identidad. Los imports internos antiguos ya
no están soportados; los consumidores externos deben adoptar rutas canónicas.

La comprobación documental cubre enlaces y anclas internos: sin errores. Se comprobaron
por existencia 93 destinos externos al repositorio: 17 disponibles y 76 ausentes en
el checkout hermano; no se modificaron esas fuentes ni se verificaron sus anclas.
