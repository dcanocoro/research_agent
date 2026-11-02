# E2 — bucle continuo con intervenciones

Fecha: 2026-11-01. Base Git: `690313ced9c6311512f5623a90c20521bca458b2`.
Implementación autorizada, sin commits, cambios en FinMate ni campañas reales.
El [protocolo](../experiments/e2-intervenciones/protocol.md) define contraste y límites.

## Cambio implementado

El continuo mantiene un solo ciclo del investigador con herramientas y cuatro
responsabilidades separables: renovación, evaluación, observación y reconciliación.
Se retiraron las fases intelectuales y la autorrevisión fija. El controlador anterior
se conserva en Git, sin selector ni segunda implementación local.

Las políticas se componen mediante funciones explícitas. La identidad congelada recoge
constantes, instrucción y composición. report_work declara hitos/bloqueos y tratamiento
de referencias con recibos, sin escribir conocimiento ni certificar semántica.
Se conservan herramientas E1, versiones, transacciones, protección de materiales,
cancelación, timeout y captura. El modo acotado conserva sus reglas.

La reconstrucción conserva contexto protegido e intercambios completos. Checkpoint
semántico: hasta dos llamadas ordinarias; texto del investigador y resultados se
archivan con referencias recuperables. Las incertidumbres siguen recuperables al
renovar. El estado operativo se publica atómicamente fuera del workspace y se recupera
por identidad, workspace y mandato; versiones diferentes invalidan declaraciones previas.
No se restaura automáticamente todo el chat ni se reejecutan herramientas.

Evaluación por evento con separación cinco y respaldo veinte; observaciones deduplicadas, con entrega conjunta de hasta 8 KiB por interacción.
La reconstrucción intenta dejar 16 KiB de margen bajo el umbral, conservando siempre
el intercambio reciente imprescindible si solo cabe bajo el máximo duro.
Las versiones revisadas se extraen de documentos realmente incluidos en el paquete,
sin atribuir al evaluador los omitidos. Los informes por evento no se sobrescriben.
Los hallazgos se conservan como pendientes declarados por el evaluador.

Todas las llamadas gestionadas comparten --max-calls. El desglose histórico
llm_calls_by_phase contiene propósitos researcher/checkpoint/evaluator. La CLI añade
--renewal-bytes y mantiene alias obsoleto con rechazo de contradicciones. Se adaptaron
preparación, congelación, lanzador, informes y progreso offline de campañas.

## Verificación local

- Suite general con exclusión del test histórico no coleccionable: 380 pruebas pasadas
  (306,25 s).
- Tras los últimos ajustes de referencias textuales, margen y avisos: 147 pruebas
  afectadas pasadas (47,96 s), con modelos/herramientas simulados.
- Mypy: sin errores en research_agent y research_campaigns (44 archivos).
- La invocación completa de pytest detectó un problema previo de colección:
  tests/test_price_review.py importa scripts/review_historical_prices.py, ausente en
  esta base. No se restaura un script histórico ajeno para ocultar esa limitación.
- git diff --check: sin errores. Enlaces y anclas internos afectados: correctos.
  Persiste una referencia previa a un ADR de FinMate ausente en el checkout hermano;
  no se modificó FinMate. Los logs locales en artifacts/ no son evidencia portable.

Las pruebas del antiguo calendario de fases se sustituyeron por comprobaciones del
contrato E2: techo total, checkpoint acotado, herramientas disponibles, referencias,
continuaciones íntegras, errores, recuperación y evaluación independiente.

## Límites y siguiente paso

No hay campaña E2 ni evidencia de mejora semántica o financiera. Una declaración
integrada puede ser incorrecta; una referencia recuperable no demuestra comprensión.
El controlador no detecta por sí solo contradicciones económicas ni dependencias
generales. La recuperación tras un cierre abrupto solo garantiza lo ya registrado;
no reconstruye razonamiento no comunicado. El volumen total de archivo/estado operativo
no está acotado, aunque las vistas entregadas al modelo sí lo están.

Preparar el control histórico con adaptación presupuestaria exclusiva y conservar
su diff antes del contraste de seis ejecuciones. La entrega no ejecuta ese contraste.
