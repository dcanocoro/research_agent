# Pareja FinData de 150 llamadas: trayectoria y notas

Fecha de revisión: 2026-11-07. Revisión retrospectiva de capturas locales,
sin proveedores, sin cambiar el estado de los agentes y sin relanzar.

## Condiciones y procedencia

Una ejecución sin nota y una con nota, estados nuevos, Progress abierto, misma
petición/mandato/objetivo; cartera sintética MSFT 12%, AMZN 10%, GOOGL 8%, resto
70% desconocido. FinData vivo en solo lectura, corte por instrucción 2026-11-05.
Modelo gpt-6-luna, razonamiento medium, salida 16000 tokens, transporte/proveedor
180 segundos; techo total 150 llamadas y renovación 400000 bytes en ambos.

Captura local: `artifacts/expedientes-findata-baseline-150-repeticion-20261107-122229`.
Runs: `e49ef376-f7d2-497c-b790-4a3a438ec7a7` (sin nota),
`882e6b3d-a040-4ad3-92fe-a2de1f20cace` (con nota).
Se revisaron manifiestos, resultados, todos los informes Progress, los seis documentos
Markdown finales por brazo, eventos y trazas; se cotejaron notas con acciones y
payloads sucesores y el bloqueo de balance con el material AMZN original.
Las capturas son locales e ignoradas, no evidencia portable. No se revalidaron las
cifras contra fuentes externas ni se hizo una evaluación financiera exhaustiva.
Las [tentativas anteriores](baseline-150.md) siguen conservadas.

## Observación operativa

Ambos llegaron a 150 y `call_limit`, error final nulo, sin errores de captura.
Los contadores del resultado agregan checkpoints dentro de researcher; el desglose
real por propósito procede de `engine.llm_call`, un registro por llamada.

| Medida | Sin nota | Con nota |
|---|---:|---:|
| Investigador ordinario | 91 | 74 |
| Checkpoints | 45 | 43 |
| Evaluador Progress | 13 | 11 |
| Nota | 0 | 21 |
| Cierre | 1 | 1 |
| Renovaciones | 29 | 22 |
| Herramientas intentadas | 132 | 116 |
| Herramientas fallidas | 7 | 8 |
| Eventos de escritura por archivo | 34 | 34 |
| Materiales capturados | 38 | 42 |
| Tokens entrada, incluidos cacheados | 5487471 | 6444474 |
| Tokens salida reportados | 162535 | 206836 |
| Duración de pared aproximada | 31 min 6 s | 36 min 56 s |

Con nota: 20 notas válidas, una truncada (12), una omitida por reserva (22).
Las 20 válidas aparecen en el input del modelo posterior a su renovación, comprobado
en payloads archivados; contienen entre 3230 y 5696 bytes. Las 21 llamadas de nota
consumieron 1143632 tokens de entrada y 62531 de salida. No se conoce coste monetario.
Hubo un informe inicial inválido de Progress en el brazo con nota, reparado al
segundo intento. No hubo un truncamiento terminal de investigador ni se ejercitó
su nueva recuperación en esta pareja; la nota truncada usó su fallback existente.

## Trayectoria y estado sin nota

1. Investigar exposición cloud común: cifras consolidadas y márgenes FY2025, sin
   segmentos que permitan cuantificar Azure/AWS/Google Cloud.
2. Profundizar en FCF AMZN FY2021–FY2025; luego FCF y capex/ingresos MSFT.
3. Reexaminar cobertura segmentaria. Buscar servicios cloud en search_companies no
   encontró compañías; el propio estado limita correctamente el alcance de esa prueba.
4. Integrar debt_to_equity de las tres empresas y comprobar sus componentes. El estado
   distingue AMZN, con deuda y caja pero sin patrimonio, de las otras dos extracciones.
5. Integrar comparación de margen FCF FY2021–FY2025. Intentar ampliar capex/ingresos:
   quedan cuatro cálculos AMZN sin integrar y la comparación de tres empresas pendiente.

Estado: agenda, índice, `empresas/{MSFT,AMZN,GOOGL}/modelo.md` y
`compartido/dependencia-cloud.md`. Conserva hipótesis, fuentes, límites, series y
cambios de prioridad. La evaluación Progress de llamadas 138/142 registra estancamiento;
el cierre no resume todo lo guardado, se centra en el último tramo incompleto.
GOOGL conserva una frase de comparación pendiente pese a que la comparación FCF ya
está en el documento compartido; el índice aún invita a confirmar cobertura cloud
que la agenda considera suspendida. Persistencia y coherencia no son equivalentes.

## Trayectoria y estado con nota

1. Intensidad inversora FY2025: capex/ingresos y capex/OCF de las tres posiciones.
2. Integrar expedientes y comparación; contrastar deuda/patrimonio y margen FCF.
3. Pasar de buscar segmentos/componentes no resueltos a comparar margen operativo y
   absorción de caja por capex FY2023–FY2025. Los cálculos se integran hacia llamada 125.
4. Añadir crecimiento móvil de ingresos y empezar comprobación de múltiplos; no
   completar valoración comparable ni el último compromiso de capitalización/FCF.

Estado: agenda, índice, `empresas/{MSFT,AMZN,GOOGL}/evaluacion.md` y
`compartido/inversion-infraestructura-cloud.md`. La comparación recoge margen
operativo y capex/OCF de tres años y crecimiento de ingresos, con cautelas sobre
periodos y causalidad. Capex/OCF de captura: MSFT 32,09%→47,41%; AMZN
62,07%→94,48%; GOOGL 31,70%→55,52%, FY2023–FY2025.
No prueba retorno ni destino cloud. Las evaluaciones siguen siendo provisionales.

Hay límites: la agenda termina con prioridad antigua de crecimiento ya investigado;
el documento común conserva un siguiente paso de balance superado y un encabezado
Markdown pegado al párrafo previo. H2 de deuda/patrimonio acumula varios temas.
El resumen de bloqueo de balance es demasiado amplio: la captura AMZN contiene
`total_debt` y `cash_and_short_term_investments` FY2025 (USD 66103 y 86810 millones),
aunque no patrimonio. No distinguirlo pierde información disponible. Ese resumen
se arrastra en varias notas; la nota no valida la fidelidad de lo que conserva.

## Evidencia sobre utilidad de las notas

- Nota 1 conserva los cálculos FY2025 aún no integrados y el conflicto de agenda.
  Tras renovar, llamada 26 lee agenda y 27 guarda el lote. No siguió literalmente
  la sugerencia de separar agenda, pero recuperó el objetivo de persistencia.
- Nota 4 conserva la serie MSFT y propone AMZN/GOOGL; llamadas 42/43 consultan
  esas series. La información no guardada continúa hasta su integración posterior.
- Notas 14–18 conservan cálculos hechos y pendientes por empresa/año a través de
  varias renovaciones. Llamadas 103/111/113/115/116 completan ratios; llamada 125
  integra los cinco documentos. Nota 18 distingue calculado de integrado.
- Notas 19/20 distinguen reconciliación operativa de cálculo pendiente y evitan
  presentar la matriz completada como inexistente; después se explora crecimiento.
- No toda continuidad exige nota: tras fallar nota 12, llamadas 84–91 calculan
  márgenes y llamada 93 los integra utilizando el contexto/estado conservado.

## Interpretación e hipótesis

Hay evidencia de utilidad operativa local para conservar trabajo en curso y cifras
antes de integrarlas. En esta pareja, el estado con nota ofrece una síntesis de
inversión/caja más completa. No se puede atribuir esa diferencia solo a las notas:
una ejecución por brazo, elecciones divergentes desde el primer compromiso, fuente
viva y evaluación retrospectiva con etiquetas visibles. Menos renovaciones tampoco
demuestra mejor memoria ni es un efecto causal identificado.

El coste es material: nota ocupa 14% de llamadas totales; entrada total +17,4% y
salida +27,3% frente al otro brazo. No reduce claramente la carga de checkpoints
(43 frente a 45) ni los fallos de herramienta. Persisten lecturas y reconciliaciones.
Puede conservar también bloqueos imprecisos o prioridades caducadas.

Hipótesis para otro contraste: notas útiles sobre todo entre obtención e integración
de resultados, y menos útiles cuando repiten conocimiento ya persistido. La pareja
no identifica qué subconjunto bastaría ni demuestra que haya que cambiar el mecanismo.
La entrega final es débil en ambos brazos: se construye con una vista reducida y no
ofrece una síntesis fiel de todo el expediente. No confundir el último tramo con
el resultado global, ni el volumen documental con mejor juicio financiero.
