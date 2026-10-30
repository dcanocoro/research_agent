# Arquitectura implementada

> Estado local a 2026-10-24. Autoridad: código, schemas y wheel instalado.

## Frontera y componentes

Desde el 2026-10-26 existe además el [modo continuo opcional](experiments/contexto-continuo-v1/protocol.md).
La descripción del ciclo acotado siguiente conserva su contrato por defecto.

A posee un único ciclo modelo → herramienta → modelo → respuesta. No importa
`finmate`, `engine` ni `api`; Findata, Infra y los contratos comunes se consumen desde
el wheel instalado. Findata abre transacciones PostgreSQL de solo lectura, sin ingestas
ni migraciones. No hay motor DCF preimplementado, grafo obligatorio ni variantes A0–A3. La cartera ficticia existe solo
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

## Operadores Python opcionales

Desde el 2026-10-27, `build_agent(..., python_enabled=True)` o `--python` registra
`describe_python_operator` y `run_python` en el mismo registro, también con simulación.
Por defecto no están disponibles. No cambian las fases: ambas se excluyen de
consolidación y las revisiones permanecen sin herramientas.

La [integración](../src/research_agent/integrations/python_tools.py) resuelve JSON/CSV
del workspace, valida código y contratos, captura la petición exacta y ejecuta el
[worker](../src/research_agent/python_worker.py) asíncrono. Hay cuatro familias:
calculate, transform, evaluate y model; estas dos últimas exigen respectivamente
criterios y supuestos como objetos no vacíos. Los contratos detallados se empaquetan
como recursos recuperables bajo demanda; no existe otro registro de herramientas.

La interfaz de herramienta transmite `inputs_json`, `input_refs_json` y
`parameters_json` como textos de objetos JSON, que el runtime valida y decodifica.
Así admite claves libres sin schemas de objetos abiertos incompatibles con el
`strict=True` del adaptador OpenAI instalado. `run(inputs, parameters)` recibe
diccionarios normales; el wheel compartido no se cambia.

Cada ejecución usa un proceso local desechable, entorno mínimo y directorio temporal.
En Windows se lanza directamente el intérprete base con las bibliotecas del entorno
actual para evitar un launcher intermedio; no se procesan sus archivos `.pth`.
El worker no importa A, Infra, Findata, Audit ni campañas. Solo recibe datos resueltos.
NumPy, pandas, SciPy y numpy-financial son dependencias opcionales. La política y
versiones efectivas quedan en `configuration.python_operators` del manifiesto y en
la captura de cada cálculo.

Los filtros AST/builtins/APIs previenen usos accidentales; **no constituyen aislamiento
de seguridad**. No hay límite duro de memoria. Límites: código 32 KiB UTF-8, entradas
y parámetros resueltos 1 MiB, salida 1 MiB, stderr 16 KiB y 30 segundos incluyendo
arranque. Las tuberías se consumen con límites; ante error, timeout o cancelación se
termina y espera el proceso antes de cerrar el run. El código generado no tiene APIs
admitidas para archivos, red, procesos, paquetes o acceso a servicios.

`execution_ref` permite recuperar código, entradas exactas, parámetros y entorno
mediante `read_artifact`. Eventos `lab.python.prepared/completed/failed` enlazan los
intentos; las salidas exitosas son materiales originales y usan la paginación habitual.
No se añaden archivos `.py` al estado ni un registro de funciones reutilizables.
Un DCF generado puede ejecutarse, sin que ello valide su metodología o supuestos.
El [protocolo](experiments/python-operators-v1/protocol.md) separa comprobación local
y evaluación semántica pendiente.

[research_campaigns](../src/research_campaigns/cli.py) posee definiciones, campañas
y revisión en la misma distribución. Depende de A; A no importa campañas ni Audit.
Las campañas conservan la captura nativa de cada ejecución; no hay conversión compacta
ni lectores de los formatos retirados. La [guía de campañas](campaigns.md) describe
el registro único, las modalidades y la recuperación.

## Estado, instrucciones y ejecuciones

### Continuidad V6 — 2026-10-29

La [intervención V6](experiments/continuidad-v6/protocol.md) mantiene un investigador,
ReAct y el perfil de herramientas `v5`, con contratos `state-tools-v6.1`. No añade
supervisores LLM. Nuevos experimentos deliberativos reciben una agenda con prioridades,
investigación activa, aplazadas y decisiones. Sus copias de instrucciones definen el
mantenimiento; continuaciones no reescriben agendas o instrucciones existentes.

`context_seed` incorpora la agenda una sola vez y un localizador de su sección activa,
derivado por ATX. Agenda antigua o ambigua: foco no disponible, sin inventarlo ni migrarlo.
La ausencia de índice es explícita. No se cargan automáticamente expedientes. La
consolidación guarda lo aún pendiente; la revisión sin herramientas reevalúa progreso
y puede orientar actualizaciones en la continuación ordinaria, sin llamadas nuevas.

`StateOperations` instala en Workspace una política de escritura de expedientes:
todos los escritores de esa composición pasan los mismos checks antes de publicar.
Rechaza IDs eliminados o duplicados y vaciado de cuerpos antes poblados, usando los
mismos límites de sección que la lectura. Devuelve secciones afectadas acotadas y
advertencias sobre IDs vacíos y referencias locales literales. Permite referencias
futuras; no comprueba semántica, unidades en prosa ni validez de `source_refs`.
Workspace sin la composición V5 y editores externos no tienen esa política de dominio.

El continuo guarda `continuidad/estado-NNNN.json` e índice al inicio, revisión,
renovación y cierre. Texto exacto/CRLF y hashes del conocimiento, fase y contadores;
los materiales permanecen en sus capturas originales. La política efectiva está en
manifiesto y campaña; errores se incorporan a `capture_errors`. No son versiones de
cada edición ni transacciones multiarchivo. No se reinyectan como memoria.

`research_campaigns progress` compara estos estados offline y conserva observaciones,
escrituras por fase, lecturas y comprobaciones numéricas explícitas con Decimal sobre
materiales capturados. Progreso, calidad, utilidad y recuperación requieren rúbrica:
el informe los deja `not_assessed`, sin puntuación única ni feedback al agente.
La [guía](development.md#continuidad-v6-y-evaluación-offline) explica uso y límites.

### Herramientas de estado V5 — 2026-10-28

Los experimentos nuevos incorporan el perfil `v5` en `herramientas.json`, fuera de
`estado/`, y una guía congelada en sus instrucciones. Los existentes sin configuración
conservan `legacy`. La API directa mantiene `legacy` por defecto; la CLI resuelve el
perfil del experimento. La [guía de desarrollo](development.md#herramientas-de-estado-v5)
explica creación y adopción explícita.

[StateOperations](../src/research_agent/state_tools.py) implementa vistas deterministas
sobre Workspace: inventario/mapa, lectura por bytes/líneas/sección, búsqueda contextual,
creación exclusiva y edición exacta. Cada consulta usa bytes y hash de la misma lectura;
las continuaciones vinculan argumentos y versiones. Las secciones reconocen encabezados
ATX fuera de código cercado; los mapas no certifican cobertura semántica. Las lecturas
pueden continuar dentro de una línea larga. Las búsquedas se ordenan por ruta/línea,
con hasta 50 coincidencias y contextos largos explícitamente parciales.

Las nuevas mutaciones y las escrituras anteriores comparten un bloqueo por raíz dentro
del proceso. Crear publica un temporal mediante enlace duro sin reemplazo; editar valida
todas las sustituciones/inserciones en memoria y comprueba de nuevo el hash antes de
reemplazar. Sigue sin haber CAS frente a editores externos ni transacciones multiarchivo.
Las herramientas antiguas conservan sus schemas y permiten reemplazo sin versión.

La capa de empresa resuelve exclusivamente `empresas/<simbolo>/<dimension>.md` para
modelo, valoracion y evaluacion. Orienta, recupera y crea/revisa una dimensión; no crea
las otras automáticamente. Los IDs iniciales de encabezados son localizadores y los
duplicados se informan. La edición específica preserva los IDs reconocidos, pero no
puede comprobar su significado. No hay motor de dependencias ni validación financiera.

[El registro V5](../src/research_agent/integrations/state_tools.py) declara schemas
cerrados, campos condicionales nullables y propósito obligatorio. Las operaciones se
admiten en consolidación; la revisión periódica continúa sin herramientas. Cada resultado
nuevo, incluido el envoltorio, se limita a 32 KiB; vistas paginadas reservan espacio para
metadatos y escapado. El original de la respuesta se conserva como artefacto recuperable.

El registro identifica mutaciones mediante metadata, incluyendo los escritores previos.
Actualiza `files_written` antes de capturar; si falla la captura posterior informa
`applied=true` con el recibo de versión. Reintentar exige inspeccionar el estado real.
Los contratos empaquetados se consultan opcionalmente con `describe_state_tools` y sus
textos/versiones/hashes se conservan en el manifiesto. Las continuaciones registran y
anuncian cambios respecto al run anterior del mismo workspace. No hay almacén nuevo
de versiones ni restauración automática de cada edición.

El cálculo inicial de presupuesto de `research_campaigns` registra el mismo perfil
efectivo y las campañas congelan su configuración. La aceptación local y los límites
se conservan en la [entrega](deliveries/2026-10-28-state-tools-v5.md).

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

Las campañas conservan esa captura nativa y generan un `README.md` con enlaces a
respuestas, snapshots, eventos y trazas. `campaign.json` concentra el control y los
diagnósticos. No se compacta ni transforma la evidencia al cerrar. Las referencias
`archivo/run/resultado-herramienta-N.json` se leen desde sus archivos nativos con
comprobación de identidad del workspace. La [guía de campañas](campaigns.md)
explica las modalidades, revisión y límites de recuperación.

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

`research_campaigns` congela escenario, instrucciones, perfil y dataset
obtenido en solo lectura; ejecuta procesos nuevos y posee calendario/checkpoints.
El simulador reside fuera del workspace editable. La memoria no es el registro económico.
La [decisión](decisions/0002-simulacion-longitudinal.md) y el
[protocolo](experiments/colaboracion-historica-v1/protocol.md) fijan disponibilidad
estimada, límites de cartera y recuperación; el [baseline previo](baseline.md) se conserva.

## Condición experimental de intención persistente

`AgentRequest.mandate`, opcional y añadido al final del contrato, activa la condición
deliberativa. La CLI lo recibe mediante `--mandate PATH`, fuera de estado y ejecuciones.
`prepare_experiment(deliberative=True)` copia `deliberacion.md` y crea `estado/agenda.md`
con la plantilla compacta V6. Las continuaciones exigen ambos y el mandato; no migran instrucciones antiguas.

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

## Metodología financiera y selección de instrucciones — 2026-10-25

Los prompts nuevos por defecto incorporan análisis económico acumulativo y la
convención `empresas/<simbolo>/modelo.md`, `valoracion.md` y `evaluacion.md`: ubicación
obligatoria al desarrollar una evaluación con continuidad prevista, contenido progresivo.
No se crean documentos por anticipado ni se exige un expediente para consultas breves.
Las hipótesis importantes tienen IDs locales; las referencias entre documentos usan
ruta e ID. La revisión de dependencias la realiza A mediante lectura y búsqueda, sin
parser ni propagación automática. Índice, agenda, materiales y recuperación selectiva
mantienen sus contratos; no se carga automáticamente el conjunto de empresas.

El prompt general conserva el núcleo general y remite a la especialización. El
financiero permite estimaciones justificadas mediante la aritmética existente con
resultados conservados, sin atribuir un motor DCF ni capacidades nuevas. La agenda
relaciona preguntas, fundamentos, bloqueos y siguientes acciones sin imponer workflow.

`prepare_experiment(..., instructions_dir=...)` permite sustituir el conjunto inicial
completo solo al crear un experimento, sin instrucciones adicionales simultáneas. El
controlador longitudinal expone `run --instructions-dir`; valida nombres canónicos,
contenido UTF-8 no vacío y ausencia de entradas adicionales antes de construir clientes.
Las copias efectivas quedan congeladas con los hashes existentes. Las continuaciones
manuales conservan sus copias; `resume` rechaza cambios y no acepta otro conjunto.

El [protocolo financiero](experiments/analisis-financiero-v1/protocol.md) prepara control
e intervención bajo la misma condición deliberativa. Hay verificación mecánica con
clientes controlados; no campaña ni aceptación semántica. No cambia el baseline histórico.

La revisión coordinada del 2026-10-25 unifica los tres prompts en español y asigna un
propietario por responsabilidad: el general conserva rigor, recuperación selectiva,
guardado y límites; deliberación elige investigaciones y mantiene la agenda; el financiero
define metodología, ubicaciones y revisión de dependencias. Al cambiar una hipótesis
identificada exige consultar sus dependientes relevantes antes de dar por terminada la
actualización, revisándolos, justificando ausencia de impacto o marcando revisión pendiente.
`oportunidades.md` conserva comparaciones y `cartera.md` opcional conserva interpretación
de la asignación; las herramientas siguen siendo autoridad sobre posiciones y operaciones.
Son instrucciones al LLM, sin enforcement nuevo del runtime ni validación semántica.

## Modo continuo experimental — 2026-10-26

`AgentRequest.continuous: ContinuousConfig | None` activa el mismo A con un ciclo
renovable implementado en `research_agent.continuous`. Requiere mandato explícito.
`None` mantiene el ciclo y los límites anteriores. No añade agentes ni planificador.
El presupuesto opcional de llamadas ordinarias, herramientas y duración se define en
`ContinuousConfig`; `AgentLimits.timeout_seconds` conserva el timeout finito por operación,
sin imponer sus otros máximos al modo continuo.

Las respuestas son registros intermedios. El runtime añade una continuación técnica
mediante `ConversationContext`, separada de las peticiones humanas. El calendario no
avanza: las órdenes simuladas permanecen pendientes. El modo no introduce espera autónoma.

`context_budget.ByteCounter` mide los bytes UTF-8 de la representación JSON tipada
que contiene instrucciones, historial, herramientas y continuaciones opacas. No requiere
mapping de modelo, tiktoken ni descarga de tablas. El presupuesto es
`ceil(input_bytes * 1.10) + max_output_tokens * 8`: el factor de salida es una reserva
heurística en bytes, no una conversión garantizada entre bytes y tokens. La salida
máxima del proveedor sigue expresada en tokens. Los eventos distinguen `input_bytes`,
`reserved_output_bytes` y `budgeted_bytes`; el consumo real disponible sigue en las
trazas del proveedor, sin inventar valores ausentes.

`ContinuousConfig.max_context_bytes` vale 524288 por defecto y
`consolidation_threshold_bytes` 262144; ambos comparan el presupuesto con margen y
reserva, no solo el texto. Son límites locales de tamaño, no una garantía de caber en
la ventana remota. El piloto usa umbral 196608 y verifica que la semilla protegida
quepa antes de preparar el comando. Las opciones antiguas en tokens se rechazan;
las capturas históricas conservan sus unidades originales.

Al llegar al umbral se ofrecen hasta cuatro llamadas de consolidación con herramientas
de persistencia. Cada una descuenta recursos globales. Después se reconstruye con
instrucciones, mandato, petición inicial, fecha/metadatos, índice, agenda y presupuesto
actual. No se conserva cola ni se genera otro resumen. Escrituras opcionales. Los
errores devueltos por herramientas se entregan al modelo igual que en investigación:
no terminan la ejecución ni reinician el presupuesto. A puede corregir argumentos o
elegir otra operación con las llamadas restantes. Al responder o agotar las cuatro
llamadas se reconstruye, también si hubo errores o no se escribió; esto no acredita
que el conocimiento haya quedado conservado. Los límites globales, cancelación,
timeouts y fallos operativos siguen teniendo sus motivos de cierre. Se rechazan arranques o
reconstrucciones cuyo contexto protegido no quepa. La entrega de un resultado se compara
con el máximo de contexto, en ambas fases; superar solo el umbral conserva el contenido
y activa consolidación en la siguiente iteración. Un resultado que exceda el máximo se
entrega por referencia paginable conservando el original; nunca se elimina una llamada aislada
ni se corta una continuación. Si el intercambio no cabe, se pausa sin enviarlo.

`conversacion-completa.jsonl` conserva incrementalmente cada item por número de contexto;
los resultados originales están en los artefactos referenciados. `conversacion.json`
conserva solo la ventana activa al cerrar. Los eventos registran método/versiones,
presupuestos, renovaciones, archivos modificados y causas de pausa. El manifiesto conserva
configuración continua y no declara la política de cierre acotada. Las capturas del
proveedor y snapshots mantienen su formato. Las salidas intermedias se registran en eventos;
`respuesta.md`, cuando existe, conserva la última, sin significar encargo completado.

Errores/cancelación cierran el proceso con evidencia disponible. La continuación explícita
arranca desde archivos y simulador actuales, con nuevo presupuesto por ejecución; no
restaura chat ni repite operaciones. Un cierre abrupto no garantiza que lo no escrito
en memoria se pueda recuperar. La ventana está acotada; el volumen del archivo y las
listas de captura/eventos en memoria de proceso no tienen un límite total en esta versión.

El piloto de [contexto continuo](experiments/contexto-continuo-v1/protocol.md) se prepara
sin clientes ni bases durante las comprobaciones de `research_campaigns`. Congela mandato, instrucciones,
perfil, fuentes instaladas, dataset y estado nuevo, y comprueba las condiciones antes del lanzamiento integrado. En simulación, `allow_web: false`
omite `search_web`; su ausencia conserva el comportamiento anterior con web.

## Revisión periódica permanente — 2026-10-27

Toda ejecución continua realiza una llamada de revisión sin herramientas después de
cada diez llamadas de investigación, si queda presupuesto ordinario para actuar.
La frecuencia y la instrucción viven en `continuous.py`, sin interruptor ni opciones
nuevas. El mismo modelo recibe el contexto activo y el aviso técnico en español;
su elección breve se incorpora al historial. El harness no elige la investigación,
no escribe una reflexión en el estado ni sustituye `answer` o `respuesta.md` con ella.
La siguiente llamada ordinaria puede actuar o conservar lo que el modelo considere útil.

`ContinuousConfig.max_llm_calls` y `--max-calls` limitan investigación más
consolidación; las revisiones son adicionales. `AgentResult.llm_calls` sigue siendo
el total real intentado. `llm_calls_by_phase` distingue `research`, `consolidation`
y `review`; su valor vacío por defecto conserva la construcción anterior del contrato.
El contexto técnico distingue total consumido, desglose, límite ordinario y restante.
El tiempo global, el timeout por operación y los límites de bytes también cubren
la revisión. No hay llamadas adicionales después de alcanzar un límite de parada.

La consolidación técnica tiene prioridad sobre una revisión pendiente; esta se realiza
tras reconstruir, antes de retomar la investigación. El contador sobrevive a las
reconstrucciones y se reinicia en cada run. Un fallo o timeout conserva las capturas
y detiene el ciclo. Una herramienta inesperada durante revisión no se ejecuta y pausa
con `review_tools_disabled`; un timeout usa `review_timeout`. Una respuesta vacía permite
continuar sin inventar una decisión. La revisión usa la reserva de salida habitual.

El manifiesto registra `review_policy`, incluidos texto, frecuencia y presupuesto.
Los eventos `lab.model.started`/`lab.model.finished` asocian fase, índice correlativo
y duración de cada llamada al cliente. `trazas/events.jsonl` incorpora esa fase e
índice también a los intentos del proveedor dentro de la llamada, conservando sus
IDs, duración, consumo y referencias a payloads originales. Consumo ausente no es cero.
La lectura y el informe de campañas muestran total y desglose; resultados históricos
sin desglose se presentan como desconocidos. El ciclo acotado no cambia.

La [decisión](decisions/0004-revision-periodica.md) conserva la elección permanente;
el [protocolo](experiments/contexto-continuo-v1/protocol.md#v4--revisión-periódica-permanente)
separa la verificación mecánica de la futura observación semántica.
