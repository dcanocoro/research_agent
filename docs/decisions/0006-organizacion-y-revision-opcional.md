# ADR-0006 — Organización por responsabilidades y revisión general opcional

Estado: Aceptada
Fecha: 2026-11-05

## Contexto

El usuario aprobó retirar V8, organizar el código por responsabilidad, conservar y
aislar las extensiones y eliminar aliases. Eligió poder desactivar la revisión general,
conservándola activada por defecto. Esta decisión procede del encargo, no de resultados
comparativos nuevos. El mecanismo activo por objetivos es Progress.

## Decisión y alternativas

Mantener un único motor ReAct y composición explícita. Separar núcleo, persistencia,
captura, regímenes, extensiones, capacidades y gestión experimental. Campañas continúa
como paquete hermano. Retirar V8 y aliases internos, preservando el contrato vigente de
objetivos y la lectura de estado histórico necesaria. No añadir plugins ni migraciones.

Añadir ContinuousConfig.general_review=True y --general-review on/off. La revisión
puede omitirse en continuo conservando checkpoints, reconciliación y cierre técnico.
Progress desactiva la revisión general y conserva su evaluador. No cambiar presupuestos
ni opciones de otras extensiones. Registrar selección solicitada y efectiva por run.

La alternativa era conservar revisión obligatoria e imports históricos; el usuario
eligió revisión opcional y eliminación de aliases. Se modifica la obligatoriedad de
[ADR-0004](0004-revision-periodica.md) y la compatibilidad de rutas de
[ADR-0005](0005-nucleo-react-extensiones.md), conservando el motor único.

## Justificación

La separación permite localizar activación y propietarios y probar fronteras sin
cargar extensiones. La retirada de V8 responde a su sustitución por Progress; no afirma
que Progress produzca mejor investigación. La revisión opcional permite seleccionar
su coste y comportamiento de forma explícita.

## Consecuencias

Cambian imports internos y fingerprints. Se conservan comandos, copias congeladas y
bytes de runtime.json. Campañas incompatibles siguen rechazándose. No se reescribe
estado ni se convierte assessment_path en un disparador del mecanismo retirado.
Las verificaciones locales se registran en la entrega; no certifican calidad financiera.
