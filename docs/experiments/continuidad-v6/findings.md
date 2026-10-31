# V6: campaña de 100 llamadas frente a la repetición V5

Fecha: 2026-10-29. Ejecución real autorizada expresamente por el usuario después de
la implementación. **Alcanzó las 100 llamadas ordinarias, con captura completa. Hubo
menos errores instrumentales, pero no se observó escritura durante investigación ni
menor carga de consolidación. La continuidad del conocimiento sigue siendo parcial.**

El [protocolo](protocol.md) y la rúbrica previa (`campaigns/contexto-continuo-v6/rubrica.md`; referencia local histórica)
delimitan el contraste. Referencia: [repetición V5](../herramientas-estado-v5/findings.md).
La captura nativa (`artifacts/contexto-continuo-v6/piloto-100-llamadas/README.md`; referencia local histórica),
el resumen mecánico (`artifacts/contexto-continuo-v6/piloto-100-llamadas/resumen-observacion.json`; referencia local histórica)
y las comprobaciones posteriores (`artifacts/contexto-continuo-v6/piloto-100-llamadas/comprobaciones-locales.json`; referencia local histórica)
son locales, ignorados por Git y no portables por estar enlazados aquí.

## 1. Condiciones y cierre

Run `50fa8107-c8f1-4e92-aa64-a633485068b1`. Destino nuevo:
`artifacts/contexto-continuo-v6/piloto-100-llamadas`. Lanzador y análisis reproducibles
en `artifacts/contexto-continuo-v6/`; no se cambió el runtime durante la campaña.

Se comprobó igualdad con V5 del escenario salvo ID: 50 empresas, fecha simulada fija
2023-01-01, USD 100.000 ficticios, diez posiciones máximas, dataset SHA-256
`4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`, mandato y
petición idénticos byte a byte. Coinciden perfil completo OpenAI `gpt-6-luna`, medium,
salida máxima 16000, Python/bibliotecas/política, código compartido y límites:
100 llamadas ordinarias, 150 herramientas, 1200 s, umbrales 262144/524288 bytes.
Web desactivada, sin BD remota ni nuevas ingestas. Estado y cartera nuevos.

Cambian conjuntamente código/prompts V6, agenda inicial y observación/rúbrica V6.
Los contratos se mantienen en la familia `v5`, versión efectiva `state-tools-v6.1`.
No se introdujo un supervisor LLM ni se devolvieron observaciones del análisis a A.

| Medida | V5 | V6 |
|---|---:|---:|
| Llamadas ordinarias | 100 | 100 |
| Investigación | 66 | 62 |
| Consolidación | 34 | 38 |
| Revisión adicional | 6 | 6 |
| Total modelo / intentos registrados | 106 / 106 | 106 / 106 |
| Herramientas: éxito / rechazo | 82 / 13 | 87 / 6 |
| Renovaciones | 10 | 12 |
| Escrituras aplicadas | 19 | 13 |
| Escrituras durante investigación | 0 | 0 |
| Duración del agente | 779,157 s | 595,861 s |
| Captura completa / errores | Sí / 0 | Sí / 0 |

El lanzamiento completo duró 600,750 s, unos diez minutos. Cierre:
`interrupted: call_limit`, no cumplimiento del mandato. El registro de campaña
conserva `failed` porque exige `agent_status=completed`; no implica caída ni pérdida
de captura. No se reinterpretó esa etiqueta ni se repitió la campaña para mejorarla.

## 2. Investigación y progresión

A eligió AAPL y ADBE. Recuperó series anuales y mantuvo la distinción entre precios
normalizados y cotizaciones negociables. No fabricó valoración ni cursó órdenes.
Conservó una hipótesis descriptiva de AAPL y dejó ADBE principalmente en la agenda.

El primer cálculo Python, llamada total 76, calculó crecimientos y márgenes de AAPL;
ADBE quedó parcial porque el código buscó `2015-11-27`, mientras el material contiene
`2015-11-30`. Esto no era ausencia del dato en el corpus. Tras recuperar ese periodo,
un cálculo ADBE falló por esperar un envoltorio `value` inexistente (93); la llamada
94 corrigió el acceso y produjo tasas y márgenes. A incorporó el resultado a la agenda.

Al final amplió la exploración a AMZN (102–106), con CFO positivo y FCF negativo como
pregunta material. Solo quedaron materiales originales: el nuevo foco no se incorporó
a agenda o expediente antes del límite. No se afirma que esa línea se recuperase después.

No se desarrolló una explicación suficientemente fundada de mecanismos económicos,
sostenibilidad o atractivo. Los cálculos y sus cautelas son progreso descriptivo;
no bastan para una evaluación de inversión. El menor número de empresas documentadas
no es por sí solo fracaso; aquí tampoco aparece una profundidad económica que lo compense.

## 3. Herramientas, escrituras y recuperación de errores

Las operaciones V5/V6 recibieron 49 intentos, 45 exitosos y cuatro rechazados, frente
a 57/44/13 en V5. No hubo selectores inválidos ni búsquedas fallidas del índice ausente
en esta ejecución; es una observación, no un efecto causal demostrado de los prompts.
No se consultó `describe_state_tools`; sí dos veces el contrato Python.

| Error | Llamada total | Resultado posterior |
|---|---:|---|
| `read_artifact`: referencia no encontrada | 40 | Continúa con orientación y otras lecturas. |
| `edit_state`: versión incorrecta | 46, 48, 49 | Relee/reintenta, pero consume la consolidación; reparación posterior en la 56. |
| `edit_state`: objetivo exacto ausente/ambiguo | 79 | No se aplica; la renovación conserva lo ya escrito. |
| `run_python`: `KeyError: value` | 93 | Corregido con ejecución satisfactoria en 94. |

Los seis errores se entregaron al modelo y todos tuvieron llamadas posteriores.
Continuar no significa resolver inmediatamente la causa. La repetición de conflictos
de versión sigue siendo fricción material.

Hubo **13 escrituras: diez de agenda y tres del modelo AAPL, todas en consolidación**.
Las 17 mutaciones intentadas se reprodujeron deterministamente y el resultado coincide
con el snapshot final; cuatro fueron rechazadas sin cambios parciales. El 38 % de las
llamadas ordinarias se dedicó a consolidación, frente a 34 % en V5.

Quedaron agenda y modelo AAPL, más 18 materiales originales. No hay índice, expediente
ADBE, valoraciones o evaluaciones. H1 es único y su lectura devuelve argumento y cifras,
sin sección vacía. Ninguna escritura activó el rechazo por vaciado/IDs: no se puede
atribuir la ausencia de ese fallo a una protección que aquí no llegó a dispararse.

## 4. Continuidad y coherencia

Las trece ventanas conservan mandato íntegro y agenda. Se guardaron veinte checkpoints:
inicio, seis revisiones, doce renovaciones y cierre; todos completos y con hashes
coherentes. Hay investigación posterior a la duodécima renovación. El
informe offline (`artifacts/contexto-continuo-v6/piloto-100-llamadas/ejecuciones/2026-10-29-piloto/progreso-v6.json`; referencia local histórica)
conserva observaciones mecánicas; sus dimensiones semánticas siguen `not_assessed`.
La valoración de esta sección es posterior y separada de ese informe.

| Rúbrica | Observación y evidencia |
|---|---|
| Mandato | Conservado en todas las ventanas; fecha/cartera y límites se mantienen. |
| Dirección | Foco AAPL–ADBE reconocible, con incertidumbre y acción tentativa; giro a AMZN final sin persistir. Parcial. |
| Fundamentos | H1 recuperado por sección en 44 y por ID en 66, 78, 84 y 88; cálculos y fuentes localizables. No demuestra interpretación económica suficiente. |
| Persistencia | Trece escrituras, ninguna ordinaria: no se observa el comportamiento incremental buscado. |
| Bloqueos | Restricción de precios correctamente mantenida; falsa falta de Python corregida más tarde. Parcial. |
| Coherencia | Agenda actualizada con métricas ADBE, pero H1 aún considera pendiente el cálculo comparativo. Parcial. |
| Repetición | Varias recuperaciones del mismo corpus y cinco consultas al universo; no toda relectura es redundante, pero no se observa avance proporcional. |
| Utilidad | Comparación cuantitativa descriptiva con límites; sin evaluación de sostenibilidad o atractivo. |

Hay tres discontinuidades materiales:

1. **Capacidad confundida con fase.** En la agenda y la respuesta de la llamada 63
   se declara que no hay aritmética/Python. Están deshabilitados durante consolidación,
   pero disponibles en investigación desde el inicio. La agenda corrige explícitamente
   esta afirmación en la consolidación posterior al primer cálculo. No era falta real
   de capacidad ni de autorización.
2. **Pendiente desactualizado.** La agenda final incorpora los cálculos ADBE y declara
   resuelta esa brecha; el modelo AAPL sigue diciendo «cálculo común aún pendiente».
   La actualización no se propagó al documento afectado. No se corrige retrospectivamente.
3. **Entrega textual antigua.** `respuesta.md` corresponde al último texto intermedio,
   generado en la llamada 70, antes de los cálculos de 76/94. Su frase «no se calcularon
   tasas o márgenes» era anterior a esos avances y ya no describe el cierre. No es un
   resumen final nuevo ni prueba de que los cálculos no se ejecutasen. La captura
   completa y los documentos vigentes son necesarios para interpretar el resultado.

La agenda está mejor separada por secciones, pero ocupa 5449 bytes y todavía mezcla
cifras, historia, correcciones y próximos pasos en una sección activa extensa. La
estructura no garantiza depuración. Tras la última renovación no se recuperó el modelo
de ADBE porque nunca se creó; parte de su conocimiento depende de la agenda.

## 5. Fidelidad numérica y referencias

Dos cálculos Python exitosos y uno rechazado. El primero exitoso fue parcial para ADBE;
el segundo corrigió la selección de datos. Sus trabajadores exitosos sumaron 2,360 s,
sin incluir preparación por el modelo ni el intento fallido.

La comprobación independiente con Decimal contrastó 14 salidas derivadas y 15
transcripciones de entrada (12 observaciones distintas; algunas se repiten entre
ejecuciones), controlando empresa, ejercicio, moneda y unidad. Coinciden dentro de
tolerancia relativa/absoluta 1e-12. Se conservaron también las tres observaciones
ADBE existentes que el primer cálculo no seleccionó.

El comprobador V6 se aplicó a ocho porcentajes narrativos escogidos en agenda/H1,
con cita exacta y operandos de los materiales: los ocho coinciden, considerando redondeo
a dos decimales. Es una comprobación limitada, no certificación de toda la prosa,
unidades o inferencias. El
informe con cifras (`artifacts/contexto-continuo-v6/piloto-100-llamadas/ejecuciones/2026-10-29-piloto/progreso-con-cifras.json`; referencia local histórica)
conserva especificación y resultados. Las referencias completas comprobadas existen;
las abreviaturas de citas no se dan por validadas automáticamente.

## 6. Interpretación y límites

**Observación:** se completó el presupuesto, hubo recuperación de errores, menos
rechazos y un H1 recuperable. Las capturas intermedias permiten localizar cuándo se
guardó o corrigió conocimiento. La agenda corrigió una falsa limitación instrumental.

**Interpretación:** esta ejecución no respalda todavía la mejora conjunta buscada.
Persisten escritura concentrada en consolidación, reconstrucción repetida, pendientes
obsoletos y progreso económico limitado. La consolidación y las renovaciones aumentaron,
aunque bajó el tiempo observado. Menor duración no demuestra mayor eficiencia intelectual.

**Hipótesis posterior, sin implementación aquí:** examinar cómo el agente diferencia
capacidades de investigación/consolidación, cómo mantiene pendientes entre agenda y
expediente, y cómo se presenta al cierre una última respuesta intermedia desactualizada.
No se añadió un controlador ni se cambió el runtime durante o después de la campaña.

Once muestras externas observaron hasta 390447104 bytes RSS agregados y 343805952
bytes privados del lanzador y descendientes. No son pico real ni memoria aislada de A;
RSS puede duplicar páginas compartidas. Tokens reportados: 2309127 de entrada y 37842
de salida; razonamiento 19325 es parte del desglose, no una cantidad adicional a sumar.

Una ejecución por versión, con elecciones autónomas diferentes, no establece causalidad
ni superioridad estadística. El dataset es retrospectivo, su disponibilidad histórica
parcialmente estimada y el modelo puede conocer el futuro. No es un backtest limpio ni
evidencia de rendimiento de inversión. Se conservan todos los errores y artefactos.

## Procedencia y disponibilidad

Consolidación documental del 2026-10-31. Carpeta original: `artifacts/contexto-continuo-v6`.
Se contrastaron manifiestos, resultados, eventos y snapshots finales disponibles;
los informes locales y los hallazgos anteriores se leyeron como síntesis, sin
repetir sus replays, comprobaciones exhaustivas o campañas.

| Ejecución original | ID | Total LLM / herramientas | Resultado registrado |
|---|---|---:|---|
| `piloto-100-llamadas/ejecuciones/2026-10-29-piloto` | `50fa8107-c8f1-4e92-aa64-a633485068b1` | 106 / 93 | interrupted |

Las capturas completas son locales y pueden archivarse fuera del checkout; no se
conoce aún su destino externo. Las referencias permiten identificar los originales,
pero no garantizan acceso. Los resultados narrativos se entienden sin esas carpetas;
repetir una auditoría de cifras, fuentes o trayectoria requiere recuperarlas. No se
trasladan payloads privados ni expedientes completos a Git.
