# V7 real: 200 llamadas ordinarias, conocimiento parcial y objetivo inversor pendiente

Fecha: 2026-10-30. Campaña autorizada por el usuario. El [protocolo](protocol.md)
y la [rúbrica previa](rubrica.md) se fijaron antes de ejecutar. **Se consumieron
200 llamadas ordinarias en tres tentativas, con 211 llamadas al modelo en total.
Quedaron seis modelos de empresa y una comparación de cribado; no hay valoración,
evaluación de inversión completa ni propuesta de asignación.**

La [captura local](../../../artifacts/inversion-real-v7/piloto-200-llamadas/README.md),
el [resumen mecánico](../../../artifacts/inversion-real-v7/piloto-200-llamadas/resumen-observacion.json),
las [comprobaciones escogidas](../../../artifacts/inversion-real-v7/piloto-200-llamadas/comprobaciones-locales.json)
y el [replay de escrituras](../../../artifacts/inversion-real-v7/piloto-200-llamadas/replay-escrituras.json)
son locales, ignorados por Git y no portables por sus enlaces. Lanzadores, preflight
y análisis están en el directorio padre de esa captura. No se sobrescribieron
los materiales, respuestas ni trazas de las tentativas fallidas.

## 1. Datos reales y condiciones

La CLI se lanzó sin simulador, con PostgreSQL Findata, búsqueda y extracción Tavily,
aritmética y Python habilitado. El preflight observó `transaction_read_only=on`,
503 empresas, perfil para las 503, precios para 502 y estados financieros para 501.
Las muestras AAPL/ADBE/AMZN comprobaron acceso, no determinaron la selección de A.
Los precios más recientes observados eran del 9-oct-2026. No hubo ingestas,
escrituras financieras, cartera conectada ni órdenes reales.

Modelo OpenAI `gpt-6-luna`, razonamiento medium, salida máxima 16000. Presupuesto
acumulado: 200 llamadas ordinarias, 300 herramientas y 3600 segundos de ejecución;
máximo local 524288 bytes y umbral 262144, con reserva de salida. El contexto inicial
presupuestado fue 193114 bytes. Capital de referencia: USD 100.000 y hasta diez
posiciones, como problema analítico. No es una cartera real ni una simulación histórica.

## 2. Tentativas y desviaciones conservadas

| Tentativa | Investigación | Consolidación | Autorrevisión | Revisión externa | Total LLM | Herramientas | Cierre |
|---|---:|---:|---:|---:|---:|---:|---|
| Inicial, `c8e7803c-a2e9-4917-a5ba-9cff5fbe0f58` | 20 | 14 | 1 | 0 | 35 | 32 | LLMTimeout |
| Continuación 02, `25ce871c-3a50-4402-9e6a-627555d3948c` | 6 | 2 | 0 | 0 | 8 | 7 | LLMTimeout |
| Continuación 03, `56246269-692b-42db-ac4c-6efea796e036` | 88 | 70 | 8 | 2 | 168 | 156 | call_limit |
| **Acumulado** | **114** | **86** | **9** | **2** | **211** | **195** | Presupuesto agotado |

Las dos primeras fallaron al alcanzar 45 s de presupuesto de llamada del proveedor
durante consolidación. Se continuó desde archivos, sin restaurar conversación ni
repetir intencionadamente operaciones, con 166 y después 158 llamadas ordinarias
restantes. Los límites de herramientas y tiempo también descontaron lo consumido.
La suma de tiempos de lanzamiento fue 1946,313 s, unos 32 min 26 s; no incluye toda
la preparación y los intervalos de diagnóstico entre tentativas.

Para la tercera se ampliaron `LLM_TIMEOUT_SECONDS` y `LLM_CALL_BUDGET_SECONDS` a
180 s, dentro del límite de operación de 300 s ya previsto. Modelo, razonamiento,
salida máxima e instrucciones se mantuvieron. Los perfiles por tentativa constan
en `campaign.json`; no se presenta como una ejecución ininterrumpida homogénea.

Se corrigieron dos defectos de instrumentación entre tentativas:

- El organizador contaba `ejecuciones/transacciones/` como otro run. Ahora exige
  manifiesto nativo para descubrir runs, también en recuperación longitudinal.
  El diagnóstico original «found: 2» se conserva antes de la reinspección.
- El aviso de ausencia de informe histórico se emitía antes de enlazar el contexto
  del run, dejando `run_id=null`. Se movió dentro del contexto enlazado. Las dos
  primeras capturas conservan esa incidencia; sus eventos no fueron reparados.

El informe respeta el runtime congelado de cada tentativa al reinspeccionar capturas.
La tercera tiene `capture_complete=true`; las primeras dos no superan íntegramente
la comprobación de correlación, aunque conservan payloads y resultados disponibles.
El organizador mantiene `failed` porque el agente no devolvió `completed`: el último
run está `interrupted: call_limit`, no caído ni declarado cumplido retrospectivamente.

El contador de revisiones se reinicia por run: la revisión externa intermedia ocurrió
en la tercera tentativa tras 80 llamadas ordinarias de esa tentativa, no en la llamada
100 acumulada de campaña. Esta desviación limita el contraste previsto.

## 3. Qué investigó y qué quedó construido

A inició `search_companies("all")`, que devuelve coincidencias de texto, no el
universo completo: AJG, ALL, ALLE, BALL, HAL, HII y LNT. Reconoció en sus documentos
que ese conjunto de siete no agotaba Findata. No se le impuso esa selección.

El cribado distingue aseguradora, intermediación, seguridad industrial, envases,
servicios petroleros, construcción naval y eléctrica regulada. HII y LNT concentran
el trabajo de contraste primario. AJG quedó principalmente en la comparación,
con intentos tardíos de recuperar resultados recientes y un extracto sindicado.

Estado final: agenda, índice, `oportunidades.md` y seis `modelo.md` de ALL, ALLE,
BALL, HAL, HII y LNT, además de 86 materiales originales. No hay `valoracion.md`,
`evaluacion.md`, DCF ejecutado ni recomendación de pesos. Son modelos de alcance
desigual; no seis expedientes de inversión completos.

Hay avance económico parcial: HII conecta caja con calendario de facturación,
capital circulante y ejecución contractual; LNT relaciona inversión con financiación
y recuperación tarifaria. Se preservan límites de fuentes, precio y comparabilidad.
Eso no establece beneficio normalizado, reversibilidad de caja, creación de valor,
atractivo relativo o retorno esperado a cinco años.

## 4. Persistencia, fricción y fidelidad

- **50 escrituras de archivo, todas durante consolidación.** La consolidación consumió
  86/200 llamadas ordinarias (43 %). No apareció persistencia durante investigación.
- 21 renovaciones entre las tres tentativas. Los reinicios operativos también exigieron
  recuperación desde archivos y algunas consultas repetidas.
- 27 intentos de escritura conjunta: 22 operaciones aceptadas con diario committed.
  Junto con las ediciones individuales, 33 mutaciones intentadas: 26 aceptadas y siete
  rechazadas. El replay reproduce los nueve archivos finales por SHA-256.
- 195 herramientas: 183 éxitos y 12 errores. Hubo conflictos de versión, objetivos
  exactos ambiguos, eliminación de ID protegida, selectores inválidos, un expediente
  ausente y un error operativo de lectura Findata. No todos se resolvieron al primer intento.
- 35 búsquedas web y 21 lecturas/extracciones; un cálculo aritmético y ningún operador
  Python utilizado, aunque estaba habilitado. Recalcular 86181 − 53139 reproduce 33042;
  comprueba esa operación, no la selección de fuente ni su inferencia económica.

**Discrepancia material escogida:** HII E2 presenta USD 515 millones como ingresos
semestrales de Newport News. El pasaje capturado del 10-Q describe un *incremento*
de USD 515 millones, equivalente al 17 %. El valor del incremento pasó a representar
el nivel de ingresos. Persiste en el modelo final; no es un fallo de la calculadora.
La comprobación conserva la cita, ruta y hashes. No es una auditoría exhaustiva de cifras.

La comparación conserva tareas de verificación inicial mientras HII y LNT ya tienen
contrastes primarios posteriores. La agenda reconoce progreso y bloqueos, pero también
deja acciones parcialmente recorridas. Coherencia y depuración siguen siendo parciales.

## 5. Revisión externa y sus límites reales

Las dos revisiones externas finalizaron con JSON válido. El investigador registra
aceptación del feedback sobre verificabilidad y aplaza la vía AJG tras resultados
insuficientes. El informe final concluye que el resultado es cribado, sin selección
de inversiones ni asignación. Eso es una observación del revisor, no aceptación humana.

**El paquete intermedio omitió 26 evidencias y solo incluyó una salida de búsqueda.**
El final omitió 36 evidencias y no incluyó ninguna. También se truncaron documentos
y omitieron acciones; el final omitió un documento. Los inputs miden 63842 y 64011
bytes y declaran esas limitaciones. Las revisiones observaron principalmente lo
escrito por el investigador, sin las fuentes originales necesarias para contrastarlo.
No detectaron el error de interpretación de HII E2. Un JSON válido y un informe
crítico no acreditan verificación independiente de las afirmaciones económicas.

## 6. Interpretación y siguiente pregunta

**Observación:** hay uso real de Findata/web, más contenido primario en algunos
modelos, recuperación tras fallos y operaciones conjuntas verificables. No se alcanzó
el objetivo de evaluaciones útiles para decidir inversiones; persistencia ordinaria,
coste de consolidación, fidelidad y coherencia siguen sin resolverse.

**Interpretación:** ampliar presupuesto y disponibilidad de fuentes permitió investigar
más, pero no aseguró convergencia. El control estructural protege algunas propiedades;
la revisión externa quedó limitada por la selección del paquete de evidencia. La
integridad de archivos no equivale a fidelidad semántica.

**Hipótesis para otro encargo:** estudiar primero qué consume las renovaciones y la
edición, qué información material llega realmente al revisor y cómo convertir una
incertidumbre investigada en juicio provisional explícito. Este informe no implementa
otra intervención ni autoriza un cambio de arquitectura o nueva campaña.

No es comparación causal con V6: cambian universo, fuentes, web, presupuesto y mandato,
y hay reinicios/correcciones instrumentales/configuración de timeout. No es un backtest
ni evidencia de rendimiento inversor. Los 4851436 tokens de entrada y 121621 de salida
son los reportados disponibles; caché y razonamiento son desgloses, no cantidades a
sumar de nuevo. Los valores ausentes en errores no se interpretan como cero ni coste.

Verificación local de correcciones: 73 pruebas de campañas/longitudinal y, después,
51 pruebas finales de campañas/V7 aprobadas; mypy correcto. La primera comprobación
offline de replay encontró PermissionError local y la segunda un error del propio
comprobador (comparaba hashes con texto); ambos constan en su informe. El replay final
compara hashes de ambos lados y coincide, sin modificar el estado de campaña.
