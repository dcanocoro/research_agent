# Microsoft: evaluación provisional producida, decisión todavía incompleta

Fecha: 2026-10-31. Campaña autorizada con esta pregunta literal, conservada sin
reformulación en petición, objetivo y captura:

> Evaluar si Microsoft merece una inversión a cinco años al precio de referencia, frente a esperar, con fundamentos, escenarios, riesgos y condiciones de revisión

El [protocolo](protocol.md) fijó condiciones antes del lanzamiento. Se consumieron
las **100 llamadas ordinarias**, sin fallo operativo ni exceso de agenda. Se produjeron
modelo, valoración con escenarios cuantificados y evaluación provisional. El juicio
del investigador fue esperar, con confianza baja; **no constituye recomendación validada**.
Los escenarios no se actualizaron por completo con los últimos datos recuperados.

## Captura y condiciones

Campaña local (`artifacts/evaluacion-msft-v1/campana-100-llamadas/README.md`; referencia local histórica),
resumen mecánico (`artifacts/evaluacion-msft-v1/campana-100-llamadas/resumen-observacion.json`; referencia local histórica),
trayectoria (`artifacts/evaluacion-msft-v1/campana-100-llamadas/trayectoria-cobertura.json`; referencia local histórica),
comprobaciones escogidas (`artifacts/evaluacion-msft-v1/campana-100-llamadas/comprobaciones-locales.json`; referencia local histórica)
y replay (`artifacts/evaluacion-msft-v1/campana-100-llamadas/replay-escrituras.json`; referencia local histórica)
son locales e ignorados; no son portables por enlazarlos. La carpeta conserva definición,
instrucciones, código propio, perfil/wheel identificado, materiales, eventos, snapshots,
conversación y payloads originales. No se copian implementaciones compartidas de FinMate.

Estado nuevo y una empresa fijada por el usuario. Findata en solo lectura, Tavily,
aritmética y Python habilitado; sin cartera ni órdenes. Precio de referencia comprobado
en preflight: **535,07 USD, cierre 9-oct-2026**, no cotización del día. OpenAI
`gpt-6-luna`, medium, salida 16000, timeout/presupuesto del proveedor 180 s. Una tentativa:
50 llamadas de investigación, 50 de consolidación, cinco autorrevisiones y tres
evaluaciones externas: **108 LLM y 95 herramientas**, 1190,921 s (19 min 50,9 s).

El run termina `interrupted: call_limit` y la CLI retorna 0; el organizador conserva
`failed` porque no hubo `completed`. No es un fallo operativo ni prueba de cumplimiento.
Inspección nativa: `capture_complete=true`, sin errores de captura. Las 108 llamadas
del proveedor registran éxito. Tokens disponibles: 2706867 entrada y 100396 salida;
caché y razonamiento son desgloses y no se suman de nuevo a esos totales.

## Trayectoria y artefactos

El agente obtuvo datos y contexto corporativo, creó pronto los tres documentos y
revisó el juicio durante la investigación. Detectó incompatibilidades del snapshot,
construyó escenarios de crecimiento/FCF y múltiplos terminales, sensibilidades y umbrales
de paridad usando Python. Después incorporó evidencia FY2026 y calculó precio/EPS
y FCF mediante aritmética. No realizó cribado de otras empresas.

| Artefacto final | Contenido / límite |
|---|---|
| `empresas/MSFT/modelo.md` | Modelo económico inicial y fundamentos; menor actualización que valoración/evaluación. |
| `empresas/MSFT/valoracion.md` | Escenarios, sensibilidad, supuestos y cálculos; base FY2025 no reemplazada en todos los resultados. |
| `empresas/MSFT/evaluacion.md` | Juicio provisional de esperar, riesgos y revisión; adendas con resultados nuevos y pasajes antiguos aún no depurados. |
| `agenda.md` | 2889 bytes; reconoce el cálculo resuelto y prioriza actualizar escenarios sin buscar más evidencia para esa operación. |
| 30 materiales | Fuentes, tres ejecuciones Python y cinco cálculos aritméticos conservados. |

33 escrituras: una en investigación y 32 en consolidación. La consolidación sigue
consumiendo el 50 % de llamadas ordinarias. 14 renovaciones y 17 errores de herramientas,
incluidos selectores, versiones y sustituciones exactas rechazadas. Replay local:
31 mutaciones, 18 aceptadas y 13 rechazadas; los cuatro archivos finales coinciden
por SHA-256. No se alteró el conocimiento manualmente ni el runtime durante el run.

## Evaluación externa y adaptación

| Revisión | Cobertura | Distancia | Utilidad según evaluador | Evidencias omitidas |
|---|---:|---:|---|---:|
| Primera | 4/5; una no evaluable | Sin nueva distancia | No | 1 |
| Segunda | 4/5 | 20 % | No | 5 |
| Final | 3/5 | 40 % | No | 6 |

La primera no pudo juzgar todo el texto recortado. La segunda identificó que, con
CFO y PP&E FY2026 ya disponibles, el impedimento era calcular FCF y aplicarlo a los
escenarios. Tras el feedback hubo cálculos y escrituras: FCF FY2024/25/26 de
74071/71611/66987 millones USD. La revisión final reconoce ese avance y mantiene
el mismo impedimento en su parte decisiva: actualizar FCF por acción, escenarios y
sensibilidades y revisar el juicio. Reabre `precio_referencia` ante esa falta de propagación.
La subida de distancia es una corrección del evaluador, no necesariamente deterioro
del conocimiento. No alcanzó tres evaluaciones completas consecutivas de estancamiento.

Esta vez existe una adaptación observable y un producto más cercano a la pregunta,
pero la revisión no considera resuelta la decisión. La aritmética escogida reproduce
los tres escenarios declarados y las restas de FCF, no verifica la calibración de
supuestos, la verdad de todas las fuentes ni una rentabilidad esperable. Además,
FY2025→FY2030 no equivale automáticamente a cinco años desde un precio de oct-2026;
el calendario debe reconciliarse. Dividendos, retorno de esperar y puente de caja/deuda
no están incorporados al modelo ilustrativo. No se ha realizado auditoría financiera exhaustiva.

## Correcciones instrumentales posteriores al cierre

Se detectaron dos límites del mecanismo: la segunda revisión no recibió la primera
como antecedente por ser parcial, y la evaluación activa podía quedar recortada a
4 KiB aun habiendo espacio en el paquete. **Después de cerrar y conservar la campaña**
se corrigieron recuperación de revisión estructuralmente válida, incluida parcial,
y prioridad de evaluación hasta 16 KiB dentro del mismo paquete de 64 KiB. La distancia
sigue usando solo revisiones completas. La vista del investigador sigue limitada a 4 KiB.

Regresión local posterior: 150 pruebas aprobadas, tipado correcto en 42 archivos.
No se repitieron llamadas reales ni se reescribieron informes para simular el efecto
de esas correcciones. Fuentes de arranque y fuentes corregidas se archivan por separado.

**Observación:** se produjo y revisó una evaluación con cálculos, la agenda permaneció
compacta y el evaluador distinguió cálculo de búsqueda. Persistieron fricción de edición,
consolidación costosa y falta de actualización coherente de la conclusión.

**Interpretación:** hay señales de orientación al resultado, sin aceptación de utilidad
decisoria completa. Cambian empresa, alcance, criterios e instrucciones frente a V8 real:
no es prueba causal de superioridad, backtest ni evidencia de resultados de inversión.

## Procedencia y disponibilidad

Consolidación documental del 2026-10-31. Carpeta original: `artifacts/evaluacion-msft-v1`.
Se contrastaron manifiestos, resultados, eventos y snapshots finales disponibles;
los informes locales y los hallazgos anteriores se leyeron como síntesis, sin
repetir sus replays, comprobaciones exhaustivas o campañas.

| Ejecución original | ID | Total LLM / herramientas | Resultado registrado |
|---|---|---:|---|
| `campana-100-llamadas/ejecuciones/2026-10-31-evaluacion-msft-100` | `c91ceb5f-87ea-487d-b411-a7d52d07a069` | 108 / 95 | interrupted |

Las capturas completas son locales y pueden archivarse fuera del checkout; no se
conoce aún su destino externo. Las referencias permiten identificar los originales,
pero no garantizan acceso. Los resultados narrativos se entienden sin esas carpetas;
repetir una auditoría de cifras, fuentes o trayectoria requiere recuperarlas. No se
trasladan payloads privados ni expedientes completos a Git.
