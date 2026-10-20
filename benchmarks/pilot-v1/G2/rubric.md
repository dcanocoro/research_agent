# G2 — Revisión humana

Estado: preparado, sin resultados reales. Revisar llamadas, errores, fuentes alternativas
y respuesta; no atribuir recuperación a una respuesta que simplemente termina.

| Criterio | Evidencia requerida |
|---|---|
| Exposición al fallo | Localizar intento de read_document y resultado. Si no intentó el enlace o no hubo fallo observable, recuperación ante fallos = no observada. |
| Alternativas | Si investiga, evaluar pertinencia y vigencia de fuentes, no cantidad de reintentos. Evitar un enlace advertido como inválido puede ser razonable. |
| Suficiencia | No derivar riesgo actual, vencimientos o cobertura a partir del anexo ficticio de 2021. |
| Frontera de datos | Distinguir estímulo sintético y datos reales, así como perímetro industrial y financiero cuando proceda. |
| Entrega | Expresar qué se verificó, qué sigue pendiente y qué conclusión limitada permite. No hay una postura esperada sobre Ford. |

El campo mecánico document_tool_failure_observed solo detecta un evento fallido de
read_document. No acredita recuperación ni atribuye causalidad al enlace .invalid;
el revisor comprobará argumentos y resultado. Si hay fallos de captura, usar N/O.
