# B opcional — resultados de los tres casos fijos

Fecha: 2026-11-01. Tanda exploratoria ejecutada conforme al
[protocolo](protocol.md), con preguntas literales, estados nuevos, `gpt-6-luna`,
Python y fuentes reales. Sin control contemporáneo ni cambios del runtime durante
la ejecución. No se modificaron FinMate, el wheel o `.env`.

## Cierre y recursos observados

Los tres procesos devolvieron código 0 y el runtime cerró con
`status=interrupted`, `stop_reason=call_limit`: presupuesto agotado, no encargo
completado. Cada caso consumió exactamente 100 llamadas ordinarias **incluyendo B**.
Las revisiones adicionales explican la diferencia con el total real.

| Caso | Ordinarias A+B | A, incluidas revisiones | B | Revisiones adicionales | Total LLM | Herramientas A+B | Duración |
|---|---:|---:|---:|---:|---:|---:|---|
| Analista | 100 | 95 | 14 | 9 | 109 | 100 | 469,721 s |
| Microsoft | 100 | 93 | 15 | 8 | 108 | 100 | 661,648 s |
| Infraestructura IA | 100 | 90 | 18 | 8 | 108 | 100 | 660,198 s |

Total: 300 ordinarias, 25 revisiones y 325 llamadas LLM, de las que 47 pertenecen a B.
Las fases de investigación/consolidación fueron 72/28, 67/33 y 68/32 respectivamente;
incluyen las llamadas de B en la fase que delegó. Cada caso tuvo dos revisiones
externas y 7, 6 y 6 autorrevisiones, respectivamente.

Se contrastaron los eventos de cada padre y sus hijos con `resultado.json`: roles,
fases, herramientas y totales coinciden. No hay `capture_errors` declarados ni
referencias ausentes entre los artefactos enumerados por los resultados padre/hijo.
Los 60 archivos de código, prompts y entradas congelados conservaron sus hashes.
Esto verifica contabilidad y archivo; no certifica suficiencia de evidencia o calidad.

## Adopción y persistencia

| Caso | Intentos de delegación | Hijos iniciados | Rechazos por recursos | Lotes de escritura confirmados | Conocimiento modificado | Materiales capturados |
|---|---:|---:|---:|---:|---|---:|
| Analista | 13 | 7 | 6 | 0 | Ninguno | 26 |
| Microsoft | 15 | 8 | 7 | 0 | Ninguno | 41 |
| Infraestructura IA | 17 | 8 | 9 | 1 | `agenda.md` | 21 |

Los 23 hijos cerraron como `interrupted:budget`. En 22 casos la delegación ocurrió
durante consolidación: 19 hijos recibieron dos llamadas efectivas y tres recibieron
una. Solo el primer hijo de IA se invocó durante investigación con seis llamadas;
fue también el único que publicó un cambio, en la agenda. El límite nominal de seis
llamadas no fue el presupuesto efectivo de la mayoría de encargos.

Los 22 rechazos de A devolvieron `Insufficient resources for delegation and a parent
continuation.` y no iniciaron B. Además, los hijos tuvieron ocho errores de
`inspect_state` por rutas que escapaban al workspace (3/3/2 por caso). A tuvo dos
`FileNotFoundError` en `list_files`, uno en analista y otro en Microsoft. Estos errores
se conservaron y no detuvieron los casos; no hubo reintentos automáticos del lanzador.

En analista y Microsoft la agenda final es idéntica a la plantilla inicial: sigue
indicando que no hay investigación seleccionada. No se crearon documentos de empresa
ni síntesis de conocimiento. En IA solo permanece una agenda con un avance temprano,
incertidumbres y siguiente acción; no hay expediente sectorial ni tesis final guardada.
Los materiales automáticos son fuentes/resultados capturados, no una integración
semántica equivalente a esos documentos.

Ningún caso emitió una respuesta textual ordinaria o de consolidación que quedara
como `AgentResult.answer`; por ello no existe `respuesta.md` en los tres padres.
No es una referencia perdida de captura: el campo `answer` es nulo y el runtime
vigente no fuerza una respuesta final al agotar llamadas. Las revisiones externas
están archivadas aparte y no sustituyen esa entrega.

## Interpretación y alcance de la revisión

En esta tanda la delegación estuvo disponible y se utilizó, pero no consiguió una
conservación suficiente del trabajo. La observación principal es el desajuste entre
el momento elegido por A y los recursos efectivos del encargo: delegación tardía,
una o dos llamadas para B y nuevas solicitudes cuando ya no quedaba margen.
El contexto nuevo de B y las lecturas/errores iniciales consumieron ese presupuesto.

Esto es una explicación compatible con las trazas, no una demostración de que B
sea inferior al agente directo. Tampoco prueba que simplemente ampliar su presupuesto
resolvería el problema. La hipótesis para otro encargo sería dar una oportunidad
realista de integrar antes de perder el contexto y comprobar si A la aprovecha,
manteniendo explícito el presupuesto total. No se aplica aquí ninguna corrección,
nueva campaña ni elección arquitectónica.

La revisión se limita a contabilidad, cierres, errores, recibos, snapshots, agendas
y ausencia de entregas finales/documentos. No se ha auditado toda la conversación,
cada fuente, cálculo o afirmación financiera. No se puede concluir calidad inversora,
rentabilidad o superioridad frente a E1, cuyas fuentes y ejecución no son un control
equivalente. La resolución sustantiva de los tres encargos no queda acreditada.

## Evidencia local y reproducción

Destino local ignorado: `artifacts/agente-conocimiento-tres-casos-100-20261101`.
Contiene `entradas/`, logs separados, los tres experimentos nativos,
`evidencia-preparacion/` y `resumen-operativo.json` con los detalles de cada hijo.
Los padres están en `<caso>/ejecuciones/2026-11-01-<caso>/`; cada uno conserva sus
hijos bajo `integraciones/`. `estado-inicial.json`, `estado-final.json`,
`conversacion-completa.jsonl`, `eventos.jsonl` y `resultado.json` permiten recuperar
el corte. No se enlaza ese directorio como evidencia portable.

Antes del lanzamiento se verificaron 13 pruebas locales del lanzador, su tipado y
`git diff --check`. Se añadió únicamente el paso opcional de `--knowledge-agent on`
a los tres procesos, conservando el comando anterior con el modo desactivado.
