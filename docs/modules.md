# Mapa de módulos y activación

## Dónde buscar

| Ubicación bajo src/research_agent | Responsabilidad |
|---|---|
| core/ | Motor único, contratos neutrales, límites, despacho y cierre |
| storage/ | Workspace y transacciones recuperables |
| observability/ | Capturas, manifiestos y trazas |
| composition/ | Construcción, selección, instrucciones, configuración y metadatos |
| regimes/bounded/ | Ejecución acotada predeterminada |
| regimes/continuous/ | E2, checkpoints, contexto, observaciones y revisión general |
| extensions/deliberation/ | Mandato, agenda y foco |
| extensions/progress/ | Objetivos, compromisos y evaluador vigente |
| extensions/context_note/ | Nota LLM opcional de continuidad |
| extensions/communication/ | Publicación de avances, recordatorio temporal o comunicador independiente |
| extensions/knowledge_agent/ | Delegación y política de B preparado |
| capabilities/ | Estado, aritmética, Findata, web, Python, valoración y simulación |
| instructions/ | Guía de A y especialización financiera |
| experiments/ | Directorios, bloqueo y configuración congelada |
| cli/ | Argumentos y resolución de entradas |

`src/research_campaigns/` permanece fuera del paquete del agente: `definitions/`
posee catálogos; `execution/`, ejecución y almacenamiento; `reporting/`, evidencia e
informes. `campaigns/` contiene entradas y lanzadores, `docs/experiments/` protocolos
e historia, y `artifacts/` salidas locales ignoradas. Las pruebas reflejan estas áreas.

## Qué está activo

| Componente | Predeterminado | Activación y restricciones |
|---|---|---|
| Núcleo, persistencia, captura | Sí | Compartidos por los regímenes |
| Acotado | Sí | Sin --continuous |
| Continuo | No | --continuous; requiere mandato |
| Revisión general | Sí en continuo ordinario | --general-review on/off; Progress la desactiva |
| Deliberación | No | --mandate o entradas de --name |
| Progress | No | --progress o --objective; incompatible con B |
| Nota de continuidad | No | --context-note con continuo |
| Comunicación | No | --communication hook/communicator; alternativas por run, solo investigador principal |
| B preparado | No | --knowledge-agent prepared; continuo de 60, 70 o 100 llamadas |
| Estado, aritmética, Findata, web | Sí en composición estándar | Disponibles; no obliga a utilizarlas |
| Python | No | --python; dependencias opcionales |
| DCF Lab | No | --dcf-config con --new; wheel independiente, configuración congelada, sin simulación histórica |
| Simulación | No | --simulation; sustituye acceso financiero ordinario |

`--name progreso` activa Progress; `--name multiagente` selecciona B si no se indica
modo. Un `objetivo.json` presente se carga automáticamente. `--name` también carga
el mandato. La revisión se configura por ejecución, sin herencia implícita.

Con revisión apagada no se cargan feedback previo ni llamadas/reservas exclusivas
del revisor. Se conservan la persistencia, los avisos operativos y los límites.
`--general-review on` explícito con Progress se rechaza; `off` es compatible.

## Retirado y conservado

V8 ya no ejecuta evaluaciones de cobertura/distancia. Se conservan los formatos de
objetivo, sus hashes y el campo histórico assessment_path, sin revisión decisoria.
No quedan aliases para imports internos antiguos. La API pública de AgentA, petición,
resultado y comandos continúa; los consumidores internos usan las rutas nuevas.

Los protocolos y hallazgos históricos se conservan. Leer una captura antigua no
reproduce su mecanismo. El cambio de fingerprints sigue impidiendo continuar campañas
incompatibles; no se actualizan instrucciones congeladas ni se migran evidencias.
