# Comunicación opcional — 2026-11-11

## Cambio y contrato

Implementación del plan solicitado de comunicación mediante dos modos alternativos,
`hook` y `communicator`, con `off` predeterminado. La composición decora la política
seleccionada, sin modificar el motor ReAct ni propagar comunicación a B o llamadas
auxiliares. Compatible con acotado, continuo y Progress.

Base Git de la entrega: `7ac5ef8`. Sin commit ni cambios en bibliotecas compartidas.

El hook construye instrucciones temporales por petición y utiliza una herramienta
de publicación. El comunicador consume snapshots acotados de actividad confirmada
en una tarea asíncrona, con cliente y presupuesto separados. La publicación común
persiste antes de confirmar y emitir al callback. Los registros y errores permanecen
fuera del conocimiento editable. La [operación](../development.md#comunicación-opcional-de-progreso)
describe activación, umbrales, artefactos y límites de captura.

## Verificación

Pruebas locales con clientes y herramientas simulados: ventanas, caducidad,
publicación fallida, referencias temporales, persistencia, callbacks, snapshots,
presupuesto separado, cancelación, descarte por fase y composición con Progress.
Resultados de las tandas locales:

- Funcionalidad: `python -m pytest -q tests/extensions/test_communication.py`,
  33 pruebas aprobadas, incluidos CLI, renovación y clientes separados con la misma
  configuración de modelo. La factoría compartida cachea por perfil: el comunicador
  usa una identidad propia de perfil para no reutilizar el cliente de A.
- Regresión ampliada de agente, continuo, Progress, nota de continuidad, E2,
  integración B y CLI: 168 aprobadas, una omitida y seis deseleccionadas. Esta tanda
  incluía las primeras 25 pruebas de comunicación; las ocho adicionales se verifican
  en la tanda de funcionalidad anterior.
- Arquitectura de runtime y ejecución persistente: 53 aprobadas.
- `pip check` y `git diff --check`: correctos. `mypy` no está instalado en el entorno;
  no se presenta comprobación estática de tipos como realizada.

La primera tanda ampliada tuvo cinco fallos por entradas de campaña ausentes:
`campaigns/regimenes`, `campaigns/progreso` y `campaigns/multiagente`, tampoco
presentes en el árbol de la base Git. Corresponden a cuatro casos de
`tests/cli/test_named_cli.py` y al parámetro nombrado de
`test_cli_progress_create_and_continue` en `tests/extensions/test_progress.py`.
La repetición excluyó esos tests (incluido también su parámetro no nombrado).
No se crean campañas para resolver esa discrepancia ajena a esta funcionalidad.

Se comprobaron 138 destinos de enlaces locales en los documentos afectados. Uno
ya estaba roto en la base Git: la referencia de desarrollo a
`FinMate/docs/architecture/decisions/0004-shared-runtime-contracts.md`. Los destinos
añadidos por esta entrega existen; no se modifica esa referencia externa histórica.
Sin proveedores reales, bases remotas ni campaña comparativa.

## Límites

El contrato estructurado se solicita mediante prompt y se valida tras la respuesta;
no depende de soporte de schemas nativos del proveedor. Los snapshots son vistas
parciales declaradas y no reconstruyen el razonamiento privado. Las referencias
válidas no certifican fidelidad semántica. El coste sin tarifa observable permanece
desconocido. La independencia del presupuesto no elimina el coste adicional ni el
uso compartido de recursos del proceso.

No se implementan reproducción offline, evaluación comparativa ni cambios en
FinMate. La calidad de comunicación y su interferencia deben contrastarse mediante
un protocolo y una campaña posteriores.
