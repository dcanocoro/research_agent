# Terminación inteligente del ReAct acotado

Montaje experimental independiente de A. No se activa desde su CLI ni modifica sus
prompts o configuración predeterminados. El runner y la política experimental viven
en `src/research_campaigns/termination/`; se retiran junto a esta carpeta, su prueba y
sus referencias documentales. A nunca importa este experimento.

La captura tiene un adaptador local para los dos contratos de trazas de Infra:
la interfaz histórica y `local_trace_capture` del wheel actual. No parchea A ni
la biblioteca instalada. Las tres condiciones usan exactamente el mismo adaptador.

Consultar el [protocolo](../../docs/experiments/terminacion-react/protocol.md).
`cases.json` contiene peticiones, corpus sintético y rúbricas privadas separadas.
Solo petición y corpus se entregan al investigador. `common.md` es común a todos;
`self-control.md` se añade a V1/V2; `checkpoint.md` solo lo recibe el controlador V2.
`rubric.md` es para evaluación posterior, no para dirigir la investigación.

Desde la raíz Git, con el entorno del laboratorio instalado según
[desarrollo](../../docs/development.md):

```powershell
# Validar y preparar: no llama a modelos, web ni bases de datos.
.\.venv\Scripts\python.exe -m research_campaigns.termination validate
.\.venv\Scripts\python.exe -m research_campaigns.termination prepare --output artifacts/terminacion-piloto --repetitions 1

# Consumo real: piloto de dos casos, seis ejecuciones. No ejecutado en la entrega.
.\.venv\Scripts\python.exe -m research_campaigns.termination run --output artifacts/terminacion-piloto --case S2 --case O4

# Tanda completa independiente: 12 casos × 3 condiciones × 3 repeticiones = 108.
.\.venv\Scripts\python.exe -m research_campaigns.termination prepare --output artifacts/terminacion-tanda --repetitions 3
.\.venv\Scripts\python.exe -m research_campaigns.termination run --output artifacts/terminacion-tanda

# Regenerar informe operativo y paquetes de respuestas ciegas, sin modelo.
.\.venv\Scripts\python.exe -m research_campaigns.termination report --output artifacts/terminacion-tanda
```

`--definition` permite otra carpeta de definición antes de preparar. `--case` y
`--condition V0|V1|V2` filtran ejecuciones de un plan ya congelado. No usar filtros
para seleccionar resultados favorables. `prepare` exige destino nuevo. `run` ejecuta
secuencialmente solo trabajos no intentados; no reintenta ni sobrescribe los anteriores.
Un directorio de trabajo incompleto también cuenta como intento y requiere revisión.
Para repetir, preparar otro destino, conservando el anterior. No hay reanudación
interna de una conversación. Un lock existente bloquea procesos concurrentes; tras
un cierre abrupto comprobar que no sigue activo antes de retirar manualmente el lock.

Se congelan definición y hashes de código/wheel al preparar; el perfil LLM efectivo
se fija antes del primer trabajo real y se exige idéntico en siguientes invocaciones.
Cambios en código, definición o perfil exigen campaña nueva. El manifiesto nativo
conserva prompts y schemas efectivos de cada ejecución.

Cada `jobs/ID/` tiene `job.json`, `estado/` y `ejecuciones/`. En estas últimas están
respuesta, conversación, eventos, snapshots y payloads del proveedor. V2 añade
`terminacion/checkpoint-06*` y `checkpoint-12*`. `resultado.json` cuenta A + checkpoint;
`llm_calls_by_role` y `llm_calls_by_phase` separan ambos. El evento nativo `lab.run.*`
cuenta el presupuesto de A; `experiment.termination.completed` registra el total.
`job.json` mide tiempo de extremo a extremo, incluidas revisiones. Tokens y dinero
quedan desconocidos hasta extraerlos de las trazas; no se estiman con número de llamadas.

El retorno de `run` es 1 si algún trabajo recién intentado no completó, 2 ante
configuración inválida y 130 ante interrupción. Una respuesta con `budget` puede
tener estado operativo `completed`; no significa suficiencia. El informe conserva
todos los estados previos aunque una invocación posterior solo ejecute pendientes.

`review/answers/RNNN.json` contiene petición, corpus, rúbrica específica y respuesta,
sin condición ni consumo. Dar estos paquetes y `rubric.md` al juez de respuestas.
`review/mapping-private.json` es para el coordinador, fuera de la revisión ciega.
La trayectoria se evalúa aparte con la conversación y eventos; no hay juez automático
en este montaje. `report` conserva cualquier evaluación manual existente.

La tanda usa archivos y aritmética locales, no el catálogo completo de herramientas
de producción. Esta restricción es común a las tres condiciones. No se crean
clientes Tavily, motor SQLAlchemy, Progress, B, mandato, renovación o nota.
El único servicio remoto usado por `run` es el proveedor LLM configurado.
