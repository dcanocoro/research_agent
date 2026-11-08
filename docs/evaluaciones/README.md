# Evaluaciones de Research Agent

Registro de evaluaciones externas posteriores a las campañas. Los protocolos y
hallazgos conservan su ubicación en [experimentos](../experiments/README.md).
Esta carpeta aplica una rúbrica explícita; no sustituye capturas ni acredita inversión.

- [V0 — Progress continuo con y sin nota, 150 llamadas](V0/informe.md).
- [Rúbrica y reglas de evaluación aplicadas](protocolo.md).
- [Hallazgos y procedencia de V0](../experiments/expedientes-findata/baseline-150-findings.md).

V0 designa la campaña. V0-SN y V0-CN distinguen condiciones, una ejecución por condición.
Las tentativas fallidas anteriores se conservan como antecedentes operativos, sin
mezclar su consumo o resultados con las puntuaciones de la pareja final.

## Registro de diseño y configuración

| Ámbito | V0 |
|---|---|
| Pregunta experimental | ¿Qué aporta una nota de continuidad a Progress abierto en investigación continua de expedientes FinData? |
| Hipótesis examinada | La nota puede conservar trabajo aún no integrado tras renovar, con coste adicional. Hipótesis cualitativa examinada retrospectivamente, sin criterio numérico previo. |
| Mandato | Acumular expedientes útiles para comprender riesgos/alternativas de una cartera; autonomía para seleccionar preguntas y empresas. Texto efectivo en el informe. |
| Universo inicial | MSFT 12%, AMZN 10%, GOOGL 8%; 70% sin identificar; horizonte 5 años, riesgo moderado, máximo individual 15%. |
| Ampliación | Permitida; ambos runs permanecieron en las tres posiciones. |
| Presupuesto | 150 llamadas totales por condición, 300 en la pareja, incluyendo checkpoints, evaluaciones, notas y cierre. |
| Modalidad | Dos procesos continuos concurrentes, estados nuevos e independientes. |
| ReAct y Progress | continuous-e2, commitments-v1, objetivo open; tramos de 15 llamadas. |
| Diferencia entre condiciones | context_note false (SN) / true (CN); revisor general desactivado en ambos. |
| Contexto | Renovación 400000 bytes, máximo 524288; sin renovación anticipada por sucesión de compromiso en modo abierto. |
| Workspace | Archivos persistentes separados, sin intercambio de conocimiento. |
| Modelo | OpenAI gpt-6-luna, perfil lab, razonamiento medium, verbosity medium, salida 16000 tokens. |
| Herramientas | state-tools-e1, FinData, aritmética y report_work; schemas y huellas exactas en el informe. Python desactivado; web registrada pero prohibida y no usada. |
| Datos | FinData vivo en solo lectura, corte 2026-11-05 por instrucción; respuestas capturadas. Sin dataset previo congelado. |
| Intervención externa | Sin nuevos encargos ni evidencia programada durante las ejecuciones. |
| Repeticiones | Una por condición; no confundir condiciones distintas con repeticiones equivalentes. |
| Observación | Retrospectiva, referencia 120 con snapshots 118/124 y estado final 150. |
| Evaluación | Rúbrica 1.0 recibida tras el cierre; etiquetas visibles, sin segundo evaluador. |

## Registro de resultados y decisiones

| Elemento | V0 |
|---|---|
| Ejecución realizada | 2026-11-07; evaluación con esta rúbrica el 2026-11-08. |
| Llamadas consumidas | 150 SN y 150 CN; ambos interrupted / call_limit, error final nulo. |
| Resultado global | Conocimiento descriptivo/comparativo útil y juicios provisionales; no valoración comparable ni decisión de inversión validada. |
| Capacidades más sólidas | Evidencia fechada, cálculos recuperables, distinción consolidado/segmento e integración progresiva. |
| Principales fallos | Reconciliación costosa, pendientes obsoletos, bloqueo demasiado amplio en CN y respuesta final poco representativa. |
| Perfil D1–D5 | 2/4 funcional por dimensión, condición y corte, con justificaciones distintas. Sin media ni clasificación numérica entre brazos. |
| Evolución | Progreso material inicial en ambos. SN suma comparación FCF y deja inversión incompleta; CN integra matriz de margen/capex y crecimiento. |
| Progreso marginal | Limitado en el tramo final SN; material por integración/contraste en CN, sin causalidad ni atractivo de inversión demostrado. |
| Coste y eficiencia | SN 31 min 6 s / 29 renovaciones; CN 36 min 56 s / 22. Notas: 21 llamadas, 14% del techo CN. Entrada +17,4% y salida +27,3%; precio no disponible. |
| Conclusiones sustentadas | 20 notas válidas llegan al siguiente contexto; varias conservan cifras que después se integran. Síntesis final CN más completa para inversión/caja. |
| Limitaciones | Una ejecución por brazo, fuente viva, trayectorias distintas, rúbrica posterior, cortes desfasados y sin auditoría financiera externa completa. |
| Decisión registrada | Conservar V0 como referencia observada. Las tres propuestas del informe son hipótesis; no se acuerda cambio arquitectónico ni se lanza nada. |
