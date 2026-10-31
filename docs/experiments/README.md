# Registro de experimentos y hallazgos

La [metodología](../experiments.md) define el contraste y la [estrategia](../strategy.md)
la pregunta vigente. Implementación, ejecución y aceptación se registran por separado.
Una campaña exploratoria real no completa automáticamente un contraste controlado.

## Registro consolidado al 2026-10-31

| Pregunta / intervención | Implementación o preparación | Ejecución y resultado | Límites y registro |
|---|---|---|---|
| Evaluación decisoria Microsoft | Objetivo V8 con evaluación activa e impedimentos | 100 ordinarias, 108 LLM; evaluación provisional y escenarios, actualización incompleta | [Protocolo](evaluacion-msft-v1/protocol.md) y [hallazgos](evaluacion-msft-v1/findings.md). Correcciones posteriores solo locales; sin recomendación validada. |
| Objetivos y cobertura V8 | Objetivo fijo y evaluador por criterios implementados | Contraste controlado propuesto pendiente; mecanismo ejercitado en campañas posteriores | [Protocolo](objetivos-v8/protocol.md). Distancia condicionada por juicio y fuentes del evaluador. |
| Investigación real V8 | Continuo con objetivo | 144/200 ordinarias, 154 LLM; parada por agenda excesiva; tres evaluaciones sin reducción | [Protocolo](inversion-real-v8/protocol.md) y [hallazgos](inversion-real-v8/findings.md). Sin valoración ni asignación; no contraste causal V7/V8. |
| Investigación real V7 | Resultado de sesión, escritura conjunta y revisión externa | 200 ordinarias, 211 LLM en tres tentativas; seis modelos, sin valoración/asignación | [Protocolo](inversion-real-v7/protocol.md) y [hallazgos](inversion-real-v7/findings.md). Timeouts, cambios operativos y correlación incompleta de primeras tentativas. |
| Continuidad V6 | Agenda activa, protección de expedientes y observación offline | 100 ordinarias, 106 LLM; captura completa, persistencia solo en consolidación | [Protocolo](continuidad-v6/protocol.md) y [hallazgos](continuidad-v6/findings.md). Continuidad semántica parcial; varios factores cambian frente a V5. |
| Herramientas de estado V5 | Operaciones versionadas, expedientes y contratos | Primer intento: 11 llamadas; repetición corregida: 100 ordinarias, 106 LLM | [Protocolo y diseño histórico](herramientas-estado-v5/protocol.md), [hallazgos de ambos intentos](herramientas-estado-v5/findings.md). Adopción observada; integridad y calidad semántica distintas. |
| Operadores Python | Cuatro familias de operadores opcionales | V4 con Python: dos usos autónomos correctos, 63 LLM y 58 herramientas | [Protocolo](python-operators-v1/protocol.md) y [hallazgos](python-operators-v1/findings-v4.md). Contraste sintético controlado pendiente; no valida metodología financiera. |
| Contexto continuo V1–V4 | Renovación, entrega corregida, instrucciones y autorrevisión | Original y repetición: 60 llamadas cada uno; V3: 60; V4 sin Python: 64, incluidas cuatro revisiones | [Protocolo](contexto-continuo-v1/protocol.md) y [hallazgos consolidados](contexto-continuo-v1/findings.md). Corrección instrumental y continuidad parcial; sin causalidad ni decisión inversora. |
| Metodología financiera | Prompts y convención por empresa implementados | Usados en campañas posteriores; contraste específico con control congelado no acreditado | [Protocolo](analisis-financiero-v1/protocol.md). Cambios de instrucciones y representación conjuntos. |
| Intención persistente | Mandato protegido y agenda | Seis activaciones por condición con presupuesto ampliado | [Protocolo](intencion-persistente-v1/protocol.md) y [hallazgos](intencion-persistente-v1/findings-amplio.md). Condición inicial de 18 llamadas sin ejecutar; superioridad no demostrada. |
| Colaboración histórica | Simulador y calendario | Prueba corta de tres activaciones y registro de campaña de 24 activaciones | [Protocolo](colaboracion-historica-v1/protocol.md), [prueba corta](colaboracion-historica-v1/historical-smoke.md) y [precios](colaboracion-historica-v1/price-review.md). Captura larga ausente; contaminación temporal web, sin alfa. |
| Longitudinal sintético | Tres historias de seis sesiones preparadas históricamente | Sin ejecución real acreditada | [Protocolo](longitudinal-v1/protocol.md). Definiciones retiradas del checkout. |
| Benchmark piloto | Cuatro casos preparados históricamente | Checks locales, sin campaña real acreditada | [Protocolo](benchmark-pilot-v1/protocol.md). No aceptación semántica. |
| Baseline NVIDIA | Estado de archivos | Observación inicial concluida | [Hallazgos retrospectivos](baseline-nvidia-2026-10-18/findings.md). Sin protocolo previo ni control. |
| E001 / E002 | Modo de expedientes retirado | Persistencia inicial insuficiente; conservación y recuperación posterior con límites | Antecedentes recuperables desde Git, indicados abajo; no describen el runtime actual. |

## Aprendizajes transversales y preguntas abiertas

- **Capturar y recuperar no basta para mantener significado.** V1–V4 conservaron
  documentos y renovaron contexto, pero también dejaron referencias o pendientes
  desactualizados. La repetición inicial corrigió una redirección de resultados;
  no resolvió por ello la revisión entre documentos.
- **La persistencia incremental sigue abierta.** V4 sin Python tuvo dos escrituras
  ordinarias; V5 repetido, V6 y V7 real concentraron las suyas en consolidación.
  V8 real y Microsoft tuvieron una escritura durante investigación cada uno.
  Son trayectorias observadas, no una tendencia causal demostrada entre versiones.
- **Cálculo correcto y evaluación útil requieren comprobaciones diferentes.** Los
  operadores ejecutaron cálculos recuperables; V3 y V5 también dejaron errores en
  prosa. Microsoft produjo escenarios, pero no propagó todos los datos nuevos al juicio.
- **El feedback depende de lo que recibe y de lo que cambia después.** V4 mostró
  seguimiento parcial de prioridades; V8 mantuvo cobertura sin reducción y sufrió
  omisiones del paquete. Microsoft distinguió cálculo de búsqueda, sin cerrar la
  actualización decisoria. Ningún recuento acredita superioridad inversora.

La [estrategia](../strategy.md) conserva estas preguntas para el siguiente encargo.
Los registros individuales explican controles, desviaciones y límites que impiden
convertir esta síntesis en una comparación causal.

## Cómo mantener el registro

Usar un registro por pregunta o intervención: `protocol.md` para condiciones e hipótesis,
y `findings.md` cuando haya observación. Una repetición conserva fecha, cambios y resultado
del intento original. Los diseños previos se identifican como históricos al consolidarlos.
No crear hallazgos vacíos ni reescribir las condiciones originales con resultados posteriores.

Los hallazgos deben conservar condiciones efectivas, tentativas, fallos, resultado,
interpretación e incertidumbres y una sección de procedencia y disponibilidad. Las rutas
originales de `artifacts/` identifican capturas locales que pueden archivarse fuera del
checkout; no son enlaces portables. No se conoce su futura ubicación externa. El relato
permite entender el experimento, pero no reemplaza los originales para repetir auditorías.
Las pruebas y entregas fechadas no se presentan como verificaciones repetidas hoy.

## Antecedentes E001 y E002

Los cuatro documentos no están en el árbol. Se comprobó que esta revisión Git permite
recuperar sus protocolos y hallazgos, sin restaurar archivos:

```powershell
git show 20afee9:docs/experiments/E001-nvidia-casefile/protocol.md
git show 20afee9:docs/experiments/E001-nvidia-casefile/findings.md
git show 20afee9:docs/experiments/E002-persistent-research/protocol.md
git show 20afee9:docs/experiments/E002-persistent-research/findings.md
```

Las entregas de [expedientes](../deliveries/2026-10-17-casefile.md) y
[conservación](../deliveries/2026-10-17-persistent-research.md) resumen los intentos.
El [baseline](../baseline.md) conserva la transición al estado de archivos. Estos
antecedentes no constituyen aceptación del mecanismo vigente ni de una arquitectura FinMate.
