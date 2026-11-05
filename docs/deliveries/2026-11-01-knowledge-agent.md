> Implementación histórica, sustituida por [B preparado en el checkout original](2026-11-02-b-prepared-original.md).

# Agente de conocimiento opcional

Fecha: 2026-11-01. Base Git: `690313c`, sobre un checkout que ya contenía cambios
de preparación de investigación autónoma y techo total. Se conservan esos cambios.
No se ha hecho commit ni lanzado una campaña o llamada real a proveedores.

## Cambio implementado

La CLI permite crear un experimento con `--knowledge-agent on|off`, desactivado por
defecto. El modo se conserva en `agente-conocimiento.json`; las continuaciones lo
heredan y rechazan cambiarlo. Experimentos anteriores sin configuración permanecen
desactivados. No hay migración automática ni cambios en FinMate o el wheel instalado.

Con B activado, A conserva investigación y lectura y delega la escritura de avances
mediante `integrate_knowledge(task, advance, evidence_refs, scope)`. B reutiliza el
ciclo acotado con contexto e instrucciones propios, herramientas de lectura y
escritura versionada y el mismo workspace. A espera; no hay paralelismo, recursión
ni llamadas periódicas obligatorias. Las guías de ambos roles se copian al crear
el experimento y las instrucciones de B no se incluyen en el contexto de A.

B puede leer dependencias fuera del ámbito de escritura. Se valida todo el lote
contra ese ámbito antes de publicar y se mantienen las protecciones existentes de
rutas, versiones, materiales y documentos. Los diarios de transacción usan la raíz
de ejecuciones del padre, aunque la evidencia hija viva bajo `integraciones/`.
Un fallo de recuperación sigue siendo fatal para la ejecución padre.

Cada encargo permite hasta 6 llamadas LLM, 12 herramientas, 90 segundos y 128 KiB
de entrada serializada, recortados por el presupuesto de padre y fase. Las llamadas
y herramientas de B consumen también los límites agregados. Se reserva una llamada
de A para procesar el resultado. Las llamadas hijas no disparan las revisiones por
contador de investigación de A. El resultado añade `llm_calls_by_role`, conservando
el total real y el desglose por fase del continuo.

Cada hijo conserva manifiesto vinculado al padre, conversación, resultados,
snapshots y trazas. La captura anidada atribuye cada payload una sola vez y restaura
el archivo de destino del padre. Las lecturas de artefactos del padre mantienen la
comprobación de identidad del workspace.

Los recibos se recogen en el runtime antes de capturar resultados. El resultado
distingue estado operativo, resumen y pendientes del modelo, archivos/versiones,
consumo y registro hijo. Las escrituras confirmadas se conservan en el resumen de A
también ante timeout, cancelación o fallo posterior de captura. Agotar llamadas
después de escribir devuelve trabajo parcial, aunque no exista respuesta final de B.

No se añade activación desde campañas. Se adapta únicamente la congelación del
preparador continuo existente para conservar también el nuevo archivo de configuración
desactivado, evitando una regresión en su comprobación de entradas.

## Verificación

Las 26 pruebas locales de `tests/test_knowledge.py` pasan con clientes simulados y
directorios temporales. Cubren A → B → A, composición real de ambos clientes con
el mismo perfil, activación y continuación CLI, ámbito por lote,
protección de materiales, versiones desactualizadas, ausencia de cambios, fallos,
cancelación, expiración real del deadline, presupuestos agregados, consolidación,
captura anidada y conservación de recibos ante fallo de captura.

`mypy src/research_agent src/research_campaigns --follow-imports=silent` pasa sobre
43 archivos. `pip check` no detecta dependencias incompatibles.
`git diff --check` pasa. Los enlaces locales nuevos y sus anclas se han comprobado;
se mantienen dos referencias anteriores a documentos no disponibles del checkout
hermano de FinMate (visión de producto y ADR de contratos compartidos).

La ejecución sin exclusiones de `pytest -q tests` se detiene durante la colección:
`tests/campaigns/test_price_review.py` referencia `scripts/review_historical_prices.py`, que
no existe en este checkout. No se ha recreado ese script histórico como parte de
esta funcionalidad. La regresión restante se comprueba excluyendo ese test.

Resultado final: `pytest -q tests --ignore=tests/campaigns/test_price_review.py --tb=short`
completa **426 pruebas superadas**, incluidas las 26 del agente opcional, en una
ejecución local sin proveedores. Se comprobó además por separado la ruta nueva
tras el cierre de los últimos ajustes de limpieza del presupuesto de delegación.

## Límites e interpretación

Son comprobaciones técnicas con modelos simulados, no aceptación semántica ni
evidencia de mejor investigación, continuidad o resultados de inversión. No se ha
ejecutado el contraste A directo frente a A delegando. No se modifica la estrategia
ni se registra una arquitectura aceptada para FinMate.

Los materiales, fuentes y avances de A siguen siendo datos revisables. Una
referencia existente y un lote estructuralmente válido no prueban el fundamento de
la inferencia económica. Tampoco hay aislamiento frente a editores externos.

Operación: [desarrollo](../development.md#b-opcional-con-contexto-preparado).
Contrato: [arquitectura](2026-11-02-b-prepared-original.md).

## Ejecución posterior autorizada el mismo día

Tras esta implementación, el usuario pidió ejecutar los tres casos fijos con B.
Se añadió el interruptor al lanzador, verificado con 13 pruebas y tipado, y se
ejecutaron tres estados nuevos con 100 llamadas ordinarias compartidas por A/B.
Los [hallazgos](../experiments/agente-conocimiento-v1/findings.md) conservan
contabilidad, limitaciones y resultado: 325 llamadas totales, una actualización de
agenda y ninguna respuesta textual final. Esto no cambia la aceptación técnica
anterior ni establece una mejora semántica.
