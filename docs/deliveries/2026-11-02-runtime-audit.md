# Auditoría previa: núcleo ReAct y extensiones

Fecha: 2026-11-02. Inspección anterior a modificar código. La propuesta fue
revisada en el chat y el usuario encargó su implementación, incluyendo unificar
los bucles acotado y continuo. No es una evaluación financiera ni una campaña.

## Observación del código

| Propietario actual | Responsabilidad y consumidores | Clasificación y cambio |
|---|---|---|
| AgentA.run | Modelo/herramientas, replay, cierre acotado y cierre especial de B; CLI, tests y servicio B | Motor común; política acotada común y cierre B multiagente |
| AgentA._prepare/_finish | Prompts, manifiesto, capturas, snapshots; ambas rutas y tests de B | Preparación/cierre compartidos; metadatos e instrucciones experimentales desde composición |
| continuous | Contexto, transcript, límites acumulados, revisión, checkpoints, integración; campañas usa context_seed y constantes offline | Motor común más política de régimen continuo y evaluación en progreso |
| knowledge | Encargos duraderos, paquete preparado, recibos, permisos y 30 llamadas reservadas; bootstrap, CLI y preparación | Multiagente; reutiliza workspace, registro, transacciones y motor comunes |
| objectives/objective_review/external_review | Definiciones, cobertura, paquetes de 64 KiB, feedback, recuperación; continuo y campañas | Progreso; revisión general o por objetivos, nunca ambas por defecto |
| runtime_control | Referencias, declaraciones, hashes, recuperación y políticas E2; continuo, B y campañas | Estado E2 conservado; programación de evaluación en progreso y continuación/checkpoint en regímenes |
| continuity | Agenda, foco, evaluación activa, extractos y observación de repetición | Lectura/semilla reutilizable; observaciones de investigación en progreso |
| context_budget/context_management | Medición serializada y reconstrucción con intercambios completos | Núcleo, sin criterios de suficiencia |
| workspace/advances/state_tools | Rutas, versiones, lecturas y publicación recuperable | Compartido; no duplicar escritores ni migrar Markdown |
| tools/integrations | Schemas, ejecución, materiales y adaptadores | Registro común por sesión; B tiene su instancia y herramientas autorizadas |
| recording/tracing | Eventos, manifiestos, snapshots y captura del proveedor | Núcleo; eventos experimentales conservan nombres y procedencia |
| experiments | Directorios, bloqueo, instrucciones congeladas y adopción de B/E2 | Separar gestión común y composición; conservar imports al convertir en paquete |
| contracts | Solicitud pública importa Objective; límites/resultados usados por herramientas/captura | Separar valores neutrales del adaptador público sin cambiar argumentos |
| research_campaigns | Construcción offline, fingerprints, lanzamiento e informes | Consumidor externo; nunca dependencia del agente |

## Activación, persistencia y compatibilidad

- Acotado: predeterminado; límites propios y consolidación/respuesta. B no se
  activa por el rol textual ni por cargar un archivo del workspace.
- Continuo E2: --continuous y mandato; todas las llamadas gestionadas cuentan en
  el techo total. Renovación técnica y checkpoints no son suficiencia semántica.
  Persisten transcript, runtime/estado.json y checkpoints de conocimiento.
- Progreso: sin objetivo usa revisión general; --objective selecciona criterios.
  Eventos agrupados con separación de cinco llamadas y respaldo de veinte.
  Informes en revision-externa/ o evaluacion-objetivo/, fuera del conocimiento.
  Fallos/parcialidad consumen recursos sin inventar distancia o progreso.
- B: off/prepared congelados, continuo de 100 llamadas, 70 para A/control y 30
  protegidas. Intentos de 15 llamadas/24 herramientas/180 segundos, reserva de
  cierre y finish_integration obligatorio. Encargos y recibos fuera del estado.
- Mantener identidades, nombres de políticas (incluidos nombres de funciones en
  runtime.json), rutas y contenido congelado. Cambian fingerprints de código;
  una campaña preparada con otro código sigue rechazando deriva, sin migración.

## Propuesta concreta y riesgos

Conservar agent.py como fachada y bootstrap/CLI como composición. Crear runtime
para contratos neutrales, motor y política acotada. Convertir experiments.py en
experiment_store.py más paquete experiments con reexportaciones; añadir multiagent,
progress y regimes. Mover implementaciones específicas, dejando aliases para los
imports existentes. El núcleo no importa estos aliases ni implementaciones.

El motor ejecutará una sola secuencia de decisiones: modelo, herramienta,
renovación o cierre. Políticas conservan el orden y restricciones actuales; las
evaluaciones aisladas usan la misma interacción y el hijo B el mismo motor.
Composición conecta progreso, régimen y B; sin registro dinámico de plugins.

Riesgos principales: contar dos veces B, consumir sus reservas desde A, cambiar
el orden final de evaluación, perder continuaciones del proveedor, convertir un
timeout de fase en fallo total, capturar dos veces, romper monkeypatches de tests
o cambiar identidades por mover funciones. Verificar cada diferencia con clientes
controlados, errores de disco y versiones, además de tests de fronteras/imports.

No se ha identificado una implementación abandonada que deba eliminarse en este
refactor. V7/V8 y aliases siguen teniendo consumidores. Hay un test huérfano de
precios que importa scripts/review_historical_prices.py ausente, ya documentado
en la entrega previa; corregirlo no forma parte de este cambio.

La infraestructura de ejecución, replay, presupuestos, captura y persistencia es
candidata a reutilización en FinMate tras adaptar sus contratos y permisos. E2,
reservas concretas de B, agenda y criterios de evaluación son políticas del
laboratorio; esta separación no valida su utilidad ni autoriza trasladarlas.

## Matriz de verificación

Acotado: respuesta temprana, consolidación, cierre, errores y cancelación.
Continuo: límites, renovación, transcript, evaluación final y reanudación.
B: reservas, contexto, conflictos, publicación parcial y declaración verificable.
Progreso: objetivo inmutable, paquetes parciales, informes fallidos y recuperación.
Comunes: transacciones, contratos, CLI, campañas offline, imports y artefactos.

Base comprobada antes del cambio: 312 pruebas seleccionadas aprobadas, mypy en
45 archivos y pip check correctos. Suite completa detenida en recopilación por
el test huérfano. Estos checks no son aceptación semántica o financiera.
