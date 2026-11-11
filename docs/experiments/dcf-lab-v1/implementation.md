# DCF Lab compartido: propuesta de implementación V1

Fecha: 2026-11-11. Estado: propuesta técnica aterrizada sobre el código local.
Este documento no acredita implementación, aceptación arquitectónica ni resultados
experimentales. No cambia la estrategia vigente ni activa una campaña.

## Resultado que buscamos

Un paquete `dcf-lab` instalable que valore una fotografía financiera y un contexto
empresarial explícitos. Research Agent lo consume como herramienta opcional; FinMate
podrá consumir después el mismo paquete. La metodología `experimental-v1`, los dos
supuestos financieros y las dos llamadas especializadas permanecen como referencia.

V1 termina cuando Research Agent puede solicitar una valoración, recuperar su cálculo
y diagnóstico, continuar investigando y pedir otra evaluación enlazada a la anterior;
todo ello con entradas auditables y consumo incluido en su presupuesto. Demostrar que
esa capacidad mejora la investigación requiere un contraste posterior.

## Qué existe y qué falta

| Observación del código | Consecuencia para esta propuesta |
|---|---|
| [Paquete independiente](../../../../dcf_lab/pyproject.toml), con Pydantic como dependencia base y extras PostgreSQL/HTTPX | Distribuir un wheel propio. El paquete se ha extraído posteriormente a la carpeta hermana `dcf_lab`. |
| [Servicio](../../../../dcf_lab/src/dcf_lab/service.py): `evaluate_investment` carga datos, lee contexto, orquesta y guarda siempre | Extraer una API que reciba los datos en memoria y devuelva el resultado sin acceder al almacenamiento. Conservar la función anterior como fachada de compatibilidad. |
| [Esquemas](../../../../dcf_lab/src/dcf_lab/schemas.py): `FinancialSnapshot`, `ContextDocument`, `Assumptions`, `Synthesis`, `Evaluation` | Extender estos contratos. Evitar otra jerarquía paralela de resultados y procedencia. |
| `Evaluation` ya conserva cálculos cuando falla la síntesis; devuelve `failed` | Hacer explícita la disponibilidad parcial sin perder ese comportamiento ni los bundles históricos. |
| Contexto limitado a treinta y dos archivos y 262144 bytes; referencias por hash | Aplicar el mismo límite a entradas en memoria y conservar contenido, identidad y versión. Rechazar excesos, sin recorte silencioso. |
| [Transporte LLM](../../../../dcf_lab/src/dcf_lab/adapters/llm.py) síncrono; metadatos de modelo y uso al completar | Añadir transporte asíncrono inyectable y registrar también llamadas fallidas, duración y cancelación. |
| [Composición de Research Agent](../../../src/research_agent/composition/build.py) registra capacidades; [registro](../../../src/research_agent/core/tools.py) ya archiva resultados y permite lectura paginada | Añadir una capacidad `valuation`, sin otro dispatcher ni bucle investigador. |
| [CallBudget](../../../src/research_agent/core/limits.py) y [motor](../../../src/research_agent/core/execution.py) comparten contadores y deadline | Integrar las llamadas financieras en esos recursos; sumar costes después de ejecutar no evita sobrepasar el límite. |
| [Workspace](../../../src/research_agent/storage/workspace.py) limita rutas a dos directorios y admite materiales | Usar rutas compatibles y recuperar detalles con `read_file`/`read_artifact`, sin herramienta nueva de consulta. |

Research Agent no tiene hoy una integración DCF. Su lector `read_company` tampoco
equivale al `FinancialSnapshot` completo del laboratorio: no construir uno suponiendo
que las salidas de herramientas existentes contienen todos sus campos.

## Decisiones propuestas para V1

1. Un único código fuente en `dcf_lab`; wheel `dcf-lab` versionado
   y fijado en el entorno experimental. Research Agent no importa rutas del checkout
   hermano ni módulos `finmate`, `engine` o `api`.
2. El núcleo recibe `FinancialSnapshot`, documentos y configuración. El adaptador
   consumidor obtiene esos datos y elige dónde guardar. No hay I/O implícito al evaluar.
3. Reutilizar `Evaluation` como resultado; `run_id` es el identificador de evaluación.
   El `run_id` de Research Agent se conserva por separado como correlación.
4. Separar versión de contrato, política, fórmula y prompts. Cambiar el contrato o
   el diagnóstico no cambia por sí mismo `experimental-v1` ni `FORMULA_VERSION`.
5. Activación explícita en composición/configuración de experimento; desactivada por
   defecto. Una vez activada, disponible desde el primer paso de investigación,
   respetando las restricciones operativas de cierre existentes.
6. Primera integración en modo actual con snapshot explícito o FinData de solo
   lectura. En simulación histórica, rechazar configuración DCF hasta disponer de
   snapshots disponibles en la fecha simulada; nunca recurrir a datos actuales.

Son elecciones de esta propuesta, no ADRs aceptadas. No se modifica el motor financiero
por razones de organización del código.

## Contrato de entrada y resultado

Añadir `ValuationRequest` en `dcf_lab/schemas.py` con:

| Campo | Regla |
|---|---|
| `schema_version` | Versión explícita del contrato de solicitud. |
| `company_id` | En V1, símbolo normalizado con las reglas actuales; debe coincidir con `snapshot.profile.symbol`. No introducir resolución universal de identidades. |
| `snapshot: FinancialSnapshot` | Obligatorio, conservado íntegro para recálculo. |
| `context: list[ContextDocument]` | Opcional y vacío por defecto; reutiliza el contrato existente. Añadir `version` opcional a cada documento. |
| `policy: Policy` | Reutiliza el modelo actual; versión no soportada se rechaza antes de llamar al LLM. |
| `previous_evaluation: Evaluation | None` | Opcional; verificar empresa, contrato e integridad del bundle. No reenviar recursivamente evaluaciones completas al prompt. |

No añadir un segundo `CompanyKnowledge` que replique `ContextDocument`. El adaptador
convierte el Modelo de Empresa o documentos equivalentes en esa lista. Conserva la
ruta lógica como procedencia y el hash como identidad de contenido. El paquete verifica
hashes y unicidad de referencias; una referencia no prueba el fundamento económico.

Las referencias citables son documentos incluidos, referencias financieras existentes
y una referencia a la evaluación anterior cuando se suministre. Una ruta mencionada
en un documento no autoriza leer su destino ni se convierte automáticamente en evidencia.
No aceptar referencias externas como prueba si no se ha aportado su contenido o una
representación explícita verificable. Contar el contenido previo enviado al modelo
dentro del presupuesto; ante exceso, devolver error de entrada antes de consumir LLM.

Extender `Evaluation` con lo mínimo:

- Versión nueva de esquema, empresa explícita, `previous_evaluation_id` y hashes de
  solicitud/contexto. Conservar snapshot, política, supuestos y versiones existentes.
- Resultado por fase: `not_started`, `completed`, `rejected`, `failed` o `cancelled`,
  con código de causa. `issues` permanece legible; advertencias financieras siguen
  siendo propiedad de `inspection.warnings`, sin una segunda copia contradictoria.
- Estado `partial` cuando existe un cálculo válido pero no diagnóstico aceptado.
  La síntesis rechazada permanece en `rejected_synthesis`, nunca como conclusión válida.
- Registro por intento LLM: fase, modelo solicitado/resuelto, hashes de entrada y
  prompt, inicio, duración, estado, uso y coste cuando se conozcan. Ausencia de uso o
  precio se expresa como desconocido, nunca cero.

Mantener lectura de bundles v1 mediante conversión explícita a la representación nueva.
No reescribir originales. El recálculo verifica el hash con el esquema original antes
de convertir; un cambio de serialización no debe invalidar bundles legítimos.

## API y flujo de ejecución

La API principal nueva será asíncrona para integrarse con el runtime existente:

```python
from dcf_lab import ValuationRequest, evaluate_company

evaluation = await evaluate_company(request=request, llm=llm_adapter)
```

Añadir un protocolo LLM asíncrono con salida estructurada, sin herramientas. El adaptador
de Research Agent respeta deadline y cancelación. Conservar la API síncrona existente
`evaluate_investment(...)`: carga snapshot/contexto, ejecuta el mismo coordinador y
guarda. Su puente síncrono se usa fuera de un event loop; dentro se utiliza la API
asíncrona. No mantener dos implementaciones del pipeline.

El adaptador OpenAI propio del paquete debe disponer de transporte asíncrono. Mantener
compatibilidad con el protocolo síncrono anterior mediante puente explícito solo donde
proceda; no poner toda la evaluación en un thread que pueda seguir llamando al proveedor
o escribiendo después de cancelar la herramienta.

Secuencia: validar solicitud → inspeccionar snapshot → generar/validar supuestos →
calcular → diagnosticar/validar → devolver. La API no crea directorios ni abre la base.
La captura de errores operativos conserva fase y clase sin serializar secretos o cuerpos
HTTP. La cancelación del runtime se propaga; no se convierte en una finalización normal.

| Situación | Resultado y llamadas LLM |
|---|---|
| Solicitud inválida, símbolo incoherente o contexto excesivo | Error tipado de entrada; ninguna llamada. |
| Inspección bloquea | Estado actual `insufficient_data`, `unsupported_model` o `needs_review`; ninguna llamada. |
| Falta conocimiento cualitativo | Puede continuar con advertencia exploratoria; no bloquear solo por esa ausencia. |
| Supuestos fuera de política o con referencias inexistentes | `needs_review`; una llamada, sin cálculo ni diagnóstico. |
| Falla generación de supuestos | `failed`; registrar intento y consumo conocido. |
| DCF válido y diagnóstico fallido, rechazado o bloqueado por presupuesto | `partial`; conservar cálculo y causa, sin tercer intento automático. |
| Todo válido | `completed`; dos llamadas como máximo. |
| Cancelación/deadline | Interrumpir llamadas; el adaptador archiva el avance disponible antes de cerrar cuando sea posible, sin publicar éxito. |

Permitir al consumidor observar resultados de fase mediante un callback asíncrono
opcional, sin dependencia de su almacenamiento. Así puede archivar el cálculo antes
de la segunda llamada. Si no consigue persistirlo, registrar el fallo de captura;
no afirmar durabilidad por el mero hecho de tener un objeto en memoria.

## Diagnóstico: extensión pequeña y comprobable

Extender `Synthesis`, conservando su nombre y campos actuales, con una lista de
`research_implications`. Cada elemento contiene `kind`, `observation`, `question`,
`review_trigger` y `evidence_refs`. Tipos: supuesto material, incertidumbre,
contradicción potencial. Los campos de pregunta o condición pueden estar ausentes
cuando no apliquen; lista vacía es válida.

El peso terminal y las sensibilidades proceden de Python. El LLM describe su
significado; no se le pide un ranking cuantitativo nuevo ni otra estimación.
No exigir contradicciones si el contexto no permite identificarlas.

Extender la validación de referencias y la restricción numérica de la narración a
los campos nuevos. Mantener las cifras en bloques insertados desde Python. Versionar
prompt/esquema de salida; fixtures antiguos no deben fingir que ya incluían estas
observaciones. Las implicaciones orientan la investigación y no disparan herramientas.

## Herramienta de Research Agent

Proponer esta firma en `capabilities/valuation/tools.py`:

```text
evaluate_company(company_id, knowledge_paths, previous_evaluation_ref)
```

`knowledge_paths` es una lista explícita, vacía si no hay documentos; la referencia
anterior admite `null`. Esto resuelve la selección de contexto sin imponer un nombre
de Modelo de Empresa ni recorrer silenciosamente todo el workspace. El registro actual
marca todas las propiedades como requeridas: expresar ausencia con lista vacía/null.

El adaptador valida rutas con `Workspace`, captura bytes/hash/versiones y construye
la solicitud. La configuración congelada del experimento elige la fuente de snapshot
y parámetros macro. Reutilizar `dcf_lab.adapters.findata.FindataSource` o el lector de
snapshots, sin replicar consultas, FCFF o política. Leer FinData en transacción de solo
lectura y cerrarla antes de esperar al LLM. No introducir ERP ni tasas por defecto nuevos.

Guardar el bundle completo como material recuperable, por ejemplo
`materiales/dcf-<evaluation_id>.json`, y el informe opcional junto a él. Conservar una
copia de auditoría fuera del estado editable y su hash: la copia del workspace no es
una garantía de inmutabilidad. El adaptador valida procedencia e integridad al reutilizar
una evaluación anterior. No añadir una base de datos ni actualizar documentos de tesis.

La salida al ReAct tendrá un máximo propuesto de 8 KiB UTF-8: identificador, estado,
referencias de recuperación, fecha/moneda/precio utilizado, valores por escenario,
dos supuestos, peso terminal, advertencias, diagnóstico e implicaciones resumidas.
Las cifras salen del cálculo. Ante exceso, omitir elementos completos con contador
y referencia al original; conservar siempre estado y advertencias de bloqueo.

El archivado automático de `ToolRegistry` guarda la salida de la herramienta, no
necesariamente su bundle completo. No confundir ambos: el adaptador debe persistir
el bundle antes de devolver su referencia. Usar los controles de rutas y captura
existentes; no marcar la operación como una edición de tesis.

## Presupuesto y trazas: condición de integración

Conectar el adaptador LLM a la sesión activa mediante un enlace pequeño de recursos
en composición. Reutilizar `CallBudget` y el transporte gestionado; ampliar el punto
de enlace para llamadas especializadas si hace falta. El núcleo no importa DCF Lab.

- La llamada del investigador que solicita la herramienta ya consume una llamada.
  La herramienta consume una invocación; sus dos llamadas internas consumen otras
  dos del mismo techo LLM. No aparecen como dos pasos ReAct ni como dos herramientas.
- Antes de comenzar la parte LLM, comprobar disponibilidad para ambas llamadas y
  respetar la reserva de cierre de la política activa. Cobrar cada intento antes
  del transporte; no cobrar llamadas que no se llegaron a iniciar.
- Revalidar presupuesto, tiempo y cancelación antes del diagnóstico. Si ya existe
  cálculo, devolver `partial` cuando esa fase no pueda iniciarse. No exceder el techo
  para completar una evaluación ni reservar recursos permanentemente para DCF.
- Etiquetar propósitos `valuation_assumptions` y `valuation_diagnosis`; incluirlos
  en totales y desgloses existentes. Capturar `run_id`, `tool_call_id`, evaluación,
  fase, modelo, uso, duración y resultado. Conservar también errores e interrupciones.
- Aplicar un timeout finito a la herramienta y cada llamada, limitado por el tiempo
  restante. No usar el timeout ordinario de una consulta breve sin considerar que
  hay dos llamadas. Ninguna escritura tardía tras cerrar el run.

El coste se calcula con una tabla de precios versionada y la fecha pertinente cuando
esté disponible; conservar tokens y coste desconocido si no puede calcularse. No hace
falta construir un servicio de facturación para V1.

## Entregas y aceptación

| Entrega | Archivos principales | Se acepta cuando… |
|---|---|---|
| 1. API portable | `dcf_lab/{schemas,service,__init__}.py`, adaptador LLM y pruebas del paquete | Una solicitud en memoria funciona sin FinMate/Research Agent/base/archivos. Fachada y CLI anteriores siguen funcionando. Mismos snapshots/supuestos/política producen los mismos cálculos. |
| 2. Contexto, diagnóstico y bundles | `schemas.py`, `service.py`, `reporting.py`, fixtures | Hay referencias verificadas, límite en bytes, diagnóstico ampliado y parciales explícitos. Bundles v1 se leen y recalculan; alteraciones se detectan y originales no se sobrescriben. |
| 3. Capacidad experimental | Nueva `capabilities/valuation/`, composición, configuración/CLI, recursos y pruebas de Research Agent | Activación opcional, datos en solo lectura, bundle recuperable, contador global correcto, deadline/cancelación y cierre respetados. La configuración y versión del wheel quedan congeladas. |
| 4. Protocolo y piloto | Protocolo específico y definición de campaña posterior | Ensayo local con proveedores simulados; después, piloto real separado y contraste con entradas, presupuesto y rúbrica prefijados. No confundir checks locales con utilidad demostrada. |
| Posterior. FinMate | Adaptador en sus capacidades y pruebas de sus consumidores | Consume el mismo wheel/API; enlaza cálculo y documentos respetando revisiones/idempotencia del producto, sin motor o prompts paralelos. Fuera de las primeras cuatro entregas. |

En la entrega 3, añadir dependencia opcional fijada a la versión realmente construida,
actualizar explícitamente el wheel instalado en el laboratorio y comprobar sus imports.
No copiar código a Research Agent ni editar `site-packages`. Actualizar las guías de
cada repositorio solo al cambiar su comportamiento efectivo.

Pruebas necesarias: rechazo sin LLM; ausencia de contexto; límites UTF-8 y rutas;
supuestos inválidos; referencia inventada; regresión de cálculo; fallo/rechazo del
diagnóstico con cálculo conservado; lectura/recálculo v1 y nuevo; fallo de persistencia;
presupuesto insuficiente sin HTTP; consumo de intentos fallidos; cancelación entre
fases; recuperación paginada; configuración apagada y rechazo en simulación histórica.
Usar snapshots sintéticos y LLM simulado. Las pruebas locales no necesitan red ni base
compartida; el piloto real se prepara como una operación distinta.

## Contraste inicial que permitiría decidir

Propuesta: una empresa elegible, tres activaciones por condición y workspace persistente
dentro de cada condición, aislado entre control y tratamiento. Activación inicial con
información incompleta; segunda con evidencia material para crecimiento/margen; tercera
con información redundante y un cambio de precio separado. No imponer cuándo valorar.
Congelar datasets y fechas; evitar consultas vivas que expongan información futura.

Control sin herramienta DCF y tratamiento con ella, mismo investigador, instrucciones
comunes, evidencia y techo global LLM, incluidos los especialistas. Fijar un límite
monetario adicional si la comparación pretende igualdad de coste: igual número de
llamadas no significa igual gasto. El tratamiento dispone de menos llamadas para
investigar cuando utiliza DCF; eso forma parte del coste de esta capacidad.

Evaluar fundamento de supuestos, fidelidad del cálculo, identificación y seguimiento
de incertidumbres, revisión proporcionada y calidad de la evaluación final. Revisores
independientes sin etiqueta de condición, reconociendo que el contenido puede revelar
el tratamiento. Mantener las mismas condiciones de las extensiones opcionales en ambas
ramas. Conservar todos los intentos, fallos, latencias y consumo; ninguna puntuación
vive en DCF Lab.

Una pareja longitudinal sirve como piloto de viabilidad, no como prueba causal de
superioridad. Si el agente no usa la herramienta, registrar esa observación sin forzar
una invocación a posteriori. Replicar después antes de decidir la incorporación estable.

## Primer encargo ejecutable

Implementar primero las entregas 1 y 2 en el paquete existente: API sin almacenamiento,
coordinador único, diagnóstico ampliado y bundles compatibles. Ejecutar pytest y mypy
del paquete, verificar CLI y comparar recálculos con sus fixtures deterministas.
Después integrar recursos y herramienta en Research Agent. No lanzar una campaña ni
modificar el producto FinMate como efecto secundario de este primer corte.

La secuencia evita que la API quede definida accidentalmente por un consumidor y
permite revisar primero una biblioteca portable con un resultado comprobable.
