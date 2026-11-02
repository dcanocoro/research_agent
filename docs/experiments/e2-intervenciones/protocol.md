# E2 — control ligero mediante intervenciones

Fecha: 2026-11-01. Implementación autorizada; campaña real no ejecutada.
La [entrega](../../deliveries/2026-11-01-e2-interventions.md) registra verificaciones.

## Pregunta e intervención

¿Un bucle ReAct con intervenciones oportunas mejora integración de resultados,
continuidad y coherencia con un coste proporcionado frente al controlador por fases?
Es un cambio del conjunto del controlador: no aísla causalmente cada mecanismo.

E2 sustituye el continuo del mismo A: retira autorrevisión fija y consolidación obligatoria,
mantiene herramientas ordinarias, introduce report_work y evaluación independiente por
eventos, y aplica techo LLM total. No modifica FinMate, el conocimiento financiero ni
los contratos de escritura E1. No añade grafo de dependencias o supervisor económico.

La referencia del control es Git `690313ced9c6311512f5623a90c20521bca458b2`.
No se mantiene una segunda implementación seleccionable dentro del runtime E2.

## Condición efectiva

Política `interventions-e2-v1`, congelada con su instrucción en runtime.json:

- Evaluar ante cambio de evaluación identificada, hito/bloqueo declarado o repetición
  posterior a aviso; separación mínima de cinco llamadas del investigador y respaldo de veinte.
- Objetivo formal: evaluador por criterios; sin objetivo: revisor general. Mismo perfil,
  contexto separado, sin herramientas ni escrituras. Fallos cuentan y no se reintentan inmediatamente.
- Renovación técnica con contexto protegido y cola de intercambios íntegros, intentando
  dejar 16 KiB de margen. Texto emitido y resultados mantienen referencias recuperables. Si hay
  resultados pendientes/desconocidos o texto sin tratamiento declarado, hasta dos llamadas
  ordinarias de checkpoint. Conservar referencias aunque no se resuelva integración.
- Observaciones operativas y reconciliación deduplicadas; versiones diferentes son
  cambios observables, no contradicciones económicas demostradas.
- report_work es puntual: comunica hito/bloqueo o tratamiento pendiente/integrado/irrelevante,
  referencias, documentos/versiones y motivo. Integración exige documentos actuales;
  la validación no acredita corrección semántica. No hay obligación por turno.
- Últimas cinco llamadas: aviso de cierre. Última llamada reservada a evaluación final;
  presupuesto inicial uno: priorizar investigador. Techo incluye todas esas llamadas.

Las políticas se componen explícitamente en Python y pueden retirarse en contrastes
posteriores. Las garantías de tamaño, presupuesto, integridad y cancelación permanecen.
Un cambio de composición requiere conservar el diff e identidad efectiva: no se etiqueta
como misma condición. Evaluación por eventos y reconciliación pueden retirarse de POLICIES;
checkpoint semántico puede contrastarse con su constante a cero, manteniendo renovación segura.

## Contraste futuro: seis ejecuciones mínimas

Usar los [tres casos fijos](../casos-fijos/protocol.md): analista, Microsoft e infraestructura
de IA, cada uno bajo control y E2, con estados iniciales equivalentes y directorios distintos.
No compartir memoria. No crear objective.json para estos encargos. Conservar mandato y
preguntas exactas; report_work, instrucciones técnicas y renovación son parte del tratamiento.

Antes de lanzar, congelar código/diff, wheel, schemas, instrucciones, perfil efectivo y datos
iniciales. Verificar perfil gpt-6-luna sin sustituciones automáticas. Presupuesto propuesto:
100 llamadas LLM gestionadas totales, 200 herramientas, timeout operativo 300 s y contexto
máximo/umbral 524288/262144 bytes. Timeouts de proveedor 180 s como en E1, por proceso,
sin editar .env. No imponer duración global adicional en los casos fijos.

El control archivado necesita una adaptación presupuestaria exclusiva antes de comparar:
aplicar el techo total también a revisión/consolidación y a la evaluación final, sin alterar
sus fases o instrucciones. Conservar y revisar ese diff por separado. No usar directamente
las 100 llamadas ordinarias históricas como presupuesto equivalente a 100 totales E2.
Esta entrega no implementa ni ejecuta ese checkout de control; es prerrequisito de lanzamiento.

Los datos congelados permiten un contraste más controlado. Si se mantienen Findata/web
en vivo, conservar respuestas y fechas, alternar orden control/E2 entre casos y declarar
la variación de fuentes. Las seis ejecuciones son exploratorias; repetir condiciones
antes de atribuir diferencias al mecanismo. No descartar errores ni interrupciones.

## Rúbrica y aceptación

Examinar con referencias concretas, por caso y condición:

| Dimensión | Evidencia |
|---|---|
| Recursos | LLM total y por propósito, herramientas, tiempo, intentos del proveedor; coste/tokens solo observados |
| Administración | Trabajo real de guardar/recuperar/revisar, también dentro de llamadas ordinarias |
| Continuidad | Fundamentos, incertidumbres y pendientes recuperados tras renovación; material perdido o desconocido |
| Integración | Dato nuevo incorporado, descartado con motivo o aplazado; coherencia de escenarios y juicio |
| Investigación | Materialidad, fundamento, fechas/unidades, cálculos y revisión de hipótesis |
| Cierre | Concordancia entre documentos, agenda y respuesta; insuficiencia explícita y pendientes fieles |

Clasificar suficiente/parcial/insuficiente/no evaluable, con pasajes y versiones; no sumar
una puntuación única. Considerar prometedor menor coste administrativo en al menos dos
pares sin deterioro material detectado en ningún caso; es criterio exploratorio, no prueba
estadística de equivalencia. Cero llamadas llamadas consolidación no demuestra ahorro.

La aceptación técnica exige contabilidad completa, recuperación, integridad y pruebas
locales. No demuestra continuidad semántica, decisiones correctas ni rentabilidad.

## Procedencia y disponibilidad

Código, protocolo y entrega son portables. artifacts/ conserva únicamente comprobaciones
locales ignoradas. No hay capturas de campaña E2, hallazgos financieros ni evaluación
independiente inventada. Las campañas reales requieren un encargo posterior.
