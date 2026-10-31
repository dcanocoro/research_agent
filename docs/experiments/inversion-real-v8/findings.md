# V8 real: campaña conservada, interrupción por agenda y cobertura sin reducción

Fecha: 2026-10-31. El usuario autorizó repetir una campaña como V7 y guardarla.
El [protocolo](protocol.md), mandato, rúbrica y [objetivo](objective.json) se fijaron
antes de lanzar. **La ejecución consumió 144 de un máximo de 200 llamadas ordinarias
y se detuvo porque la agenda excedió su límite al renovar contexto.** Captura nativa
completa según el inspector; ese resultado no significa objetivo cumplido.

La campaña local (`artifacts/inversion-real-v8/piloto-200-llamadas/README.md`; referencia local histórica),
el resumen (`artifacts/inversion-real-v8/piloto-200-llamadas/resumen-observacion.json`; referencia local histórica),
la trayectoria de cobertura (`artifacts/inversion-real-v8/piloto-200-llamadas/trayectoria-cobertura.json`; referencia local histórica),
el diagnóstico (`artifacts/inversion-real-v8/piloto-200-llamadas/diagnostico-interrupcion.json`; referencia local histórica)
y el replay de escrituras (`artifacts/inversion-real-v8/piloto-200-llamadas/replay-escrituras.json`; referencia local histórica)
son artefactos locales e ignorados; sus enlaces no los convierten en evidencia portable.
Se conserva además una copia de las fuentes propias del laboratorio con hashes;
el wheel compartido se identifica sin copiar sus implementaciones.

## Condiciones y consumo observado

Estado nuevo; Findata PostgreSQL de solo lectura, web/extracción Tavily y Python
habilitado, sin simulador, cartera conectada ni órdenes reales. Preflight: 503 empresas,
precios para 502 y estados financieros para 501; `transaction_read_only=on`. Los
precios observados llegan al 9-oct-2026, no al día de ejecución. Las muestras de
preflight no se incorporaron al estado ni seleccionaron empresas para A.

OpenAI `gpt-6-luna`, razonamiento medium, salida 16000 y timeout/presupuesto del
proveedor 180 s desde el inicio, como la última tentativa V7. Máximos: 200 llamadas
ordinarias, 300 herramientas, 3600 s; contexto 524288/262144 bytes. La semilla inicial
presupuestó 196070 bytes. No se modificaron runtime, instrucciones ni objetivo durante
la ejecución.

| Fase | Llamadas |
|---|---:|
| Investigación | 71 |
| Consolidación | 73 |
| Ordinarias consumidas | **144** |
| Autorrevisión | 7 |
| Evaluador de objetivo | 3 |
| Total LLM | **154** |

Una tentativa, run `81472841-1a03-42d3-829a-f67588c4ea06`, 140 herramientas y
1387,469 s de lanzamiento (23 min 7,5 s). Las 154 llamadas del proveedor registran
éxito; no fue un timeout remoto. Consumo disponible: 3952256 tokens de entrada y
103670 de salida; caché y razonamiento son desgloses, no cantidades a sumar otra vez.

## Resultado, persistencia y feedback

El investigador eligió AAPL, MSFT, GOOGL, AMZN, CEG y COF, conservando seis `modelo.md`
y agenda, con 59 materiales. Paginar la búsqueda textual `a` amplió la muestra; la
agenda reconoce que sus coincidencias no son el universo completo. Después del aviso
de estancamiento priorizó MSFT/AMZN como contraste de investigación, sin declararlos
oportunidades de inversión seleccionadas. Esto registra un cambio de foco posterior
al feedback, no demuestra causalidad ni utilidad superior.

La última respuesta intermedia es anterior a los últimos cambios de foco: describe
COF exploratoria, sin valoración ni base para asignar capital. No se produjeron
archivos de valoración/evaluación ni una propuesta de asignación. No se ha realizado
una auditoría financiera exhaustiva de los seis modelos.

Hubo 49 escrituras de archivo: una durante investigación y 48 durante consolidación.
La consolidación consumió 73/144 llamadas ordinarias (50,7 %). Los 22 intentos de
escritura conjunta incluyen 20 diarios committed; dos se rechazaron. El replay local,
sin proveedores ni BD, reproduce 36 mutaciones intentadas: 31 aceptadas, cinco
rechazadas y los siete archivos finales coincidentes por SHA-256. Comprueba integridad
de escritura, no fidelidad económica. Hubo además una lectura de artefacto con referencia
inválida; los seis errores de herramientas se conservaron.

| Evaluación | Cubiertos / total | Distancia | Evidencias incluidas / omitidas | Documentos omitidos |
|---|---:|---:|---:|---:|
| Primera | 1/7 | 85,7 % | 7 / 0 | 0 |
| Segunda | 1/7 | 85,7 % | 8 / 9 | 0 |
| Tercera | 1/7 | 85,7 % | 9 / 16 | 1 |

Las tres respuestas fueron estructuralmente completas; cubrieron únicamente
`conocimiento_recuperable`. La tercera devolvió la intervención prevista de justificar
continuidad o cambiar de enfoque. No hubo reaperturas ni fallos del evaluador. Los
paquetes también omitieron 21, 46 y 60 acciones, respectivamente. Sus tamaños fueron
65168, 65224 y 65193 bytes, con parcialidad declarada.

Que el evaluador emita una respuesta completa no implica que haya recibido todas las
fuentes o que su juicio sea correcto. La última distancia es previa al cierre fallido;
no hubo evaluación final después del fallo operativo, conforme a la política V8.

## Interrupción reproducida y límites de interpretación

El modelo dejó `agenda.md` en **8987 bytes**, por encima del límite protegido de
**8192**. Al reconstruir contexto, `deliberative_context` lanzó `ValueError`:
`agenda.md exceeds 8 KiB; compact it explicitly before continuing.` La reproducción
offline con los archivos finales confirma el error sin llamar al modelo ni a Findata.
El evento original solo conservó el tipo de excepción; el diagnóstico explicita cómo
se verificó su causa. Faltaban 56 llamadas ordinarias y 160 herramientas del máximo.

La tentativa, estado y capturas se conservan sin recortar manualmente la agenda ni
reescribir resultados. No se lanzó otra tentativa: la misma validación impediría
arrancar desde ese estado. El fallo de la campaña queda registrado como `failed`,
sin confundirlo con captura incompleta, timeout o presupuesto agotado.

**Observación:** funcionaron captura, evaluación periódica, aviso y persistencia,
pero la cobertura medida no disminuyó, la persistencia siguió concentrada en
consolidación y una agenda excesiva impidió continuar.

**Interpretación:** el mecanismo de feedback se ejercitó, pero no garantizó convergencia
ni continuidad operativa. La reserva de evidencia mejoró su presencia inicial y no
evitó omisiones posteriores. Son límites observados, no una demostración causal de
superioridad o inferioridad frente a V7.

**Siguiente pregunta:** estudiar la compatibilidad entre escritura de agenda,
consolidación y semilla protegida, y la suficiencia del paquete evaluador. Este informe
no modifica esos mecanismos ni autoriza otra campaña, migración o cambio en FinMate.

## Procedencia y disponibilidad

Consolidación documental del 2026-10-31. Carpeta original: `artifacts/inversion-real-v8`.
Se contrastaron manifiestos, resultados, eventos y snapshots finales disponibles;
los informes locales y los hallazgos anteriores se leyeron como síntesis, sin
repetir sus replays, comprobaciones exhaustivas o campañas.

| Ejecución original | ID | Total LLM / herramientas | Resultado registrado |
|---|---|---:|---|
| `piloto-200-llamadas/ejecuciones/2026-10-31-investigacion-real-200` | `81472841-1a03-42d3-829a-f67588c4ea06` | 154 / 140 | failed / ValueError |

Las capturas completas son locales y pueden archivarse fuera del checkout; no se
conoce aún su destino externo. Las referencias permiten identificar los originales,
pero no garantizan acceso. Los resultados narrativos se entienden sin esas carpetas;
repetir una auditoría de cifras, fuentes o trayectoria requiere recuperarlas. No se
trasladan payloads privados ni expedientes completos a Git.
