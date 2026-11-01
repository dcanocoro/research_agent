# E1 — hallazgos de la campaña de simplificación

Fecha: 2026-10-31. Se ejecutaron los tres casos fijos sobre el agente simplificado,
una ejecución aislada por caso. Las capturas locales completas están en
`artifacts/e1-simplificacion/` y no forman parte portable del repositorio.

## Condiciones observadas

- Los tres manifiestos registran `gpt-6-luna`, `LLM_TIMEOUT_SECONDS=180`,
  `LLM_CALL_BUDGET_SECONDS=180`, 100 llamadas ordinarias y máximo 200 herramientas.
  No se cambió `.env`; los valores se fijaron en el proceso de lanzamiento.
- Las ejecuciones usaron workspaces y estado separados. Las capturas contienen
  manifiesto, entradas, eventos, resultado, respuesta, estado inicial/final y Git.
- Los tres procesos del lanzador devolvieron código 0. Las ejecuciones del agente
  terminaron `interrupted` por `call_limit`; agotaron sus 100 llamadas ordinarias.
  No es evidencia de que los encargos quedaran resueltos.
- No hubo errores de captura (`capture_errors=[]`) en ningún caso.

| Caso | Fases ordinarias: investigación + consolidación | Consolidación | LLM total, incluidas revisiones | Llamadas a herramientas | Eventos `lab.tool.failed` |
|---|---:|---:|---:|---:|---:|
| Analista abierto | 60 + 40 = 100 | 40 | 108 | 96 | 4 |
| Microsoft | 67 + 33 = 100 | 33 | 108 | 97 | 4 |
| Infraestructura de IA | 64 + 36 = 100 | 36 | 108 | 99 | 9 |

Las ocho llamadas LLM adicionales por caso se reparten entre revisión (6) y revisión
externa (2). Los eventos de fallo no se convierten en tasas: no se ha establecido aquí
un denominador homogéneo de intentos por herramienta. La duración capturada entre el
primer y último evento fue 10:15, 14:50 y 13:53, respectivamente; no incluye
necesariamente inicialización ni salida del proceso.

Identificadores y evidencia principal de cada captura local:

- Analista — run `27e04b35-e989-4020-bf0d-83fa9d895bed`; `analista/ejecuciones/2026-10-31-analista/resultado.json`, `respuesta.md`; estado `analista/estado/oportunidades.md`, `agenda.md`.
- Microsoft — run `fbc36baa-e6e4-4bc7-90de-ef9d74a1260c`; `microsoft/ejecuciones/2026-10-31-microsoft/resultado.json`, `respuesta.md`; estado `microsoft/estado/agenda.md`, `empresas/MSFT/evaluacion.md`, `empresas/MSFT/valoracion.md`.
- Infraestructura de IA — run `05efc4d0-6eb9-49d7-aa2e-cd4049d764d8`; `sector-ia/ejecuciones/2026-10-31-sector-ia/resultado.json`, `respuesta.md`; estado `sector-ia/estado/compartido/infraestructura_ia.md`, `agenda.md`.

Los fallos incluyeron `invalid_edit`, `ambiguous_target`, selectores inválidos y
continuaciones alteradas en lectura/escritura de estado; Microsoft registró además un
fallo `read_document` y uno `read_financials`. La simplificación redujo las vías de
escritura, pero no eliminó la ambigüedad de las operaciones ni la fricción de versión.

## Revisión de resultados por caso

Clasificación cualitativa según el protocolo; no es una puntuación agregada.

| Caso | Fundamento y análisis | Continuidad | Coherencia de cierre | Resolución |
|---|---|---|---|---|
| Analista | Parcial: contrastó cifras capturadas y corrigió una referencia errónea de material; quedan por conciliar fechas de publicación, definiciones y períodos. | Suficiente en lo observable: guardó oportunidades, índice y agenda; la agenda conserva cálculos previos y pendientes adicionales. | Parcial: la agenda registra ratios descriptivos de márgenes/crecimiento y capitalización/FCF ya calculados; la respuesta describe la comparación cuantitativa y esos ratios como pendientes. Puede referirse a trabajo adicional, pero no lo delimita con claridad. | Parcial; priorización exploratoria, sin recomendación ni valoración intrínseca. |
| Microsoft | Parcial: actualizó información de FY2026/FY2027 y expuso límites de escenarios y precio. | Parcial: guardó evaluación, valoración, modelo e agenda, pero no propagó a estos documentos la cotización de $521,91 del 30-oct citada en la respuesta final. | Insuficiente en este punto material: la respuesta promete guardar la referencia y revisar cálculos, mientras agenda y evaluación mantienen $530,14 del 29-oct como precio posterior verificado y recálculos pendientes. | Parcial; postura provisional de esperar, no conclusión de sobrevaloración. |
| Infraestructura de IA | Parcial: tesis y escenarios rivales con señales de demanda y capex; proyecciones, backlog y extractos no demuestran beneficios ni retornos sostenibles. | Suficiente en lo observable: guardó documento sectorial, índice y agenda con asuntos pendientes. | Suficiente: respuesta, tesis y agenda mantienen el análisis como provisional y sin valoración. | Parcial; identifica mecanismos de captura y riesgos, sin resolver atractivo financiero. |

Estas clasificaciones se basan en la respuesta final, documentos, agenda y estado final
de las capturas locales. No constituyen una auditoría exhaustiva de cada afirmación o
fuente. La respuesta de Microsoft introduce un precio secundario cuya extracción se
describe como incompleta; la falta de propagación y revisión hace que el cierre sea
incoherente aunque la agenda preserve un precio oficial fechado y sus límites.

## Observación, interpretación e hipótesis

**Observación.** Los tres casos produjeron artefactos recuperables y mantuvieron
trabajo material pendiente. Las consolidaciones consumieron entre 33 y 40 de las 100
llamadas ordinarias. Se registraron 4, 4 y 9 eventos de herramienta fallida. El sector
IA cerró de forma coherente con su agenda; analista dejó ambiguo el alcance de cálculos
ya registrados, y Microsoft no propagó una referencia nueva que sí apareció en la
respuesta final.

**Interpretación.** La intervención conjunta es operable y preservó continuidad básica,
pero la fricción de edición siguió siendo visible. La simplificación de instrucciones y
escritura no basta para garantizar que el agente use selectores válidos, reconcilie
versiones o sincronice respuesta, agenda y evaluaciones. El resultado de Microsoft es
una debilidad concreta de consolidación/cierre; no prueba por sí solo deterioro general.

**Hipótesis para el siguiente paso.** Si se mantiene una sola intervención por
experimento, una revisión del contrato/instrucciones de selectores y edición podría
reducir `ambiguous_target`, `invalid_selector` y `continuation_changed`. Conviene
separarla de cualquier cambio de recuperación o de presupuesto, y probarla con control
contemporáneo si se pretende atribuir una mejora.

## Límites del contraste

### Comparación descriptiva con la reejecución timeout-180

Se contrastaron directamente estas capturas con `artifacts/mi-experimento-timeout-180/`,
la ejecución anterior con los mismos tres casos. Coinciden el perfil `gpt-6-luna`,
timeouts de 180 segundos, límites de 100 llamadas ordinarias/200 herramientas y el
hash de la agenda inicial; los tres encargos fijos y el mandato son idénticos byte a
byte. Cambiaron deliberadamente las instrucciones del agente y el contrato de
escritura. Ambas tandas acabaron en `call_limit` y tuvieron cero errores de captura.

| Caso | Investigación + consolidación anterior → E1 | Herramientas anterior → E1 | Fallos anterior → E1 (tasa sobre intentos) | Duración anterior → E1 |
|---|---:|---:|---:|---:|
| Analista | 52 + 48 → 60 + 40 | 98 → 96 | 7 → 4 (7,1% → 4,2%) | 16:46 → 10:15 |
| Microsoft | 56 + 44 → 67 + 33 | 99 → 97 | 3 → 4 (3,0% → 4,1%) | 18:24 → 14:50 |
| Infraestructura de IA | 54 + 46 → 64 + 36 | 98 → 99 | 13 → 9 (13,3% → 9,1%) | 15:13 → 13:53 |
| **Total** | **162 + 138 → 191 + 109** | **295 → 292** | **23 → 17 (7,8% → 5,8%)** | **50:23 → 38:58** |

Las tasas usan intentos `lab.tool.started` como denominador; el contador coincide con
`tool_calls` de cada resultado. La duración es el tiempo entre primer y último evento
capturado, por lo que no incluye necesariamente inicialización o salida del proceso.
Cada ejecución anterior tuvo 107 llamadas LLM (5 revisiones + 2 externas); E1 tuvo 108
(6 + 2). El total agregado pasó de 321 a 324 llamadas LLM. Costes monetarios y tokens
no se comparan aquí.

**Lectura operativa.** E1 movió 29 llamadas ordinarias desde consolidación a
investigación y redujo los intentos de herramienta en 3. Los fallos agregados bajaron
en 6, aunque Microsoft empeoró de 3 a 4; los otros casos bajaron de 7 a 4 y de 13 a
9. El tiempo capturado descendió en los tres casos. Es una señal descriptiva favorable
para fricción/tiempo, con un caso que contradice la tendencia y sin medir coste/token.

**Calidad del razonamiento, investigación y juicio.** En el caso abierto, la ejecución
anterior construyó hipótesis y expedientes individuales para ADBE y MSFT, más una
evaluación secundaria de NXP; estudió calidad de caja/SBC, pero reconoció que sus
periodos y fuentes no permitían estimar caja por acción ni valor intrínseco. E1 produjo
una comparación más homogénea de GOOGL, MSFT y META: calculó con Python márgenes
operativos y FCF, capex/ventas, crecimientos y capitalización/FCF, y relacionó capex
creciente con FCF plano o decreciente. Eso mejora la construcción de un cribado
comparativo; su límite es depender de cifras anuales del proveedor con periodos
fiscales distintos y `published_at` ausente. No realizó valoración por empresa ni
desarrolló expectativas o balances. Además, su respuesta final llama pendientes a
ratios ya documentados en el estado. El avance analítico es real en el documento, pero
no llegó con precisión al cierre conversacional.

En Microsoft, la ejecución anterior sí había recalculado escenarios EPS×múltiplo desde
$524,38 del 29-oct (precio secundario no corroborado) y lo comparó con un umbral
hipotético DGS5 de 4,78%; el caso central lo superaba y el bajista no. Su evaluación
esperaba sin afirmar sobrevaloración y dejó claras las limitaciones de los supuestos.
Sin embargo, la respuesta final dijo que los escenarios seguían pendientes y citó la
base antigua de $535,07: contradijo el propio estado. E1 incorporó en agenda y
evaluación el cierre oficial de $530,14 del 29-oct, una mejora en calidad de evidencia,
pero no recalculó los escenarios desde ese precio; la valoración conserva como base
$535,07. Su respuesta final añadió $521,91 de Yahoo para el 30-oct, reconoció que la
extracción era incompleta y volvió a dejar el recálculo como futuro. Por tanto, E1
mejoró el dato de precio registrado, pero no avanzó la comparación de valoración frente
a esperar y volvió a fallar al reconciliar documentos, agenda y respuesta. En ambas
ejecuciones el juicio de esperar es prudente; ninguna demuestra retorno esperado
suficiente, ROIC incremental ni valor razonable.

En infraestructura IA, las dos capturas contienen tres escenarios explícitos, no cuatro:
el anterior cubre base, alza y baja; E1 cubre demanda monetizable, comoditización y
sobreconstrucción. Ambos mantienen una tesis condicional y niegan que crecimiento de
demanda pruebe retornos. La ejecución anterior tiene mayor amplitud de señales sobre
HBM, redes/Arista y regulación eléctrica regional; E1 formula con más claridad las
condiciones para que el capital invertido y la monetización determinen quién captura
valor, y añade evidencia de capex/vida útil de Microsoft. Cambia el foco de la cadena,
sin evidencia suficiente para decir que la tesis económica sea superior en conjunto.

**Balance semántico.** Hay una mejora concreta en el cribado cuantitativo del caso
abierto y una mejora de procedencia en el precio oficial de Microsoft. No se observa
una mejora general del razonamiento de inversión: la valoración de Microsoft queda
menos actualizada de lo que permite la nueva evidencia, los supuestos siguen sin validar
y el cierre final no refleja fielmente el estado; el análisis sectorial es un cambio de
énfasis. La intervención simplificó operaciones, pero no resolvió la disciplina de
actualizar dependientes y formular un juicio alineado con evidencia y cálculos.

**Nota comparativa orientativa (calidad del análisis y juicio, excluye eficiencia):**

| Caso | Ejecución anterior | E1 | Razón principal |
|---|---:|---:|---|
| Analista abierto | 6/10 | 6,5/10 | E1 compara mejor métricas homogéneas entre empresas; la anterior profundiza más en expedientes individuales. E1 pierde parte de la ventaja porque la respuesta final contradice cálculos ya guardados. |
| Microsoft | 6,5/10 | 5,5/10 | La anterior dejó una sensibilidad recalculada y una referencia hipotética para esperar; E1 encontró mejor evidencia oficial de precio, pero no actualizó con ella el modelo y añadió otra cotización sin persistirla. |
| Infraestructura de IA | 6/10 | 6/10 | Ambas son prudentes y condicionales; cambian el énfasis y la cobertura de fuentes sin resolver retornos ni valoración. |
| **Media simple** | **6,2/10** | **6,0/10** | **Ligera ventaja de la anterior, concentrada en Microsoft; diferencia orientativa, no concluyente.** |

La escala es un juicio retrospectivo aplicado a los documentos y respuestas disponibles,
no una calificación ciega ni una medición objetiva. La cercanía entre notas refleja que
E1 mejora la comparación financiera del caso abierto, pero no la decisión de inversión
en conjunto.

Estas son dos tandas secuenciales, no un contraste controlado: las fuentes web y los
datos disponibles pudieron variar, solo hubo una ejecución por caso y las dos
intervenciones —prompts y herramientas de escritura— cambiaron juntas. Por eso no se
puede atribuir causalmente a E1 la reducción de fallos/tiempo ni afirmar no inferioridad
de calidad. Esta revisión compara directamente los documentos, cálculos y juicios
guardados de ambas tandas, pero no es una reevaluación ciega ni cubre exhaustivamente
cada afirmación y fuente.

La evidencia permite concluir que el agente simplificado produjo una ronda de
investigación capturada hasta el límite y generó estados continuables, con fricción de
herramientas y dos problemas de coherencia de cierre de distinta gravedad. No permite
concluir que la simplificación mejore o empeore el agente en general, ni que los
análisis constituyan decisiones de inversión validadas.
