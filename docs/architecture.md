# Arquitectura implementada

> Estado local a 2026-10-18. Autoridad: código, schemas y wheel instalado.

## Frontera y componentes

A posee un único ciclo modelo → herramienta → modelo → respuesta. No importa
`finmate`, `engine` ni `api`; Findata, Infra y los contratos comunes se consumen desde
el wheel instalado. Findata abre transacciones PostgreSQL de solo lectura, sin ingestas
ni migraciones. No hay DCF, cartera, grafo obligatorio ni variantes A0–A3.

| Componente | Responsabilidad |
|---|---|
| [AgentA](../src/research_agent/agent.py) | Contexto, replay del proveedor, presupuestos y cierre |
| [Workspace](../src/research_agent/workspace.py) | Estado UTF-8 acotado y materiales originales |
| [ToolRegistry](../src/research_agent/tools.py) | Schemas, despacho, materiales y entrega paginada |
| [RunRecorder](../src/research_agent/recording.py) | Manifest, eventos, respuesta y snapshots |
| [Experimentos](../src/research_agent/experiments.py) | Crear/continuar, bloqueo y observación de Git |
| [build_agent](../src/research_agent/bootstrap.py) | Composición de A con las bibliotecas compartidas |
| [capture_traces](../src/research_agent/tracing.py) | Logs y payloads locales del proveedor |

## Estado, instrucciones y ejecuciones

Cada experimento CLI tiene su propio estado y puede recibir varios runs:

```text
experimento/
  instrucciones/
    agente.md
    investigacion-financiera.md
  estado/
    indice.md
    evaluacion.md
    materiales/
      2026-10-18-inicial-01-read-document.json
  ejecuciones/
    2026-10-18-inicial/
      peticion.md
      respuesta.md
      manifiesto.json
      resultado.json
      conversacion.json
      eventos.jsonl
      estado-inicial.json
      estado-final.json
      git-final.json
      trazas/
        modelo-0001.json.gz
```

La profundidad máxima de carpetas es tres desde la raíz del experimento, sin contar
los internos de Git. Evaluación y pendientes son nombres sugeridos, no una plantilla.
Los nombres de runs son humanos, con fecha local y sufijo consecutivo ante colisiones;
los IDs técnicos permanecen dentro de los registros. La fecha de los nombres utiliza
`Europe/Madrid` en el código actual.

Hay tres estados distintos: archivos persistentes, contexto transitorio de A y evidencia
de ejecución. Solo `indice.md` se carga automáticamente, hasta 8 KiB, con continuación
explícita; el resto se consulta bajo demanda. La CLI crea una instancia nueva por run:
continuar reutiliza archivos, sin restaurar el chat. Audit conserva su instancia entre
mensajes del escenario y mantiene su organización propia, compatible con su wheel.

Las instrucciones CLI son copias editables de los prompts al crear el experimento;
los runs usan esas copias, conservando texto y hashes efectivos en el manifiesto.
Las fuentes y archivos del estado son datos, nunca instrucciones de desarrollo.
Un bloqueo de proceso excluye runs simultáneos del mismo experimento y se libera al
morir el proceso. El archivo `.run.lock` no debe borrarse para resolver contención.

## Herramientas y materiales

| Grupo | Herramientas |
|---|---|
| Archivos | `list_files`, `read_file`, `search_files`, `write_file` |
| Compatibilidad | `write_markdown`, `read_artifact` |
| Findata | `search_companies`, `read_company`, `read_financials`, `read_metric_trend` |
| Web | `search_web`, `read_document` |
| Cálculo | `calculate` (aritmética determinista con referencias) |

`write_file` admite Markdown, JSON válido, TXT y CSV UTF-8 hasta 128 KiB. Reemplaza
atómicamente cada archivo. Lecturas paginadas hasta 32 KiB; búsquedas literales acotadas.
No se permite escapar del estado, acceder a rutas ocultas, streams de Windows,
enlaces o junctions, escribir formatos ejecutables o sobrescribir `materiales/`.
Estas comprobaciones no son un sandbox frente a procesos externos concurrentes.

Las siete herramientas de Findata/web/cálculo conservan automáticamente cada resultado
satisfactorio completo en `materiales/`, con nombres por run, secuencia y herramienta.
El contenido mantiene el schema y metadatos originales, incluidas ausencias y recortes.
El registro asocia argumentos, herramienta, hash y productor. Errores quedan en las trazas.
Cada resultado de esas siete herramientas devuelve `material_ref` y el alias `artifact_ref`; referencias relativas
al estado permiten continuar después de trasladar el experimento. Los resultados grandes
no se truncan en disco: se entregan referencias para leerlos por páginas.

Los resultados de herramientas de archivos y otras operaciones permanecen en el archivo
de ejecución; `read_artifact` es un adaptador para materiales y resultados archivados.
Las referencias del archivo técnico siguen acotadas al workspace del run; para continuidad
portable deben usarse los materiales. Guardar un resultado no incorpora su interpretación
a una evaluación, ni una cita certifica inferencias o comparabilidad numérica.

## Conservación y cierre de la investigación

Con los defaults hay 18 llamadas al cliente, 30 herramientas, 300 segundos y 256 KiB
de contexto serializado. Son máximos, no una obligación de completar 18 turnos.
Cada llamada al modelo puede pedir una herramienta o devolver texto para terminar.
Los resultados se añaden al historial; si superan 32 KiB se incorpora una referencia
para recuperarlos por páginas. Se reservan hasta dos llamadas de consolidación y una de respuesta.
Consolidación se adelanta cuando quedan 45 segundos, dos herramientas o 32 KiB de contexto
(como máximo un cuarto en límites pequeños). Se conserva la corrección temporal de E002:
al entrar antes por llamadas/contexto puede usar el tiempo restante salvo la reserva de
respuesta, sin imponer un tope fijo prematuro de 15 segundos.

Consolidación ofrece solo lectura, búsqueda y escritura del estado, incluidos los aliases.
Una escritura no fuerza el cierre; una respuesta sin escritura es válida. No se exige
publicar ni modificar una evaluación para resolver una consulta breve. Con presupuestos
menores de cuatro llamadas o dos herramientas se conserva el cierre básico con respuesta
reservada, sin intentar la fase adicional de consolidación. Los eventos registran recursos,
fases, timeout y fallos; el replay del proveedor permanece completo.

`AgentResult.state` contiene `files_written`, `materials` y `capture_errors`. No significa
completitud del conocimiento ni aceptación financiera. `completed` indica respuesta obtenida;
fallo, cancelación e interrupción conservan los archivos y capturas disponibles.

`respuesta.md` guarda automáticamente la entrega; no actualiza el estado. Los snapshots
conservan contenidos iniciales/finales de los cuatro formatos, con errores identificados.
No reconstruyen cada edición intermedia. El archivo se mantiene fuera del alcance de
escritura del agente. CLI agrupa eventos del ciclo y payloads del proveedor dentro del run;
Audit mantiene su captura externa existente. No ejecutar capturas simultáneas en un proceso,
porque el adaptador compartido emplea configuración global temporal.

El benchmark consolida esa captura **después de ejecutar**: cada sesión conserva
`ejecucion.json`, `trayectoria.jsonl.gz`, respuesta y dos snapshots. La trayectoria
reúne eventos, payloads del modelo y herramientas; distingue resultado original y
resultado entregado, conservando argumentos y escrituras intermedias. Los materiales
se referencian por ruta/hash en lugar de repetirse en los snapshots. Las referencias
históricas `archivo/run/resultado-herramienta-N.json` siguen funcionando mediante
`read_artifact`, con la misma comprobación de identidad del workspace. No modifica
las decisiones de A ni sus límites. Capturas incompletas se conservan en formato nativo.
La [operación](development.md#benchmark-piloto) explica lectura y exportación sin proveedor.

## Git manual e interfaces

Git es una herramienta humana para versionar estado e instrucciones, separada del Git
del código. Se registra commit y cambios iniciales/finales solo si el experimento tiene
repositorio propio; sin `.git` propio se indica ausencia, aunque exista un padre Git.
No se ejecuta init, add, commit, checkout, reset, push ni creación de ramas.
Las capturas inicial/final permiten auditar runs realizados con cambios sin commit.

`build_agent(workspace, runs, limits)` mantiene el contrato de Audit; los argumentos
opcionales `experiment` y `run_name` sirven al organizador CLI. Los nombres de archivos
técnicos del consumidor básico permanecen compatibles. CLI usa la organización española.
La operación y los comandos están en [desarrollo](development.md). El
[baseline](baseline.md) distingue capacidad implementada, resultado observado y
aceptación semántica pendiente.

## Modo experimental de expedientes

El modo `cases`, `CaseStore`, sus herramientas y su contrato de publicación se retiraron
al adoptar el estado de archivos. No hay migración automática. Los protocolos y resultados
históricos de [E001](experiments/README.md#antecedentes-e001-y-e002) y
[E002](experiments/README.md#antecedentes-e001-y-e002) describen el candidato ejecutado
entonces. Sus documentos ya no están en el árbol actual; el
[registro histórico](experiments/README.md#antecedentes-e001-y-e002) indica su recuperación desde Git. La [decisión](decisions/0001-estado-por-experimento.md)
registra el cambio local, sin elegir la arquitectura final de FinMate.
