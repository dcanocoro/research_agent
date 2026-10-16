# Desarrollo y operación

> Estado: uso del proyecto externo, revisado el 2026-10-16.

## Arranque y configuración

Empezar por [dependencias](dependencies.md) para crear el entorno. Los ejemplos siguientes
se ejecutan desde la raíz de Research Agent con su `.venv` y configuración local.
No modificar fuentes de FinMate para una consulta ni ejecutar migraciones para arrancar A.

```powershell
.\.venv\Scripts\python.exe -m research_agent "Investiga NVIDIA: fundamentos, riesgos y límites de los datos, sin DCF" --workspace ./artifacts/workspace --runs ./artifacts/runs
```

La CLI imprime la respuesta y `run_id`; devuelve 0 cuando el estado es `completed`,
1 para otros estados operativos y 2 ante determinados errores de entrada.
Revisar `result.json` y el motivo de cierre, no solo el código de salida.
`--timeout-seconds` cambia el presupuesto temporal. `--instructions archivo.md` puede
repetirse y añade instrucciones a las incluidas. No sirve para seleccionar el futuro A0.

Workspace y archivo de ejecuciones deben ser disjuntos y estar fuera del código/prompts.
La memoria Markdown persiste; el historial del proceso CLI no. Actualizar el índice
permite descubrir las notas en la siguiente intervención; no carga automáticamente
todos los informes. Véanse las tres clases de estado en [arquitectura](architecture.md).

## Campañas nativas de Experience Audit

Usar `lab`, no el atajo del runner de recorridos del producto:

```powershell
$auditRoot = Join-Path $PWD.Path "artifacts/audit"
.\.venv\Scripts\python.exe -m experience_audit lab ./scenarios --output $auditRoot
```

El comando ejecuta todos los YAML/YML del directorio con IDs únicos. Para seleccionar
un subconjunto, preparar un directorio con esas definiciones y sus instrucciones.
Las intervenciones son secuenciales; no iniciar capturas concurrentes dentro del mismo
proceso. No se arranca frontend, backend, navegador ni sesión de usuario del producto.

El runner conserva `run.json` y archiva evidencia con `execution_kind=lab`, diferenciada
de las campañas históricas del producto. Los fallos y estados incompletos también son
evidencia. No asumir que el comando `resume` del producto restaura una conversación de A.

### Contrato del escenario

| Campo | Contenido |
|---|---|
| `schema_version` | `lab-v1` |
| `id`, `title` | Identidad única y descripción |
| `messages` | Una o varias intervenciones ordenadas |
| `instructions` | Rutas opcionales a Markdown dentro del directorio de escenarios |
| `memory` | Mapa opcional de rutas Markdown y contenido inicial |
| `requirements` | `llm`, `postgresql`, `tavily`; por defecto `llm` |
| `limits` | Ajustes de `AgentLimits` para esa condición |
| `checks` | Lista de comprobaciones deterministas |

Ejemplo mínimo que usa el modelo configurado, sin exigir datos financieros:

```yaml
schema_version: lab-v1
id: lab_revision_example
title: Revisión de una conclusión sintética
requirements: [llm]
memory:
  memory/index.md: "Caso ficticio; consulta notes/source.md."
  notes/source.md: "Beneficio 20, de los cuales 12 son extraordinarios."
messages:
  - Lee la nota y explica qué permite concluir sobre el beneficio recurrente.
checks:
  - {id: finished, kind: completed}
  - {id: source_read, kind: tool_used, value: read_file}
```

`requirements` declara preflight, no desactiva herramientas ni añade credenciales.
LLM/Tavily comprueban presencia de claves, no disponibilidad real del proveedor.
PostgreSQL comprueba una lectura mínima; no garantiza cobertura suficiente de datos.

Checks disponibles: `completed`, `answer_contains`, `tool_used`, `file_contains`.
`step` selecciona intervención desde 1. `file_contains` consulta el workspace final;
no acredita por sí solo el contenido histórico de un paso. Una cadena vacía comprueba
legibilidad del archivo, no calidad de memoria. Los checks de texto son literales;
una cita correcta, una revisión bien razonada o un análisis financiero necesitan otra revisión.

### Consultar y exportar

Reutilizar la ruta **absoluta** de salida en estos comandos. En la biblioteca actual,
algunos comandos de archivo resuelven rutas relativas desde la instalación de Audit,
mientras `lab` las resuelve desde el directorio de trabajo. Especificar solo la misma
cadena relativa puede abrir otro archivo.

```powershell
$auditRoot = Join-Path $PWD.Path "artifacts/audit"
.\.venv\Scripts\python.exe -m experience_audit history --output $auditRoot
.\.venv\Scripts\python.exe -m experience_audit show ID_DE_EJECUCION --full --output $auditRoot
.\.venv\Scripts\python.exe -m experience_audit export ID_DE_EJECUCION --format json --full --output $auditRoot --destination ./artifacts/export.json
.\.venv\Scripts\python.exe -m experience_audit report RUTA_AL_RUN_JSON
```

Sustituir los marcadores por el ID de una ejecución archivada y la ruta devuelta por
`lab`. El informe genera resumen y `dashboard.html`, que se abre localmente. El lanzador
`ui` de campañas del producto no es la entrada visual de este laboratorio.

Conservar el archivo completo, no solo el dashboard o una copia de la respuesta.
Las definiciones, snapshots, herramientas y payloads permiten investigar qué ocurrió.
La captura refleja interacciones observables; no proporciona todo el razonamiento
privado del modelo. Antes de exportar fuera de la máquina, revisar datos privados.
Los comandos de limpieza pueden eliminar detalle o ejecuciones: no son mantenimiento
necesario para investigar y no deben borrar tentativas incómodas de una comparación.

## Verificación proporcionada al cambio

| Cambio | Verificación esperada |
|---|---|
| Solo documentación | Contrastar afirmaciones, enlaces, ejemplos y `git diff --check` |
| Ciclo, memoria o herramientas | Tests locales afectados y regresión de fronteras |
| Contrato compartido | Pruebas de sus consumidores en FinMate, wheel nuevo y regresión local |
| Proveedor o acceso a datos | Primero transportes controlados; después aceptación real autorizada y archivada |
| Hipótesis financiera | Campaña y revisión semántica con rúbrica previa, además de checks |

Comandos de comprobación local sin campaña real:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe -m mypy src/research_agent --follow-imports=silent
.\.venv\Scripts\python.exe -m pip check
git diff --check
```

La suite incluye subprocess que bloquea imports de `finmate`, `engine` y `api`.
El proyecto no tiene el comprobador documental ni catálogo de FinMate: comprobar
enlaces de README, AGENTS y `docs/` aquí. Si también cambia documentación de FinMate,
ejecutar allí su propio flujo documental; no copiar el catálogo al laboratorio.

Un cambio documental no necesita llamadas a modelos o PostgreSQL. Tampoco acredita
aceptación financiera. No confundir un resultado histórico enlazado con una prueba
repetida en el entorno actual. Registrar qué se comprobó y qué quedó fuera.

## Entrega y continuidad

Actualizar la referencia propietaria y el índice cuando cambie el mapa. Las entregas
en `docs/deliveries/` indican fecha, base, cambio, verificaciones, límites y siguiente
paso. Las propuestas experimentales permanecen en [experimentos](experiments.md).

No versionar `.env`, payloads privados, bases locales ni workspaces reales. `artifacts/`
está ignorado; citar una ruta allí no hace portable la evidencia. Las guías pueden
describir el procedimiento, mientras las capturas completas se conservan localmente.
No realizar commit, push o despliegue sin autorización del usuario.
