# Integración de conocimiento delegada — tres casos fijos

Fecha: 2026-11-01. Ejecución autorizada por el usuario tras implementar B opcional.
Estado: tanda ejecutada; [hallazgos y límites](findings.md).

## Pregunta y condiciones

Observar si A utiliza B para conservar avances y qué ocurre con los fundamentos,
coherencia, recuperación y coste. Es una tanda exploratoria: una ejecución por cada
uno de los [tres casos fijos](../casos-fijos/protocol.md), sin control contemporáneo.
No permite atribuir causalidad ni demostrar superioridad frente a E1.

Se conservan literalmente sus tres preguntas y mandato. Estado nuevo y separado
por caso; ejecución en tres procesos, perfil efectivo OpenAI `gpt-6-luna`, salida
máxima 16000 tokens, Findata de solo lectura, web y Python disponibles, sin objetivo
JSON ni simulación. La diferencia declarada es `--knowledge-agent on`: A conserva
lectura e investigación y delega la escritura de avances en B. Ambos usan el mismo
perfil con contextos independientes.

Por caso: 100 llamadas ordinarias **incluyendo B**, 200 herramientas agregadas,
300 segundos por operación de A, contexto máximo/umbral 524288/262144 bytes.
Autorrevisión y revisión externa siguen siendo adicionales y se informan aparte.
Sin timeout global nuevo. B mantiene sus límites de 6 llamadas, 12 herramientas,
90 segundos y 128 KiB por encargo, subordinados al padre/fase y con reserva para A.
Los timeouts del proveedor se fijan en el proceso a 180/180 segundos mediante
`LLM_TIMEOUT_SECONDS` y `LLM_CALL_BUDGET_SECONDS`; no se modifica `.env`.

Se congelan antes del lanzamiento código/prompts, diff y metadatos no secretos de
perfil, dependencias y entradas en el destino local. No se modifica el runtime ni
se reinician automáticamente los casos durante la tanda. Se conservan errores,
interrupciones y estados parciales. La captura nativa es local e ignorada.

```powershell
$env:LLM_TIMEOUT_SECONDS = "180"
$env:LLM_CALL_BUDGET_SECONDS = "180"
.\.venv\Scripts\python.exe scripts/run_fixed_cases.py --output artifacts/agente-conocimiento-tres-casos-100-20261101 --knowledge-agent on
```

## Revisión prevista

- Cierre, integridad de captura, total LLM, fases, roles, herramientas y duración.
- Adopción de B: encargos, escrituras confirmadas, ausencia de cambios, errores,
  interrupciones y consumo por encargo; comprobar que no se ocultan llamadas hijas.
- Lectura de respuesta final, agenda y documentos materiales por caso: qué se logró,
  qué quedó pendiente y contradicciones observables entre lo guardado y la respuesta.
- Fuentes y cálculos: distinguir referencias disponibles, ejecución determinista e
  inferencia económica; no validar afirmaciones por tener una cita o hash.

No premiar número de archivos, delegaciones o agotamiento de presupuesto. La revisión
final será acotada por la evidencia inspeccionada y separará hechos operativos,
observaciones semánticas e hipótesis. No es validación de recomendaciones o inversión.
