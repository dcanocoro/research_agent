# Adobe: resultado del piloto de integración DCF Lab

Fecha: 2026-11-11. [Protocolo previo](adbe-longitudinal.md). Solo brazo experimental,
según corrección del usuario. Revisión posterior de las capturas por el mismo
asistente que preparó la ejecución; no es independiente ni ciega. No hubo control,
réplicas ni auditoría externa de las cifras financieras extraídas.

## Resultado y alcance

**Integración espontánea observada, integración económica todavía incompleta.** A
invocó DCF Lab sin instrucción de hacerlo, interpretó sus límites, investigó después
crecimiento, costes, caja y dilución y justificó mantener una conclusión de
insuficiencia. No convirtió el escenario central en recomendación. La única
invocación se produjo antes de construir el Modelo de Empresa y envió contexto
documental vacío; no se observó un DCF posterior alimentado por el conocimiento
construido. Los resultados apoyan la utilidad exploratoria del diagnóstico en esta
trayectoria, no una mejora causal respecto a A sin herramienta.

El agente terminó voluntariamente a las **17:37 del 11/11/2026, Europe/Madrid**:
`completed: researcher_completed`, sin agotar el techo. Cuando el usuario pidió
parar, el proceso ya había finalizado. No se mató ni relanzó ningún proceso para
esta revisión. El cierre técnico no acredita suficiencia del análisis.

## Condiciones efectivas e incidencias

Investigador y especialistas `gpt-6-luna`; A continuo, revisión general activada,
sin Progress, B, Python opcional ni nota de continuidad. Se añadieron antes de
lanzar límites ReAct separados y cierre textual voluntario opt-in. Las instrucciones
comunes no mencionaban DCF ni imponían fases o frecuencia. Snapshot DCF congelado;
Findata ordinario y web vivos. No hubo escrituras financieras ni actualización de
datos por ingesta. Precio de referencia y parámetros temporales: ver protocolo.

| Tramo | ReAct | Revisión general | Especialistas DCF | Herramientas | Cierre |
|---|---:|---:|---:|---:|---|
| R0: primer lanzamiento | 1 | 0 | 0 | 0 | HTTP 400, `invalid_function_parameters` |
| R1: repetición limpia | 10 | 0 | 2 | 9 | Timeout LLM en checkpoint, 45 s |
| R2: continuación del workspace de R1 | 103 | 5 | 0 | 102 | Voluntario, sin error terminal |
| **Total conservado** | **114** | **5** | **2** | **111** | **121 llamadas LLM gestionadas** |

R0 no produjo investigación. Se retiró `uniqueItems` del schema publicado de
`evaluate_company`, manteniendo el rechazo de duplicados en el adaptador. R1 inició
con workspace nuevo y produjo el DCF. El timeout dejó materiales pero ningún modelo
empresarial propio persistido. R2 recuperó ese workspace, con timeout y presupuesto
del proveedor ampliados a 180 s; su techo fue 289 ReAct para contar también las
once llamadas anteriores dentro de las 300 autorizadas. No se descartaron fallos
ni se restauró artificialmente un estado exitoso.

No fue una única ejecución ininterrumpida: interrupción, recuperación y ampliación
temporal son desviaciones operativas documentadas, no factores controlados. No se
introdujo feedback económico manual. Las cinco revisiones generales del runtime sí
orientaron la investigación y limitan atribuir la actividad posterior solo al DCF.

## Cronología reconstruida

Identificación: R0 es `experimental/ejecuciones/2026-11-11-adbe`; R1 y R2 están en
`experimental-retry-01/ejecuciones/`, con nombres `2026-11-11-adbe` y
`2026-11-11-adbe-cont-01`. Los números siguientes cuentan ReAct dentro del tramo;
`seq` identifica el evento de su `eventos.jsonl`. Las horas son Europe/Madrid.

| Momento y referencia | Evidencia observable | Consecuencia |
|---|---|---|
| 17:11, R1 ReAct 6, seq 46 | `evaluate_company(ADBE, [], null)`, después de leer empresa y financieros | No existían modelo, valoración ni evaluación empresariales persistidos; solo agenda inicial y materiales. El contexto de documentos fue vacío. |
| 17:11–17:12, R1 seq 47–50 | Supuestos y diagnóstico especializados completados | Bundle completo `62047d628ec34d61b0cf0efa1a5194f1`; diagnóstico indeterminado, confianza baja e implicaciones de investigación. |
| R1 ReAct 7–9 | Recupera informe DCF, busca y lee 10-K FY2025 | Investigación empresarial posterior al DCF, todavía anterior a cualquier revisión general. La secuencia no basta para probar causalidad exclusiva. |
| 17:15, R2 ReAct 11, seq 80 | Primera escritura conjunta de modelo, valoración, evaluación, índice y agenda | Integra DCF y evidencia FY2025; conserva incertidumbre y evita usar el punto central como valor justo. |
| R2 revisión `event-0012` y ReAct 12–25 | Revisor pide evidencia posterior, conciliación y mercado coherente; A busca Q3 FY2026 | Seguimiento compatible con las implicaciones DCF, pero también explícitamente atribuido por A al revisor general. |
| 17:19, R2 ReAct 28, seq 262 | Revisa H1–H3 y los documentos dependientes | Fortalece expansión agregada; no identifica ARR con retención ni crecimiento de AI-first ARR con rentabilidad incremental. Mantiene DCF exploratorio. |
| 17:21–17:25, R2 ReAct 36, 43 y 48, seq 389, 488, 559 | Incorpora CFO/SBC/recompras y corrige capital de trabajo como saldo, no flujo | Mejora distinciones económicas sin fabricar FCFF ni revalorar. |
| 17:25–17:32, R2 ReAct 51–80 | Repite extracción del PDF, integra agregados y repara documentos | Obtiene más contexto, pero no capex/deuda ni puente completo; varios intentos de escritura se rechazan por ancla ambigua. Ganancia marginal limitada. |
| 17:33, R2 ReAct 84, seq 1065 | Dice que acaba de localizar un filing no localizado antes | Es la misma URL SEC ya consultada en ReAct 25, 30 y 33. Regresión concreta de continuidad operativa. |
| 17:33–17:35, R2 ReAct 86–93 | Dos nuevas extracciones dirigidas de SEC | Añade narrativa de flujos y recompras, pero sigue sin conciliación; mantiene explícito que no permite actualizar DCF. |
| 17:36–17:37, R2 ReAct 98–103 | Verifica metadata de extracción, precisa su alcance y publica cierre | Reconoce `returned_url_verified=false`; conclusión final de atractivo indeterminado. Una única valoración DCF, sin revisiones posteriores del cálculo. |

## Valoración conservada y controles numéricos

El especialista eligió crecimiento inicial de ingresos **9 %** y margen objetivo
FCFF **35 %**, apoyándose en historia y descripción financiera, sin hipótesis propias
del agente. WACC **11,0935 %**, crecimiento terminal **2,5 %**. Resultados mecánicos:

| Escenario | USD/acción | Peso terminal |
|---|---:|---:|
| Conservador | 214,37 | 64,21 % |
| Central | 291,86 | 67,43 % |
| Favorable | 385,06 | 69,81 % |

Se compararon con 242,27 USD al 09/10/2026, no con una cotización actual verificada.
Los escenarios no tienen probabilidades. El rango de sensibilidad central conservado
es 249,70–351,75 USD/acción. Son cálculos del modelo con entradas fechadas, no una
validación externa de valor intrínseco.

La revisión offline comprobó integridad del bundle, igualdad de su copia editable
con auditoría, huella del paquete instalado coincidente con el manifiesto y
reproducción **exacta** de `calculations` con el código instalado, sin proveedores ni
nuevas llamadas LLM. También comprobó los cocientes de ingresos/suscripción y la
identidad aritmética de flujos agregados conservados. Esto valida reproducción y
consistencia interna, no autenticidad del contenido extraído ni calidad de supuestos.

## Ciclos de retroalimentación

1. **Historia → DCF → sostenibilidad.** El diagnóstico pregunta por persistencia de
   crecimiento y margen. El expediente posterior distingue expansión observada,
   retención no demostrada, oportunidad de IA y costes no atribuidos. Hay seguimiento
   pertinente, pero la revisión general interviene antes de buscar Q3.
2. **FCFF aproximado → búsqueda de conciliación → mantener insuficiencia.** A recupera
   CFO, SBC, recompras y agregados de inversión/financiación; intenta obtener capex,
   deuda y movimientos operativos. Corrige saldo frente a flujo y no convierte CFO,
   inversión neta o nueve meses en FCFF anual. La conclusión se mantiene con una
   justificación más concreta. Es el ciclo mejor respaldado del piloto.
3. **Fuentes parciales → contraste de metadata → juicio calibrado.** El agente
   comprueba la captura y rebaja el alcance de la extracción atribuida a SEC. No
   sustituye una extracción parcial por una verificación íntegra de filing.
4. **Valor terminal/incertidumbre → contraste cuantitativo adicional:** no observado.
   No traduce las hipótesis nuevas a sensibilidades de negocio o umbrales valor/precio.
   Tampoco alimenta una segunda valoración con el Modelo de Empresa.

La ausencia de segunda invocación no se considera fallo por sí sola: no se obtuvieron
datos que el agente considerase suficientes para cambiar la base. Además, el snapshot
congelado de la herramienta no se reemplazaba con las cifras web; un contexto nuevo
podía informar supuestos, pero no sincronizar automáticamente caja, deuda y acciones.

## Evaluación semántica

Juicios de esta revisión sobre trazas y documentos, no puntuaciones del runtime.
General 0–4 conforme a la rúbrica habitual; integración DCF 0–3 conforme al protocolo.
No se calcula una media ni se premia el número de invocaciones.

| Capacidad general | Nota | Soporte y límite |
|---|---:|---|
| G1 Investigación | 2/4 | Consulta fuentes pertinentes y conserva procedencia; predominan extracciones parciales, faltan partidas decisivas y el contraste competitivo queda débil. |
| G2 Razonamiento | 2/4 | Hipótesis alternativas y distinciones ARR/retención, CFO/FCFF, saldo/flujo y recompra/retorno; falta cuantificar cómo cambiarían el valor las hipótesis nuevas. |
| G3 Integración | 2/4 | Propaga hallazgos a modelo, valoración y evaluación; persisten acumulación de actualizaciones, duplicación de agenda y metadatos de cabecera desactualizados. No se evalúa integración entre empresas. |
| G4 Aprendizaje | 3/4 | Corrige interpretación de capital de trabajo, alcance de fuente y hallazgos de revisión; mantener insuficiencia resulta más fundamentado. Pierde, sin embargo, memoria de una URL ya conocida. |
| G5 Autodirección | 2/4 | Decide invocar y cerrar antes del techo; consume muchas acciones repitiendo extracción y mantenimiento, sin cambiar suficientemente la vía de acceso. |

| Integración DCF | Nota | Soporte y límite |
|---|---:|---|
| D1 Oportunidad | 2/3 | Existe necesidad valor/precio y lee datos antes; lo usa muy pronto, sin modelo económico construido ni contraste explícito de alternativas. |
| D2 Aprovechamiento del contexto | 1/3 | Utiliza snapshot e historia; `knowledge_paths=[]`, no ejercita transferencia del conocimiento empresarial construido. No ignoró un Modelo de Empresa previo: aún no existía. |
| D3 Interpretación crítica | 2/3 | Mantiene supuestos, fechas y peso terminal como limitaciones; contrasta problemas de caja y no convierte central en recomendación. Falta contraste cuantitativo de hipótesis. |
| D4 Retroalimentación | 3/3 | Investiga incertidumbres de caja/costes y revisa documentos; justifica por qué no revalorar. La contribución propia del revisor general impide atribuir todo al DCF. |
| D5 Coherencia longitudinal | 2/3 | Conserva valoración histórica como exploratoria y propaga evidencia sin presentarla como cálculo actualizado. Consistencia entre valoraciones sucesivas: N/O, solo hubo una; actualización tras noticia externa controlada: N/O. |

T2: de R1 a la primera integración, **progreso material**; incorporación Q3 y corrección
saldo/flujo, **progreso material**; segunda mitad, **progreso limitado**, con una
regresión operativa concreta al redescubrir la URL. No hubo una postura de inversión
validada ni mejora de rentabilidad que evaluar.

## Consumo, eficiencia y límites de captura

| Componente | Llamadas | Tokens de entrada conocidos | Tokens de salida conocidos | Latencia LLM acumulada |
|---|---:|---:|---:|---:|
| ReAct: investigador y checkpoint | 114 | 2.389.515 | 67.835 | 1.250,35 s |
| Revisiones generales | 5 | 85.352 | 12.015 | 151,60 s |
| DCF: supuestos y diagnóstico | 2 | 7.972 | 2.057 | 32,39 s |
| **Total** | **121** | **2.482.839** | **81.907** | **1.434,34 s** |

Uso conocido de 119 llamadas; desconocido en HTTP 400 y timeout. Total conocido:
**2.564.746 tokens**, incluidos 40.548 tokens de razonamiento dentro de salida, no
adicionales. Entrada cacheada: 1.873.218; escrituras de caché: 609.264. El coste total
real permanece **desconocido**, sin factura, sin precio conciliado de escrituras y
retención de caché y sin costes del proveedor web. La tabla Standard archivada permite
una estimación parcial de aproximadamente 0,12065 USD para entrada/salida conocida,
excluyendo recargos de escritura, usos desconocidos y herramientas; no se presenta
como factura ni coste completo. Referencia conservada:
[precios OpenAI](https://developers.openai.com/api/docs/pricing), consultada 11/11/2026.

Tiempo entre primer inicio y cierre: **27 min 41 s**, incluidos huecos entre intentos;
tiempo nativo activo agregado: aproximadamente **25 min 04 s**. En R2 hubo **22
renovaciones de contexto** y 46 llamadas etiquetadas `checkpoint`; sumadas a R1 son
48. Esas llamadas pertenecen al ReAct y pueden investigar con herramientas: no son
48 evaluaciones externas ni un coste separado del presupuesto ReAct.

T1: de 111 invocaciones, 55 fueron navegación/lectura de estado, 17 intentos de escritura
conjunta, 9 declaraciones `report_work`, 19 búsquedas/extracciones web, 3 consultas
financieras/universo, 7 cálculos y 1 DCF. La navegación es necesaria en parte para
recuperar continuidad; estos conteos no prueban por sí solos improductividad.
R2 registra ocho errores de herramienta: tres anclas ambiguas de escritura, tres
referencias de reporte no encontradas y dos errores de selector/versión de lectura.
Las escrituras conjuntas aplicadas fueron catorce; los rechazos se conservan.

Las 119 llamadas del transporte principal tienen archivo de payload presente; el DCF
conserva dos inputs/outputs y bundle auditado. Los tres resultados nativos declaran
`capture_errors=[]`. Esto no recupera tokens que el proveedor no devolvió. No hay
informe de revisión general final adicional tras cierre voluntario: se conserva la
última revisión periódica y la respuesta final, de acuerdo con la opción activada.

## Fallos principales y siguiente experimento

- **Contexto empresarial no transferido.** La herramienta se descubre, pero la única
  ejecución usa historial financiero sin Modelo de Empresa. Falta observar si una
  valoración posterior utiliza hipótesis y evidencia realmente construidas por A.
- **Extracción como cuello de botella.** Repetir preguntas y URLs devuelve agregados
  parciales. El agente conserva el bloqueo, pero no obtiene capex/deuda ni una vía
  alternativa suficiente. El DCF no resuelve una limitación de acceso a evidencia.
- **Continuidad operativa débil.** El filing redescubierto ya estaba consultado;
  retornos truncados del paquete de revisión inducen comprobaciones adicionales.
  Las renovaciones son un mecanismo candidato por estudiar, no una causa demostrada.
- **Mantenimiento creciente.** La agenda acumula varios «resultado de esta sesión»
  y la cabecera de modelo aún anuncia evidencia hasta FY2025 pese a incorporar Q3.
  Las reparaciones de formato y reportes consumen trabajo que no cambia la valoración.
- **Bloqueos sin prioridad efectiva suficiente.** Mantiene precio sincronizado como
  condición, pero las nueve búsquedas web se centran en informes/filings; no hay una
  búsqueda específica de cotización contemporánea. Tampoco cuantifica qué cambio
  material de crecimiento o margen modificaría la evaluación.

El siguiente contraste debería ofrecer un 10-Q íntegro y recuperable, un puente
financiero determinista y datos de mercado con fechas compatibles, sin señalar al
investigador cuándo valorar. Dentro de cada condición, comenzar limpio y después
introducir una evidencia material fechada, conservando workspace y valoración previa.
DCF necesitaría un snapshot sucesor explícito si se quiere evaluar actualización de
caja/deuda/acciones; es una condición de diseño futura, no un cambio autorizado aquí.

Conservar la autonomía y evaluar si selecciona contexto, identifica el supuesto
afectado y decide justificadamente revisar o mantener. No imponer una segunda
invocación. Repetir condiciones controladas y añadir control solo si se pretende
medir mejora. Separar en futuros contrastes el efecto DCF, el feedback del revisor y
la recuperación tras renovación; no cambiar todos a la vez ni usar más llamadas como
criterio de éxito.

## Evidencia local y entregables

Captura completa local e ignorada: `artifacts/dcf-adbe-experimental-20261111T160909Z`.
R0: `f8326aec-d7d6-44d0-ab5c-a7573cfa1a83`; R1:
`d510831b-f8c0-42e1-8764-d1fd343fb0ef`; R2:
`b44dfcd0-a5f9-439c-a49f-e51d88db6aeb`. Mantener juntos inputs, manifiestos,
eventos, conversación completa, trazas, snapshots, revisiones, bundles, logs y
registros de proceso si se trasladan las capturas.

Workspace final en `experimental-retry-01/estado/`: `indice.md`, `agenda.md` y
`empresas/ADBE/{modelo,valoracion,evaluacion}.md`, más materiales originales. No se
editó al revisar. `review-index.json` reconstruye llamadas y eventos de herramienta;
`review-checks.json` guarda comprobaciones locales. Este informe conserva hallazgos
sin copiar payloads privados y no sustituye las capturas para repetir la auditoría.

Se entregan evaluación del único brazo, cronología, ciclos observados, fallos y
recomendaciones. No hay evaluación comparativa con control: el usuario lo retiró.
