# V5: herramientas de estado y expedientes de empresa

Actualización de implementación del 2026-10-28: el plan posterior fue aprobado para
implementar V1 con pruebas locales. La [entrega](../../deliveries/2026-10-28-state-tools-v5.md)
y la [arquitectura](../../architecture.md#herramientas-de-estado-v5--2026-10-28)
describen el resultado efectivo. El texto siguiente conserva la propuesta documental
original, incluidas sus alternativas y límites de autorización de aquel encargo.

Fecha: 2026-10-28. Estado: documento de contexto y propuesta para aterrizar el diseño
contra el código. No es una implementación, un protocolo de campaña cerrado ni una
decisión arquitectónica aceptada para FinMate.

## 1. Encargo y propósito

Mejorar el instrumental de A para construir, recuperar y revisar conocimiento
acumulativo. El alcance comprende tanto el estado general como los expedientes de
empresa: no basta con facilitar la escritura de archivos ni con realizar cálculos
en Python. Las herramientas deben ayudar a desarrollar y mantener el análisis,
acompañadas de instrucciones, contratos y ejemplos recuperables.

El usuario pide preparar este documento antes de implementar. Recoge la propuesta V5
del 27 de octubre y las aclaraciones posteriores: operaciones sobre archivos o con
propósitos específicos; elección intencional de herramientas; calidad del contenido
que vuelve al contexto; y soporte específico para construir expedientes de empresa.
No autoriza ejecutar una campaña, cambiar FinMate ni modificar el ciclo ReAct.

El objetivo no es producir más documentos: es que el agente pueda conservar y revisar
qué sabe, con qué fundamento, qué supone, qué calcula y qué sigue sin resolver. El
expediente forma parte del estado persistente; no requiere un almacén paralelo.

La [visión](../../purpose.md), la [estrategia](../../strategy.md) y la
[arquitectura](../../architecture.md) siguen delimitando el laboratorio. Este encargo
documental no reescribe esas decisiones ni convierte la propuesta original V5 en una
lista de fases autorizadas para ejecución.

## 2. Punto de partida comprobado en el código

### 2.1. Propietarios y recorrido

| Fuente actual | Responsabilidad y consecuencia para el diseño |
|---|---|
| [bootstrap.py](../../../src/research_agent/bootstrap.py) | Compone el registro efectivo; comparte archivos entre modos normal e histórico y añade Python opcionalmente. |
| [file_tools.py](../../../src/research_agent/integrations/file_tools.py) | Registra lectura, búsqueda, escritura, recuperación de artefactos y aritmética. Las herramientas de archivos están habilitadas durante consolidación. |
| [workspace.py](../../../src/research_agent/workspace.py) | Posee rutas, texto UTF-8, búsqueda literal, escritura atómica y protección de materiales originales. |
| [tools.py](../../../src/research_agent/tools.py) | Valida schemas, despacha, captura resultados y crea materiales cuando corresponde; construye el payload entregado al modelo. |
| [recording.py](../../../src/research_agent/recording.py) | Conserva resultados originales, eventos y snapshots; recupera artefactos con comprobación de identidad del workspace. |
| [continuous.py](../../../src/research_agent/continuous.py) | Controla consolidación, reconstrucción y presupuesto de contexto; puede entregar una referencia si el resultado excede el máximo. |
| [experiments.py](../../../src/research_agent/experiments.py) | Separa instrucciones, estado y ejecuciones; copia prompts y bloquea ejecuciones simultáneas del experimento gestionado. |
| [financial_research.md](../../../src/research_agent/prompts/financial_research.md) | Define metodología, documentos por empresa, IDs y revisión de consecuencias. |
| [python_tools.py](../../../src/research_agent/integrations/python_tools.py) | Ejecutor programable y contratos consultables opcionalmente: precedente instrumental. |

Recorrido actual: el modelo recibe schemas y elige una herramienta; el registro valida
argumentos y ejecuta; conserva el resultado y, según configuración, un material original;
entrega un `ToolResult`; el modelo lo interpreta y decide la siguiente acción. El diseño
debe intervenir en las operaciones y en su entrega, conservando este recorrido.

### 2.2. Estado general

| Operación existente | Contrato y límites actuales | Carencia a abordar |
|---|---|---|
| `list_files` | Ruta; devuelve rutas y si son directorios. | Falta orientación por tamaño, estructura documental y paginación. |
| `read_file` | Ruta, offset y máximo de bytes; devuelve texto y siguiente offset, hasta 32 KiB por ventana. | No devuelve hash ni selectores de líneas/secciones. |
| `search_files` | Consulta literal y ruta; coincidencias con línea y texto, hasta 50. | Falta contexto alrededor, hash y continuación. Una ruta de archivo no tiene una búsqueda específica implementada. |
| `write_file` / `write_markdown` | Ruta y contenido; crean o reemplazan todo el archivo, hasta 128 KiB; devuelven tamaño y SHA-256. | No hay edición localizada ni precondición de versión. |
| `read_artifact` | Referencia y ventana en bytes; recupera JSON original como texto. | No hay selección de campos o filas. |

Se admiten Markdown, JSON, TXT y CSV. La profundidad máxima es de dos niveles de
directorios. Se rechazan escapes de ruta, enlaces y junctions. `materiales/` es de solo
lectura para A. La escritura usa temporal y sustitución atómica; JSON se valida antes
de escribir. Estos mecanismos se reutilizan, no se sustituyen por otro almacenamiento.

### 2.3. Qué existe para empresas

El prompt financiero ya establece, para evaluaciones con continuidad prevista:

- `empresas/<simbolo>/modelo.md`: negocio, mecanismos económicos, observaciones,
  interpretaciones, hipótesis, riesgos e incertidumbres.
- `empresas/<simbolo>/valoracion.md`: métodos, supuestos, escenarios, sensibilidad,
  cálculos, limitaciones y dependencias del modelo económico.
- `empresas/<simbolo>/evaluacion.md`: atractivo inversor, fundamentos, alternativas,
  postura y condiciones de cambio, enlazando modelo y valoración.

La creación es progresiva: no exige tres documentos vacíos ni un expediente para una
consulta breve. Las hipótesis y conclusiones importantes usan IDs locales y referencias
con ruta e ID. El prompt exige revisar consecuencias relevantes o declarar revisión
pendiente; distingue oportunidades, agenda y razonamiento de cartera.

Esto es una convención de instrucciones sobre Markdown. No existe hoy un servicio de
expedientes, parser de dependencias, propagación automática ni herramientas específicas
para crearlos o revisarlos. El modo histórico `cases` fue retirado: reutilizar el término
«expediente» no significa restaurar `CaseStore` ni sus contratos anteriores.

### 2.4. Qué se toma de Python y qué no se presupone

`run_python` comparte ejecutor para `calculate`, `transform`, `evaluate` y `model`.
`describe_python_operator` recupera contratos y ejemplos opcionalmente. Se conservan
código, datos resueltos, parámetros y referencias. Se propone trasladar ese patrón de
ejecución verificable y documentación bajo demanda.

La [observación V4 con Python](../python-operators-v1/findings-v4.md) registra dos usos
autónomos correctos; no demuestra una mejora causal ni valida el futuro instrumental de
estado. Sus recuentos no deben confundirse con los del piloto anterior sin Python.
Este encargo no ha reconstruido los eventos de ambos pilotos.

El ejecutor actual usa procesos locales y filtros preventivos; no es un sandbox ni
tiene límite estricto de memoria. Tampoco escribe directamente archivos desde el código
generado: devuelve JSON y el host conserva resultados. La ampliación de aislamiento,
gráficos o utilidades financieras de la propuesta V5 queda fuera de este encargo.

## 3. Principio central: intención, operación y entrega

Diseñar cada capacidad con tres contratos relacionados:

1. **Intención:** para qué necesita el agente esa operación y qué pretende obtener
   o cambiar. Una frase breve vinculada a una pregunta o revisión, no razonamiento interno
   extenso ni una justificación ceremonial.
2. **Ejecución:** objetivo y selectores verificables, precondiciones, permisos y efecto
   exacto. Una intención en lenguaje natural no amplía permisos ni sustituye selectores.
3. **Entrega:** contenido concreto que recibirá el modelo para comprobar lo ocurrido
   y continuar, con procedencia, límites y acceso al original.

Propuesta: exigir propósito en las nuevas operaciones sustantivas de recuperación y
revisión, manteniendo compatibles las llamadas existentes. Validar que esté presente
no demuestra que tenga calidad: la correspondencia entre propósito, acción y resultado
se evalúa semánticamente. No aceptar instrucciones vagas como «mejora el expediente»
para que la herramienta genere conclusiones o seleccione cambios por su cuenta.

## 4. Dos niveles de operaciones sobre una misma base

### 4.1. Primitivas generales de estado

| Capacidad propuesta | Selección/efecto | Entrega útil al contexto |
|---|---|---|
| Orientar un archivo | Encabezados y ubicaciones; tamaño y versión. | Mapa del documento, sin volcarlo completo; advertir si el mapa es parcial. |
| Recuperar contenido | Archivo, líneas, sección o fragmento identificado. | Texto original seleccionado, ubicación, contexto del encabezado y hash. |
| Buscar | Archivo concreto o ámbito de directorios, consulta literal y límites. | Coincidencias con contexto, orden declarado y continuación. |
| Crear | Ruta ausente y contenido explícito. | Confirmación, versión y referencia; rechazar colisión. |
| Revisar | Sustituciones exactas y versión esperada. | Cambios aplicados, hashes anterior/nuevo y diff acotado. |
| Insertar | Ancla inequívoca y posición antes/después. | Inserción y localización; rechazar ancla ausente o ambigua. |
| Recuperar un resultado | Referencia real y, posteriormente, selector de JSON/filas. | Parte solicitada, tipo, procedencia y advertencias de parcialidad. |

Los nombres y agrupación final de herramientas están pendientes. No hace falta una
función por cada fila ni un único dispatcher que mezcle todo. Empezar por lectura
selectiva y edición exacta; añadir selectores de secciones cuando sus reglas estén
definidas para encabezados repetidos, subsecciones y bloques de código.

Una comparación con versiones anteriores solo se puede ofrecer si su contenido se
conservó y es recuperable. Un hash permite identificar bytes, no reconstruirlos.

### 4.2. Operaciones específicas de expediente

Se recomienda una capa financiera fina sobre las primitivas, sin duplicar sus reglas
de rutas, persistencia ni concurrencia. A diferencia de un editor genérico, conoce
la convención de documentos y puede ayudar a construir y recuperar un expediente.

| Necesidad | Operación candidata y límites |
|---|---|
| Orientarse en una empresa | Inventariar sus documentos existentes, versiones, encabezados e IDs explícitos. Ausente significa no conservado, no necesariamente no investigado. |
| Desarrollar una dimensión | Crear modelo, valoración o evaluación con contenido aportado por A y ubicación validada. Sin crear las otras dimensiones por rutina. |
| Incorporar evidencia o cálculo | Insertar observación e interpretación redactadas por A con referencias a materiales/ejecuciones, fechas y unidades cuando procedan. La herramienta comprueba existencia o estructura; no acredita la inferencia. |
| Revisar una hipótesis o conclusión | Aplicar cambios explícitos a una ubicación única, preservando ID y contenido ajeno; registrar motivo y referencias. No cambiar silenciosamente el significado de un ID. |
| Localizar consecuencias | Buscar referencias textuales a ruta e ID dentro y fuera de la empresa. Devolver candidatos y límites de búsqueda, no declarar impacto económico ni exhaustividad semántica. |
| Conservar revisión pendiente | Escribir una nota explícita aportada por A en el documento afectado. No convertirla en una tarea financiera elegida por el runtime. |
| Revisar estructura | Detectar referencias internas no localizables, IDs duplicados o documentos ausentes. Informar anomalías comprobables sin un sello de «análisis completo». |

No se propone un comando que «construya la tesis» mediante otro LLM oculto. La ayuda a
construir análisis viene de operaciones expresivas, instrucciones concretas, plantillas
opcionales y recuperación de sus fundamentos. El LLM principal redacta y juzga; Python
ejecuta procedimientos; las herramientas preservan y permiten revisar el trabajo.

El primer diseño debe escoger pocas operaciones de expediente que aporten algo frente
a llamadas genéricas. Se recomienda empezar por orientación/recuperación por empresa y
creación o revisión de una dimensión. El resto es una agenda de evaluación, no una
lista de interfaces que deban implementarse juntas.

## 5. Documentación y descubrimiento de capacidades

Toda capacidad nueva se entrega con schema, implementación, descripción breve,
contrato extenso recuperable, ejemplos ejecutables y pruebas. El contrato explica:
propósito, cuándo usarla, selectores, efectos, salidas, límites, errores y recuperación.

Agrupación propuesta: estado general y expedientes de empresa, reutilizando la
documentación Python. Las instrucciones financieras explican cómo construir conocimiento:
separar observación, inferencia, supuesto, cálculo y juicio; conservar contradicciones;
fundamentar cambios; revisar consecuencias; reconocer insuficiencia. Las de estado explican
cómo localizar y modificar contenido. No duplicar manuales completos en ambos lugares.

Preferencia inicial: documentación empaquetada recuperable mediante una herramienta
de descripción, siguiendo Python. `read_file` accede al estado editable, no a recursos
instalados; no ampliar su frontera para leer documentación. Reutilizar el registro
efectivo en vez de mantener un catálogo global independiente. La descripción puede
agrupar operaciones, sin una herramienta de inspección por archivo o empresa.

Consulta opcional, ejecución directa y catálogo breve visible. Anunciar únicamente
capacidades presentes en el modo y fase actuales. Congelar versión/hash de contratos
en la captura para que una continuación pueda detectar cambios. El conocimiento
instrumental conservado por A puede enlazar ese contrato; no copiarlo a la agenda.

Las plantillas no imponen un esquema financiero universal ni exigen rellenar huecos.
Los estados previos conservan sus copias de instrucciones; cualquier adopción se hará
explícita, manteniendo trazabilidad y sin modificar campañas históricas.

## 6. Calidad de la información inyectada en contexto

Conservar resultado completo y elegir una vista útil son responsabilidades distintas.
Hoy `ToolRegistry` archiva resultados y sustituye los mayores de 32 KiB por referencia,
exceptuando las lecturas paginadas. Esto acota entrega; no garantiza selección relevante.
La propuesta añade vistas deterministas por operación antes de considerar resúmenes LLM.

Cada respuesta debería incluir contenido útil, localización, versión, selector aplicado,
límites y continuación real. El presupuesto de entrega tiene que contemplar también
metadatos, envoltorio y escapado JSON: limitar bytes del texto no limita el payload total.

Reglas de entrega:

- Lectura: fragmento original, archivo/sección de origen, rango y versión; preservar
  advertencias dentro del ámbito seleccionado. No presentar un extracto como documento completo.
- Búsqueda: contexto alrededor y criterio de orden explícito. No inventar probabilidades
  ni devolver solo títulos que obliguen a otra consulta para entender cada coincidencia.
- Expediente: estructura y pasajes seleccionados; un mapa de encabezados no resume la
  calidad del análisis ni demuestra que no existan riesgos fuera del fragmento.
- Escritura: cambio aplicado, versión y diff limitado; evitar repetir todo el archivo.
- Error: causa estable y accionable, sin éxitos parciales engañosos. Si un cambio se
  aplicó pero falló su captura, distinguirlo de una edición no aplicada para evitar reintentos ciegos.
- Exceso: indicar qué no se entregó y cómo recuperarlo. No truncar JSON hasta volverlo
  inválido ni perder silenciosamente reservas, fuentes o referencias.

El propósito orienta la elección del selector por A; no se traduce automáticamente en
una selección semántica supuestamente óptima. La primera versión no añade un agente
resumidor o investigador dentro de las herramientas. Si se propone después, necesita
presupuesto, trazabilidad y evaluación propios.

## 7. Integración y garantías que el diseño debe resolver

1. **Compatibilidad de schemas:** `ToolRegistry.register` hace obligatorios todos los
   campos registrados. Un parámetro con default Python no es opcional para el modelo.
   Diseñar explícitamente nuevas firmas o evolución compatible con el proveedor estricto.
2. **Versiones:** hash calculado sobre los mismos bytes de los que se extrae la lectura;
   continuaciones ligadas a esa versión. Rechazar cambios entre páginas o pedir reiniciar.
3. **Escritura:** comprobar versión esperada, unicidad del objetivo y validez del resultado
   antes de guardar. Mantener escritura atómica y límites. El bloqueo de un experimento
   gestionado no protege por sí solo frente a editores externos o todas las APIs directas;
   precisar el alcance de concurrencia soportado y evitar prometer un CAS universal.
4. **Captura:** el seguimiento de archivos modificados reconoce hoy por nombre
   `write_file` y `write_markdown`; incorporar las nuevas mutaciones y sus versiones.
   Reutilizar eventos/artefactos sin crear un segundo archivo de auditoría.
5. **Fases:** decidir qué consultas de contratos y operaciones de persistencia se admiten
   en consolidación. Las revisiones periódicas siguen sin herramientas. No modificar
   umbrales ni reconstrucción como efecto lateral de esta ampliación.
6. **Empresa:** validar identificador y ruta, resolver símbolos ambiguos en el ámbito
   del experimento y no usar nombres arbitrarios para escapar del workspace. No necesita
   acceso a BD para manipular un expediente ya identificado.
7. **Integridad entre documentos:** inicialmente una escritura atómica por archivo,
   sin prometer transacción multiarchivo. Capturar cambios parciales y pendientes si se
   interrumpe una revisión; no publicar «expediente coherente» por una sola edición correcta.
8. **Temporalidad:** en simulación usar fecha simulada para el significado de la revisión;
   conservar aparte el instante real de ejecución. Leer archivos no valida que sus fuentes
   sean históricamente admisibles. No conectar fuentes vivas ni subsanar contaminación
   temporal mediante etiquetas de fecha.

## 8. Ejemplo de recorrido para diseñar y verificar

Caso sintético: AAPL tiene una hipótesis H1 sobre márgenes en el modelo, V1 depende de
ella en valoración y la evaluación referencia V1. Llega evidencia que puede afectar H1.

1. A solicita orientación del expediente con el propósito de localizar los fundamentos
   vigentes. Recibe documentos y localizadores reales, no una valoración generada.
2. Recupera H1 con su contexto y consulta el material nuevo. Decide si existe contradicción,
   diferencia de periodos o una actualización compatible.
3. Si necesita cálculo, ejecuta Python y conserva su resultado. Distingue el cálculo
   de la interpretación y los supuestos.
4. Solicita una revisión explícita de H1 con hash esperado, fundamento y motivo. Recibe
   el cambio y una referencia recuperable; las otras secciones permanecen intactas.
5. Localiza referencias a H1. Lee V1 y evalúa sus consecuencias. Revisa, confirma con
   fundamento o conserva revisión pendiente, y considera evaluación/oportunidades.
6. Tras renovar contexto, recupera las versiones vigentes y pendientes sin releer todo
   ni asumir que el expediente quedó resuelto.

Es un caso de prueba, no una secuencia obligatoria para cada investigación. El agente
puede cerrar una consulta breve, decidir que no hay impacto o trabajar otra dimensión.

## 9. Implementación propuesta en cambios pequeños

| Cambio futuro | Resultado revisable | Verificación mínima |
|---|---|---|
| 1. Estado y contratos | Lectura versionada, edición exacta y documentación consultable; captura integrada. | Preservación de bytes ajenos, conflictos, ambigüedad, Unicode, JSON, rutas, materiales, fallos de captura y compatibilidad. |
| 2. Expediente completo mínimo | Orientación/recuperación por empresa y creación/revisión de una dimensión usando esas primitivas, con instrucciones y ejemplos. | Caso H1/V1, empresa ausente, documento ausente, IDs repetidos, referencias y ausencia de documentos vacíos automáticos. |
| 3. Entrega selectiva | Líneas/secciones, contexto de búsqueda y continuación; vistas compactas con acceso al original. | Límites serializados, selección fiel, continuación estable, información negativa y advertencias conservadas. |
| 4. Contraste controlado | Protocolo congelado y comparación de comportamiento, una vez autorizado ejecutar. | Entradas/modelo/presupuesto iguales y capturas de fallos, coste y revisión semántica independiente. |

No separar documentación de la herramienta que explica. Cada cambio implementado debe
cerrar un recorrido ejecutable, no dejar una colección de interfaces vacías. Los tests
actuales de [agente](../../../tests/test_agent.py),
[metodología financiera](../../../tests/test_financial_methodology.py),
[continuidad](../../../tests/test_continuous.py) y
[Python](../../../tests/test_python_operators.py) orientan la regresión local.

FinData batch, web, aislamiento Python y modelado financiero adicional siguen siendo
líneas posibles de V5, pero no dependencias para este primer recorrido de expedientes.

## 10. Evaluación y decisiones pendientes

Separar tres niveles: integridad mecánica, utilidad del contexto devuelto y calidad
del análisis construido. Una llamada exitosa no acredita los otros dos.

Medir preservación y conflictos; exactitud/localización de recuperación; información
material omitida; bytes/tokens entregados cuando estén disponibles; reconsultas;
elección acorde al propósito; uso opcional de contratos; recuperación tras renovación;
fidelidad de evidencia/cálculos; coherencia entre modelo, valoración y evaluación.
Una reducción de llamadas o bytes puede empeorar el análisis: evaluar ambos lados.
No premiar número de archivos, inspecciones o cambios de postura.

Para atribuir efectos, comparar primero las operaciones manteniendo instrucciones
equivalentes y después valorar la intervención conjunta de herramientas e instrucciones.
No asumir que leer el mismo documento otra vez sea redundante: puede haber cambiado
o ser necesario para revisar una conclusión. No fijar porcentajes de mejora sin baseline.

El siguiente diseño debe resolver de forma concreta:

- Qué operaciones merecen herramienta financiera propia frente a contrato de uso de
  primitivas generales; preferencia inicial por una capa mínima de expediente.
- Cómo representar selectores e IDs con compatibilidad con Markdown previo y sin parser
  financiero completo. No convertir las guías actuales en schema obligatorio sin acuerdo.
- Cuánto contexto adyacente entregar y cómo permitir ampliarlo sin otra lectura completa.
- Cómo adoptar contratos versionados en experimentos que conservan instrucciones copiadas.
- Qué garantía de concurrencia es viable y qué contenido previo se conservará si se ofrece
  comparación o recuperación de versiones.

Las elecciones de implementación rutinarias se resuelven con el código y pruebas. Cambiar
la organización conceptual aceptada, exigir una estructura financiera nueva o automatizar
juicios/propagación económica requiere plantear la decisión al usuario.

## 11. Cierre de este encargo documental

Este documento fija contexto, propósito, mapa del código, propuesta de operaciones y
entrega al contexto, garantías, secuencia y criterios de evaluación. No implementa las
capacidades candidatas ni declara resultados experimentales. El siguiente encargo puede
usar este texto y sus fuentes para cerrar schemas, ejemplos de salida y un primer cambio
de código completo antes de ampliar el catálogo.
