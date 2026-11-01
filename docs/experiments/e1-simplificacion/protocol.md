# E1 — simplificación conjunta del agente

Fecha: 2026-10-31. Implementación, preparación y campaña de tres casos ejecutadas.
Es una ablación sobre el mismo agente, sin variantes ni perfiles E1. Los hallazgos
están en [findings.md](findings.md); la condición simplificada no tuvo control
contemporáneo.

## Pregunta e intervención

¿Retirar vías redundantes de escritura y repeticiones de instrucciones reduce fricción
sin deteriorar análisis ni continuidad? E1 evalúa el conjunto; no identifica el efecto
individual de cada retirada ni simplifica toda la arquitectura.

Punto de partida: Git `493952fa01d5a2839110ff1379488147bbc69102`.
Conservar la revisión y el diff efectivo antes de una ejecución. El código anterior
se recupera desde Git; no hay implementación paralela en el runtime.

| Elemento | Tratamiento | Motivo / responsabilidad conservada |
|---|---|---|
| Cinco escritores alternativos | Retirados del agente y sus contratos | Una sola vía: record_research_advance; creación y edición exacta conjunta ya existentes. |
| Selección legacy/v5 y adopción | Retirada de CLI y APIs internas | Una composición; herramientas.json identifica contrato, no selecciona comportamiento. |
| Lecturas, inventario, búsqueda | Conservados | No mezclar reducción de escritura con ablación de recuperación. |
| Publicación, versiones, integridad y diarios | Conservados | Retirar opciones no elimina garantías de recuperación. |
| Guardado incremental y coherencia | Fusionados en instrucciones generales | Una obligación principal, aplicada durante investigación y cierre. |
| Progreso, bloqueos y coste de continuar | Fusionados en deliberación | Elegir trabajo material sin informes ni pasos obligatorios. |
| Mantenimiento de agenda | Fusionado en deliberación | Conservar secciones, referencias y 8 KiB; retirar pasos superados. |
| Metodología y consecuencias financieras | Condensadas en guía financiera | Mantener negocio, hipótesis, valoración, precio, alternativas y revisión de dependientes. |
| Recetas de herramientas retiradas | Retiradas; ejemplos actuales en contratos y guía | Eliminar instrucciones imposibles y duplicación de manuales. |
| Rigor, fuentes, fechas, unidades y autorización | Conservados | No son objetivos de la ablación. |
| Documentos y convenciones de conocimiento | Conservados | No introducir otra representación en el mismo estudio. |

La única ampliación puntual del contrato de edición permite target vacío sobre archivo
vacío: allí tiene exactamente una coincidencia y permite inicializar contenido con
versión. En archivos no vacíos se rechaza como ambiguo. No es reemplazo ciego.

No se retiran lectores redundantes, supervisión, revisiones, Python, fuentes, agenda,
límites ni documentos de empresa. La reducción textual se mide como descripción del
tratamiento, nunca como prueba de calidad.

## Materiales y condiciones antes de lanzar

Usar los [tres casos fijos](../casos-fijos/protocol.md), sus prompts y mandato sin
modificarlos: analista abierto, Microsoft e infraestructura de IA. Tres ejecuciones
totales, una por caso, sin intercambio de estado ni conocimiento inicial.

- Mismo intérprete y perfil LLM efectivo; verificar y registrar que sigue siendo
  gpt-6-luna antes de ejecutar. Si difiere, detener la preparación y resolverlo, sin
  sustituir el modelo ni presentar la tanda como equivalente.
- Mismo ciclo continuo, fuentes Findata de solo lectura y web, Python habilitado,
  revisiones del runtime y ausencia de objective.json.
- Por caso: 100 llamadas ordinarias, 200 herramientas, 300 segundos por operación,
  contexto máximo/umbral 524288/262144 bytes. Revisiones LLM adicionales se contabilizan
  por separado. Sin timeout global adicional.
- LLM_TIMEOUT_SECONDS=180 y LLM_CALL_BUDGET_SECONDS=180 en el proceso de lanzamiento;
  no modificar .env. Comprobar ambos en los manifiestos efectivos.
- Congelar código y diff, wheel y configuración no secreta, schemas, instrucciones,
  prompts y hashes. No modificar esos elementos durante el lote.

Comando preparado, **no ejecutado en esta entrega**:
```powershell
$env:LLM_TIMEOUT_SECONDS = "180"
$env:LLM_CALL_BUDGET_SECONDS = "180"
.\.venv\Scripts\python.exe scripts/run_fixed_cases.py --output artifacts/e1-simplificacion
```

El destino debe ser nuevo. El [lanzador](../../../scripts/run_fixed_cases.py) conserva
entradas, logs y capturas nativas, sin reintentos automáticos. El retorno del proceso,
integridad de captura y resolución del encargo se evalúan por separado.
Las instrucciones y capturas históricas no se migran: las continuaciones anteriores
requieren código anterior o una migración expresamente autorizada.

## Evaluación prevista

Antes de comparar, extraer de cada captura los mismos campos y revisar con esta rúbrica
los resultados anteriores disponibles. Las cifras del traspaso son contexto aportado,
no una auditoría repetida en esta entrega. Las capturas locales de octubre bajo
`artifacts/mi-experimento-timeout-180` son antecedentes descriptivos, no control equivalente.
Si faltan, registrar comparación no disponible; no reconstruir mediciones de memoria.

| Dimensión | Evidencia y criterio |
|---|---|
| Escritura | Intentos, éxitos, rechazos por categoría, errores por intento y reintentos tras rechazo. Separar errores de lectura, proveedor y captura. |
| Consolidación | Llamadas y tiempo por fase; distinguir escritura, recuperación, errores y trabajo analítico. |
| Recursos | Herramientas, llamadas ordinarias/adicionales, duración y bytes UTF-8 de argumentos de escritura. Coste y tokens solo si están capturados; ausente es desconocido. |
| Fundamento | Afirmaciones materiales respaldadas por fuentes recuperadas, alcance de extractos, fechas, periodos, moneda y unidades. |
| Cálculos y juicio | Fidelidad numérica y referencias a ejecución; supuestos, escenarios y consecuencias económicas explícitos. Una cita no valida inferencia. |
| Continuidad | Avances recuperables y conservación del contenido aún válido; revisiones de hipótesis y dependientes identificables. |
| Coherencia de cierre | Agenda, documentos y respuesta concuerdan; no quedan cálculos realizados descritos como nunca investigados ni pendientes ficticiamente resueltos. |
| Resolución | Pregunta atendida, respuesta parcial o insuficiencia fundada; qué queda abierto y por qué. call_limit no acredita cumplimiento. |

Para fundamento, cálculos/juicio, continuidad y coherencia, clasificar por caso como
suficiente, parcial, insuficiente o no evaluable, con pasajes y referencias concretas.
Suficiente exige evidencia para las afirmaciones materiales examinadas y ausencia de
contradicciones materiales detectadas; parcial indica pendientes explícitos o cobertura
incompleta; insuficiente implica errores o pérdida material no reconocida. No evaluable
requiere explicar qué captura falta. No sumar categorías ni contar documentos como calidad.

Si hay capturas anteriores comparables en esos campos, considerar el conjunto prometedor
cuando al menos dos casos muestren menor tasa de errores de escritura o menos llamadas
de consolidación, sin empeorar el otro indicador en esos casos y sin deterioro material
detectado en análisis/continuidad en ninguno. Informar también duración, texto y coste:
pueden contradecir una aparente mejora. Si faltan denominadores o evidencia de referencia,
no afirmar mejora; describir viabilidad y problemas observados.

Este criterio orienta la siguiente decisión, no es un test estadístico. Registrar
resultados mixtos, fallos, interrupciones y límites; no descartar tentativas fallidas.
Fuentes cambiantes, una ejecución por caso y cambio conjunto impiden atribución causal.
Una evaluación favorable no demuestra rentabilidad ni valida decisiones de inversión.

## Verificación y siguiente paso

La [entrega](../../deliveries/2026-10-31-e1-simplification.md) conserva los checks
locales y el [registro de hallazgos](findings.md) conserva los resultados observados.
No sustituyen aceptación semántica ni demuestran mejora causal. Antes de otra campaña,
decidir si se requiere un control contemporáneo; si se mantiene un solo cambio por
estudio, formular el siguiente experimento como una intervención aislada sobre el uso
de selectores y edición. No cambiar automáticamente el agente por una puntuación o el
agotamiento del presupuesto.
