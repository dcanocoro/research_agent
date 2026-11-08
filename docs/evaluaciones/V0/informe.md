# V0 — Evaluación de Progress continuo con y sin nota

**Campaña:** V0, expedientes FinData, 150 llamadas por condición.  
**Ejecución:** 2026-11-07. **Evaluación:** 2026-11-08, Europe/Madrid.  
**Método:** [rúbrica 1.0 y adaptación retrospectiva](../protocolo.md).  
**Estado:** revisión documental concluida; no aceptación financiera ni prueba causal.

V0-SN = sin nota; V0-CN = con nota. Una ejecución por condición. Se aplica la
estructura A–H solicitada a los límites reales de esta campaña. La rúbrica se aportó
después de ejecutarla: las puntuaciones no fueron criterios de aceptación previos.
No se modifica el estado de los agentes ni se completa su investigación.

## A. Resumen ejecutivo

- **Resultado general:** ambos runs alcanzaron 150 llamadas y cerraron por presupuesto,
  sin error técnico final. Construyeron tres expedientes, comparación, agenda e índice;
  no completaron valoración comparable.
- **Principal avance:** CN integró una comparación FY2023–FY2025 de margen operativo
  y capex/flujo operativo, contextualizada con FCF y crecimiento. SN conservó series
  y comparación FCF, con mayor precisión en algunos límites de cobertura.
- **Principal limitación:** análisis predominantemente descriptivo; faltan atribución
  económica y retorno de inversión para sostener atractivo relativo. La cautela ante
  insuficiencia es apropiada al mandato, no un fallo por sí misma.
- **Calidad del progreso:** material desde el estado inicial en ambos; limitado en
  el tramo final SN y material por integración en CN. No demuestra mejora de decisiones.
- **Notas:** 20 válidas llegaron al siguiente contexto; varias preservaron trabajo que
  después se integró. Consumen 21 llamadas, conservan imprecisiones y no reducen
  claramente los checkpoints. Utilidad local observada, sin causalidad identificada.
- **Recomendación principal:** contrastar una síntesis final basada en estado vigente:
  los cierres actuales no representan el resultado global. Tres propuestas en H,
  sin implementación ni campaña autorizadas por este informe.

## B. Ficha de ejecución

### B.1. Identidad y configuración efectiva

| Campo | V0-SN | V0-CN |
|---|---|---|
| Run ID | e49ef376-f7d2-497c-b790-4a3a438ec7a7 | 882e6b3d-a040-4ad3-92fe-a2de1f20cace |
| Carpeta de condición | progress | nota |
| Context note | false | true |
| Inicio local | 2026-11-07 12:22:35 CET | 2026-11-07 12:22:35 CET |
| Fin local | 2026-11-07 12:53:41 CET | 2026-11-07 12:59:31 CET |
| Duración de pared | 31 min 6 s | 36 min 56 s |
| Llamadas / techo | 150 / 150 | 150 / 150 |
| Estado y cierre | interrupted / call_limit | interrupted / call_limit |
| Error final / errores de captura | null / ninguno registrado | null / ninguno registrado |

Configuración común capturada en manifiestos:

- OpenAI, **gpt-6-luna**, perfil **lab**, razonamiento **medium**, verbosity **medium**,
  salida máxima **16000 tokens**. No se atribuye una revisión remota no registrada.
- Transporte/presupuesto temporal de proveedor **180 s**; max_attempts **3**.
  Reintentos internos no son llamadas extra del contador del controlador.
- **continuous-e2**, **commitments-v1**, tramos de **15 llamadas**, objetivo **open**;
  revisor general apagado, integrador B apagado, operadores Python apagados.
- Renovación **400000 bytes**, máximo de contexto **524288 bytes**; sin techo global
  de herramientas ni timeout global en continuous. Se conservan timeouts por operación.
  Los defaults acotados de limits no sustituyen esta configuración continua.
- Objetivo abierto: no cierre por suficiencia global; admite bloqueo y límites.
  Alcanzar 150 no acredita cumplimiento ni obliga a consumir todas las llamadas.
- Workspaces nuevos, sin intercambio. Estado inicial sin investigación seleccionada.
- Se usó Python 3.12 de la aplicación con dependencias instaladas del proyecto: el
  Python base de .venv no arrancaba. No se modificó el wheel para ejecutar estos runs.

### B.2. Petición, mandato y objetivo reales

Petición literal:

> Empieza la investigación abierta de la cartera y acumula expedientes de empresas con FinData.

Mandato literal conservado en la entrada de campaña:

> Construye y mantén progresivamente expedientes de empresas que ayuden a
> tomar mejores decisiones para este usuario. Parte de su cartera. Decide qué empresas
> investigar, qué preguntas son materiales y qué contrastes aportan información.
> Guarda cada avance en el expediente de la empresa con evidencia, fechas, moneda,
> unidades, cálculos, juicio vigente y qué evidencia podría cambiarlo. Relaciona
> expedientes si comparten riesgos o sirven de contraste. Después de cada avance
> selecciona otra pregunta útil. Registra qué queda abierto al cierre.
>
> Usa exclusivamente datos de FinData y herramientas locales de cálculo y estado.
> No consultes web ni sustituyas datos ausentes por supuestos sin etiquetar.
> Registra la fecha de cada observación y no uses datos posteriores al 2026-11-05.
> Si falta valoración comparable, condiciona el juicio y evita proponer operaciones.
>
> Perfil sintético. Horizonte de cinco años, riesgo moderado. Pesos del ejercicio:
> MSFT 12%, AMZN 10%, GOOGL 8%, resto diversificado fuera de estas posiciones 70%.
> Máximo por empresa 15%. El resto de posiciones no se conoce. El usuario quiere
> entender dependencias comunes y riesgos que podrían justificar revisar los pesos.

Objetivo **investigacion-cartera**, mode **open**: construir y mantener expedientes con
datos reales de FinData para comprender riesgos y alternativas relevantes para cartera.
Criterios fijos:

| ID | Criterio literal |
|---|---|
| expedientes | Cada avance material queda guardado en el expediente de la empresa, con evidencia fechada, cálculos verificables y un juicio vigente. |
| cartera | Relacionar hallazgos con posiciones, horizonte y restricciones del perfil cuando afecten a su interpretación. |
| prioridad | Elegir una incertidumbre material que pueda cambiar el juicio y que pueda investigarse con los datos disponibles. |

No se asignaron DCF, órdenes, precios objetivo ni número de empresas que completar.
Podía ampliar universo; no lo hizo. No hubo evidencia programada ni nuevos encargos
durante las ejecuciones.

### B.3. Datos, herramientas y reproducibilidad

**Datos:** FinData vivo en solo lectura; respuestas con procedencia, periodos, unidades
y metadatos capturadas. No hubo dataset previo congelado/versionado para esta pareja.
El corte se aplica por instrucción, no por barrera temporal del proveedor. published_at
ausente limita certificar disponibilidad histórica: periodo no equivale a publicación.

**Schemas expuestos:** list_files, read_file, search_files, read_artifact, calculate,
record_research_advance, inspect_state, read_state, search_state, inspect_company,
read_company_document, describe_state_tools, search_companies, read_company,
read_financials, read_metric_trend, search_web, read_document y report_work.
Web estaba registrada pero prohibida por mandato; no se observan llamadas web.
Bloqueo segmentario es límite de herramientas/consultas, no ausencia económica global.

Contrato **state-tools-e1**. Hash común de schemas calculado en esta revisión sobre
JSON canónico UTF-8 (ensure_ascii=false, sort_keys=true, separadores coma/dos puntos):
`d60fd27cef7cd448d537a66356798b934a7658145c4de22e0cb610d563018815`.

Huellas de fuentes capturadas, iguales en ambos manifiestos:

| Paquete | code_sha256 |
|---|---|
| research_agent | 8135f2ab572726737402e80ecc055c4970d4267e2141c31f535496850fc0f4c7 |
| findata | 7275d76edaa6fcab438f7998519e8c4845d6bf649bd4f25d54c9cb4e2bd74018 |
| infra | c7d497c24c68e256af539fbc572ec51ba2745efe99ffc14b51d8b9b5c6f3cb42 |
| runtime_contracts | d3a95ffa862398dee65b408fb76c159113f63b547478d6430271c34e32521677 |

Instrucciones congeladas, iguales en ambos:

| Archivo | SHA-256 |
|---|---|
| agente.md | 44977f9dc9a862c1eb118371137ddcf803b67a9ef6944f8d250b661fbe914cd0 |
| deliberacion.md | 3e8dcde2838eafa765845cbb6734932c56d9853355be11a89339d829ba10e5d9 |
| herramientas-estado.md | 1a3c028ce8a934d6b8f1d0fb96c16e917219d2a553efabe849d42aa2cd4260da |
| investigacion-financiera.md | 57f321d5a196045839cac25197cbc690eb4dffa6cae20c744d63a95330eb4fac |

Prompts exactos de Progress y definición/hash del objetivo están en manifiestos.
Huellas de código no congelan modelo/base remotos. git_initial indica ausencia de
Git propio en los workspaces experimentales, no ausencia del Git del laboratorio.
No se inventa commit de run o hash de dataset; tampoco se sustituyen versiones
capturadas por las actualmente instaladas. Se registran contratos y huellas disponibles.

### B.4. Consumo por componente

| Medida | V0-SN | V0-CN |
|---|---:|---:|
| Investigador ordinario | 91 | 74 |
| Checkpoints operativos del mismo A | 45 | 43 |
| Evaluaciones Progress | 13 | 11 |
| Notas | 0 | 21 |
| Cierre | 1 | 1 |
| Total | 150 | 150 |
| Renovaciones | 29 | 22 |
| Herramientas intentadas / fallidas | 132 / 7 | 116 / 8 |
| Materiales conservados | 38 | 42 |
| Eventos de escritura por archivo | 34 | 34 |
| Tokens entrada reportados, incluidos cacheados | 5487471 | 6444474 |
| Tokens salida reportados | 162535 | 206836 |
| Coste monetario | No disponible | No disponible |

Fuente: un engine.llm_call por llamada, eventos y resultado. researcher del resultado
agrupa ordinario/checkpoint: 136 SN y 117 CN. No son 136/117 llamadas de investigación
sustantiva. Los propósitos no separan con exactitud investigación, integración y
revisión dentro de cada llamada. Los checkpoints son llamadas de A, no otro agente
ni snapshots adicionales solicitados por el evaluador.

CN: 20 notas válidas, una truncada (12), una omitida sin llamada por reserva (22).
Las 21 llamadas de nota: 1143632 tokens entrada, 62531 salida; 14% del techo de
llamadas. CN empleó +17,4% de entrada y +27,3% de salida frente a SN; eso no equivale
directamente a precio ni demuestra por sí solo ineficiencia neta.

### B.5. Catálogo de evidencia y disponibilidad

Raíz local ignorada por Git:
`artifacts/expedientes-findata-baseline-150-repeticion-20261107-122229`.
Dentro de progress/ o nota/, el run es `ejecuciones/2026-11-07-investigacion/`.
Las rutas siguientes son procedencia original, no enlaces portables.

| ID | Evidencia concreta |
|---|---|
| E1 | Cada run: manifiesto.json, resultado.json, estado-inicial.json, estado-final.json, peticion.md; raíz: mandato.md y objetivo.json. |
| E2 | SN: continuidad/indice.json y estado-0023.json, 118 llamadas, seis Markdown, capture_complete=true, capture_errors=[]; desfase −2 para referencia 120. |
| E3 | CN: continuidad/indice.json y estado-0018.json, 124 llamadas, seis Markdown, capture_complete=true, capture_errors=[]; desfase +4. |
| E4 | SN: progreso/0002-evaluator.json (llamada 17), 0005 (54), 0006 (70), 0009 (115), 0010 (131), 0011 (138), 0012 (142), 0013 (149), e inputs. |
| E5 | CN: progreso/0001-evaluator.json inválido (1), 0002 válido (2), 0004 (37), 0006 (76), 0007 (94), 0009 (120), 0010 (139), 0011 (149), e inputs. |
| E6 | CN: continuidad/nota-0001.json, 0004, 0012, 0014–0022 e inputs; eventos lab.context.note.* y payloads trazas/modelo-NNNN.json.gz. Las 20 válidas se localizaron en provider_input de la primera llamada sucesora. |
| E7 | Final SN: empresas/{MSFT,AMZN,GOOGL}/modelo.md, compartido/dependencia-cloud.md, agenda.md, indice.md. CN: empresas/{MSFT,AMZN,GOOGL}/evaluacion.md, compartido/inversion-infraestructura-cloud.md, agenda.md, indice.md. |
| E8 | Material AMZN de ambos: estado/materiales/2026-11-07-investigacion-06-read-financials.json; deuda/caja presentes, patrimonio no. CN: cálculos 31–37; SN: cálculos finales 35–38. |
| E9 | eventos.jsonl: SN escritura 121, secuencias 998/999, y 126, secuencia 1039; CN escritura 125, secuencias 944–948. engine.llm vincula llamada, herramienta y argumentos. |
| E10 | respuesta.md y answer de resultado.json; no equivalen al workspace de conocimiento. |

Capturas completas/materiales disponibles localmente al revisar. Los snapshots de
continuidad contienen Markdown, no todos los JSON fuente; estos están en materiales
y archivo de herramientas. No existen snapshots exactos de llamada 120. No se
reconsultaron servicios externos. Los [hallazgos previos](../../experiments/expedientes-findata/baseline-150-findings.md)
son una revisión de esta misma pareja, no evidencia independiente adicional.

## C. Resultados por capacidad

Escala: 0 ausente, 1 incipiente, 2 funcional con carencias materiales, 3 sólido,
4 avanzado; N/O no observable. Sin media ponderada ni significación estadística.
Son valoraciones del evaluador, no una clasificación de rentabilidad.

### C.1. Perfil por condición y corte

| Dimensión | SN referencia 120 (snapshot 118) | SN final 150 | CN referencia 120 (snapshot 124) | CN final 150 |
|---|---:|---:|---:|---:|
| D1. Investigar | 2 | 2 | 2 | 2 |
| D2. Razonar | 2 | 2 | 2 | 2 |
| D3. Integrar | 2 | 2 | 2 | 2 |
| D4. Aprender | 2 | 2 | 2 | 2 |
| D5. Autodirigirse | 2 | 2 | 2 | 2 |

Mismo nivel funcional no significa resultados iguales: la escala de enteros no
refleja todo el progreso dentro de un nivel. No se eleva a 3 por añadir tablas si
persisten carencias materiales. Tampoco se penaliza automáticamente la ausencia de
valoración que el mandato permite condicionar cuando faltan datos. La revisión ante
contradicción externa y los resultados reales de inversión son N/O, no capacidades ausentes.

### C.2. Evidencias y límites de cada valoración

| Dimensión / condición | Justificación al corte de referencia | Evidencia final positiva | Evidencia negativa o límite que mantiene 2 |
|---|---|---|---|
| D1 / SN | Series fechadas y con unidades; distingue deuda/caja AMZN de patrimonio ausente. E2, E8. | Fuentes recuperables, sin inventar segmentos. E7. | Buscar nombres de servicios en índice de compañías no resuelve cobertura segmentaria; fuente única, publicación no certificada e inversión histórica incompleta. E4, E7. |
| D1 / CN | Capturas y cálculos fechados; 31–37 existen como materiales, no integrados en documentos del snapshot. E3, E5, E8. | Completa comparación operativa/inversión y añade crecimiento con referencias. E7. | Resumen de ausencia de balance excesivamente amplio; sin contraste externo ni disponibilidad histórica certificada. E8. |
| D2 / SN | Separa cloud de consolidados; FCF y capex MSFT permiten hipótesis limitadas. E2. | Mantiene incertidumbre causal; no convierte peso de cartera en exposición común demostrada. E7. | No descompone causas ni completa inversión de tres empresas; juicios aún descriptivos. E4, E7. |
| D2 / CN | Contrasta margen operativo/FCF y causas alternativas; documentos mantienen pendientes ratios y GOOGL FY2025. E3. | Integra capex/OCF y márgenes, debilita compresión operativa como explicación suficiente; no afirma retorno demostrado. E7, E8. | Causalidad y atractivo de inversión no resueltos. Las cautelas son correctas, pero no sustituyen un modelo económico de retorno. E7, E10. |
| D3 / SN | Tres expedientes relacionados; tabla común FCF aún no incorporada en snapshot 118. E2. | Tabla conjunta y agenda se actualizan en 121; índice después. E9. | GOOGL mantiene comparación pendiente; índice reabre búsqueda suspendida; capex AMZN sin integrar. E7, E8. |
| D3 / CN | Separa calculado de integrado; matriz aún incompleta en Markdown. E3, E5. | Integra cinco documentos en 125; crecimiento se propaga después. E9, E7. | Pendientes obsoletos, H2 acumula temas, cierre no representa el conjunto y error de cobertura persiste. E7, E10. |
| D4 / SN | Reutiliza evidencia y refina ratio/componentes; cambia de segmentos bloqueados a otras preguntas. E2, E4. | Propaga comparación FCF y conserva límites previos sin inventar causas. E7. | Actualización parcial de dependencias; sin escenario controlado de contradicción externa. E7. |
| D4 / CN | Notas distinguen calculado/guardado; pendientes sobreviven a renovaciones. E3, E6. | Integra pendientes; tras nota 12 fallida también continúa cálculos. E6, E9. | Arrastra bloqueo impreciso y prioridades caducadas; no demuestra detección autónoma de ese error. E6–E8. |
| D5 / SN | Preguntas relevantes y bloqueos acotados, con esfuerzo prolongado en ruta segmentaria limitada. E2, E4. | Cambia a FCF, deuda e inversión; reconoce insuficiencia. E4, E10. | Estancamiento final, verificaciones/errores de edición y último compromiso sin integrar. E4, E9. |
| D5 / CN | Línea de caja/inversión verificable, aunque tarda en integrar resultados ya calculados. E3, E5. | Completa contraste y pasa a crecimiento/múltiplos con cautela. E5, E7. | Checkpoints/reconciliación altos; compromiso nuevo en 149 sin margen para ejecutarlo. E5, E10. |

## D. Evolución y valor incremental

### D.1. Reconstrucción de los cortes

- **Inicial, ambos:** agenda sin investigación seleccionada; sin expedientes previos
  de las tres empresas. No se atribuye valor financiero a la plantilla inicial. E1.
- **SN, snapshot 118 (−2):** expedientes con FCF/deuda y contraste de componentes,
  tabla capex/ingresos MSFT; la tabla conjunta FCF se escribe en 121, no en 120. E2/E9.
- **CN, snapshot 124 (+4):** documentos aún marcan GOOGL FY2025 y capex/OCF históricos
  pendientes. Cálculos ya existentes en materiales: avance aritmético no integrado.
  No hay escrituras Markdown entre 120 y 124; la integración llega en 125. E3/E8/E9.
  No se atribuye esa integración al corte 120.
- **Final 150:** SN incorpora comparación FCF y deja inversión AMZN incompleta;
  CN incorpora ratios, síntesis y crecimiento y deja valoración en exploración. E7.

| Intervalo observado | Progreso / conocimiento | Regresiones o carencias | Clasificación T2 |
|---|---|---|---|
| SN, 0–118 (referencia 120) | De agenda vacía a expedientes, series y límites precisos cloud/balance; MSFT con inversión histórica. | Cobertura segmentaria consume esfuerzo sin resolver la hipótesis; comparación común incompleta. | Progreso material. |
| SN, 118–150 | Tabla común FCF, agenda/índice; cuatro cálculos capex/ingresos AMZN. | Inversión no integrada; asignación de años no verificable en vista final del evaluador; pendientes obsoletos. | Progreso limitado. |
| CN, 0–124 (referencia 120) | Tres evaluaciones, comparación FY2025, series FCF/deuda y márgenes; cálculos históricos adicionales. | Brecha calcular/integrar y bloqueo demasiado amplio. | Progreso material. |
| CN, 124–150 | Integra matriz margen/capex, añade crecimiento y explora fechas/definiciones de múltiplos. | No resuelve causalidad/valoración; conserva prioridades superadas. | Progreso material. |

Son intervalos aproximados declarados, no estimaciones exactas del rendimiento a
llamada 120 ni comparaciones a igual trabajo sustantivo. No se identifica regresión
material global demostrada, pero sí errores locales persistentes. No se declara
progreso sustancial: no culmina valoración ni juicio decisorio robusto.

### D.2. Conocimiento nuevo frente a volumen adicional

- **Información nueva:** series FCF/deuda, márgenes, inversión, crecimiento y snapshots
  de múltiplos. Parte se obtiene reutilizando capturas ya disponibles.
- **Conocimiento nuevo:** distinguir consolidados de exposición cloud; ratio de deuda
  de solvencia; distinta absorción de caja y contraste de margen operativo frente a FCF.
- **Juicios fortalecidos:** hipótesis de presión de reinversión sobre caja residual
  con contexto descriptivo, sin demostrar origen cloud, retorno o atractivo relativo.
- **Actividad sin mejora equivalente:** lecturas/reconciliaciones repetidas, notas que
  reiteran conocimiento guardado y cierres que no sintetizan el conjunto.
- **Revisión ante evidencia contradictoria:** N/O como prueba controlada. Hay contraste
  interno y acumulación, sin escenario adverso externo con verdad de referencia.

### D.3. Aportación y coste de las notas

| Episodio CN | Qué conserva | Acción posterior comprobada | Interpretación y límite |
|---|---|---|---|
| Nota 1, tras 25 llamadas | Cálculos FY2025 sin integrar, conflicto agenda y destinos. | 26 lee agenda; 27 guarda expedientes/comparación/agenda. | Continuidad local útil. No sigue literalmente separar agenda; el historial retenido también informa. |
| Nota 4, tras 41 | Serie MSFT y siguiente consulta AMZN/GOOGL. | 42 y 43 consultan ambas series. | Conserva siguiente paso; no prueba que se perdiera sin nota. |
| Notas 14–18 | Ratios hechos/pendientes por año y empresa, materiales frente a integración. | 103/111/113/115/116 completan cálculos; 125 integra cinco documentos. | Utilidad entre cálculo/persistencia, aunque el proceso fue largo. |
| Notas 19–20 | Resultados guardados y reconciliación pendiente. | 129 reconcilia; 133–136 exploran crecimiento. | Evita confundir operación pendiente con cálculo ausente. |
| Nota 12 truncada | Se aplica fallback sin nota. | 84–91 calculan márgenes; 93 integra. | La nota no es necesaria para toda continuidad. |

Las 20 notas válidas aparecen en el input posterior, no solo en un archivo. Tienen
3230–5696 bytes. Algunas reiteran conocimiento, hashes y bloqueos; la 9 y posteriores
conservan la formulación demasiado amplia sobre balance. E6/E8. No son validación
semántica ni revisión completa del estado.

**Conclusión sobre notas en V0:** utilidad operativa observada para trabajo pendiente
de integrar y estado CN más completo para caja/inversión. Coste material; efecto
causal y beneficio neto no identificados. Una pareja, elecciones divergentes y base
viva impiden atribuir la diferencia exclusivamente a la nota. Menos renovaciones
no demuestra por sí solo mejor memoria.

## E. Decisiones autónomas relevantes

Las alternativas posibles siguientes las identifica el evaluador; no se inventan
como deliberaciones del agente. Cada juicio considera lo disponible en ese momento.

| Caso | Situación / alternativas posibles | Elección y razón registrada | Resultado y evaluación contextual |
|---|---|---|---|
| Ambos: empezar por cloud | Tres tecnológicas; cobertura segmentaria desconocida. Alternativas: exposición común, caja o balance. | Progress elige nube/infraestructura por riesgo compartido; consulta financieros. E4/E5 iniciales. | Pregunta material y autorizada. Consolidados solo dan contexto; había que ajustar alcance al observar límites. |
| SN: repetir comprobación segmentaria | Ya hay consolidados y cloud no cuantificado. Alternativa: comprobar contrato y documentar límite antes. | Repite financials, busca servicios como compañías y después reconoce limitación del índice. E4; llamadas 35, 59–61. | Bajo rendimiento para resolver segmentos; finalmente delimita correctamente ausencia de ruta frente a ausencia global. |
| Ambos: interpretar debt_to_equity | Series con fórmula/componentes insuficientes. Alternativas: señal descriptiva o comprobar componentes. | Busca deuda/patrimonio/caja para no equiparar ratio y solvencia. E4/E5. | Buena cautela. SN distingue deuda/caja AMZN y patrimonio ausente; CN generaliza demasiado el bloqueo. E8. |
| CN: margen operativo frente a FCF | FCF menor/irregular, historia disponible. Alternativa: insistir en segmentos o contraste consolidado. | Calcula márgenes y capex/OCF para acotar hipótesis, con límites causales. E5, 76–125. | Pregunta útil con datos existentes; matriz integrada sin retorno demostrado. Retraso de integración conserva riesgo de pérdida. |
| CN: error de crecimiento | Matriz integrada; OperationalError al consultar crecimiento MSFT. | Consulta AMZN, reintenta MSFT, consulta GOOGL y guarda. Llamadas 133–138. | Reintento con propósito concreto y resultado; no toda repetición es improductiva. |
| Ambos: nuevo compromiso al límite | Dos llamadas restantes, cierre reservado. | SN 149 propone verificar/integrar ratios; CN 149 capitalización/FCF. E4/E5 finales. | Brechas reales sin margen operativo para ejecutarlas; quedan pendientes, no trabajo realizado. |

## F. Fallos y limitaciones

### F.1. Problemas por impacto sobre el resultado

| Impacto / problema | Observación verificable | Familia y causa probable | Confianza |
|---|---|---|---|
| Alto: amplitud del bloqueo de balance CN | AMZN 06 contiene deuda/caja; notas/agenda no conservan esa distinción. E6–E8. | Recuperación, razonamiento e integración: generalización de vista parcial; mecanismo exacto no aislado. | Alta en discrepancia; media en causa. |
| Alto: cierre poco representativo | SN se centra en último tramo AMZN; CN dice no usar herramientas en ese turno, aunque el run sí investigó y guardó. E10 frente a E7. | Cierre/contexto: vista reducida y foco reciente en lugar de síntesis global; no se aísla una única causa. | Alta en desajuste; media en atribución. |
| Alto: coherencia parcial | GOOGL SN mantiene comparación pendiente; índice/agenda y prioridades CN parcialmente superados. E7. | Persistencia: actualización local sin revisar todas las dependencias. | Alta en estado; media en causa. |
| Medio: coste operativo | 45/43 checkpoints y múltiples report_work/lecturas; notas no reducen claramente checkpoints. B.4. | Contexto y reconciliación; no se cuantifica qué parte es evitable. | Alta en consumo; media en evitabilidad. |
| Medio: fallos de herramientas | SN: 7, entre conflictos, edición inválida, list_files y destino ambiguo. CN: 8, entre conflictos, selector, edición, protección de sección y OperationalError. | Uso de contratos/versiones y proveedor; conflicto no demuestra edición externa concurrente. | Alta en errores; causas generales no aisladas. |
| Medio: Progress parcial | Omite fuentes y declara vistas parciales; algunas etiquetas de progreso corresponden a cálculos no integrados. E4/E5. | Paquete evaluador y definición de progreso; etiqueta interna no equivale a calidad externa. | Alta en visibilidad; media en efecto sobre prioridades. |
| Medio: límites de datos | Ruta segmentaria no verificada, patrimonio faltante, definiciones de múltiplos insuficientes. E7/E8. | Cobertura de respuestas/herramientas; no ausencia global. | Alta en capturas; cobertura total N/O. |
| Acotado: evaluación inválida y nota truncada | Primer informe CN se repara; nota 12 usa fallback; ambos cierran sin error final. E5/E6. | Contrato evaluador y salida de modelo; fallo preservado. | Alta en ocurrencia; sin prueba de solución universal. |

### F.2. Límites de observabilidad y método

1. Una ejecución por condición; sin variabilidad estimada ni evaluación ciega.
   Codex también colaboró en preparación/correcciones: externo al runtime, pero sin
   independencia personal ni segundo juez.
2. Rúbrica posterior al cierre, no preregistro. Se mantiene el mandato real y no se
   añaden obligaciones retrospectivas.
3. Fuente viva sin dataset congelado. No se revalidan cifras contra fuentes externas
   ni se audita íntegramente la metodología de métricas derivadas.
4. Corte 120 aproximado y snapshots solo Markdown. Contexto y cálculos se rastrean
   aparte; no se atribuye al corte integración de llamadas 121/125.
5. Revisión robusta ante contradicción externa, rentabilidad y decisiones reales N/O.
   Insuficiencia documentada no equivale a error de juicio.
6. No se ejercitó la nueva recuperación de truncamiento de investigador en esta pareja:
   ese fallo no ocurrió; la nota fallida empleó su fallback existente.
7. Precio monetario desconocido y entrada incluye cacheados. Los propósitos no separan
   exhaustivamente todas las actividades intelectuales.

## G. Comparación histórica

No hay campaña anterior puntuada con esta misma rúbrica que permita comparación
numérica. Los [hallazgos anteriores](../../experiments/expedientes-findata/baseline-150-findings.md)
revisan esta misma pareja, no son una réplica ni una validación independiente.

Se conservan [tentativas operativas anteriores](../../experiments/expedientes-findata/baseline-150.md)
en `artifacts/expedientes-findata-baseline-150-20261107-105604`:

| Tentativa | Resultado observado | Relación con V0 puntuada |
|---|---|---|
| SN inicial | 34 llamadas, progress_evaluation_invalid; dos informes rechazados por referencias. | Código anterior de referencias/reparación; antecedente de fiabilidad, sin puntuación comparable. |
| CN inicial | 14 llamadas, LLMTruncated; sin nota, renovación ni expedientes escritos. | No ejercitó la nota; no permite valorar su utilidad. |
| Pareja final V0 | 150 por condición, call_limit, error final nulo. | Continuidad operativa en estos runs, sin probar solución universal ni mejora causal de calidad. |

Las 48 llamadas iniciales son consumo histórico separado de las 300 de la pareja
puntuada. Se conservan sus fallos y no se mezclan configuraciones como si fueran una.

## H. Recomendaciones derivadas de V0

Tres propuestas, no decisiones arquitectónicas aceptadas ni órdenes de implementar
o lanzar. El informe no crea ni define otra campaña.

### H.1. Síntesis final basada en conocimiento vigente

- **Problema:** la respuesta final infrarrepresenta el trabajo del run.
- **Evidencia:** E10 frente a los seis documentos y resultados de E7.
- **Mecanismo candidato:** paquete final acotado de juicios vigentes, avances,
  fuentes y pendientes, reutilizando índice, agenda y documentos.
- **Hipótesis verificable:** mejor representación global sin atribuir trabajo no guardado.
- **Experimento propuesto:** sobre estados/trazas V0 congelados, comparar cierre actual
  y cierre con paquete, mismo modelo y presupuesto de salida, evaluación a ciegas.
- **Indicador de éxito:** menos omisiones materiales y afirmaciones erróneas sobre lo
  ejecutado, sin nuevas conclusiones financieras no sustentadas.

### H.2. Verificar bloqueos y actualizar pendientes dependientes

- **Problema:** resúmenes pierden distinciones de cobertura y conservan pendientes resueltos.
- **Evidencia:** deuda/caja AMZN E8 frente a CN; agenda/índice/GOOGL E7.
- **Mecanismo candidato:** cotejar extracto relevante y pendientes afectados al cerrar
  compromiso, con herramientas existentes; no requiere grafo ni schema financiero nuevo.
- **Hipótesis verificable:** distinguir campo ausente, no visible, comparación incompleta
  y límite global; reducir pendientes superados.
- **Experimento propuesto:** replay de mismos estados/extractos V0 con/sin ese cotejo,
  sin nuevas fuentes y a presupuesto igual.
- **Indicador de éxito:** conservar que AMZN tiene deuda/caja y no patrimonio, retirar
  pendientes ya resueltos y no convertir omisiones de vista en ausencia global.

### H.3. Proporcionalidad de las notas

- **Problema:** utilidad para pendientes no integrados, repetición si ya están guardados;
  21 llamadas de nota no eliminan 43 checkpoints.
- **Evidencia:** episodios D.3, consumo B.4 y reiteración de bloqueos E6.
- **Mecanismo candidato:** notas breves centradas en el delta o emisión ligada a trabajo
  material aún no integrado; la detección fiable de esa condición no está demostrada.
- **Hipótesis verificable:** conservar continuidad con menor coste y menos información obsoleta.
- **Experimento propuesto:** misma tarea/corpus local congelado, modelo y techo total,
  condición actual frente a una única intervención de nota, con repeticiones y etiquetas ocultas.
- **Indicador de éxito:** mantener exactitud e integración, reducir recursos auxiliares
  y no aumentar pérdidas de evidencia o falsas ausencias.

## Verificación del informe

Comprobación local de identidades, configuración, snapshots 118/124 y final, trazas
por propósito y material AMZN; enlaces locales y git diff --check. Sin proveedores
ni consultas remotas, sin modificar estados originales. Puntuaciones interpretativas
documentadas, sin auditoría financiera exhaustiva ni puntuación agregada.
