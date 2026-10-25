# Arquitectura implementada

> Estado local a 2026-10-24. Autoridad: código, schemas y wheel instalado.

## Frontera y componentes

A posee un único ciclo modelo → herramienta → modelo → respuesta. No importa
`finmate`, `engine` ni `api`; Findata, Infra y los contratos comunes se consumen desde
el wheel instalado. Findata abre transacciones PostgreSQL de solo lectura, sin ingestas
ni migraciones. No hay DCF, grafo obligatorio ni variantes A0–A3. La cartera ficticia existe solo
en el modo experimental de simulación, separado de Findata y del producto.

| Componente | Responsabilidad |
|---|---|
| [AgentA](../src/research_agent/agent.py) | Contexto, replay del proveedor, presupuestos y cierre |
| [Workspace](../src/research_agent/workspace.py) | Estado UTF-8 acotado y materiales originales |
| [ToolRegistry](../src/research_agent/tools.py) | Schemas, despacho, materiales y entrega paginada |
| [RunRecorder](../src/research_agent/recording.py) | Manifest, eventos, respuesta y snapshots |
| [Experimentos](../src/research_agent/experiments.py) | Crear/continuar, bloqueo y observación de Git |
| [build_agent](../src/research_agent/bootstrap.py) | Composición de A con las bibliotecas compartidas |
| [capture_traces](../src/research_agent/tracing.py) | Logs y payloads locales del proveedor |

## Organización del código

`research_agent` posee el ciclo y la captura. `AgentA.run` delega preparación y cierre
en `_prepare` y `_finish`. Cada herramienta declara ejecución (`inline`, `thread`,
`async`), conservación como material y disponibilidad durante consolidación; su
validador se construye al registrarla. Las operaciones de archivos se ejecutan en
línea para evitar escrituras en hilos después de cerrar un run.

[research_benchmarks](../src/research_benchmarks/runner.py) posee catálogo, campañas,
extracción y compactación, en la misma distribución. Depende de A; A no importa
campañas ni Audit. [archive](../src/research_agent/archive.py) contiene la lectura
compacta compartida, incluida la recuperación de artefactos históricos. Los nuevos
manifiestos de campaña registran hashes de ambos paquetes con prefijo de paquete.

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
de ejecución. En baseline solo `indice.md` se carga automáticamente, hasta 8 KiB, con continuación
explícita; el resto se consulta bajo demanda. La CLI crea una instancia nueva por run:
continuar reutiliza archivos, sin restaurar el chat. La integración local con
Experience Audit se ha retirado; no se mantiene su contrato de ejecución externa.

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

Desde el 2026-10-21, el [prompt general](../src/research_agent/prompts/agent_a.md)
incorpora M1 como evolución de A: recuperar la evaluación anterior, clasificar la novedad,
contrastar fundamentos y revisar solo lo justificado. Recomienda conservar juicio vigente,
fundamentos y evidencia, incertidumbres, condiciones de revisión e historial breve de cambios
materiales en los archivos existentes, localizables desde `indice.md`. Separa hipótesis de
evaluación factual y marca información superada; permite no escribir ante ruido o redundancia.
No impone schema, nombres de archivos ni puntuaciones. Es una instrucción de comportamiento,
no una garantía validada por el runtime ni evidencia de mejora semántica. No añade M2.
Las copias de instrucciones de experimentos ya creados conservan su texto anterior; véase
[continuación](development.md#ejecutar-a-nuevo-experimento-o-continuación).

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
escritura del agente. Todas las ejecuciones agrupan eventos del ciclo y payloads del proveedor dentro del run,
con nombres españoles. No ejecutar capturas simultáneas en un proceso,
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

`build_agent(workspace, runs, limits)` permite componer A directamente; los argumentos
opcionales `experiment` y `run_name` sirven al organizador CLI. La captura utiliza
siempre el mismo formato propio, también en las construcciones directas de pruebas.
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

## Simulación longitudinal opcional

`research_agent.simulation` posee reloj por activación, herramientas históricas,
cartera local y comunicaciones explícitas. `build_agent(simulation=...)` sustituye
las lecturas actuales y Extract por las herramientas acotadas; no abre conexión a
Findata durante las activaciones. Sin ese argumento la composición es la habitual.

`research_benchmarks.longitudinal` congela escenario, instrucciones, perfil y dataset
obtenido en solo lectura; ejecuta procesos nuevos y posee calendario/checkpoints.
El simulador reside fuera del workspace editable. La memoria no es el registro económico.
La [decisión](decisions/0002-simulacion-longitudinal.md) y el
[protocolo](experiments/colaboracion-historica-v1/protocol.md) fijan disponibilidad
estimada, límites de cartera y recuperación; el [baseline previo](baseline.md) se conserva.

## Condición experimental de intención persistente

`AgentRequest.mandate`, opcional y añadido al final del contrato, activa la condición
deliberativa. La CLI lo recibe mediante `--mandate PATH`, fuera de estado y ejecuciones.
`prepare_experiment(deliberative=True)` copia `deliberacion.md` y crea `estado/agenda.md`
vacío. Las continuaciones exigen ambos y el mandato; no migran instrucciones antiguas.

El mandato auténtico se entrega como mensaje de usuario separado; la agenda se entrega
como `ConversationContext.deliberative_agenda`, memoria revisable sin autoridad.
Se conservan el índice y las herramientas de recuperación. Mandato no vacío: hasta
16 KiB UTF-8; agenda: hasta 8 KiB, vacía permitida. Se rechazan ausencias, UTF-8 inválido
y excesos antes de llamar al modelo, sin truncamiento. El manifiesto registra `condition`
y `persistent_context` con texto/hash de mandato y agenda inicial. La API directa
valida el contexto; sin experimento gestionado añade la guía deliberativa del paquete
si no se proporcionó una copia. En un experimento gestionado exige la copia explícita.

`longitudinal run --condition baseline|deliberative` congela condición y hash.
En deliberative escribe `agente/mandato.md` con mensajes auténticos hasta la fecha,
fuera del estado. Cada intento lo reconstruye desde el escenario; al reconocer su
captura contrasta el manifiesto con el mandato esperado y la agenda del checkpoint.
Campañas antiguas sin condición se interpretan como baseline, manteniendo los checks
de identidad. Las dos llamadas de consolidación y la respuesta final no cambian.

El [protocolo](experiments/intencion-persistente-v1/protocol.md) y la
[decisión experimental](decisions/0003-intencion-persistente.md) delimitan el piloto
preparado, sin campaña real ni aceptación semántica.
