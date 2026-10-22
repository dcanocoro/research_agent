# Portabilidad e instalación reproducible

Fecha: 2026-10-22. Base Git: `5b444e3`; cambios locales sin commit.

## Cambio y contrato

La copia del repositorio dependía de un wheel privado situado en otro checkout,
constraints incompletas y configuración local sin plantilla. Se añade la
[guía de traslado](../installation.md), `.env.example` sin secretos y
`requirements-windows-py312.lock`: 91 distribuciones con versiones y hashes,
incluidas las herramientas de desarrollo y construcción. La instalación en destino
usa exclusivamente wheels locales con `--no-index`; las dependencias se verifican
con `--require-hashes`. El wheel de Research Agent se identifica por su propio hash.

No se modifica el ciclo del agente, sus prompts, herramientas, datos financieros,
FinMate ni las bibliotecas compartidas. Tampoco se altera la `.venv` habitual ni `.env`.

La suite inicial detectó cuatro fallos preexistentes: pruebas que aún requerían
`longitudinal-v1`, `longitudinal-v2` y `argumentative-continuity-v1`, retirados en
`5b444e3`. Se actualizan al catálogo vigente `longitudinal-v2-1`, conservando
validación sin servicios, 18 sesiones simuladas, presupuestos y propagación del
perfil. La antigua comparación de copias de catálogos se sustituye por los controles
de la suite vigente; no demuestra igualdad con las definiciones históricas.
Los protocolos históricos identifican cómo recuperar sus archivos desde `c75dd01`;
la documentación operativa usa comandos del catálogo disponible.

## Evidencia de instalación

Entorno nuevo en `artifacts/portability/clean-env/`, Windows x86-64, CPython 3.12.6.
Dependencias descargadas como wheels y reinstaladas sin índice, con hashes.
Research Agent construido e instalado como wheel, sin editable. Los comandos de
ejecución y pytest se lanzan desde `artifacts/portability/relocated/`, sin `.env`.
Las pruebas leen definiciones del checkout; los imports del agente y benchmark
apuntan a `clean-env/Lib/site-packages/`, no a `src/`.

- Wheel compartido: `findata-0.1.0-py3-none-any.whl`, SHA-256
  `70cd4a370e1ca4690631f104291a7cc3281acbf6972e43b3c14cb18fe7662e4f`.
- Wheel del agente: `research_agent-0.1.0-py3-none-any.whl`, SHA-256
  `174531aaf9ef662004b22f77ce8ab333b1f19239346bf0e8a668a9a4e57e2f2d`.
- `pip check`: sin dependencias rotas. Descarga offline completa a una segunda
  carpeta mediante el lock y `--require-hashes`: correcta.
- CLI `--help`, catálogo v2.1 (3 casos/18 sesiones), los tres prompts empaquetados
  y zona `Europe/Madrid`: correctos.
- Composición `live` con URL PostgreSQL/psycopg, imports Tavily y respuesta simulada:
  correcta, sin ejecutar herramientas remotas ni conectar a la base de datos.
- Mypy: sin errores en 23 archivos de ambos paquetes.

Primera suite: 96 aprobadas y cuatro fallidas por los catálogos retirados. Tras
corregir las referencias: **100 aprobadas en 100,29 segundos**, con el wheel
instalado y sin `.env` en el directorio de trabajo. Incluye continuación en procesos
nuevos, traslado de estado y frontera sin imports del producto.

Documentación: 38 Markdown, 521 enlaces locales, cero errores; `git diff --check`
sin errores de whitespace. Se prepara además un paquete local en
`artifacts/portability/research-agent-windows-py312.zip`, con fuentes, documentación,
pruebas, lock, plantilla y wheels. `paquete.json` identifica los archivos y sus
SHA-256; no incorpora la configuración privada del ordenador ni su entorno virtual.
El ZIP no incluye historia Git: para consultas históricas, conservar el repositorio.

## Límites

Es una instalación limpia en el mismo ordenador, no una prueba física en otro equipo.
No se comprueban Linux/macOS/ARM ni otras versiones de Python. El lock fija los
artefactos seleccionados para Windows/Python 3.12, no todas las plataformas declaradas
por el proyecto. Las capturas y wheels locales de `artifacts/` están ignorados;
deben copiarse expresamente si se quieren trasladar. La guía y el lock sí forman
parte de los cambios revisables del repositorio.

No se llama a proveedores ni a PostgreSQL remoto. Credenciales, conectividad,
permisos, disponibilidad del modelo y datos deben comprobarse en destino. No se
ejecutan campañas financieras ni se establece aceptación semántica. Reproducibilidad
del software no implica respuestas idénticas ni datos externos congelados.
