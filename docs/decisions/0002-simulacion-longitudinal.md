# ADR-0002 — Entorno longitudinal experimental

Estado: Aceptada
Fecha: 2026-10-24

## Contexto

El encargo aprobado pide estudiar colaboración prolongada y cartera ficticia sin
elegir la arquitectura financiera de FinMate ni demostrar alfa. Findata conserva
fundamentales anuales sin fecha de publicación; excluirlos todos impediría el baseline.

## Decisión y alternativas

Reutilizar A y su memoria por archivos. El controlador posee calendario y checkpoints;
un simulador privado posee datos temporales y cartera. Las herramientas calculan una
disponibilidad anual estimada de 120 días naturales tras el cierre cuando falta fecha
real, etiquetándola y sin modificar los registros financieros. No se delega el corte
temporal al modelo.

El escenario inicial comprende 50 empresas y como máximo 10 posiciones, incluyendo
aperturas pendientes. No se añaden evaluador, subagentes, nueva base de datos o
planificador cognitivo. El [protocolo](../experiments/colaboracion-historica-v1/protocol.md)
posee las convenciones operativas.

## Justificación

Decisión explícita del usuario al aprobar el plan revisado. La simplicidad permite
observar continuidad e iniciativa aceptando aislamiento histórico imperfecto. No se
presenta esta elección como un hallazgo experimental.

## Consecuencias

La estimación puede adelantar o retrasar la publicación efectiva, y los datos guardados
pueden contener revisiones posteriores. Web, entrenamiento del modelo, supervivencia
del universo y ajustes de precios limitan inferencias económicas. Revisar estos límites
antes de convertir el laboratorio en un contraste de rentabilidad.
