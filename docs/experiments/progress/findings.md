# Progress: primera ejecución y repetición con timeout ampliado

Fecha: 2026-11-03. Dos ejecuciones exploratorias sobre el mismo objetivo de comprender
el modelo de negocio de Microsoft, estado nuevo, continuo y techo de 100 llamadas.
No es una evaluación completa de inversión ni un contraste con ReAct convencional.

## Observación

El intento `artifacts/progreso-continuo-100-20261103-213041` terminó en
`operational_failure`, error `LLMTimeout`: 17 llamadas, 15 de A y dos del evaluador,
sin respuesta final. La segunda evaluación agotó 45 segundos. El perfil efectivo
tenía `timeout_seconds=30` y `call_budget_seconds=45`; el wheel instalado limita
la operación al presupuesto interno del proveedor, aunque el runtime permita más.
Se conservaron documentos y la primera evaluación, pero ningún compromiso verificado.

La repetición `artifacts/progreso-continuo-100-20261103-215123` usó el mismo modelo
`gpt-6-luna`, mandato, objetivo y presupuesto, con ambos valores del proveedor en
180 segundos mediante variables del proceso, sin modificar `.env` ni el wheel.
El manifiesto confirmó esos valores. Terminó en `completed/objective_sufficient`
con 50 llamadas: 45 de A, cuatro evaluaciones y una de cierre; 45 herramientas,
26 materiales y ninguna incidencia de captura registrada. Duración: 8 min 52 s.

Las evaluaciones duraron 24,875; 40,797; 44,969 y 26,390 segundos. Las cuatro fueron
válidas. Se verificaron tres tramos de 15 llamadas de A. Primero se guardó la
síntesis primaria; después se amplió la descripción y la intensidad de capital;
finalmente se incorporó evidencia regulatoria británica de la CMA sobre competencia
cloud y fricciones de cambio. El evaluador declaró suficientes los cuatro criterios.
Es una descripción de las capturas, no una validación independiente de sus afirmaciones.

## Interpretación y límites

El límite interno de 45 segundos explica la parada operativa del primer intento.
La repetición demuestra que con la configuración ampliada se completó el ciclo de
selección, ejecución, reevaluación y cierre. Sus evaluaciones no superaron 45 segundos:
no demuestra que la ampliación fuera necesaria para cada una ni elimina variación
del proveedor, de las fuentes y del recorrido. No hubo reintento automático.

El cierre temprano respeta el techo de 100 llamadas: no se consumen las restantes
por obligación. La suficiencia pertenece al juicio del evaluador sobre una vista
acotada; no acredita exactitud financiera, actualidad de cada extracción ni mejor
coste/calidad que el ReAct convencional. El contraste del protocolo sigue pendiente.

## Procedencia

Las dos carpetas locales conservan manifiestos, eventos, trazas, documentos y entradas
y respuestas de `progreso/`. Sus runs se llaman `2026-11-03-inicial`. Las rutas bajo
`artifacts/` son locales e ignoradas; este relato es portable, las capturas no se
versionan. Los datos cuantitativos anteriores proceden de `resultado.json`, manifiestos
y eventos de ambas ejecuciones, consultados al cerrar la repetición.

## Revisión de checkpoints y renovación (2026-11-04)

Revisión retrospectiva de la repetición `progreso-continuo-100-20261103-215123`,
run `2026-11-03-inicial`, ID `5463d779-ebdd-425a-bbf4-6f18ad708889`.
Se consultaron eventos, conversación completa, trazas de herramientas/modelo,
instantáneas de continuidad, estado operativo y documentos finales. No se ejecutaron
proveedores, nuevas investigaciones ni cambios de comportamiento. El primer intento
fallido no está disponible en el `artifacts/` de este checkout y no se reaudita aquí.

### Coste y trabajo realmente realizado

`resultado.json` agrupa como researcher las 45 llamadas ordinarias de A. Los eventos
permiten descomponerlas: 26 researcher y 19 checkpoint, además de cuatro evaluator
y una closing. Checkpoint representa el 38 % del total y el 42,2 % de las ordinarias.
No equivale a desperdicio ni a sobrecoste causal: incluye investigación y escrituras
que también habrían sido necesarias fuera del checkpoint.

| Herramienta durante checkpoint | Intentos | Éxitos |
|---|---:|---:|
| `record_research_advance` | 7 | 5 |
| `report_work` | 6 | 5 |
| `search_web` | 2 | 2 |
| `read_company_document` | 2 | 1 |
| `read_state` | 1 | 1 |
| `calculate` | 1 | 1 |

Las cinco escrituras exitosas de checkpoint fueron las llamadas 10, 15, 21, 37 y 48:
crearon la síntesis y después incorporaron evidencia corporativa, MPC y CMA.
La llamada 31, clasificada researcher, recuperó otra escritura fallida en checkpoint.
Por tanto, guardar conocimiento no estuvo limitado a esa etiqueta, aunque cinco de
las seis llamadas de escritura exitosas ocurrieron dentro de ella.

La suma de duración de llamadas de modelo es 225,173 s para checkpoint,
115,345 s para researcher, 137,031 s para evaluator y 4,421 s para closing.
Checkpoint supone el 46,7 % de esa suma, no del tiempo completo de ejecución.
No se incluyen tiempos de herramientas ni se estima coste monetario.
Contando únicamente eventos `engine.llm` para evitar triplicar la misma llamada,
las trazas atribuyen a checkpoint 503.537 tokens de entrada y 19.644 de salida;
a researcher, 486.873 y 6.249. De los tokens de entrada de checkpoint, 438.121
figuran como cached. Tokens, llamadas, latencia y facturación son medidas distintas.

### Recorrido de las renovaciones

Bytes de la heurística local después de reconstruir; umbral 262.144 bytes.
Pendientes significa referencias con disposición unknown/pending, no brechas financieras.

| Renovación | Checkpoint: llamadas globales | Trabajo y resultado | Bytes después | Pendientes |
|---|---|---|---:|---:|
| 1 | 9–10 | Escritura inicial falla por ancla ambigua; reintento guarda modelo, agenda e índice | 221.074 | 7 |
| 2 | 15–16 | Amplía evidencia y declara integradas las 11 primeras referencias; evaluación 17 antes de renovar | 232.492 | 0 |
| 3 | 21–22 | Completa MPC y declara integradas tres referencias nuevas; fuentes anteriores vuelven a unknown | 245.497 | 11 |
| 4 | 24–25 | Intenta redeclarar fuentes antiguas con hash desactualizado de agenda; lee estado para recuperar | 227.712 | 11 |
| 5 | 29–30 | Calcula crecimiento de depreciación; escritura conjunta falla por edición inválida | 243.515 | 15 |
| 6 | 32 y 34 | Tras guardar en 31, declara integración en 32; evaluación 33; búsqueda nueva en 34 | 243.266 | 15 |
| 7 | 37–38 | Integra resumen regulatorio CMA y declara su tratamiento | 245.753 | 18 |
| 8 | 41–42 | Declara pendiente el índice CMA y busca el PDF; aún no integra nueva evidencia sustantiva | 242.976 | 21 |
| 9 | 44–45 | Lee modelo; falla siguiente lectura por selector; no escribe conocimiento | 241.318 | 22 |

La llamada 48 es un décimo episodio de checkpoint: integra extractos del resumen y
del informe final CMA, pero el evaluador declara suficiencia en 49 y el cierre ocurre
en 50, sin décima renovación. Las 19 llamadas no son nueve pares exactos.
La etiqueta checkpoint tampoco garantiza escritura: en 34 y 42 hubo búsquedas.

### Hallazgos e interpretación

**Persistencia y recuperación operativa observadas.** Hubo nueve reconstrucciones
sin fallo terminal. Se conservaron documentos versionados y referencias recuperables.
Los errores `ambiguous_target`, `version_conflict: agenda.md`, `invalid_edit` e
`invalid_selector` fueron recuperados durante el recorrido; todos ocurrieron en llamadas
checkpoint, sin que esto pruebe que el checkpoint los causara. Las capturas no registran
incidencias de captura. El evento de renovación mantiene `continuity_verified=false`.

**Poco margen entre renovaciones.** En siete de nueve reconstrucciones el tamaño
queda entre 241.318 y 245.753 bytes: sólo 16.391–20.826 bytes bajo el umbral.
Entre renovaciones 3 y 4, y entre 8 y 9, sólo hay una llamada researcher.
El algoritmo de [reconstrucción](../../../src/research_agent/regimes/continuous/context.py)
retiene intercambios completos hasta un objetivo próximo al umbral menos 16 KiB.
Esto preserva contexto reciente, pero deja poco recorrido antes del siguiente aviso.
La reserva de salida efectiva es 128.000 bytes: ya consume el 48,8 % del umbral.
Es una estimación conservadora, no ocupación medida de la ventana del proveedor.

**Invalidación demasiado amplia para el uso observado.**
[RuntimeState.refresh](../../../src/research_agent/regimes/continuous/control.py)
invalida una declaración si cambia cualquier documento declarado, incluida agenda.
Después de integrar las primeras 11 referencias, ampliar el documento y la agenda en
21 hace que vuelvan a unknown. No hay evidencia de que se hayan perdido sus contenidos:
se perdió la vigencia del comprobante basado en hashes de archivos completos.
La llamada 24 intenta repararlo y falla por versión de agenda. El estado operativo
guardado al cierre contiene 21 referencias unknown, dos pending y tres integrated;
tres de cinco declaraciones están stale. Es estado mecánico, no 23 fuentes sin leer.
La última escritura incorpora además fuentes sin emitir un nuevo `report_work`.
El cierre por suficiencia y esta cola operativa no están reconciliados.

**La recuperación favorece el comienzo antiguo del documento.**
[active_foundations](../../../src/research_agent/extensions/deliberation/agenda.py) limita la vista protegida
a 8 KiB con metadatos, tomando el prefijo del documento cuando no se cita una sección.
Desde el contexto 2, la síntesis se marca partial y sólo se inyectan 7.963 bytes de texto.
El documento acaba con 20.281 bytes. En contextos 6–9 el prefijo deja fuera secciones
posteriores sobre MPC, capital y CMA; agenda, feedback e intercambios retenidos pueden
aportarlas por otras vías. No significa que desaparezcan de toda la conversación,
pero exige recuperación adicional y favorece información antigua frente a avances.
Las llamadas 44–46 muestran recuperación del documento y una lectura fallida.

**Acumulación mejor que consolidación final.** Modelo pasa de 7.766 a 20.281 bytes;
agenda, de 2.668 a 5.530. Hay contenido sustantivo nuevo, pero persisten instrucciones
antiguas: el modelo aún pide consultar el informe final CMA tras incorporar extractos
del original, y la agenda conserva acciones de contraste e integración ya realizadas
junto a los resultados nuevos. Esto no demuestra pérdida por renovación; sí que el
checkpoint no asegura coherencia del estado vigente. Se debe distinguir leer extractos
del original de revisar íntegramente su metodología, que sigue siendo una limitación.

### Mejoras propuestas, sin implementar

1. **Separar tratamiento documental histórico de verificación vigente.** Un cambio
   de hash debe marcar que una declaración necesita revisión, conservando que la
   fuente ya fue tratada. No convertir automáticamente esa historia en material
   desconocido por una edición de agenda. Probar con extensiones y con eliminación
   real de contenido: la segunda sí debe hacer visible una pérdida de soporte.
2. **Reconstruir dejando recorrido útil.** Contrastar una cola retenida más pequeña
   y mayor margen antes del siguiente umbral; registrar tamaño de semilla, herramientas,
   cola, continuaciones y reserva por separado. No basta con subir umbral a ciegas ni
   reducir la reserva sin comprobar los límites efectivos del proveedor.
3. **Mantener una síntesis vigente breve y recuperar secciones pertinentes.** Usar las
   referencias a secciones ya disponibles y actualizar el estado actual de agenda;
   conservar detalle y antecedentes en el documento. Evitar cargar siempre su prefijo.
   Comprobar que el contexto reconstruido contiene el último hallazgo material y la
   siguiente acción aún pendiente, sin exigir más documentos por rutina.
4. **Reducir reparaciones y declaraciones repetidas.** Aprovechar versiones devueltas
   por herramientas, aclarar el contrato cursor/selector y dar ejemplos de edición
   conjunta válida. Valorar una declaración opcional de tratamiento junto a una escritura
   exitosa, preservando que es declaración del agente y no certificación semántica.
   No exigir una llamada separada cuando sólo repite el resultado de guardar.
5. **Reconciliar el cierre con el estado persistido.** Usar la última oportunidad de
   escritura para sustituir pendientes obsoletos y distinguir lo resuelto, parcial y
   desconocido. Aclarar el significado de la cola técnica al cierre; no bloquearlo
   hasta declarar artificialmente todas las referencias integradas.
6. **Medir continuidad útil y coste atribuible.** Distinguir escritura sustantiva,
   declaración, recuperación, error y nueva investigación dentro de checkpoint.
   Medir si tras renovar reconoce hallazgo, límite y siguiente acción; búsquedas repetidas
   y hechos omitidos; llamadas entre renovaciones; tokens con caché y sin caché; latencia.
   Contrastar un cambio cada vez con materiales congelados y la misma tarea, modelo
   y presupuesto. Este run no permite saber cuánto ahorró o costó frente a un control.

La valoración es favorable para persistencia y recuperación técnica, mixta para
continuidad útil y desfavorable para la eficiencia observada del control. La causa
no puede atribuirse sólo a las dos llamadas de checkpoint: intervienen tamaño de
contexto, selección de memoria, invalidación de declaraciones y disciplina de edición.
No se ha demostrado continuidad semántica ni una mejora comparativa.
