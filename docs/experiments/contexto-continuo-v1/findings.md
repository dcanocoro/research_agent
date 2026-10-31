# Contexto continuo V1–V4 — resultados y continuidad

Fecha: 2026-10-26. Estado: dos ejecuciones reales terminadas por límite de llamadas;
aceptación arquitectónica y financiera no evaluadas. El [protocolo](protocol.md)
posee escenario, límites y rúbrica. La repetición fue autorizada explícitamente por
el usuario tras revisar el bloqueo de paginación del primer intento.

## Evidencia y comparabilidad

Capturas completas locales e ignoradas, no portables por estas referencias:

- Original: `artifacts/contexto-continuo-v1/piloto/agente/ejecuciones/2026-10-26-piloto`,
  run `aa1e8d63-65b1-44b6-bae3-d042fc36a664`.
- Repetición: `artifacts/contexto-continuo-v1/piloto-entrega-maximo-v2/agente/ejecuciones/2026-10-26-piloto`,
  run `aede427e-5e82-4a44-a487-83b7a3683e3b`.
- Comparación mecánica: `artifacts/contexto-continuo-v1/comparacion-entrega-maximo-v2.json`.
  Contiene resúmenes y hash agregado de todos los archivos de la campaña original
  antes/después; el hash coincide. No se sobrescribieron sus capturas ni estado.

Antes de lanzar se verificó igualdad byte a byte de escenario, mandato, petición,
rúbrica, instrucciones, configuración del simulador y dataset; igualdad del perfil
y del hash de wheel registrado en la instalación. Ambos parten de agenda vacía,
100000 USD, sin posiciones ni órdenes y fecha 2023-01-01. OpenAI `gpt-6-luna`,
razonamiento medium y salida máxima 16000; 60 llamadas, 90 herramientas, 1200 segundos,
umbral 196608 bytes y máximo 524288. Web desactivada en ambos.

El único cambio de comportamiento de la repetición es entregar el resultado si cabe
bajo el máximo, aunque cruce el umbral de consolidación. No se cambian las herramientas
ni su límite de entrega directa de 32768 bytes. Las trayectorias del modelo difieren;
no es un replay determinista ni una comparación con múltiples réplicas.

## Observaciones mecánicas

| Medida | Original | Entrega corregida |
|---|---:|---:|
| Llamadas al modelo | 60 | 60 |
| Herramientas ejecutadas | 56 | 54 |
| Renovaciones de contexto | 6 | 6 |
| Llamadas de investigación / consolidación | 40 / 20 | 37 / 23 |
| Resultados sustituidos por referencia por el bucle continuo | 16 | 0 |
| Resultados limitados por el registro de herramientas | 3 | 4 |
| Invocaciones de `read_artifact` | 13 | 5 |
| Invocaciones de `read_file` | 13 | 16 |
| Tokens de entrada acumulados reportados | 601359 | 735443 |
| Tokens de salida acumulados reportados | 16776 | 15485 |
| Duración entre eventos inicial/final, segundos | 267,99 | 235,59 |
| Mayor presupuesto local enviado, bytes | 240614 | 261280 |
| Errores de captura | 0 | 0 |

Ambos terminan `interrupted: call_limit`, con retorno CLI 0 por pausa controlada.
Las 60 llamadas al proveedor son satisfactorias en cada intento. La fecha y cartera
permanecen iniciales, sin órdenes ni notificaciones. No hubo llamadas a `calculate`.
Los tokens de entrada incluyen contexto reenviado; no equivalen a información nueva
ni permiten deducir coste monetario sin precios y datos de facturación adecuados.

En la repetición llegaron páginas de Apple de aproximadamente 12 KB y 32 KiB;
se leyó también la cola desde offset 32768. Los materiales y originales se conservaron.
La ausencia de redirecciones del bucle continuo no significa ausencia de paginación:
siguen existiendo cuatro respuestas iniciales limitadas del registro de herramientas.

## Estado y progreso observado

El original dejó agenda, índice y un modelo provisional de Amazon con cifras parciales;
muchas lecturas quedaron sustituidas por referencias. La repetición deja agenda, índice
y modelos de Apple y Amazon, con series descriptivas más extensas: Apple FY2014–2021
y Amazon FY2015–2021 en sus tablas persistentes. Las cifras guardadas no se han sometido
a una auditoría financiera completa en esta revisión.

La comparación sigue inconclusa. Se conservan diferencias de cierre fiscal, disponibilidad
histórica estimada y limitaciones del precio normalizado. No hay valoración, evaluación
individual final ni decisión de inversión. El agente continúa solicitando desgloses o
explicaciones que no ha recuperado de este corpus de agregados, sin web.

Persisten problemas de continuidad y eficiencia: la repetición volvió a consultar Apple,
releyó notas/materiales y no ejecutó aritmética determinista. Al cierre, el modelo de Apple
todavía afirma que no hay extracción de Amazon ni evidencia comparable, aunque ya existe
el modelo de Amazon y la agenda contiene su comparación. Es una actualización pendiente
entre documentos, no una pérdida completa de mandato. La última respuesta conserva como
siguiente acción continuar una lectura de Amazon; no declara resuelta la comparación.

## Interpretación y límites

Las pruebas locales verifican que un resultado que cruza el umbral, sin superar el máximo,
se entrega y activa consolidación; el que excede el máximo sigue protegido. La campaña
confirma que las páginas reales ya no sufren la redirección adicional observada. Esta
es evidencia de corrección del bloqueo técnico específico.

No demuestra una mejora general de autonomía o calidad financiera. Hay más contenido
persistente y menos `read_artifact`, pero se consumen más tokens de entrada y sigue habiendo
repetición y documentos desactualizados. Más contenido entregado puede aumentar el contexto
reenviado; el coste por avance útil sigue requiriendo revisión semántica.

Se cumple exposición de al menos tres renovaciones con trabajo posterior; no se acredita
aceptación semántica completa. Los datos retrospectivos, disponibilidad estimada, ausencia
de fuentes narrativas y conocimiento previo del modelo limitan la inferencia histórica.
La prueba dura unos minutos y no caracteriza consumo de RAM ni comportamiento durante horas.

Antes de ampliar duración, revisar actualización entre documentos, selección de acciones
ante datos ya leídos y compatibilidad del encargo con el corpus. Conservar ambos intentos;
no tratar esta repetición como una prueba de alfa ni como decisión de arquitectura para FinMate.

## V3 — instrucciones y umbral mayor, 2026-10-27

Run `cb03b1de-bd63-42e5-bed3-062900976389`, en
`artifacts/contexto-continuo-v3/piloto/agente/ejecuciones/2026-10-27-piloto`.
La ejecución sí se realizó: 60 llamadas, 56 herramientas, cuatro renovaciones y doce
escrituras. Los eventos permiten reconstruir 44 llamadas de investigación y 16 de
consolidación, sin revisión adicional; todas las escrituras ocurrieron en consolidación.
El resultado registra `interrupted: call_limit`, sin errores de captura. El umbral
subió a 262144 bytes y cambiaron instrucciones frente a los pilotos iniciales;
no se trata de una réplica con un único factor aislado.

Conservó agenda, índice y modelos AAPL/AMZN. Ejecutó catorce cálculos y amplió AMZN
a FY2017–2021: la inversión relativa ya aumentaba en FY2020 sin FCF negativo, lo que
matiza una explicación simple de FY2021. Esa revisión descriptiva no demuestra
causalidad económica ni sostenibilidad. AAPL quedó menos actualizado; hubo recuperación
repetida y Adobe no llegó a tener modelo persistente. No produjo valoración ni decisión.

El modelo AMZN escribió un incremento de ingresos de 69.542 millones de USD para
FY2020: los importes declarados 386.064 y 280.522 millones dan **105.542 millones**.
Es un error en la prosa, no una salida válida de cálculo. La corrección se documenta
sin modificar el estado histórico. Las unidades normalizadas de precio no permiten
inferir múltiplos o atractivo; cartera y fecha continuaron sin avance.

## V4 — revisión periódica, 2026-10-27

Run `dfb4fd81-ad4b-4985-8c89-ee3c78c87581`, en
`artifacts/contexto-continuo-v4/piloto/ejecuciones/2026-10-27-piloto`.
El informe local `informe-resultados.md` se incorpora aquí en síntesis, contrastado
con resultados, manifiesto, eventos y snapshot. Es el piloto **sin Python**;
la repetición con Python es otra ejecución y tiene [hallazgos propios](../python-operators-v1/findings-v4.md).

| Medida | V3 | V4 sin Python |
|---|---:|---:|
| Investigación / consolidación / revisión | 44 / 16 / 0 | 44 / 16 / 4 |
| Total LLM / herramientas | 60 / 56 | 64 / 58 |
| Renovaciones | 4 | 4 |
| Escrituras ordinarias / totales | 0 / 12 | 2 / 13 |
| Cálculos aritméticos | 14 | 16 |
| Modelos conservados | 2 | 3 |

Las revisiones ocurrieron en las llamadas totales 15, 30, 41 y 60, después de diez,
veinte, treinta y cuarenta llamadas de investigación. Las consolidaciones no cuentan
para su frecuencia. La ejecución duró unos 348 segundos, con 64 respuestas del
proveedor y 58 herramientas satisfactorias. Cierre por `call_limit`, sin errores de
captura; `failed` en campaña expresa que no hubo `completed`, no una caída operativa.

Se actualizaron Apple y Amazon y se conservó Adobe. Las dos escrituras ordinarias
fueron la actualización de Apple en la llamada 47 y la revisión final de Adobe en
la 64. Las otras once siguieron concentradas en consolidación. V4 no reproduce la
ampliación AMZN FY2017–2018 de V3: más cálculos no equivalen a mayor profundidad.

La primera revisión confundió no tener herramientas en esa fase con una incapacidad
de la activación completa; una respuesta posterior lo corrigió. La tercera anunció
cerrar los cálculos y ampliar a otra empresa, transición que después ocurrió. La
cuarta orientó a buscar evidencia operativa: las últimas llamadas conservaron el
alcance infructuoso de las interfaces consultadas, sin demostrar ausencia de toda
fuente descriptiva. Reconocer una incertidumbre no aporta el método para resolverla.

Persistieron nueva extracción de Apple, consulta repetida del universo y relectura
de Adobe. Las páginas observadas comenzaron en offset cero: no se puede asumir lectura
completa de todo material. AMZN citó el inexistente `10-read-financials.json` cuando
el material era `08-read-financials.json`; la referencia sobrevivió a su revisión.
El incremento erróneo de ingresos de V3 no aparece en AMZN final, pero no se atribuye
esa diferencia causalmente a la autorrevisión.

La última respuesta textual procede de la llamada 51 y la agenda de la 58; el estado
incluye trabajo hasta la 64. `respuesta.md` no representa por sí sola el resultado
final. Las revisiones 15 y 60 recibieron el contexto reconstruido, sin el historial
completo anterior. Las cuatro consolidaciones consumieron cuatro llamadas cada una:
no redujeron ese gasto respecto a V3.

El informe local registra 1.123.113 tokens de entrada y 22.333 de salida, frente a
1.238.863 y 17.948 en V3; no son información nueva ni una factura. Los tiempos de
proveedor sumados fueron 343,1 s (24,3 s de revisión), distintos del tiempo de ciclo.
La entrada sin caché reportada subió de 202.267 a 211.328; no cabe inferir menor coste
monetario de la reducción de entrada acumulada. Estos desgloses se conservan como
observación del informe local, no se recalcularon todas las trazas en la consolidación.

Mandato, dataset, perfil, prompts y límites compartían hashes, pero la petición V3
presentaba caracteres mal codificados que V4 recibió correctamente. Cambian runtime
y presupuesto adicional, hay un intento por condición y las trayectorias divergen
antes de revisar. Solo hay señales parciales de conservación y seguimiento de
prioridades, sin mejora causal demostrada. Termina con 100.000 USD ficticios, sin
posiciones ni órdenes, en 2023-01-01; no hay valoración ni resultado de inversión.

## Procedencia y disponibilidad

Revisión documental del 2026-10-31: se leyeron manifiestos, resultados, eventos y
snapshots finales de los cuatro pilotos, además de los documentos finales V3/V4 y
el informe V4. Los recuentos de herramientas, escrituras y renovaciones se contrastaron
con eventos; no se repitieron campañas ni una auditoría financiera completa.
Las carpetas originales y los IDs constan arriba. La comprobación inicial
`artifacts/contexto-continuo-v1/comprobacion-inicial` es preparación, no otro resultado
semántico. Las capturas son locales y pueden archivarse fuera del checkout; esta
narrativa conserva lo aprendido, pero una auditoría detallada exige recuperar originales.
