# Simplificación de main sin persistencia SQL

Fecha: 2026-10-24. Base Git: `736bd87` (`main`). Referencia del portado: `5b444e3`.
Cambios locales sin commit, adaptados selectivamente; sin merge ni cherry-pick.

## Cambio

Las campañas actuales pasan a `research_benchmarks`: catálogo, controlador,
extracción y compactación. La entrada es `python -m research_benchmarks`, con los
mismos comandos y opciones de main. Ambos paquetes siguen en la distribución
`research-agent`. Los nuevos manifiestos registran hashes de ambos con prefijo de
paquete; las salidas de campaña no pueden solaparse con ninguno de sus directorios.

La lectura compacta compartida vive en `research_agent.archive`, para que A recupere
artefactos sin importar campañas. Se conservan formato compacto y referencias
históricas, incluida la lectura de manifiestos nativos antiguos en inglés.
Los nuevos registros usan exclusivamente nombres españoles y captura propia.
Se retiran escenarios, pruebas y operación local de Experience Audit, sin modificar
el wheel compartido ni FinMate.

`AgentA.run` delega preparación y cierre a `_prepare` y `_finish`, manteniendo la
selección efectiva de prompts y el ciclo de main. Las herramientas declaran
modalidad de ejecución, conservación de materiales y disponibilidad en consolidación;
el registro prepara cada validador una vez. Las operaciones de archivos terminan
en línea. Clientes y fixtures repetidos se comparten en `tests/support.py`.

No se portan SQL, expedientes estructurados, modos experimentales, callbacks de
captura de conocimiento ni configuración de ejecución de feature/sql. Prompts,
límites, schemas expuestos, corpus, rúbricas y estrategia permanecen intactos.
La [arquitectura](../architecture.md#organización-del-código) y la
[operación](../development.md#campañas) describen el resultado.

## Verificación

- Base previa: `pytest -q tests`: 68 aprobadas y 2 fallos por referencias al catálogo
  ausente `pilot-v1`. La prueba específica de Audit se retira; las dos referencias
  obsoletas se adaptan a la suite existente `longitudinal-v1`.
- Regresión final: `pytest -q tests`: 76 aprobadas en 64,31 segundos.
  Se añaden siete casos sobre lectura nativa histórica, ejecución explícita,
  validación/materiales y protección de archivos y directorios fuente.
- Mypy sobre ambos paquetes: sin errores en 22 archivos.
- `pip check`: sin requisitos rotos. La instalación editable descubre el paquete
  nuevo sin reinstalación; setuptools incluye ambos paquetes en la distribución.
- `python -m research_benchmarks validate benchmarks/longitudinal-v1`: tres casos,
  18 sesiones; ayuda con `validate`, `run`, `extract` y `compact` disponible.
- Documentación: 29 Markdown, 487 enlaces locales, cero errores;
  `git diff --check` limpio.
- Comparación AST de las 13 llamadas de registro: nombres, descripciones, schemas y
  funciones intactos. Diff de prompts, contratos/límites, corpus y estrategia vacío.

La suite usa clientes y transportes simulados; cubre continuidad por procesos,
reservas de cierre, cancelación, captura incompleta, ejecución de herramientas,
validación, materiales, aislamiento, compactación y lectura histórica. La lectura
compacta se comprueba también en un proceso sin acceso a campañas ni Audit.

El comprobador documental detectó nueve enlaces previos al catálogo piloto retirado.
Su protocolo conserva las rutas como referencias históricas y explica cómo recuperar
el catálogo desde `22bcaa5`, sin restaurar ni modificar el corpus actual.

No se ejecutan campañas reales, llamadas a proveedores ni consultas remotas. Los
checks no miden rendimiento, calidad financiera ni aceptación semántica. No se hace
commit, push, actualización de wheel o cambio de estrategia.
