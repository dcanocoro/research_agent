# Entrega — Simulación longitudinal

Fecha: 2026-10-24. Base local de Research Agent: `3ed48ff`. Sin commit ni publicación.

## Cambios

Se añade simulador privado, disponibilidad temporal anual estimada, herramientas de
cartera y comunicación local, y controlador mensual con checkpoints y resume. A mantiene
el ciclo y prompts existentes. El [protocolo](../experiments/colaboracion-historica-v1/protocol.md)
describe el contrato y los comandos; la [decisión](../decisions/0002-simulacion-longitudinal.md)
conserva las elecciones aprobadas.

Durante la integración se corrigió una clasificación de errores: un OSError al ejecutar
una herramienta (por ejemplo, archivo ausente) permanece como fallo de herramienta;
un OSError al conservar su resultado sí marca captura incompleta. Las trazas mantienen
ambos. Se preserva la compatibilidad de la CLI y composición ordinarias.

## Dependencia compartida

Cambios en FinMate: nuevo `findata/read/historical.py`, parámetros temporales opcionales
en `infra/adapters/tavily_web_search.py` y pruebas sin servicios. No hay cambios de
ingesta, esquema ni datos financieros.

`scripts/build_longitudinal_wheel.py` aplica exclusivamente esos dos archivos sobre el
wheel privado aprobado SHA-256
`70cd4a370e1ca4690631f104291a7cc3281acbf6972e43b3c14cb18fe7662e4f`.
Así no incorpora los otros cambios locales de FinMate. El wheel instalado tiene hash
`1c047e24e2b2799c1b5a408f33523726a94002460b99598cee361ed0ede142c0`.
La revisión de referencia de FinMate es `651686c23921ee002f7b38be5f23101cc81a6d25`;
`provenance.json` registra además hashes de los overlays. El commit solo no identifica
el wheel porque el checkout tiene cambios locales.

Construcción e instalación reproducibles desde Research Agent (destino nuevo):

```powershell
.\.venv\Scripts\python.exe scripts/build_longitudinal_wheel.py --base artifacts/portability/wheels/findata-0.1.0-py3-none-any.whl --finmate ../FinMate-longitudinal --output artifacts/wheel-longitudinal-NUEVO
.\.venv\Scripts\python.exe -m pip install --no-index --no-deps --force-reinstall artifacts/wheel-longitudinal-NUEVO/findata-0.1.0-py3-none-any.whl
.\.venv\Scripts\python.exe -m pip check
```

El wheel y la procedencia están localmente en `artifacts/longitudinal-wheel-v1/`.
No se actualiza silenciosamente el paquete de portabilidad anterior ni se atribuye
el comportamiento nuevo a su wheel. Para volver al baseline se puede reinstalar el
wheel aprobado original con `--no-index --no-deps --force-reinstall`.

### Aislamiento posterior en rama de develop

Por petición del usuario, los dos archivos compartidos y sus pruebas se trasladaron
a `codex/longitudinal-historical-tools`, basada en `origin/develop` a
`d9e63b72a0d6b0aac67d5792e16e82112edd54ae`. El worktree está en
`C:\Users\Daniel\Proyectos\FinMate-longitudinal`; los cambios siguen sin commit ni push.
Se retiraron únicamente estos cambios de `feature/tesis`, conservando su migración
previa a `runtime_contracts` y el resto del trabajo local.

Develop mantiene imports de Engine. La receta del wheel normaliza solo esos dos
imports del adaptador al contrato del wheel aprobado; registra hashes de fuentes y
overlays por separado. La comprobación en `artifacts/longitudinal-wheel-branch-check/`
produjo los mismos hashes de ambos overlays que la implementación instalada. El zip
puede tener otro hash por el empaquetado: ese wheel de comprobación no se instaló.
El wheel instalado y las campañas existentes permanecen intactos. La transferencia
conserva copia y registro local en `artifacts/finmate-longitudinal-move-20261024/`.

Verificación del traslado: dos pruebas compartidas pasadas sobre la rama nueva y
hashes de ambos módulos instalados intactos. La documentación del nuevo worktree
hereda una referencia rota a `roadmaps/investment-case-evolution.md` y un catálogo
desactualizado de develop. Se comprobó la regeneración y se conservó el catálogo
original para no incorporar una limpieza ajena al traslado. `git diff --check` pasa.

También se construyó `artifacts/longitudinal-dist/research_agent-0.1.0-py3-none-any.whl`
(SHA-256 `18867226b362535ae8f4878f78d61fbe854f1efa1720d242fbda4c034097e7ad`).
Se comprobó que contiene simulador/controlador y que valida el escenario importando
directamente desde el wheel. El laboratorio sigue instalado editable; este build
no reemplaza el paquete de portabilidad anterior.

## Cobertura observada y límites

Actualización posterior solicitada por el usuario: la
[revisión de precios](../experiments/colaboracion-historica-v1/price-review.md) completa
las 50 series ajustadas y documenta el fallback de AVB; la
[prueba corta histórica real](../experiments/colaboracion-historica-v1/historical-smoke.md)
completa tres activaciones con captura íntegra. Los bloqueos y resultados siguientes
describen el primer corte y se conservan como antecedente. El wheel no se modificó.

Preflight real de solo lectura en `artifacts/longitudinal-preflight-v1/`: 50 empresas,
25.400 precios y 6.619 fundamentales; 2.776 hechos disponibles al inicio con la política
de 120 días. No hubo problemas de cobertura detectados en las activaciones.

El único bloqueo declarado es la revisión de precios: Findata utiliza
`TIME_SERIES_DAILY` y no almacena ajustes/acciones corporativas. No se ejecutó la cartera
histórica de 2023–2024 con esa revisión pendiente. Resolverla con evidencia antes de
crear una campaña nueva; el retraso estimado de fundamentales ya no es un bloqueo.

La selección es alfabética dentro de la cobertura almacenada, sin resultados futuros;
no acredita representatividad del mercado ni ausencia de sesgo de supervivencia.

## Verificación

Suite completa final: **102 pruebas pasadas en 90,07 segundos**. Suite específica:
26 pruebas pasadas, incluyendo procesos
reales de CLI/A con proveedor controlado, calendario de dos años/50 empresas y
recuperación antes/después de efectos, pérdida de captura y preparación interrumpida.
Mypy: 26 archivos sin errores. `pip check`: sin requisitos rotos. Documentación local:
32 Markdown, 504 enlaces, cero errores; `git diff --check` sin errores.

En FinMate pasan 17 pruebas sin servicios: dos nuevas de disponibilidad estimada,
payload temporal, análisis de fecha HTTP y compatibilidad de búsqueda sin filtros,
y 15 existentes de documentos Tavily.
No se ejecutó la suite completa del producto ni se modificó su base de datos.
El comprobador documental de FinMate encuentra 11 errores previos por referencias a
entregas ausentes bajo `artifacts/`; ninguno corresponde a los enlaces añadidos a la
guía del laboratorio. No se han fabricado esos artefactos ni corregido documentación
ajena para ocultar el resultado. El catálogo se regeneró, pero la verificación
documental continúa fallando por esos errores. `git diff --check` no detectó errores de whitespace.

Prueba real corta en `artifacts/longitudinal-smoke-live-v2/campaign/`: tres activaciones
completadas, 32 llamadas LLM, 29 herramientas y cero errores de captura. Se comprobaron
lecturas de la nota previa, escrituras posteriores y tres búsquedas Tavily con límite
histórico. En la activación temporal se observaron consultas e investigación sin nueva
orden ni comunicación explícita. La compra de 100 USD se ejecutó el 2023-01-02; el
cierre solicitado el 2023-03-01 se ejecutó el 2023-03-02. Al 2023-03-31 quedaron
100.000 USD, sin posiciones ni órdenes pendientes, como corresponde a precios constantes
sintéticos. Estas cifras no miden rentabilidad.

El primer intento real permanece en `artifacts/longitudinal-smoke-live-v1/`: A respondió,
pero una lectura de archivo ausente se clasificó como fallo de captura. No se presenta
como campaña completa. La segunda prueba conserva su propia identidad de fuentes; los
refuerzos posteriores de recuperación están verificados con transportes controlados.
Los archivos son locales y no se incorporan al Git del código. No hay revisión
independiente ni aceptación semántica general del baseline histórico.
