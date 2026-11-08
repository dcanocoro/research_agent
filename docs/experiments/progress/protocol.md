# Progress: investigación por compromisos verificables

Fecha: 2026-11-03. Estado: implementación local; contraste real pendiente.
Encargo autorizado: sustituir la selección activa V8 por el mecanismo mínimo de
objetivo, evaluador y controlador, independiente de B y combinable con continuo.

## Mecanismo y límites

Un único ReAct conserva libertad de herramientas y orden de trabajo. El objetivo
define suficiencia; una llamada semántica evalúa criterios, brechas y 2–4 alternativas,
priorizando reducción de una brecha material respecto al esfuerzo y valor informativo.
El controlador entrega un compromiso con resultado observable y verificación, y
reevalúa tras hasta 15 llamadas de A o una entrega/bloqueo anticipados. No es A* formal.

CLI: `--progress`, `--objective PATH`, `--progress-step-calls 15`, `--max-calls 100`.
Sin archivo, una llamada genera el objetivo, fijo entre continuaciones. El total
incluye generación, evaluaciones, intentos fallidos y cierre. No hay porcentajes,
fases financieras obligatorias, subagentes ni nueva herramienta DCF. En continuo
se conservan controles técnicos y renovación, sustituyendo las revisiones semánticas.

El evaluador recibe una vista acotada con versiones y omisiones. Suficiencia exige
referencias persistidas; progreso requiere además soporte en un resultado cambiado,
con explicación semántica. Un hash distinto no demuestra calidad. Una tentativa
sin progreso debe reconsiderarse antes de continuar. Desde el 2026-11-07, una evaluación inválida admite un intento de reparación
si quedan recursos; si sigue inválida, detiene el control y conserva el último estado válido; no inventa cumplimiento ni bloqueo.

El estado operativo y hasta 20 compromisos recientes quedan en `progreso/estado.json`
del run; las capturas completas de evaluaciones conservan el resto del historial.
La continuación recupera únicamente el mismo workspace y reevalúa el conocimiento.
Un objetivo explícito distinto abre otra serie. V8 no se migra automáticamente.

## Contraste preparado

Comparar ReAct convencional frente a ReAct con progress, usando los mismos encargos,
estado inicial, herramientas, modelo y presupuesto total. Primero contrastar sin
continuo; una comparación posterior puede fijar continuo en ambas condiciones.
Usar las mismas entradas de `campaigns/casos-fijos` y fijar antes de lanzar el objetivo
y la rúbrica por encargo. La campaña de negocio `progreso` no equivale a una
evaluación financiera completa y no debe puntuarse como si la solicitara.

Revisar, por separado:

- Llamadas y coste hasta la primera evaluación financiera completa para encargos que la pidan.
- Valoración reproducible: datos, periodos, unidades, supuestos y cálculo recuperable.
- Consultas redundantes y compromisos sin cambio verificable relevante.
- Reorientación cuando aparecen brechas, contradicciones o cálculos insuficientes.
- Fundamento, coherencia e incertidumbre de las conclusiones, con revisión independiente.

Conservar fallos, interrupciones y límites de contexto. Ni los estados del evaluador
ni los tests locales prueban estas hipótesis. No se ha ejecutado el contraste en
esta entrega ni se han registrado hallazgos financieros.
