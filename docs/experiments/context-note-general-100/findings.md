# Prueba abierta de nota de continuidad — 2026-11-04

## Condiciones y alcance

El usuario autorizó una campaña de propósito general con 100 llamadas para investigar
empresas, construir expedientes y evaluarlas. Es exploratoria: sin control contemporáneo
ni rúbrica financiera nueva. Se comprueba operación, captura, persistencia y renovación;
no superioridad causal ni calidad de inversión.

Entrada: mandato de `campaigns/regimenes/mandato.md` y encargo abierto de
`campaigns/casos-fijos/analista.md`, añadiendo construcción/revisión de expedientes.
Estado nuevo, continuo E2, `--context-note`, sin Progress ni B, sin Python opcional.
Modelo efectivo `openai/gpt-6-luna`; timeouts de proveedor y presupuesto por llamada
de 180 segundos. Umbral 262144 bytes, máximo 524288; reserva de salida ordinaria
128000 bytes. El trigger semántico de Progress no se prueba en esta campaña.

Captura local ignorada:
`artifacts/context-note-general-100-20261104-204853/`.

## Primera tentativa: observación

Run `2026-11-04-general-100`, ID `aef7f048-e832-4f2b-a5b6-49a93e2ef828`.
Terminó con `operational_failure` / `LLMTruncated` en la llamada 32, al solicitar
la cuarta nota con límite de salida de 1024 tokens. El adaptador instalado lanza
`infra.llm_errors.LLMTruncated` cuando la respuesta no termina por
`max_output_tokens`; esa clase no deriva de `OperationalFailure`, por lo que el
fallback de notas no la capturó. No es prueba de falta de contexto de entrada.

Consumo: 19 llamadas de investigación, 8 de checkpoint, 4 de nota y 1 de revisión;
27 herramientas. Hubo tres notas válidas incorporadas y tres renovaciones por tamaño:
328215 → 224463, 329967 → 231894 y 329797 → 218224 bytes presupuestados, conservando
dos intercambios cada vez. Captura sin errores registrados. Se guardaron agenda,
índice, oportunidades y `empresas/DIS/modelo.md`, con 13 materiales. El cribado
declarado fue parcial, con DIS/PG priorizadas y WFC/TSCO aplazadas.

También hubo un `FileNotFoundError` en `report_work`; se conserva en la captura.
La revisión general señaló fuentes parciales, ausencias y periodos no conciliados.
El expediente no constituye una evaluación de inversión completa ni validada.

## Interpretación y corrección acotada

La nota opcional no debe abortar la investigación por truncamiento de su propia
salida. Se corrigió únicamente ese caso tipado para reconstruir sin nota, sin
reintentar ni aumentar los 1024 tokens. Se conservó la tentativa fallida.
La continuación dispuso de 68 llamadas, manteniendo 100 como techo agregado;
recuperó archivos y estado operativo, no el historial completo. Es una trayectoria
interrumpida con corrección entre runs, no una ejecución ininterrumpida ni un contraste.

La corrección captura `LLMTruncated` exclusivamente en la nota. No captura errores
de configuración ni cancelación. Verificación: 32 tests locales de notas y
arquitectura aprobados; mypy sin errores en 70 archivos. No se modificó el wheel.

## Continuación y resultado agregado

Run `2026-11-04-continuacion-68`, ID `e345c120-bbec-409c-860a-819e4454c7ef`.
Terminó `interrupted` / `call_limit`, sin error terminal, tras 68 llamadas y
50 herramientas. La salida del proceso fue 0: cierre operativo por presupuesto,
no cumplimiento de la investigación. La captura no registra errores.

| Medida | Primera tentativa | Continuación | Total |
|---|---:|---:|---:|
| Llamadas LLM | 32 | 68 | 100 |
| Investigación ordinaria | 19 | 28 | 47 |
| Checkpoint | 8 | 24 | 32 |
| Nota de continuidad | 4 | 11 | 15 |
| Revisión general | 1 | 5 | 6 |
| Herramientas | 27 | 50 | 77 |
| Renovaciones completadas | 3 | 12 | 15 |
| Notas válidas incorporadas | 3 | 5 | 8 |

Siete de las quince llamadas de nota terminaron con `LLMTruncated`: una detuvo el
primer run; las seis posteriores reconstruyeron sin nota y continuaron. Otra
renovación omitió la llamada de nota por `call_reserve`. Las 15 renovaciones
completadas son ocho con nota y siete sin ella. Las conversaciones finales contienen
respectivamente una y cero notas: no se acumularon. El coste directo de generar
notas fue el 15 % de las llamadas, incluso cuando fallaron. Los checkpoints mantienen
herramientas y pueden realizar trabajo útil; sus llamadas no son automáticamente
coste perdido.

Persistieron cinco documentos: `agenda.md`, `indice.md`, `oportunidades.md`,
`empresas/DIS/modelo.md` y `empresas/PG/modelo.md`; además, 29 materiales. Hay cribado
y dos expedientes iniciales con hipótesis y pendientes, no una valoración completa
ni decisión de inversión validada. Se conservaron tres
`report_work:FileNotFoundError` y un `record_research_advance:ValueError`. En al menos
una declaración fallida A mezcló referencias de auditoría (`revision-externa/...`)
con referencias del workspace.

La última respuesta reconoce que una nueva extracción parcial del 10-K de DIS no
resolvió los faltantes y que la deuda ya estaba localizada en la nota: no constituyó
un hallazgo nuevo. También declara información pendiente de guardar. No cabe
equiparar notas válidas, persistencia completa y ausencia de repetición.

## Interpretación y límites

El fallback corregido soportó seis truncamientos reales y la reserva evitó una
llamada adicional de nota al cierre. La nota pudo conservar referencias, pendientes
e intentos fallidos, pero no aseguró evitar repeticiones o integrar todo al terminar.
1024 tokens resultaron insuficientes para completar casi la mitad de las solicitudes
de nota con este perfil y estas entradas; no se identifica aquí cuánto correspondió
a razonamiento interno y cuánto a texto visible. No se ajustó el límite durante
la prueba.

Es evidencia diagnóstica para revisar coste, generación y uso de notas, sin mejora
demostrada frente a E2: no hubo control contemporáneo, hubo interrupción y corrección,
y Findata/web son variables externas. No se probó el trigger semántico ni se validaron
inferencias financieras. Conviene contrastar una generación de nota más fiable y
su uso para evitar repeticiones innecesarias antes de ampliar mecanismos. Esto no
autoriza cambiar modelo, límites o estrategia.

Resumen mecánico local: `summary.json` en la carpeta de captura indicada arriba.
La captura íntegra incluye ambos runs y sus prompts/manifiestos; `artifacts/` no es
evidencia portable. Este informe conserva las condiciones y limitaciones.

## Cambio posterior, sin repetición de campaña

El usuario solicitó después ampliar a 5000 tokens la nota y mejorar sus instrucciones.
La [entrega](../../deliveries/2026-11-04-context-note.md) registra el margen de salida,
el límite coherente de texto y la orientación para conservar pendientes y aprovechar
intentos previos. Estos cambios no estaban en los runs descritos aquí; su eficacia
semántica no ha sido contrastada en otra campaña.
