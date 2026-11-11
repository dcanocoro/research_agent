# Adobe: integración espontánea de DCF Lab en investigación continua

Fecha: 2026-11-11. Protocolo previo al lanzamiento. El usuario sustituye el contraste
de dos brazos por **una ejecución experimental**, con hasta 300 llamadas ReAct y
consumo especializado adicional. No se ejecuta control ni se atribuirá mejora causal.
Este piloto estudia la trayectoria dentro de una investigación inicial; no introduce
resultados nuevos semanas después ni acredita actualización longitudinal externa.

## Contrato y entradas

- Adobe (ADBE), workspace nuevo y aislado; mismo A continuo implementado.
- [Mandato](../../../campaigns/dcf-adbe-longitudinal/mandato.md),
  [instrucciones operativas](../../../campaigns/dcf-adbe-longitudinal/operativas.md)
  y [petición](../../../campaigns/dcf-adbe-longitudinal/peticion.md), extraídos del
  texto aportado. No mencionan DCF Lab ni prescriben fases, frecuencia o invocaciones.
- Investigador y dos especialistas: `gpt-6-luna`. Herramientas habituales por defecto
  más `evaluate_company`; sin B, Python opcional ni Progress. Revisión general
  continua activada; nota de continuidad desactivada. No se genera objetivo JSON.
- `--max-react-calls 300` cuenta investigador, checkpoints ReAct y respuesta de cierre;
  evaluadores y especialistas se registran adicionalmente. `--max-calls` sigue siendo
  un techo total independiente y no se establece en este piloto. El máximo no es una
  meta de consumo; cierre autónomo y fallos se conservan. Timeout global: 24 horas.
- `--allow-voluntary-stop` hace que una respuesta textual sustantiva sin herramienta
  publique la evaluación y cierre la ejecución. Es opt-in; el continuo anterior
  trata las respuestas como intermedias y conserva ese comportamiento por defecto.
  El sistema efectivo explica esta elección; no impone criterios de suficiencia.
- Snapshot DCF congelado desde Findata en solo lectura; herramientas ordinarias de
  Findata y web siguen vivas. No es un corpus totalmente congelado ni un backtest.
  Configuración, hashes, fuentes y capturas completas quedan en la carpeta local.
- ERP implícita estadounidense de Damodaran/NYU: **4,41 % al 01/11/2026**, trailing
  twelve months with adjusted payout, publicada en su
  [página primaria](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/home.htm),
  consultada el 11/11/2026. Es una estimación externa, no un hecho de Adobe. Se usa
  la convención Treasury sin ajuste por impago; no se añade prima país.
- Inspección sin LLM: `completed`, sin bloqueos. Conserva nueve advertencias:
  aproximación FCFF/CFO, mediana histórica, dilución no modelada, ausencia de fechas
  de publicación verificadas, procedencia de capitalización/beta y antigüedad/desfase
  de perfil, precio y tasa libre de riesgo. Precio: 242,27 USD al 09/10/2026;
  Treasury del snapshot: 5,22 % al 08/10/2026, frente al 5,29 % de la fuente ERP.
  No se actualiza Findata ni se presenta esta combinación como precio actual.

## Captura y revisión

Conservar run nativo completo, estado final, eventos, conversación, trazas y cada
bundle DCF con sus inputs/outputs especializados. La selección de documentos con
contenido/hash permite recuperar el contexto empresarial exacto de cada invocación;
si no selecciona documentos o no mantiene Modelo de Empresa, declararlo.
Reconstruir cambios intermedios con las escrituras archivadas, no solo el snapshot final.

Cronología: llamada ReAct, motivo observable, documentos/contexto seleccionado,
supuestos, cálculo, diagnóstico, implicaciones, siguientes acciones relacionadas,
cambios de hipótesis/conclusión y causa de cada reevaluación. Distinguir secuencia
temporal de evidencia explícita de causalidad. Si no invoca la herramienta, también
es resultado; no intervenir para forzar uso ni descartar la tentativa.

Desglosar ReAct, revisión/contexto y especialistas; tokens, coste conocido/desconocido,
latencia, errores y límites de captura. Un fallo con uso no devuelto conserva consumo
desconocido, no cero. Revisión externa posterior por el mismo asistente que prepara
el piloto; no se presenta como revisión independiente o ciega.

## Rúbrica previa

Aplicar las cinco capacidades y T1/T2 de la
[rúbrica habitual](../../evaluaciones/protocolo.md#4-rúbrica-de-evaluación), escala
general existente 0–4. El adjunto habla de 0–3; esa escala se usa exclusivamente en
las dimensiones específicas siguientes para no reescribir la rúbrica habitual.
Nombrar G1–G5 las generales en el informe para evitar colisión de etiquetas.

| Dimensión DCF (0–3) | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| D1 Oportunidad | Uso injustificado o sin necesidad reconocida | Necesidad vaga o momento poco útil | Necesidad económica material y momento razonable | Selección proporcionada y justificada frente a alternativas |
| D2 Contexto | Ignora contexto disponible | Contexto superficial/desactualizado | Usa hipótesis y evidencia empresarial pertinentes | Vincula contexto, supuestos y limitaciones de forma trazable |
| D3 Interpretación crítica | Acepta o ignora sin interpretar | Repite resultados/advertencias | Examina supuestos, sensibilidad y límites materiales | Contrasta discrepancias y calibra su juicio económico |
| D4 Retroalimentación | Ignora diagnóstico | Menciona incertidumbres sin actuar | Investiga una incertidumbre material surgida de la valoración | Usa el contraste para revisar o justificar mantener la evaluación |
| D5 Coherencia longitudinal | Inconsistencias sin reconocer | Revisiones sin causas claras | Cambios y vigencia trazables | Revisiones proporcionadas ligadas al conocimiento y reconciliadas |

N/O si no hubo oportunidad observable; no convertir ausencia de invocaciones en cero
automático de todas las dimensiones, ni una sola valoración en fallo de D5. Puntuar
con evidencia favorable/contraria y límites, sin premiar cantidad de llamadas,
documentos, cambios de opinión o invocaciones DCF.

Entregables posteriores: estado operativo, evaluación de calidad del experimental,
cronología DCF, ciclos observados, fallos y recomendaciones. La comparación de calidad
con control queda fuera del alcance corregido por el usuario. No fabricar hallazgos.
