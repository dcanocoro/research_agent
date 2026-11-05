# Arquitectura implementada

> Referencia documental consolidada el 2026-10-31. Autoridad: código, schemas y
> configuración efectiva; el wheel instalado puede diferir de las fuentes de FinMate.

## Nota de continuidad opcional

`ContinuousConfig.context_note` (`--context-note`, solo con `--continuous`) activa
una llamada auxiliar de A antes de renovar. Sin la opción se conserva E2. El umbral
alto sigue siendo `consolidation_threshold_bytes`; una selección sucesora explícita
de Progress permite renovar desde el 60 % de ese umbral. La primera selección y los
resultados terminales no disparan ese evento; se consume una sola vez. Se comprueba
entre intercambios completos y el motivo por tamaño tiene prioridad.

Se conserva el checkpoint de persistencia y se resuelven integraciones antes de
pedir la nota. La llamada usa el transporte común, el contexto activo y ninguna
herramienta, con salida de hasta 5000 tokens y texto aceptado de hasta 40000 bytes UTF-8.
Cuenta como `context_note`, dentro del presupuesto de A, sin avanzar el compromiso.
Se mantienen cinco llamadas de reserva y la reserva temporal de finalización; no
se usa presupuesto protegido de B. Si no cabe, faltan recursos, la respuesta es
inválida o hay fallo recuperable, se reconstruye sin nota y sin reintento. Errores
terminales y cancelación mantienen sus causas.

La reconstrucción relee la semilla existente y agrega la nota como datos
provisionales, seguida de intercambios completos recientes mientras quepan. No
amplía la recuperación automática ni modifica conocimiento. La ventana se valida
antes de sustituirla; si la nota impide reconstruir, se vuelve a intentar sin ella.
Las notas no forman parte de los intercambios retenibles y no se acumulan.
`continuidad/nota-NNNN-input.json` y `nota-NNNN.json` registran entrada, respuesta o
causa de omisión. Eventos y trazas conservan motivo, tamaño, coste y resultado;
`conversacion-completa.jsonl` sigue capturando la conversación original. Estos
checks no certifican continuidad semántica. Véase la
[entrega](deliveries/2026-11-04-context-note.md).

La nota distingue lo persistido de lo pendiente, conserva cifras materiales no
guardadas con procedencia y documenta intentos fallidos y condiciones para volver
a intentarlos. La instrucción de uso, solo con la opción activa, orienta a recuperar
selectivamente, integrar pendientes y justificar repeticiones con una pregunta o
método que pueda aportar información. Se distinguen rutas del workspace y artefactos
de auditoría; no se amplían los contratos de herramientas. Son instrucciones a A,
no un detector determinista de redundancia ni una garantía de persistencia.

## Frontera y componentes

En `experiment/fileAgent`, B opcional integra encargos duraderos con contexto
preparado y presupuesto protegido. Solo existen `off` y `prepared`.
La [entrega actual](deliveries/2026-11-02-b-prepared-closing.md) describe alcance,
recuperación y límites. Se conserva el controlador E2 sin infraestructura de campañas.

B tiene 30 llamadas protegidas dentro de las 100 totales; A y controlador conservan
70. Cada intento reserva 15 llamadas, 24 herramientas y hasta 180 segundos. El
runtime inicia cierre con cuatro llamadas/herramientas o 60 segundos restantes,
protege 15 segundos para la declaración y restringe la última oportunidad a
`finish_integration`. Una respuesta textual solicita declaración y no cierra el
encargo. Agotamiento o fallo sin declaración válida conserva `pending` y recibos.
Incluso `pending` debe confirmar las versiones de todos los documentos publicados.

El paquete de hasta 64 KiB conserva mandato y encargo, petición original de A
(recortada explícitamente si excede la vista), contexto reciente de A al delegar,
agenda, índice, documentos afectados, evidencias y declaraciones/recibos previos.
La captura completa del contexto productor se archiva antes de ejecutar B y queda
recuperable mediante `read_artifact`; documentos y materiales mantienen hashes y
paginación. Los recortes no equivalen a cobertura semántica. Encargos históricos
sin captura de origen lo indican; no se reconstruye un contexto inexistente.
Las copias congeladas de prompts se conservan al continuar; el control de cierre
del runtime se aplica también a esas continuaciones.

A dispone de ciclo acotado y continuo opcional. Ambos usan el mismo agente y
registro de herramientas; sus presupuestos y formas de cierre son distintos.

A posee un ciclo modelo → herramienta → modelo → respuesta; B opcional reutiliza
su ejecución acotada con contexto y herramientas propios. No importa
`finmate`, `engine` ni `api`; Findata, Infra y los contratos comunes se consumen desde
el wheel instalado. Findata abre transacciones PostgreSQL de solo lectura, sin ingestas
ni migraciones. No hay motor DCF preimplementado, grafo obligatorio ni variantes A0–A3. La cartera ficticia existe solo
en el modo experimental de simulación, separado de Findata y del producto.

| Componente | Responsabilidad |
|---|---|
| [AgentA](../src/research_agent/agent.py) | Fachada pública y entrada al motor compartido |
| [Motor ReAct](../src/research_agent/core/execution.py) | Interacciones, herramientas, timeouts, bindings y finalización |
| [Workspace](../src/research_agent/storage/workspace.py) | Estado UTF-8 acotado y materiales originales |
| [ToolRegistry](../src/research_agent/core/tools.py) | Schemas, despacho, materiales y entrega paginada |
| [RunRecorder](../src/research_agent/observability/recording.py) | Manifest, eventos, respuesta y snapshots |
| [Directorios de experimentos](../src/research_agent/experiments/store.py) | Crear/continuar, bloqueo y observación de Git |
| [build_agent](../src/research_agent/composition/build.py) | Composición de A con las bibliotecas compartidas |
| [capture_traces](../src/research_agent/observability/tracing.py) | Logs y payloads locales del proveedor |

## Organización del código

El [mapa de módulos](modules.md) distingue núcleo, servicios compartidos, regímenes,
extensiones y capacidades. `AgentA.run` selecciona una política mediante composición;
`core.execution.execute` es el único bucle modelo/herramienta. El núcleo no importa
regímenes, extensiones, campañas ni adaptadores financieros. No hay descubrimiento de plugins.

La política acotada es predeterminada. `--continuous` selecciona E2, con revisión
general activada por defecto; `--general-review off` omite revisiones periódicas y
finales sin suprimir checkpoints, report_work, reconciliación, respuesta o renovación.
Progress conserva su evaluador y desactiva la revisión general. `--general-review on`
explícito con Progress se rechaza. El selector explícito requiere continuo.

`extensions/progress` contiene solo objetivos y compromisos vigentes. El evaluador
V8 de cobertura/distancia ha sido retirado. Sus formatos de objetivo siguen siendo
legibles: `assessment_path` se conserva como dato, sin activar revisión decisoria.
Los aliases antiguos no se mantienen; imports internos y consumidores usan rutas canónicas.

B preparado, deliberación y nota de continuidad viven en `extensions/`; estado,
aritmética, Findata, web, Python y simulación en `capabilities/`. Prompts y contratos
propios acompañan a su componente. Las copias congeladas conservan nombres y bytes.
`research_campaigns` es un paquete hermano, organizado en definiciones, ejecución e
informes; Research Agent no depende de él.

Los manifiestos registran selección solicitada y efectiva de revisión general,
además de extensiones y presupuestos. La identidad histórica `runtime.json` conserva
sus bytes; el selector nuevo se registra por run. Los fingerprints de código cambian
y las campañas preparadas siguen rechazando incompatibilidades. No se migran estados,
instrucciones congeladas ni evidencias anteriores. Véase la
[decisión de reorganización](decisions/0006-organizacion-y-revision-opcional.md).

Cada herramienta declara ejecución (`inline`, `thread`, `async`), conservación como
material y disponibilidad durante consolidación. Las escrituras de archivos siguen
en línea y con recuperación transaccional.

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

### Herramientas de estado

<a id="herramientas-de-estado-v5--2026-10-28"></a>

La [ablación E1](experiments/e1-simplificacion/protocol.md) deja una sola composición
del agente. `herramientas.json` conserva la identidad `state-tools-e1`, no un perfil
seleccionable. Los experimentos nuevos congelan `herramientas-estado.md`; las
continuaciones con contratos anteriores se rechazan sin migración automática.
La [operación](development.md#herramientas-de-estado) detalla compatibilidad.

[StateOperations](../src/research_agent/capabilities/state/operations.py) conserva inventario, mapas,
lecturas por bytes/líneas/sección y búsqueda contextual. Cada consulta vincula bytes
y hash; continuaciones vinculan argumentos y versiones. Secciones ATX fuera de código
y mapas no certifican cobertura semántica. Las lecturas continúan dentro de líneas
largas; búsquedas de hasta 50 coincidencias marcan extractos parciales.

Las vistas de empresa resuelven `empresas/<simbolo>/<dimension>.md`, para modelo,
valoracion y evaluacion. No crean documentos. Los IDs son localizadores; no hay motor
de dependencias ni validación financiera.

El [registro](../src/research_agent/capabilities/state/tools.py) declara schemas
cerrados, consultas con propósito y contratos opcionales. Las vistas se limitan a
32 KiB incluyendo envoltorio y su original queda recuperable. Se conservan las
restricciones por fase.

`record_research_advance` es la única escritura pública del agente. Crea o edita
con fragmentos exactos y hash vigente, en lotes recuperables de 1–5 archivos.
Valida todo antes de publicar, conserva diarios fuera del estado y restaura el lote
ante fallo; si falla recuperación detiene el run. No ofrece aislamiento frente a
editores externos. Un ancla vacía solo se admite sobre un archivo vacío.

Workspace conserva las primitivas internas de publicación y la política estructural
de documentos de empresa. La eliminación de herramientas no elimina validación de
IDs, cuerpos poblados, rutas, tamaños ni materiales protegidos. El registro marca
mutaciones, actualiza `files_written` y, ante fallo posterior de captura, devuelve
`applied=true` con recibos. No reintentar sin inspeccionar.

Los contratos, schemas, instrucciones y configuración efectiva quedan en los
manifiestos. Los consumidores de campañas usan la misma composición del agente;
el núcleo no los importa. El protocolo de E1 separa implementación de ejecución.

### Continuidad V6 — 2026-10-29

La [intervención V6](experiments/continuidad-v6/protocol.md) introdujo un investigador
con ReAct y herramientas V5. El agente actual conserva sus garantías sobre el contrato E1. No añade
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
cada edición ni sustituyen los diarios de escritura conjunta. No se reinyectan como memoria.

`research_campaigns progress` compara estos estados offline y conserva observaciones,
escrituras por fase, lecturas y comprobaciones numéricas explícitas con Decimal sobre
materiales capturados. Progreso, calidad, utilidad y recuperación requieren rúbrica:
el informe los deja `not_assessed`, sin puntuación única ni feedback al agente.
La [guía](development.md#continuidad-v6-y-evaluación-offline) explica uso y límites.

## Mandato persistente y agenda

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

`research_campaigns run DEFINICION --condition baseline|deliberative` congela condición y hash.
En deliberative escribe `agente/mandato.md` con mensajes auténticos hasta la fecha,
fuera del estado. Cada intento lo reconstruye desde el escenario; al reconocer su
captura contrasta el manifiesto con el mandato esperado y la agenda del checkpoint.
Campañas antiguas sin condición se interpretan como baseline, manteniendo los checks
de identidad. Las dos llamadas de consolidación y la respuesta final no cambian.

El [protocolo](experiments/intencion-persistente-v1/protocol.md) y la
[decisión experimental](decisions/0003-intencion-persistente.md) delimitan el piloto
y sus resultados posteriores; no acredita aceptación semántica.

## Instrucciones y especialización financiera

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
clientes controlados y usos posteriores de las instrucciones en campañas; el contraste
controlado específico y la aceptación semántica siguen pendientes. No cambia el baseline histórico.

La revisión coordinada del 2026-10-25 unifica los tres prompts en español y asigna un
propietario por responsabilidad: el general conserva rigor, recuperación selectiva,
guardado y límites; deliberación elige investigaciones y mantiene la agenda; el financiero
define metodología, ubicaciones y revisión de dependencias. Al cambiar una hipótesis
identificada exige consultar sus dependientes relevantes antes de dar por terminada la
actualización, revisándolos, justificando ausencia de impacto o marcando revisión pendiente.
`oportunidades.md` conserva comparaciones y `cartera.md` opcional conserva interpretación
de la asignación; las herramientas siguen siendo autoridad sobre posiciones y operaciones.
Son instrucciones al LLM, sin enforcement nuevo del runtime ni validación semántica.

## Herramientas y materiales

| Grupo | Herramientas |
|---|---|
| Archivos | `list_files`, `read_file`, `search_files` |
| Archivo de resultados | `read_artifact` |
| Findata | `search_companies`, `read_company`, `read_financials`, `read_metric_trend` |
| Web | `search_web`, `read_document` |
| Cálculo | `calculate` (aritmética determinista con referencias) |
| Estado | `inspect_state`, `read_state`, `search_state` |
| Empresa | `inspect_company`, `read_company_document` |
| Contratos | `describe_state_tools` |
| Escritura conjunta | `record_research_advance` |
| Python opcional | `describe_python_operator`, `run_python` |

El guardado admite Markdown, JSON válido, TXT y CSV UTF-8 hasta 128 KiB por archivo
y 8 KiB para agenda. Crea o edita por fragmentos con versión vigente. Lecturas paginadas hasta 32 KiB; búsquedas literales acotadas.
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

## Operadores Python opcionales

Desde el 2026-10-27, `build_agent(..., python_enabled=True)` o `--python` registra
`describe_python_operator` y `run_python` en el mismo registro, también con simulación.
Por defecto no están disponibles. En continuo E2 permanecen disponibles durante
el trabajo ordinario y checkpoints; los evaluadores no tienen herramientas.

La [integración](../src/research_agent/capabilities/python/tools.py) resuelve JSON/CSV
del workspace, valida código y contratos, captura la petición exacta y ejecuta el
[worker](../src/research_agent/capabilities/python/worker.py) asíncrono. Hay cuatro familias:
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

## Conservación y cierre de la investigación

Desde el 2026-10-21, el [prompt general](../src/research_agent/instructions/agent.md)
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

Consolidación ofrece solo lectura, búsqueda y escritura del estado.
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

## Ciclo continuo y presupuesto de contexto

Desde E2 (2026-11-01), el continuo ejecuta un único bucle ReAct con intervenciones.
`regimes/continuous/policy.py` aporta las decisiones al motor común;
`regimes/continuous/control.py` conserva estado operativo y reconciliación.
`regimes/continuous/context.py` reconstruye intercambios completos; la nota opcional
vive en `extensions/context_note/`. Los imports internos antiguos han sido retirados.
No hay selector del controlador anterior ni fases intelectuales. El modo acotado conserva
su cierre por consolidación/respuesta y sus restricciones anteriores.

`max_llm_calls` limita todas las llamadas gestionadas, incluidos checkpoints y evaluadores.
`llm_calls_by_phase` conserva su nombre por compatibilidad, con propósitos `researcher`,
`checkpoint`, `evaluator`. Los eventos conservan `phase` como alias de propósito para
lectores históricos; no selecciona herramientas. Reintentos internos del proveedor
siguen en las trazas y no se convierten en llamadas adicionales del controlador.

Los límites opcionales de herramientas y tiempo, la cancelación, las versiones y las
transacciones siguen siendo obligatorios. El timeout por operación permanece finito.
El contador usa JSON UTF-8, margen del 10 % y ocho bytes por token máximo de salida:
es una heurística local, no una garantía sobre la ventana remota. Máximo/umbral por
defecto: 524288/262144 bytes; `consolidation_threshold_bytes` conserva el nombre Python
histórico, pero representa renovación. CLI: `--renewal-bytes`, con alias obsoleto.

La reconstrucción intenta dejar 16 KiB de margen para la siguiente interacción.
La renovación incorpora mandato, petición, agenda, fundamentos, feedback del mecanismo
activo y cola de intercambios completos. No corta continuaciones opacas ni repite
herramientas. Si hay integración pendiente/desconocida o texto sin tratamiento declarado,
ofrece hasta dos llamadas ordinarias con todas las herramientas. Después renueva,
conservando pendientes recuperables y sin certificar continuidad semántica. El texto
del investigador también se archiva como referencia recuperable de integración desconocida. El límite
duro puede adelantar la renovación; si la base/intercambio imprescindible no cabe,
se registra fallo explícito. Los resultados grandes mantienen original y lectura paginada.

`conversacion-completa.jsonl` conserva cada item; `runtime/estado.json` guarda atómicamente
referencias, declaraciones, versiones, contadores y deduplicación fuera del conocimiento.
Los extractos de pendientes incluyen referencia a un artefacto completo recuperable.
Una continuación recupera estado compatible del mismo workspace/mandato, verifica versiones
y abre un nuevo presupuesto; no restaura todo el chat. El archivo y las listas de captura
no tienen un límite global de almacenamiento.

Los experimentos nuevos congelan `runtime.json` con política e instrucción exactas;
continuar en E2 exige identidad compatible. Experimentos anteriores requieren código
anterior o migración autorizada. `herramientas.json` sigue identificando escritura E1.
La referencia anterior es Git `690313ced9c6311512f5623a90c20521bca458b2`.

## Autorrevisión periódica

E2 sustituye experimentalmente la revisión fija del investigador cada diez llamadas.
La [decisión histórica](decisions/0004-revision-periodica.md) conserva sus condiciones;
el [protocolo E2](experiments/e2-intervenciones/protocol.md) define el cambio autorizado.

Con revisión general activada, la evaluación independiente responde a hitos,
bloqueos o repetición posterior a un aviso. Agrupa señales, separa intentos por cinco
llamadas del investigador y tiene respaldo a veinte. El evaluador no escribe conocimiento.
Fallos consumen presupuesto, quedan capturados y no provocan reintentos inmediatos.
Las observaciones operativas y de reconciliación tienen un máximo conjunto de 8 KiB
por interacción, además de los avisos operativos existentes, y se deduplican por contenido
versionado; no certifican progreso ni obligan a adoptar un juicio.

`report_work`, solo durante continuo, comunica hitos/bloqueos y tratamiento de referencias:
pendiente, integrado o irrelevante. Exige motivo, referencias existentes y hashes actuales
para integración; no edita conocimiento ni valida semántica. Una escritura cualquiera no
resuelve pendientes. Cambios posteriores invalidan declaraciones vinculadas a versiones
anteriores. Sin grafo, las contradicciones económicas dependen del investigador/evaluador.

Durante las últimas cinco llamadas se entrega una orientación de cierre; la última se
reserva a evaluación final cuando la revisión está activa; con revisión apagada se usa
para una respuesta textual sin herramientas. Con presupuesto inicial de una llamada se prioriza al investigador.
El cierre por herramientas puede evaluar si quedan llamadas y tiempo. No se evalúa tras
cancelación/fallo/agotamiento temporal. `call_limit` continúa siendo interrupción, no éxito.

## Revisión externa y escritura conjunta

El continuo ordinario usa el revisor general salvo `--general-review off`. Progress
usa su evaluador por compromisos y desactiva el general. Cada mecanismo conserva su
política de activación y comparte el presupuesto total del run. Los informes de revisión
general tienen identificadores únicos por intento y un archivo final separado.

El mismo cliente/perfil revisa secuencialmente un paquete separado (64 KiB), sin
herramientas ni conversación del investigador. Recibe mandato, agenda, estados,
acciones y evidencia referenciada con recortes explícitos. JSON inválido, herramientas
o timeout producen informe fallido sin reintento. El feedback (8 KiB) es observación,
no autoridad; solo A modifica conocimiento. Informes e inputs viven fuera del estado,
en `revision-externa/` del run. El cierre no sustituye `respuesta.md` ni acredita
cumplimiento del mandato. La siguiente ejecución gestionada puede recuperar el último
informe final completo del mismo workspace como referencia histórica.

La agenda distingue investigación longitudinal y resultado revisable de sesión.
La semilla recupera hasta dos referencias Markdown explícitas del foco (8 KiB de
contenido, IDs opcionales), con versión y parcialidad, sin recorrido recursivo.
El registro efectivo define las herramientas disponibles para el investigador. Los avisos mecánicos
son informativos y no certifican progreso ni fuerzan escrituras o prioridades.

`record_research_advance` conserva 1–5 cambios conjuntos. Prevalida formatos, versiones
y protecciones actuales, guarda un diario fuera del estado y publica atómicamente por
archivo. Ante fallo restaura; al arrancar recupera diarios pendientes. No hay atomicidad
visible a lectores externos: un conflicto con una edición externa detiene sin borrarla.
Un fallo de recuperación es fatal, no un error de herramienta ordinario. Los recibos y
la captura identifican todos los archivos incluso si falla el archivado posterior.

La [entrega V7](deliveries/2026-10-30-v7.md) registra alcance y verificación.

## Progreso por compromisos

Desde el 2026-11-03, `--progress` compone un decorador de política con el ReAct
acotado o continuo. `objective.py` conserva el objetivo fijo; `evaluator.py` construye
una vista acotada y valida una evaluación semántica; `policy.py` selecciona y
verifica compromisos. No hay otro bucle, proveedor ni despacho de herramientas.
El [protocolo](experiments/progress/protocol.md) fija el contraste pendiente.

Cada tramo tiene hasta 15 llamadas de A; objetivo generado, evaluaciones y cierre
consumen el presupuesto total, 100 llamadas por defecto en CLI. En continuo se
conservan renovación, checkpoints y avisos técnicos, sustituyendo las revisiones
semánticas periódicas. Sin progress, E2 y B conservan su comportamiento.

`progreso/estado.json` de cada run guarda atómicamente el objetivo, última evaluación,
alternativas y hasta 20 compromisos recientes. Las entradas y respuestas de cada
evaluación quedan archivadas por separado. Continuar recupera el último estado del
mismo workspace y reevalúa; una revisión explícita del objetivo inicia otra serie.
No se duplican documentos financieros. Las referencias verifican existencia y
versión, no validez económica. Las omisiones y vistas parciales se declaran.

<a id="objetivos-y-evaluación-de-cobertura"></a>

## Objetivos y evaluación de cobertura V8 (histórico)

El mecanismo siguiente fue sustituido por Progress y su implementación se retiró el
2026-11-05. Este apartado conserva el contrato histórico, no módulos ni comportamiento
vigentes. Sus formatos de objetivo y capturas permanecen legibles para auditoría, sin
selección activa ni migración automática. `assessment_path` ya no activa su evaluación.

`AgentRequest.objective: Objective | None` añade un objetivo fijo al continuo. El
contrato y cálculo viven en `experiments/progress/objectives`; el paquete y recuperación
en `objective_review` del mismo ámbito. Las señales de evaluación pertenecen a progreso
y el régimen continuo solicita su ejecución al motor. El objetivo es externo al estado,
inmutable durante el run y congelado con hash en manifiesto. Sin objetivo se mantiene
el revisor general; con objetivo se sustituye por evaluación de criterios según la política E2.

El evaluador comparte cliente/perfil y deadline, con contexto separado y sin herramientas.
Sus llamadas consumen el mismo techo total que el investigador. Un paquete
de 64 KiB reserva espacio para fuentes antes de acciones; recortes, versiones y omisiones
quedan explícitos. No es una garantía de suficiencia de fuentes ni validación económica.
La respuesta por criterios distingue cubierto, no cubierto y no evaluable. Solo una
evaluación completa actualiza distancia y variación frente a la última completa válida.

El feedback acotado orienta pendientes, reaperturas, reconsideración tras tres evaluaciones
no decrecientes y síntesis al alcanzar cero, sin imponer acciones ni terminar el continuo.
Fallos, parcialidad y omisiones interrumpen estancamiento; se conserva la última cobertura
completa por separado. El cierre por recursos puede evaluar o reutilizar una evaluación
solo si el paquete completo coincide exactamente, sin llamadas tras fallo, cancelación o deadline.

`evaluacion-objetivo/` conserva inputs, respuestas, métricas y referencias por run fuera
del workspace editable. Renovaciones recuperan feedback; continuaciones gestionadas
solo recuperan cobertura histórica del mismo workspace y hash. Cambiar criterios inicia
otra serie. La [operación](development.md#operación-v8) y el
[protocolo](experiments/objetivos-v8/protocol.md) detallan contratos, captura y límites.

### Dirección hacia una evaluación decisoria

El encargo posterior del 2026-10-31 añade `Objective.assessment_path`, opcional y
externo al estado: ruta Markdown relativa del resultado revisable. Sin ese campo
se conserva el hash de definiciones anteriores. La semilla incluye una vista actual
versionada de hasta 4 KiB; se actualiza cuando cambia el documento y se recupera tras
renovar. Su ausencia es explícita: el runtime no crea una plantilla ni escribe juicios.
La instrucción por llamada con objetivo orienta a resolver impedimentos materiales
para decidir, distinguiendo evidencia, cálculo e interpretación con lo disponible.

El evaluador añade `decision_review`: utilidad para decidir, impedimentos identificados
y clasificados con impacto y referencias, IDs resueltos y revisión de la adaptación.
Se exige para objetivos con `assessment_path`; los informes anteriores siguen siendo
legibles. La distancia binaria permanece auxiliar. El investigador elige el método;
ante estancamiento explicita qué cambió y qué resultado espera, y se revisa después.
La última revisión estructuralmente válida, incluso parcial, se conserva separada de
la última distancia completa, también tras fallos y continuaciones. El paquete del
evaluador prioriza hasta 16 KiB de la evaluación activa dentro del máximo de 64 KiB;
las vistas del contexto investigador siguen acotadas a 4 KiB.

Todas las escrituras de `agenda.md` se prevalidan con máximo de 8192 bytes UTF-8,
también en operaciones conjuntas: se rechaza antes de publicar ningún cambio. No se
recorta estado previo automáticamente. La reconstrucción valida la semilla efectiva
y el intercambio imprescindible antes de sustituir la ventana activa.
El [protocolo de Microsoft](experiments/evaluacion-msft-v1/protocol.md) posee la campaña
autorizada, cuya pregunta ha fijado literalmente el usuario.

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
