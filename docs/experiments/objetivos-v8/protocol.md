# V8: objetivos explícitos y evaluación periódica de cobertura

Estado: mecanismo implementado con verificación local; contraste semántico controlado
propuesto y sin ejecutar. Encargo aceptado el 2026-10-31. Posteriormente se autorizó
la [campaña real V8](../inversion-real-v8/protocol.md), separada del contraste controlado.

## Pregunta y límites

¿Un objetivo explícito y feedback periódico sobre lo pendiente ayudan al investigador
a orientar mejor su trabajo? La distancia observa cobertura según el evaluador LLM;
no certifica fidelidad económica, calidad financiera ni rentabilidad. La
[campaña V7](../inversion-real-v7/findings.md) observó paquetes con fuentes omitidas;
motiva reservar espacio para fundamentos, sin demostrar que V8 resuelva el problema.

Un objetivo activo, criterios fijos, pesos iguales y un investigador A. No introduce
grafos, dependencias, selección de objetivos ni planificador. El evaluador no tiene
herramientas, no escribe conocimiento ni redefine criterios. El núcleo es general;
la especialización pertenece al objetivo suministrado.

## Contrato e intervención

El archivo JSON externo al estado y a ejecuciones contiene `id`, `description` y
`criteria` (objeto de identificador a descripción). Máximo 16 KiB UTF-8; se rechazan
vacíos, campos adicionales y claves JSON duplicadas. `Objective` usa criterios
inmutables y hash canónico. `AgentRequest.objective` requiere continuo; la CLI valida
antes de crear clientes. Manifiesto conserva definición, hash y política efectiva.

El investigador recibe el objetivo al comenzar y tras reconstruir contexto. Con
objetivo, el evaluador sustituye las revisiones externas V7; sin objetivo se conserva
V7. La autorrevisión permanente de diez llamadas permanece separada.

Cada 20 llamadas de investigación, si quedan recursos ordinarios, se evalúa tras
consolidación y autorrevisión pendientes. Los contadores sobreviven a renovaciones;
no se acumulan evaluaciones atrasadas y se reinician por ejecución. Se usa el mismo
perfil/cliente en secuencia, con contexto separado, sin herramientas ni chat del
investigador. Investigación y consolidación consumen el máximo ordinario; la fase
adicional `objective_evaluation` cuenta en el total real y comparte deadline global.

El paquete de 64 KiB incluye objetivo, último feedback completo válido, conocimiento
actual, fuentes referenciadas, presupuesto y acciones. Tras reservar metadatos y margen,
divide el espacio entre documentos y evidencia; las acciones solo usan el sobrante.
Prioriza documentos por coincidencia textual con la descripción y criterios (heurística,
no validación semántica). Recupera referencias explícitas `materiales/*.json`, incluso
desde documentos omitidos. Extractos hasta 4 KiB, versiones, parcialidad, errores y
recuentos de omisión explícitos. No recorre dependencias ni busca nuevas fuentes.

El evaluador devuelve exactamente una entrada por criterio, con `criterion_id`,
`status` (`cubierto`, `no_cubierto`, `no_evaluable`), `justification`, `references`
y `pending`. Cubierto exige referencias y `pending: null`; los otros estados explican
qué falta. Un título no acredita cobertura. Referencias existentes no prueban por sí
solas la inferencia; el parser valida estructura, no verdad ni suficiencia semántica.

Python calcula `D = 1 - cubiertos/total` solo cuando todos son evaluables. `delta_distance`
es distancia completa anterior menos actual; inicialmente es ausente. Parcialidad y
fallos no actualizan la última distancia completa ni significan falta de progreso.
Se conserva la última evaluación completa con referencia y fecha, separada del diagnóstico
actual. Una reapertura justificada puede aumentar D.

Tres evaluaciones completas consecutivas con distancias no decrecientes y pendientes
producen un aviso para justificar continuar o cambiar de enfoque. Una mejora inicia
otra secuencia; fallo, omisión o parcialidad la interrumpen. No se ordena abandonar.
La transición a D=0 pide síntesis con fundamentos y límites una vez; no detiene el
continuo. Una reapertura permite un nuevo cierre. En una continuación histórica,
la cobertura debe reevaluarse antes de solicitar un cierre vigente.

Al cerrar por llamadas o herramientas se evalúa si queda tiempo; si el contenido y
las fuentes referenciadas no cambiaron, se reutiliza la última evaluación válida,
incluida una parcial, con referencia explícita. No se añaden llamadas tras cancelación,
fallo operativo o límite temporal. Si no queda presupuesto investigador, la intervención
final queda registrada, sin llamada extra para redactar síntesis. Un fallo del evaluador
se captura y no detiene investigación con recursos; sin reintento automático.

## Captura y recuperación

En `evaluacion-objetivo/` del run: `evaluation-NNNN-input.json`, `evaluation-NNNN.json`,
`summary.json` y, en cierre controlado, `final.json`. Se guardan hash de objetivo,
paquete y contenido, fecha, referencia anterior, respuesta, métricas e intervenciones.
Los fallos JSON conservan salida cruda; las trazas nativas conservan payloads disponibles.
Los estados completos, parciales, fallidos, omitidos y cancelados se distinguen.
Feedback hasta 8 KiB, con parcialidad y referencia al informe íntegro.

Las renovaciones recuperan feedback y última evaluación completa. Las continuaciones
gestionadas solo recuperan evaluaciones completas del mismo workspace y hash de objetivo,
marcadas históricas; no recuperan la racha de estancamiento. Cambiar el objetivo cambia
la serie y no permite calcular variación frente a criterios distintos. No se migra
estado ni se reescriben instrucciones congeladas.

El piloto continuo admite `objective.json` opcional en su definición: se congela,
incluye en la semilla de comprobación y pasa por CLI. Comprobación de inputs e inspección
del run detectan identidad distinta. Su informe separa última cobertura completa,
estado actual, fallos, parciales y llamadas adicionales. Se mantiene la restricción
existente: el controlador continuo no ofrece `resume`; continuar manualmente crea
otro run, mientras `check` exige preparar un piloto nuevo tras una tentativa.

## Comprobación técnica y contraste posterior

La [entrega](../../deliveries/2026-10-31-v8.md) conserva las verificaciones reales.
Los clientes simulados ejercitan validación, cálculo, fuentes recortadas, prioridad,
recuperación, fallos, cierre, contabilidad y lectores, sin proveedores ni BD remotas.

Contraste semántico futuro: objetivo explícito sin feedback frente al mismo objetivo
con feedback V8, entradas/corpus congelados, mismo investigador, herramientas, perfil
y presupuesto total comparable, incluyendo revisiones y evaluador. El control requiere
preparación propia antes de ejecutar; no se añade un interruptor experimental al runtime
en esta entrega. Fijar antes corpus, repeticiones, presupuesto y rúbrica independiente.

Evaluar materialidad de pendientes resueltos, errores, fundamento, fidelidad y utilidad
del resultado, además de costes y trayectoria de cobertura. Una caída de D o checks
aprobados no bastan para aceptar la hipótesis. La [campaña real](../inversion-real-v8/findings.md)
aporta observaciones de ejecución; no sustituye el contraste controlado pendiente.
