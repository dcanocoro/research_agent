# Terminación del ReAct acotado — resultados de la tanda

Campaña del 2026-11-08. [Protocolo](protocol.md),
[piloto y lanzamiento](execution-2026-11-08.md).

## Alcance y estado de la revisión

Se completaron los 108 trabajos previstos: 12 casos sintéticos, tres condiciones y
tres repeticiones. El piloto de seis trabajos queda excluido de estos resultados.
La tanda comenzó a las 20:46:35 y terminó a las 21:03:39, Europe/Madrid.
Las tres condiciones usaron `gpt-6-luna`, razonamiento medium, con archivos y
aritmética locales, sin web, Findata, continuo, Progress, nota o B.

Este informe combina contabilidad determinista y una revisión abierta de las 108
respuestas finales, sus secuencias de herramientas y las 32 decisiones del checkpoint.
La revisión conoce las condiciones y no sustituye al juez ciego independiente previsto
en el protocolo. No se han asignado puntuaciones retrospectivas ni anotado de forma
exhaustiva todos los primeros prefijos suficientes. La calidad que se comenta es un
juicio de revisión, no una aceptación semántica independiente ni una prueba estadística.

## Resultado principal

No aparece una mejora global demostrada de terminación sobre V0. V1 consume casi
las mismas llamadas y tiempo. V2 reduce el trabajo de A, pero sus revisiones cuestan
más llamadas de las que ahorra en el agregado. Hay cierres puntuales razonables y
también pérdida de contenido respecto de la rúbrica. No se recomienda adoptar V2
como control predeterminado a partir de esta tanda.

| Medida | V0 actual | V1 autocontrol | V2 autocontrol + checkpoint |
|---|---:|---:|---:|
| Trabajos con respuesta | 36 | 36 | 36 |
| Llamadas de A | 331 | 332 | 309 |
| Llamadas de checkpoint | 0 | 0 | 32 |
| Llamadas totales | 331 | 332 | 341 |
| Media de llamadas por trabajo | 9,19 | 9,22 | 9,47 |
| Herramientas ejecutadas | 295 | 296 | 273 |
| Segundos acumulados de los trabajos | 901,59 | 894,94 | 1011,62 |
| Segundos medios por trabajo | 25,04 | 24,86 | 28,10 |
| Tokens de entrada del proveedor | 2065290 | 2055924 | 2215651 |
| Tokens de salida del proveedor | 55849 | 50204 | 61144 |

El tiempo acumulado suma trabajos, no representa duración de pared de toda la tanda
paralela. Las diferencias de latencia pueden incluir contención del proveedor.
Los tokens de salida incluyen generación interna, no solo longitud de respuesta final.
No se estimó coste monetario ni se consultó una tarifa.

V1 frente a V0: +1 llamada (+0,3 %), −0,7 % de tiempo acumulado y −10,1 % de tokens
de salida. El último dato es una diferencia observada de consumo, pero no demuestra
que el prompt haya mejorado el criterio de cierre ni que las respuestas finales sean
un 10 % más cortas.

V2 frente a V0: A usa 22 llamadas menos (−6,6 %), pero añade 32 revisiones: total
de 10 llamadas más (+3,0 %). Usa +12,2 % de tiempo acumulado, +7,3 % de tokens de
entrada y +9,5 % de salida. El coste del control no desaparece porque A trabaje menos.
Los checkpoints suman 337209 tokens de entrada y 11644 de salida, sin entrada cacheada
registrada; el cacheado difiere entre condiciones, por lo que llamadas y tokens no
deben convertirse directamente en euros.

Se verificaron los 1004 registros LLM de la tanda y la lectura de sus archivos gzip:
todos con estado success, sin usage ausente ni errores de archivo detectados. Coinciden
con el total de llamadas gestionadas. No hay herramientas fallidas ni capture_errors.
Esto acredita integridad operativa, no corrección económica de todas las respuestas.

## Qué hizo el agente en cada caso

Las cifras son medias de tres repeticiones; V2 incluye el coste del checkpoint.
El análisis de respuestas se refiere a esta revisión abierta, sin puntuar calidad.

| Caso | V0 | V1 | V2 | Conducta y resultado observado |
|---|---:|---:|---:|---|
| S1 Alba: extraer ingresos | 2,00 | 3,33 | 3,00 | Identifican 240 millones EUR. V0 lee y responde; otras repeticiones listan carpetas antes de leer una ruta ya indicada en el índice. No hay checkpoint. |
| S2 Brisa: crecimiento | 5,33 | 5,00 | 6,67 | Responden 25 %, con fórmula y fuente. La secuencia usual resta, divide y convierte a porcentaje. En V2 la navegación adicional hace alcanzar el umbral en una repetición y el control añade una revisión sin mejorar la respuesta. |
| S3 Cauce: PER sin precio | 4,33 | 4,67 | 4,00 | Reconocen que falta precio/capitalización y no inventan PER. Casi todos calculan opcionalmente BPA de 2 EUR. El cierre por insuficiencia ya funciona en V0. |
| S4 Duna: corrección | 3,33 | 4,00 | 3,67 | Usan 135 millones de operaciones continuadas y reconcilian los 15 de la unidad discontinuada. Algunas repeticiones añaden una suma/resta; ninguna necesita el controlador. |
| M1 Encina: márgenes | 9,33 | 12,33 | 10,00 | Responden 10 % → 15 %, +5 puntos; no inventan causa económica. V1 navega más y alguna vez repite un cálculo. V2 cierra una repetición tras los márgenes sin exigir cuantificar todos los crecimientos opcionales. |
| M2 Faro: caja ajustada | 15,67 | 14,00 | 15,00 | Distinguen FCO 60→90 reportado y 50 ajustado; FCF 40→65 y 25 ajustado. Evitan equiparar el ajuste a una depuración completa de recurrencia. V1 ahorra algo; V2 pierde parte del ahorro con revisiones. |
| M3 Greda/Haya: comparación | 10,67 | 10,33 | 11,33 | Calculan 20 % reportado y 5 % sin adquisición en Greda, frente a 25 % de nueve meses de Haya. No ordenan crecimiento orgánico anual con periodos incompatibles. Las tres revisiones de V2 piden continuar; solo añaden coste. |
| M4 Isla: liquidez | 13,00 | 11,67 | 15,00 | Excluyen caja restringida y línea no firmada. Obtienen recursos de 65 y 45 frente a deuda de 70, déficits de 5 y 25, sin garantizar liquidez por falta de calendario. V2 revisa dos veces cada trabajo y cierra casi donde V0 ya respondía. |
| O1 Junco: calidad del crecimiento | 14,67 | 13,33 | 14,33 | Separan +30 % de volumen, caída de margen 15 %→10 % y caja tras capex 27→−5. No convierten la promesa de liberar inventario en hecho. V1 ahorra en agregado; V2 detiene dos respuestas, pero el control compensa el ahorro. |
| O2 Linde: concentración | 7,33 | 8,00 | 7,33 | Cuantifican 200 de ingresos expuestos, 60 de contribución perdida y −10 de operativo en estrés. No concluyen insolvencia ni tratan el estrés como previsión. Dos cierres V2 no producen ahorro global frente a V0. |
| O3 Marea: empresa mejor/acción barata | 11,33 | 10,33 | 10,33 | Distinguen mejora operativa de valoración sin precio. Una repetición V1 y otra V2 omiten el cálculo de caja tras capex de 75 previsto en la rúbrica; ambas son más cortas. En V2 esa omisión aparece después de REQUEST_FINISH. |
| O4 Noria: recuperación corregida | 13,33 | 13,67 | 13,00 | Usan 230/16 corregidos, no 260/26 preliminares; cuestionan la caja sostenida por cobros heredados. V2 ahorra ligeramente en promedio, con un cierre solicitado en la tercera repetición; el gran ahorro del piloto no se repite. |

## Cómo funcionó el controlador externo

32 revisiones válidas: 20 CONTINUE y 12 REQUEST_FINISH. Ninguna falló o se reparó.
De las 12 solicitudes de cierre, cinco fueron tras la llamada 6 y siete tras la 12.
Las otras 24 respuestas de V2 terminaron voluntariamente. No se debe interpretar cada
REQUEST_FINISH como ahorro: puede llegar justo antes de una respuesta que A ya iba a dar.

Ejemplos que aclaran el resultado:

- **Cierre útil plausible, M1-03-V2:** a la sexta llamada ya tenía los dos márgenes
  y su diferencia. El checkpoint pidió terminar y la respuesta conservó 10 %, 15 %,
  +5 puntos y ausencia de causa documentada. Total 8 llamadas frente a 10 en V0 y
  13 en V1 para la misma repetición. Omitió tasas de crecimiento adicionales que
  no eran obligatorias para expresar la comparación cualitativa pedida.
- **Control sin ahorro, M4:** en las tres repeticiones de V2 se revisó tras 6 y 12.
  Se hizo el análisis de liquidez y se respondió con 13 llamadas de A más 2 de control.
  V0 también usó 13 llamadas por repetición, sin control. La instrucción externa
  pudo ser razonable y aun así aumentar el coste.
- **Omisión a revisar, O3-03-V2:** el checkpoint permitió cerrar tras cuatro cálculos:
  márgenes y relaciones de crecimiento. Conservó la conclusión económica principal,
  pero la respuesta no calculó los 75 de flujo operativo menos capex exigidos por
  la rúbrica previa. No es un error numérico; es cobertura incompleta respecto de
  ese criterio. El prompt del caso pide cálculos pertinentes sin enumerarlos, lo que
  introduce margen de juicio al decidir la gravedad. La misma omisión aparece en
  O3-03-V1 sin checkpoint: no debe atribuirse exclusivamente al control externo.
- **Umbral de suficiencia variable, M1:** en dos repeticiones el evaluador pidió
  calcular las tasas de crecimiento de beneficio/ingresos antes de cerrar; en la
  tercera permitió terminar con los márgenes ya calculados y comparó esas tasas
  en su propia razón. La distinción entre comprobación necesaria y ampliación
  opcional no fue estable.

El controlador identifica bien varios pendientes materiales (FCF de Faro, estrés
de Isla, ajuste de caja de Noria). Pero un checkpoint periódico solo observa ciertos
momentos: no sabe si A habría cerrado en el siguiente paso, y puede llegar después
de cálculos opcionales. No se midió un contrafactual de la misma trayectoria sin
intervención; las otras condiciones son repeticiones comparables, no su continuación exacta.

## Interpretación y límites

El patrón dominante fue leer, calcular y responder. No hubo bucles largos de nuevas
fuentes ni expedientes innecesarios: ninguna de las 108 secuencias invocó escritura
de análisis. V0 terminó sus 36 trabajos voluntariamente; tres respuestas llegaron
a la fase de consolidación por reserva, pero no cerraron por agotamiento del máximo.
Las instrucciones base ya piden materialidad, evitar relecturas rutinarias y permitir
consultas breves sin expediente. V1 no se compara con un agente carente de esas guías.

Las herramientas también explican el consumo. Hubo 215 cálculos en V0, 209 en V1
y 190 en V2. Cada calculate realiza una sola operación binaria; una fórmula con
resta, división y porcentaje puede exigir tres llamadas al modelo. Esas llamadas
no son automáticamente sobretrabajo. También hubo 101 listados de directorio en
total, aunque el índice señalaba la ruta del único corpus. Algunas repeticiones
hicieron más navegación o aritmética repetida sin cambiar la respuesta. Este
hallazgo orienta una hipótesis futura sobre acceso directo y granularidad de cálculo;
no autoriza modificar las herramientas ni demuestra de antemano su mejora.

La revisión abierta encuentra conclusiones centrales generalmente alineadas con los
casos y buena calibración de insuficiencia. No se afirma «108 respuestas correctas»:
hay omisiones citadas, variación en trazabilidad de referencias y ninguna evaluación
ciega adjudicada. No se calcula una tasa definitiva de cierre prematuro.

Estos 12 casos tienen corpus único, breve y completo, sin búsqueda web ni latencias de
datos. Son adecuados para una primera prueba de suficiencia y cálculos, pero apenas
reproducen investigación abierta con fuentes redundantes. Tres repeticiones por caso
no establecen significación ni generalización a otros modelos, herramientas o FinMate.
El piloto por sí solo habría sugerido un ahorro de V2 que la tanda no confirmó.

**Recomendación provisional:** mantener V0 como referencia; no adoptar V2 por defecto
ni declarar V1 superior en terminación. Completar la revisión ciega prevista antes
de cerrar el juicio de calidad. Si se autoriza otro contraste, distinguir ahorro
por mejor cierre de ahorro por reducir navegación/cálculos accesorios y probar
casos donde la investigación pueda realmente prolongarse sin aportar valor.

## Procedencia y disponibilidad

Raíz local original: `artifacts/terminacion-paralelo-20261108-204413/`.
La tanda está en `full/V0`, `full/V1`, `full/V2`, cada una con36 trabajos y sus
manifiestos, respuestas, conversación, eventos y payloads. `full/launch.json`
registra finalización y retorno0 de los tres procesos. `analysis/metrics.json` y
`analysis/trajectories.json` son derivados locales de esta revisión, no nuevas
ejecuciones ni sustitutos de las capturas originales. El perfil/wheel y la
preparación están descritos en la [entrega](../../deliveries/2026-11-08-termination-experiment.md).

Las capturas siguen disponibles localmente al revisar. `artifacts/` es ignorado y
no portable; este informe conserva condiciones, resultados y límites sin requerirlo.
Para repetir auditoría, conservar la raíz original completa y el wheel efectivo.
No se ejecutó un juez adicional, ni se cambió código, modelo, prompts o herramientas
como consecuencia de estos hallazgos.
