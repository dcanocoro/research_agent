# Instalar en otro ordenador

Ruta reproducible verificada: **Windows x86-64 y CPython 3.12.6**. El proyecto
declara Python >=3.11, pero esta comprobación no certifica otras versiones,
Linux, macOS o ARM. Es una aplicación CLI local; no requiere servidor HTTP,
Docker, frontend ni el checkout de FinMate para ejecutarse.

El [lock](../requirements-windows-py312.lock) fija versiones y SHA-256 de las
91 distribuciones necesarias para ejecución, pruebas y construcción. Incluye
el wheel privado `findata`, psycopg 3 binario y tzdata. No reutilizar la `.venv`
de otro ordenador: contiene rutas propias. `constraints.txt` conserva el corte
histórico y no sustituye este lock.

## Qué necesitas trasladar

- Este repositorio en una revisión identificada, incluidos prompts, benchmarks,
  pruebas, lock y `.env.example`. Los cambios sin commit deben trasladarse también.
- El wheel aprobado `findata-0.1.0-py3-none-any.whl`, con SHA-256
  `70cd4a370e1ca4690631f104291a7cc3281acbf6972e43b3c14cb18fe7662e4f`.
  Es el artefacto utilizado en la verificación, no cualquier wheel llamado `0.1.0`.
  Su ubicación original es
  `../FinMate/artifacts/experience-audit-validation/relocation-2026-10-16/wheels/`.
  Conservar una copia junto al paquete de traslado: esa ruta es local e ignorada.
- Python 3.12 de 64 bits; Git para los checks que prueban versionado manual.
- Para investigación real: acceso al proveedor LLM, claves propias y, en perfil
  `live`, Tavily y PostgreSQL ya poblado. No se traslada la base de datos mediante
  estos comandos. Las claves se configuran por separado, fuera de Git.

El código de las bibliotecas comunes permanece en FinMate. No hay que instalar
un paquete homónimo desde un índice público. Reconstruir el wheel desde otras
fuentes puede cambiar su contenido: exige revisar hash, lock y pruebas.

## Preparar los archivos instalables

En una máquina con conexión, desde la raíz del repositorio, usando PowerShell.
En cada paso comprobar que el comando terminó con código 0 antes de continuar.
Utilizar una carpeta nueva para evitar mezclar wheels de entregas diferentes:

```powershell
py -3.12 -m venv .venv
$raPython = (Resolve-Path .venv/Scripts/python.exe).Path
$raWheels = "artifacts/traslado/wheels"
New-Item -ItemType Directory -Path $raWheels
# Sustituir ORIGEN por la carpeta que contiene el wheel aprobado.
Copy-Item "ORIGEN/findata-0.1.0-py3-none-any.whl" $raWheels
Get-FileHash "$raWheels/findata-0.1.0-py3-none-any.whl" -Algorithm SHA256
& $raPython -m pip download --only-binary=:all: --require-hashes --find-links $raWheels -r requirements-windows-py312.lock --dest $raWheels
& $raPython -m pip install --no-index --find-links $raWheels --require-hashes -r requirements-windows-py312.lock
& $raPython -m pip wheel --no-deps --no-build-isolation --wheel-dir $raWheels .
Get-FileHash "$raWheels/research_agent-0.1.0-py3-none-any.whl" -Algorithm SHA256
```

Conservar el SHA-256 del wheel de Research Agent junto a la revisión Git y el lock.
Su hash cambia cuando cambia el código o el artefacto de construcción; no está
incluido en el lock de dependencias. Los hashes de dependencias se comprueban al
descargar e instalar. No quitar `--require-hashes` para superar un fallo.
Si falta una descarga, obtener el artefacto aprobado o revisar explícitamente la
dependencia; no sustituir versiones silenciosamente.

Trasladar el repositorio y `artifacts/traslado/wheels/` completos. Este último
directorio no viaja al clonar Git: debe copiarse por separado. La carpeta generada
solo contiene wheels públicos y el código compartido/local; no incluir `.env`,
la `.venv`, estados ni trazas privadas en ese paquete de instalación.

## Instalar en destino, sin acceder a índices

Desde la raíz de la copia recibida, con una `.venv` nueva:

```powershell
py -3.12 -m venv .venv
$raPython = (Resolve-Path .venv/Scripts/python.exe).Path
$raWheels = "artifacts/traslado/wheels"
# Comparar con el hash registrado al preparar el paquete.
Get-FileHash "$raWheels/research_agent-0.1.0-py3-none-any.whl" -Algorithm SHA256
& $raPython -m pip install --no-index --find-links $raWheels --require-hashes -r requirements-windows-py312.lock
& $raPython -m pip install --no-index --no-deps "$raWheels/research_agent-0.1.0-py3-none-any.whl"
& $raPython -m pip check
& $raPython -m research_agent --help
& $raPython -m research_benchmarks validate benchmarks/longitudinal-v2-1
& $raPython -m pytest -q tests
```

Esta instalación usa el wheel, no el código editable. Para desarrollar después,
instalar explícitamente con `pip install --no-deps --no-build-isolation -e .`.
No hacerlo para comprobar que el wheel es autónomo.

## Configurar y operar

Copiar `.env.example` a `.env` **solo si este no existe**, editarlo con credenciales
propias y elegir proveedor/modelo accesibles en esa cuenta. El ejemplo recoge
los nombres efectivos del wheel aprobado; no comprueba disponibilidad del modelo.
La aplicación lee `.env` desde el directorio de trabajo. Ejecutar desde la raíz
configurada o proporcionar variables de entorno; no depende del checkout original.

En perfil `live`, usar `postgresql+psycopg://...` para el controlador incluido.
Las credenciales, host, SSL, permisos y datos se preparan en destino. SQLite no
sustituye Findata. No ejecutar migraciones ni ingestas para probar la instalación.
`closed-corpus` no necesita PostgreSQL/Tavily, pero una investigación real sigue
necesitando el proveedor LLM. Los checks anteriores son offline y no lo llaman.

Los [comandos de ejecución y continuación](development.md#ejecutar-a-nuevo-experimento-o-continuación)
usan `--experiment`, `--new`/`--continue` y `--run-name`. Para trasladar una
investigación existente, detener sus procesos y copiar **toda** la carpeta del
experimento, incluidos materiales, instrucciones, `experimento.json` si existe,
`conocimiento/` si existe y ejecuciones. Conservar su Git si se utiliza. Copiar
solo `respuesta.md` no permite continuar el conocimiento. Revisar datos privados
antes de transferirlos; el archivo de auditoría es distinto del código instalable.

## Alcance comprobado

La [verificación fechada](deliveries/2026-10-22-portability.md) distingue instalación,
pruebas y servicios. Reproducir las dependencias y el mecanismo no congela respuestas
del modelo, páginas web ni datos financieros. El cierre final en otro ordenador
requiere repetir los checks allí y comprobar sus credenciales/conectividad durante
una ejecución real autorizada. No se ha probado hardware distinto en esta entrega.
