# Campaña V5 — primer intento y repetición corregida

Fecha: 2026-10-28. Registro consolidado de dos intentos: interrupción temprana
y repetición de 100 llamadas tras la corrección. La sección inicial conserva el primer intento.
El [protocolo](protocol.md) fijó el escenario V4, estado nuevo, Python, V5 y 100 llamadas
ordinarias. **Solo se realizaron 11 llamadas; no se alcanzó el límite solicitado.**
No se corrigió el runtime ni se repitió el intento para ocultar esta observación.

## Condiciones y evidencia

Mandato, petición, rúbrica y dataset coinciden por hash con la última V4 con Python.
El dataset conserva SHA-256 `4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`.
Fecha fija 2023-01-01, 50 empresas, 100.000 USD ficticios y cartera nueva; sin web
ni consultas a BD remota. Modelo `gpt-6-luna`, medium, salida máxima 16000.
El manifiesto confirma V5 y Python habilitados. Presupuesto inicial efectivo: 184979
bytes, con reserva de salida de 128000; umbral 262144 y máximo 524288.

Run: `640c90fa-d9eb-4e97-85e5-71cea9bd9053`.
Captura local (`artifacts/contexto-continuo-v5/piloto-100-llamadas/README.md`; referencia local histórica) y
resumen verificable (`artifacts/contexto-continuo-v5/piloto-100-llamadas/resumen-observacion.json`; referencia local histórica).
Son artefactos locales ignorados por Git: el enlace no los convierte en evidencia portable.

| Observación | Resultado |
|---|---|
| Límite configurado | 100 llamadas ordinarias, revisiones adicionales; 150 herramientas; 1200 segundos |
| Llamadas realizadas | 11: 10 investigación, 1 consolidación, 0 revisión |
| Herramientas | 10 exitosas, 1 rechazada |
| Renovaciones | 0; exposición insuficiente para la rúbrica de continuidad |
| Tiempo | 40,006 s de ejecución según eventos; 46,125 s del lanzamiento completo |
| Cierre | Agente `interrupted: consolidation_failed`; registro de campaña `failed` |
| Captura | Completa según inspector nativo; cero errores de captura |
| Estado editable | Ninguna escritura de conocimiento; agenda inicial sigue vacía |
| Materiales | Seis originales conservados automáticamente |
| Cartera | 100.000 USD, sin posiciones, órdenes ni comunicaciones; fecha intacta |
| Uso reportado | 170974 tokens de entrada y 1582 de salida; 122181 de entrada cacheada; 11 intentos de proveedor |

## Qué ocurrió

La primera operación fue `inspect_state`, que devolvió `agenda.md` existente y vacía
(0 bytes, SHA-256 del contenido vacío). A comenzó una comparación de AAPL y AMZN,
consultó universo, cartera, perfiles y fundamentales; recuperó resultados con
`read_artifact`. No utilizó Python ni las operaciones específicas de empresa.

Al entrar en consolidación intentó conservar la investigación con `edit_state` sobre
la agenda. Envió el hash correcto del archivo vacío, pero una sustitución cuyo objetivo
era el carácter NUL (`\u0000`), inexistente en el documento. La herramienta rechazó
el objetivo con `ambiguous_target`; el mensaje cubre tanto ausencia como ambigüedad.
El rechazo conserva el archivo: no hubo escritura parcial ni conflicto de versión.

La traza exacta (`artifacts/contexto-continuo-v5/piloto-100-llamadas/ejecuciones/2026-10-28-piloto/trazas/herramienta-0064.json`; referencia local histórica)
conserva argumentos y respuesta. El texto propuesto para la agenda está en esos
argumentos, **no** en el estado editable. No confundir ese borrador archivado con
conocimiento persistido y recuperable en la siguiente ventana de A.

La política del ciclo continuo vigente en ese intento finalizaba la ejecución
ante cualquier resultado no exitoso de una herramienta en consolidación. Por ello
el modelo no recibió otra oportunidad para corregir el ancla o elegir un escritor
compatible. El límite de 100 llamadas, las herramientas y el tiempo no fueron la causa.

## Interpretación y límites

**Observado:** adopción inicial de orientación V5 y un intento de edición con propósito
explícito. La validación protegió el estado y la captura conservó el fallo. La combinación
de una operación inválida elegida por A y la política de cierre impidió continuar.

**No demostrado:** utilidad de la lectura selectiva, expedientes acumulativos,
recuperación tras renovación, revisión de dependencias, calidad financiera o mejora
frente a V4. No hubo exposición suficiente ni un control equivalente; tampoco hubo
valoración calculada o decisión de inversión evaluable.

Se preservó una muestra externa de RAM del lanzador y sus descendientes: suma de RSS
382832640 bytes y memoria privada 338001920 bytes. Una muestra no establece pico,
estabilidad ni consumo propio de A; sumar RSS puede contar páginas compartidas dos veces.
El resumen conserva por separado el uso reportado en trazas, sin inferir precio o coste.

## Siguiente intervención propuesta

Antes de otra campaña larga, resolver dos puntos mediante un encargo explícito y
pruebas locales: cómo inicializar con versión un archivo ya existente pero vacío,
y si los errores recuperables de herramienta deben permitir corrección dentro del
presupuesto de consolidación. Las herramientas antiguas permiten escribir la agenda,
pero no ofrecen la precondición de versión de V5. No se introduce una excepción que
trate NUL como comodín ni se flexibiliza silenciosamente la unicidad de los objetivos.

Una repetición posterior debe conservar este intento, declarar cualquier cambio de
schema/instrucciones/política y comenzar con un estado nuevo. Este hallazgo no acepta
una modificación del ciclo ni una arquitectura nueva por sí solo.

Encargo posterior del usuario, 2026-10-28: eliminar el cierre automático ante errores
de herramienta en consolidación. La [entrega](../../deliveries/2026-10-28-state-tools-v5.md)
registra la corrección y sus pruebas locales. No modifica los resultados de este
intento ni constituye una repetición de la campaña.

## Repetición tras la corrección del 2026-10-28

Fecha: 2026-10-28. Ejecución real autorizada, posterior a la corrección de errores
durante consolidación. **La campaña alcanzó las 100 llamadas ordinarias previstas.
El ciclo pudo recuperarse de errores, pero la calidad del conocimiento conservado es
parcial: hubo fricción instrumental, organización semántica defectuosa y una cifra
incorrecta trasladada al texto.** No se ha demostrado superioridad financiera.

El [protocolo](protocol.md) fija condiciones y límites. Se conserva el
primer intento de 11 llamadas descrito arriba, sin modificar sus resultados.
La captura nativa (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/README.md`; referencia local histórica),
el resumen mecánico (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/resumen-observacion.json`; referencia local histórica)
y las comprobaciones posteriores (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/comprobaciones-locales.json`; referencia local histórica)
son evidencia local, ignorada por Git; los enlaces no la hacen portable.

### 1. Qué se ejecutó y cómo terminó

Run `02bca6eb-c836-484f-a7d4-e83a0b343329`. Mandato, petición, rúbrica, escenario e
instrucciones coinciden con el primer V5; el perfil y los límites también. La comparación
de fingerprints encuentra un único archivo de ejecución modificado: `continuous.py`.
La intervención elimina el cierre automático ante errores de herramienta y lo explica
en el aviso técnico de consolidación. No se alteraron herramientas durante la campaña.

Se mantuvieron 50 empresas, fecha simulada 2023-01-01, 100.000 USD ficticios, máximo
de diez posiciones, estado inicial nuevo y Python habilitado. Web desactivada y datos
locales congelados, sin consultas financieras a BD remota. Modelo OpenAI `gpt-6-luna`,
razonamiento medium y salida máxima 16000. Dataset SHA-256
`4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`.

| Medida | Resultado |
|---|---:|
| Llamadas ordinarias | 100 de 100 |
| Investigación | 66 |
| Consolidación | 34 |
| Revisión periódica, adicional | 6 |
| Total de llamadas al modelo | 106 |
| Intentos de proveedor registrados | 106; sin intentos adicionales observados |
| Herramientas | 95: 82 exitosas y 13 rechazadas |
| Renovaciones de contexto | 10 |
| Duración del agente según eventos | 779,157 s, aproximadamente 12 min 59 s |
| Duración del lanzamiento completo | 785,390 s, aproximadamente 13 min 5 s |
| Captura | Completa; cero errores de captura |
| Cierre del agente | `interrupted: call_limit` |

Las 106 llamadas respetan el límite: las seis revisiones son adicionales a las 100
ordinarias. La campaña no terminó el mandato; agotó su presupuesto. El registro general
la etiqueta `failed` porque el controlador exige `agent_status=completed`. Aquí esa
etiqueta no significa una caída del proceso ni corrupción de la captura.

### 2. Recorrido de investigación y continuidad

A empezó comparando AAPL y AMZN. Conservó cifras anuales y una hipótesis sobre su
generación de caja; después precisó que la caída de FCF de AMZN combinaba menor caja
operativa y mayor capex, sin establecer causalidad. Buscó explicación narrativa o por
segmentos en las extracciones disponibles y dejó constancia de su insuficiencia.

Más adelante amplió el contraste a ADP, calculó márgenes y cambios entre ejercicios,
y moderó la preferencia provisional por su aparente estabilidad. Finalmente añadió
AON como candidato de análisis posterior, con reservas sobre variación de márgenes,
deuda y falta de explicación económica. Selección para investigar no equivale a compra.

| Renovación | Llamada total al renovar | Archivos cambiados y continuación observada |
|---|---:|---|
| 1 | 14 | Agenda y modelos AAPL/AMZN; después profundiza en financieros de AMZN. |
| 2 | 22 | Agenda y AMZN; recupera documentos de ambas empresas para contrastarlos. |
| 3 | 36 | Modelo AAPL, tras intentos de reparación estructural; vuelve a materiales corporativos. |
| 4 | 43 | Agenda y AAPL; continúa leyendo materiales e intentando recuperar el modelo vigente. |
| 5 | 51 | Agenda; falla la consulta a un índice inexistente y se orienta mediante inventario y lecturas. |
| 6 | 59 | Agenda; consulta el universo y abre ADP. |
| 7 | 70 | Agenda y modelo ADP; recupera su serie financiera y fundamentos. |
| 8 | 77 | Agenda y ADP; necesita corregir dos selectores antes de leer el documento. |
| 9 | 83 | Sin cambios de archivos; después recupera las bases y ejecuta la comparación con Python. |
| 10 | 97 | Agenda y ADP con los cálculos; amplía a AON y conserva su cribado al final. |

El mandato original aparece íntegro en las once ventanas del historial. La agenda
se incorpora a cada reconstrucción y hay investigación posterior a las diez
renovaciones. Se supera la exposición mínima de la rúbrica; esto acredita continuidad
del mecanismo, no fidelidad semántica completa. AON se guardó al final: no se observó
su recuperación en una ventana posterior.

Hubo 19 escrituras de conocimiento exitosas, **todas durante consolidación**. No se
observó guardado ordinario durante las llamadas de investigación. La consolidación
consumió el 34 % del presupuesto ordinario; no debe confundirse ese trabajo con nuevas
consultas económicas ni atribuirle utilidad por el número de archivos producidos.

### 3. Adopción de herramientas y recuperación de errores

Las herramientas V5 recibieron 57 de las 95 llamadas a herramientas; 44 tuvieron éxito
y 13 fueron rechazadas. Las restantes fueron consultas financieras, utilidades antiguas
de archivos y Python. La adopción es real, pero no hubo un control de igual presupuesto
que permita atribuirle una mejora de eficiencia.

| Herramienta V5 | Intentos | Éxitos | Rechazos |
|---|---:|---:|---:|
| `inspect_state` | 8 | 4 | 4 |
| `read_state` | 6 | 4 | 2 |
| `search_state` | 1 | 1 | 0 |
| `create_state` | 1 | 0 | 1 |
| `edit_state` | 8 | 8 | 0 |
| `inspect_company` | 8 | 8 | 0 |
| `read_company_document` | 13 | 9 | 4 |
| `update_company_document` | 12 | 10 | 2 |
| `describe_state_tools` | 0 | 0 | 0 |

Los contratos de estado estaban disponibles, pero A no los consultó. Sí consultó dos
veces el contrato Python. Las respuestas V5 observadas no superaron 13794 bytes
serializados. Esto comprueba acotación en este intento, no selección óptima del contexto;
la conservación de un fragmento no demuestra que contenga todos los fundamentos.

Los 13 errores se distribuyeron en cinco llamadas de consolidación y ocho de investigación:

| Motivo | Casos | Observación |
|---|---:|---|
| Selector inválido o rango fuera del archivo | 6 | Combinó ID y selector, usó línea/sección cero o pidió bytes más allá del final. |
| `indice.md` inexistente | 4 | Se repitió la búsqueda en distintas ventanas; el archivo nunca se creó. |
| Crear una agenda ya existente | 1 | La agenda inicial existía aunque estuviera vacía. |
| Sustitución cuyo objetivo no estaba presente | 1 | El hash era correcto; el texto exacto solicitado no coincidía. |
| Eliminar un ID reconocido | 1 | La edición habría retirado `E2`; no era un conflicto de versión. |

La recuperación tras error se observó de forma directa:

- Llamada 13: `create_state` rechaza la agenda existente. La 14 la guarda con
  `write_markdown` y se renueva el contexto.
- Llamadas 34 y 35: fallan dos revisiones de AAPL. La 36 aplica otra revisión y
  la ejecución continúa. La protección de IDs no se desactiva para conseguirlo.
- Llamada 40: lectura fuera de rango. La 41 corrige el selector; las 42 y 43
  actualizan modelo y agenda dentro de la misma consolidación.

Las trazas correspondientes son
0076 (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/ejecuciones/2026-10-28-piloto/trazas/herramienta-0076.json`; referencia local histórica),
0082 (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/ejecuciones/2026-10-28-piloto/trazas/herramienta-0082.json`; referencia local histórica),
0195 (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/ejecuciones/2026-10-28-piloto/trazas/herramienta-0195.json`; referencia local histórica),
0200 (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/ejecuciones/2026-10-28-piloto/trazas/herramienta-0200.json`; referencia local histórica)
y 0206 (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/ejecuciones/2026-10-28-piloto/trazas/herramienta-0206.json`; referencia local histórica).

Los trece errores están en el historial y todos fueron seguidos por nuevas llamadas
del modelo. Continuar no implica resolver la causa: la ausencia del índice, por ejemplo,
se sorteó con otras operaciones, pero siguió causando consultas fallidas.

### 4. Qué quedó conservado y qué problemas presenta

Quedaron cinco documentos de conocimiento: agenda y modelos de AAPL, AMZN, ADP y AON,
además de veinte materiales originales. No se crearon índice, valoraciones ni evaluaciones.
La representación sigue siendo progresiva; la ausencia de esos documentos no prueba
por sí sola falta de investigación, pero aquí tampoco hubo valoración cuantitativa.

La reproducción determinista de las 22 mutaciones intentadas —19 aplicadas y tres
rechazadas— coincide con el snapshot final. No se detectaron IDs duplicados bajo la
convención ATX. Estas comprobaciones de integridad no validan el significado del texto.

La revisión focalizada encontró tres problemas materiales:

**AAPL: ID conservado, argumento mal localizado.** La sección `H1` quedó con un
encabezado y líneas vacías; parte del razonamiento que le correspondía aparece bajo
`E3`. Una lectura posterior por `identifier="H1"` devuelve solo el encabezado vacío.
A había identificado el problema estructural en sus motivos de edición, pero la
reparación aplicada no lo resolvió. Preservar el ID y aceptar la escritura no garantiza
continuidad semántica. Puede verse en el
modelo final (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/estado/empresas/AAPL/modelo.md`; referencia local histórica)
y en la comprobación de lectura por ID guardada en `comprobaciones-locales.json`.

**ADP: revisión parcial del pendiente.** `E2` incorpora la comparación calculada y
explica que modera `H1`, mientras que el apartado pendiente de `H1` todavía pide
recuperar los datos para cuantificar esos ratios. El documento conserva tanto el
avance como una tarea que ya está parcialmente resuelta. La referencia a
`valoracion.md#V1` no se puede resolver, aunque se declara expresamente futura y
pendiente de crear; no debe presentarse como una valoración existente.

**Agenda: acumulación de intenciones.** Conserva límites y fundamentos útiles, pero
superpone un siguiente paso sobre AON con otros anteriores de ADP/AAPL/AMZN. Reúne
historia y prioridad vigente sin depuración suficiente. Esto dificulta interpretar
qué debe recuperarse y qué trabajo sigue realmente pendiente.

La revisión de referencias fue literal y limitada: treinta referencias completas
fueron comprobadas por existencia e IDs. Las abreviaturas como `...05-...` quedaron
fuera de esa comprobación automática; los materiales originales conservan los nombres
completos. Existencia de una fuente no certifica la inferencia que la cita.

### 5. Python, aritmética y fidelidad del documento

Se ejecutaron dos operadores `calculate`, ambos con éxito. El primero usó NumPy para
comparar márgenes FCF, media, extremos y cambios entre ejercicios de ADP, AAPL y AMZN.
El segundo usó Python básico para márgenes y cambios de AON. Las duraciones del ejecutor
sumaron 4,516 s, sin incluir las llamadas al modelo que prepararon el código.

La comprobación posterior con Decimal contrastó **30 observaciones de entrada** con
sus materiales citados, controlando empresa, ejercicio, moneda y escala, y **42 salidas
numéricas derivadas** con las fórmulas programadas, a tolerancia relativa/absoluta
1e-12. Coinciden. Algunas salidas expresan el mismo ratio como fracción y porcentaje;
no son 42 hallazgos económicos independientes.

Eso no cierra la validación de unidades ni del texto:

- En AON, el campo de salida `fcf_margin_change_pp` vale `0.021528...`: el código
  devuelve una diferencia de fracciones pese al sufijo de puntos porcentuales.
  Convertido correctamente son aproximadamente **2,15 puntos porcentuales**, como
  sí aparece en el documento. El nombre del campo es engañoso.
- El modelo de AON afirma que el margen operativo cayó **8,99 puntos** entre 2020 y
  2021. Las entradas y la salida de Python dan aproximadamente **25,131 % → 17,141 %**:
  caída de **7,99 puntos**, no 8,99. El error está en el texto conservado, no en las
  divisiones ejecutadas. Esa diferencia adicional tampoco se devolvió como tal en
  el resultado Python.

Las fuentes de comprobación son los materiales
16 — comparación (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/estado/materiales/2026-10-28-piloto-16-run-python.json`; referencia local histórica),
20 — AON (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/estado/materiales/2026-10-28-piloto-20-run-python.json`; referencia local histórica)
y el modelo final de AON (`artifacts/contexto-continuo-v5/repeticion-100-llamadas/estado/empresas/AON/modelo.md`; referencia local histórica).
Se conservan estos errores en la evidencia: no se corrigen retrospectivamente los
documentos generados por A.

Como aspecto favorable, los documentos distinguen asociación de causalidad, ejercicios
fiscales diferentes y selección para investigar de atractivo inversor. Reconocen que
el precio normalizado 100 no permite valorar por acción. No se emitieron órdenes:
la cartera conserva 100.000 USD, sin posiciones, operaciones ni comunicaciones.
No hubo DCF ni una evaluación de inversión completa.

### 6. Consumo y límites de observación

| Fase | Llamadas | Tokens de entrada reportados | Tokens de salida reportados |
|---|---:|---:|---:|
| Investigación | 66 | 1058843 | 10856 |
| Consolidación | 34 | 954968 | 32851 |
| Revisión | 6 | 100466 | 8790 |
| Total | 106 | 2114277 | 52497 |

Las trazas reportan 1648364 tokens de entrada cacheados y 29863 de razonamiento.
Son desgloses, no cantidades que deban sumarse de nuevo al total. No se infiere precio
ni coste monetario. La entrada acumulada incluye contexto repetido, no conocimiento
nuevo en esa cantidad. La consolidación concentra aproximadamente el 63 % de la salida
reportada; no es evidencia por sí sola de gasto inútil o de conservación adecuada.

El presupuesto inicial fue 184979 bytes, incluida una reserva heurística de salida
de 128000. El máximo observado antes de una llamada fue 512724, bajo el límite de
524288. Es contabilidad local serializada con margen, no un tokenizer remoto exacto.

Se tomaron siete muestras externas del lanzador y sus descendientes. La mayor suma
observada de RSS fue 389189632 bytes, unos 371,2 MiB; la de memoria privada,
343470080 bytes, unos 327,6 MiB. No son el pico real ni la memoria aislada de A:
las muestras pueden omitir trabajadores breves y RSS puede contar páginas compartidas
dos veces. No permiten afirmar estabilidad o un límite duro de memoria.

### 7. Valoración y próximos contrastes

**Confirmado mecánicamente:** se completó el presupuesto previsto; los errores de
herramienta dejaron de ser fatales; hubo renovación, recuperación de archivos,
adopción sustantiva de V5 y dos cálculos Python contrastados. La captura permite
reconstruir qué ocurrió, incluidos errores e intentos de reparación.

**Parcial en el plano analítico:** A amplió candidatos y moderó una hipótesis con
evidencia cuantitativa, pero los modelos son principalmente cribados financieros.
No establecen suficientemente mecanismos económicos o sostenibilidad, y contienen
problemas de localización, actualización y fidelidad numérica. No es aceptación de
V5 como solución semántica ni prueba de mejor inversión.

Para un siguiente encargo, las prioridades respaldadas por este intento son:

1. Reducir errores de selección: aclarar lectura completa, numeración y exclusión
   entre ID y selector; observar si mejora el uso sin imponer consultas rituales.
2. Verificar el contenido recuperable tras revisar un ID, no solo su existencia;
   reproducir el caso H1/E2/E3 de AAPL en un contraste acotado.
3. Contrastar las cifras finales y sus unidades con las ejecuciones, incluyendo
   diferencias adicionales redactadas fuera del procedimiento programado.
4. Revisar cómo distinguir prioridad vigente, antecedentes y pendientes resueltos,
   y cómo evitar consultas reiteradas a un índice conocido como ausente.

No se implementan esas propuestas en esta campaña. Tampoco se extrapolan resultados
a FinMate. El dataset sigue siendo retrospectivo, con disponibilidad histórica
parcialmente estimada y posibles revisiones; un modelo puede conocer acontecimientos
posteriores. La ejecución no es un backtest limpio ni permite atribuir mejoras
financieras causales a la corrección del ciclo.

## Procedencia y disponibilidad

Consolidación documental del 2026-10-31. Carpeta original: `artifacts/contexto-continuo-v5`.
Se contrastaron manifiestos, resultados, eventos y snapshots finales disponibles;
los informes locales y los hallazgos anteriores se leyeron como síntesis, sin
repetir sus replays, comprobaciones exhaustivas o campañas.

| Ejecución original | ID | Total LLM / herramientas | Resultado registrado |
|---|---|---:|---|
| `piloto-100-llamadas/ejecuciones/2026-10-28-piloto` | `640c90fa-d9eb-4e97-85e5-71cea9bd9053` | 11 / 11 | interrupted |
| `repeticion-100-llamadas/ejecuciones/2026-10-28-piloto` | `02bca6eb-c836-484f-a7d4-e83a0b343329` | 106 / 95 | interrupted |

Las capturas completas son locales y pueden archivarse fuera del checkout; no se
conoce aún su destino externo. Las referencias permiten identificar los originales,
pero no garantizan acceso. Los resultados narrativos se entienden sin esas carpetas;
repetir una auditoría de cifras, fuentes o trayectoria requiere recuperarlas. No se
trasladan payloads privados ni expedientes completos a Git.
