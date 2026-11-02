# Investigación autónoma con presupuesto de 1.000 llamadas

Fecha: 2026-11-01. Preparación autorizada; sin ejecución en esta entrega.
El encargo sustituye la propuesta conversacional de tres tandas por una única
trayectoria abierta sobre `experiment/fileAgent`, base Git 690313c.

## Pregunta y condiciones

Observar cómo A selecciona, desarrolla, relaciona y revisa investigaciones financieras
con un presupuesto prolongado, y si el trabajo adicional resuelve impedimentos para
producir conocimiento útil. No se asigna empresa ni tarea financiera concreta.

El [mandato](../../../campaigns/investigacion-autonoma-1000/mandato.md) conserva
literalmente el texto del usuario. La [petición](../../../campaigns/investigacion-autonoma-1000/peticion.md)
aclara que el estado inicial es nuevo: la mención del mandato al conocimiento previo
no significa que se hayan importado expedientes. No se seleccionan semillas de campañas.

Se usa A de File Agent con sus instrucciones vigentes y controlador por fases:
investigación, consolidación, autorrevisión periódica y revisión externa general,
sin objective.json. Mantener las instrucciones técnicas
de continuidad y cierre por recursos no obliga a completar una evaluación o recomendar.
No incorporar intervenciones E2 ni cambiar prompts generales, herramientas o wheel.
La única adaptación del controlador es un techo total opcional de llamadas.

Una sola ejecución, un proceso y workspace nuevo; 1000 llamadas gestionadas totales,
incluidos investigación, consolidación, autorrevisión y revisión externa. Herramientas: máximo 2000, Python
habilitado, Findata de solo lectura y Tavily reales; sin simulador, inversiones ni
escrituras financieras. Perfil OpenAI gpt-6-luna, medium, salida máxima 16000;
timeout/presupuesto de proveedor 180 s y límite por operación 300 s. Contexto
máximo/umbral de consolidación 524288/262144 bytes. Sin timeout global adicional.
`--max-calls 1000` conserva el límite ordinario y la política de punto medio;
`--max-total-calls 1000` limita además todas las revisiones, reservando una llamada
para la revisión final. Una ejecución de una sola llamada prioriza al investigador.

La [receta ejecutable](../../../campaigns/investigacion-autonoma-1000/README.md)
usa la CLI nativa existente. No se añade otro controlador, formato de campaña ni
reanudación automática. No cambiar entradas o código durante el run. Conservar
manifiesto, instrucciones efectivas, políticas, hashes/configuración y
capturas nativas; los reintentos internos del proveedor se examinan aparte del techo.
Ante fallo, conservar la tentativa y diagnosticar antes de decidir otra ejecución;
no prometer que 1000 llamadas se consumirán. No reiniciar automáticamente el presupuesto.

## Revisión de la trayectoria

Examinar retrospectivamente los cortes de 100, 300, 600 y 1000 llamadas totales,
o el último punto disponible si termina antes. No pausar, añadir mensajes ni pedir
informes al investigador en esos cortes. Usar eventos, conversación y escrituras
capturadas y checkpoints de `continuidad/indice.json`; no se garantiza un snapshot
exacto en cada corte de llamadas ni después de cada edición.
Declarar desconocido lo que no se pueda reconstruir con esa evidencia.

Aplicar una rúbrica cualitativa con pasajes, referencias y versiones:

| Dimensión | Qué observar |
|---|---|
| Dirección | Elección de preguntas materiales y cambios de foco justificados por aprendizaje, bloqueo o coste de oportunidad. |
| Comprensión | Explicaciones económicas contrastadas; distinción entre evidencia, supuestos, interpretación y ausencias. |
| Evaluación | Cuando haya fundamento, conexión entre negocio, escenarios, cálculos, precio fechado, riesgos y alternativas; insuficiencia calibrada cuando falte. |
| Relación y revisión | Uso de conocimiento anterior y transversal; novedades propagadas a cálculos, evaluaciones y pendientes afectados. |
| Continuidad | Recuperación tras renovar contexto; repetición, pérdida de fundamentos o documentos contradictorios. |
| Recursos | LLM total y por propósito, herramientas, errores, renovaciones, tokens, tiempo y coste solo si están observados. |

Para cada tramo, identificar avances sustantivos, impedimentos resueltos o persistentes
y trabajo repetido. Clasificar las dimensiones como suficiente/parcial/insuficiente/
no evaluable con motivos; no sumar una puntuación única. Separar trabajo administrativo
de integración útil por sus resultados, no únicamente por la etiqueta de fase.
La consolidación restringe herramientas y la autorrevisión no dispone de ellas.

## Interpretación y límites

Progreso posterior al corte 100 sería compatible con una contribución del presupuesto;
repetición sin resolver impedimentos sugeriría que ampliarlo no basta en esta trayectoria.
Ninguno de esos patrones demuestra causalidad. Solo hay una trayectoria, sin repetición
ni control contemporáneo, con datos/web variables y evaluador del mismo perfil.
No es una comparación causal con E1, Microsoft u otras campañas de tareas diferentes.

El éxito no requiere recomendación al terminar ni cobertura de una cuota de empresas.
No premiar documentos, llamadas ni mera amplitud. Separar calidad del conocimiento,
utilidad para decidir, integridad de captura y resultado operativo. call_limit es
interrupción por presupuesto, no resolución; el ensayo no evalúa rentabilidad ni alfa.
No hay hallazgos hasta ejecutar y revisar evidencia. artifacts/ es local e ignorado.
