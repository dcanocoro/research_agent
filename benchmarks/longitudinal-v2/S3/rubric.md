# S3 — Rúbrica longitudinal v2

Rúbrica independiente, congelable antes de una campaña; no suministrar al agente.


## Evaluación longitudinal v2 (solo evaluador)

Aplicar observado/parcial/fallo/N/O, con referencia a respuesta, sequence de herramienta/modelo y revisión de estado. Evaluar juicio financiero, consistencia argumentativa, precisión de revisión, memoria/trazabilidad y eficiencia/complejidad. No sumar puntuación global. El formato Markdown o SQLite no constituye un criterio de calidad.

Por sesión: distinguir lo disponible, lo leído, lo usado y lo conservado. Por trayectoria: contrastar causas de cambios, fundamentos intactos, contradicciones pendientes e historia. Por estado final: verificar juicio vigente, dependencias necesarias y capacidad de recuperar anteriores fundamentos sin acceso a trazas del revisor. Una respuesta correcta no corrige por sí sola un estado incorrecto. N/O requiere explicar la falta de oportunidad o captura; no oculta una omisión observable.

La representación explícita podría facilitar localizar dependientes e historia; una narración fiel con referencias también puede resolver cada dificultad. Evaluar las mismas propiedades económicas en ambas condiciones, sin exigir nombres de entidades, número de relaciones ni una recomendación bursátil determinada. No suministrar esta rúbrica al agente.

| Sesión | Información y revisión esperable v2 |
|---|---|
| 01 | Industrial y Credit iniciales: caja y deuda separadas; 17/14=1,214 industrial es cobertura estática orientativa, no conclusión de solvencia ni ratio que se exija calcular. |
| 02 | Resumen de deuda: reconciliar perímetros, no sumar recursos de Credit libremente. |
| 03 | Fuente indisponible: desconocer covenants no equivale a holgura; 503 simulado no prueba recuperación técnica. |
| 04 | Agosto antes de corrección: no restringida 13 y vencimientos restantes 10; cobertura estática 1,3, insuficiente para asegurar riesgo cero. Horizonte sigue 2031-12-31. |
| 05 | Nueva corrección: inicial no restringida 15, junio 11; coberturas estáticas corregidas 15/14=1,071 y 11/10=1,1. Puente 20-1-4+3-2=16. Revisar liquidez libre y lectura del flujo operativo; no duplicar ajustes ni alterar deuda/Credit. Rechazar atribución histórica de riesgo cero si no consta. |
| 06 | Distinguir cifras publicadas entonces de reexpresadas después: antes de agosto 10 no podía conocerse corrección. Preservar evolución y cálculos originales como superados, sin mantenerlos como cifras vigentes ni fingir que siempre se conoció el error. |

Dependencias privadas: clasificación de caja→liquidez utilizable→cobertura estática→juicio condicionado; reclasificación de flujos→sostenibilidad observada; deuda/vencimientos/Credit independientes de la corrección. Desconocidos: covenants, mínimo operativo y flujos futuros. Error material: tratar reexpresión como salida nueva, sumar dos veces los 2, borrar la historia o concluir impago/ausencia de riesgo sin evidencia. Aceptar distintas valoraciones cualitativas fundadas.
