# Colaboración histórica v1

Estado: infraestructura implementada; aceptación corta y preflight registrados en la
[entrega](../../deliveries/2026-10-24-longitudinal.md). No es una evaluación de alfa.

La [revisión de precios de las 50 empresas](price-review.md) habilita un dataset real
ajustado con procedencia y excepción AVB documentadas. La
[prueba corta histórica real](historical-smoke.md) completó tres activaciones en
junio–agosto de 2024. El escenario original pendiente se conserva; el revisado requiere
el dataset auditado mediante `--data`. La campaña de dos años completó 24 activaciones;
su [informe local](../../../artifacts/campana-historica-completa-v1/informe-ejecucion.md)
conserva el análisis posterior. Los artefactos son locales e ignorados, no evidencia
portable. El informe documenta pérdida parcial del mandato y contaminación temporal web;
no acredita alfa. La [siguiente comparación](../intencion-persistente-v1/protocol.md)
está preparada y todavía no se ha ejecutado.

## Pregunta y condiciones

Observar continuidad, investigación, revisión, iniciativa y gestión de una cartera
ficticia durante ejecuciones independientes de A. Se conserva el ciclo y los prompts
vigentes; no se añade evaluador ni planificación cognitiva.

El [escenario](../../../benchmarks/colaboracion-historica-v1/scenario.yaml) fija
2023–2024, 50 empresas, 100.000 USD, máximo de 10 posiciones, 24 oportunidades
mensuales y ocho mensajes trimestrales. Mensaje y revisión coincidentes se fusionan.
Las otras 16 activaciones no incluyen un mensaje humano nuevo. Se mantienen los
límites de 18 llamadas, 30 herramientas y 300 segundos por activación.

Las empresas se seleccionaron por cobertura y orden alfabético mediante
`scripts/prepare_longitudinal_scenario.py`, sin utilizar rentabilidades posteriores.
Esta selección no representa el mercado y conserva sesgo de supervivencia del universo
almacenado. No se deben exigir investigaciones de las 50 empresas ni diez inversiones.

## Tiempo y fuentes

El controlador fija una fecha por activación, interpretada como información disponible
al terminar ese día; el simulador no permite que A avance el reloj. Los timestamps
técnicos siguen siendo reales. Las herramientas calculan la disponibilidad antes de
limitar los períodos: fecha real de publicación cuando existe; en su ausencia, cierre
fiscal más 120 días naturales exclusivamente para fundamentales anuales. El día 120
está incluido. Otros períodos sin fecha real se excluyen.

`published_at` permanece real o nulo. `available_on`, `availability_basis` y
`availability_lag_days` identifican la disponibilidad efectiva y su estimación. No se
rellena `provider_published_at` ni se escribe en Findata. La regla no demuestra que
las empresas hubieran publicado ni recupera versiones anteriores a revisiones.

Findata se exporta en una transacción de solo lectura a un dataset privado congelado.
Las herramientas exponen solo la parte permitida por fecha y universo. La búsqueda
lista 25 identidades por página; la consulta vacía permite recorrer las 50. No expone
capitalización, ratios ni descripciones actuales. Las tendencias derivadas actuales
están deshabilitadas; siguen disponibles observaciones y aritmética.

Tavily aplica `end_date`, pide fecha y excluye resultados sin fecha detectable.
Extract está deshabilitado. La fecha de búsqueda no garantiza contenido histórico
intacto; el modelo también puede conocer acontecimientos futuros. Se conservan
consultas y resultados, pero una repetición contra la web puede obtener otras fuentes.

Los precios almacenados proceden de Alpha Vantage `TIME_SERIES_DAILY`, sin campos de
ajustes o acciones corporativas. El escenario declara revisión pendiente y el
preflight impide negociar una serie no revisada. Resolver mediante una serie ajustada
con procedencia o una revisión documentada de acciones corporativas; no basta cambiar
el estado de revisión sin evidencia. Una revisión cambia el escenario experimental
y requiere una nueva campaña, preservando el intento anterior.

## Cartera y comunicaciones

Compras por importe USD, ventas por participaciones y cierre de toda la cantidad
disponible. Cálculo Decimal con precisión 34; participaciones fraccionarias. Sin
cortos, apalancamiento, comisiones, impuestos o dividendos separados.

Las órdenes reservan efectivo o participaciones y se ejecutan al siguiente cierre
disponible estrictamente posterior a la decisión, cuando avanza el simulador. Al
solicitarlas no se muestra precio ni fecha futura de ejecución. La valoración usa
el último cierre conocido e informa de su fecha.

El máximo cuenta símbolos con posición o compra pendiente de apertura. Ampliar una
posición no consume otra plaza. Vender no libera plaza hasta ejecutar; no hay ventas
automáticas para abrir una undécima. Al finalizar se ejecutan las órdenes cuyo cierre
ya ocurrió y se cancelan las restantes. Las órdenes no financian compras con ventas
todavía pendientes.

En activaciones temporales el cierre es interno. `notify_user` registra una
comunicación local explícita; no envía mensajes externos. Una activación puede terminar
sin herramientas, comunicación, cambios de memoria ni operaciones. La respuesta a
mensajes humanos se conserva en el archivo de su ejecución.

## Operación y recuperación

Desde la raíz, usando el wheel experimental descrito en la entrega:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal validate benchmarks/colaboracion-historica-v1/scenario.yaml
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal preflight benchmarks/colaboracion-historica-v1/scenario.yaml --output artifacts/preflight-NOMBRE-NUEVO
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal run benchmarks/colaboracion-historica-v1/scenario.yaml --output artifacts/campana-NOMBRE-NUEVO
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal resume artifacts/campana-NOMBRE-NUEVO
```

`validate` no importa servicios. `preflight` consulta Findata sin escrituras y guarda
cobertura y datos locales. `run` crea una carpeta nueva, congela configuración y
exporta datos; una revisión pendiente devuelve 1 sin llamar al LLM. `resume` exige
el mismo código efectivo, perfil/modelo, dependencias, instrucciones, límites y datos.
Las credenciales no forman parte de los manifiestos. Valores de retorno: 0 completado,
1 preflight no listo o activación fallida/interrumpida, 2 entrada inválida o error de
entorno. No son puntuaciones financieras.

El archivo separa `agente/estado`, `simulador` e `intentos`. Cada intento conserva
checkpoint de memoria, estado económico inicial, comando, stdout/stderr, captura y
pasos. Las ejecuciones nativas de A conservan entradas/salidas, materiales y snapshots.
`progress.json` es el cursor; las capturas se inspeccionan antes de confirmarlo.

Si A terminó y el cursor no se confirmó, resume reconoce su captura. Si el intento
está incompleto, conserva su memoria fallida, restaura el checkpoint y lo repite con
otro identificador. La repetición del modelo puede diferir: no se promete reproducir
decisiones ni evitar costes de llamadas repetidas. Se impiden efectos económicos
acumulados de intentos descartados. Un bloqueo excluye controladores concurrentes.
No se compactan destructivamente los intentos.

Al completar se guardan `portfolio-final.json`, `history-final.json` y
`communications.json`. La evidencia sigue siendo local e ignorada bajo `artifacts/`;
para trasladarla debe conservarse toda la campaña tras revisar datos privados.

La prueba corta se prepara y ejecuta explícitamente con:

```powershell
.\.venv\Scripts\python.exe scripts/longitudinal_smoke.py --output artifacts/smoke-NOMBRE-NUEVO --run
```

Usa cifras y precios sintéticos identificados y LLM/Tavily reales; la compra inicial
solicitada comprueba integración, no iniciativa ni calidad de inversión.
