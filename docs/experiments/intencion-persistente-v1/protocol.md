# Intención persistente v1

Estado: condición inicial de 18 llamadas preparada sin ejecutar; **ampliación real
completada en ambas condiciones**, con [hallazgos preliminares](findings-amplio.md). Encargo
aceptado el 2026-10-24. La [decisión experimental](../../decisions/0003-intencion-persistente.md)
registra la elección; no acredita una mejora semántica.

## Ampliación de presupuesto autorizada — 2026-10-24

Después de preparar la condición de 18 llamadas, el usuario autorizó ejecutar ambas
condiciones con más recursos. El [escenario ampliado](../../../benchmarks/intencion-persistente-v1/scenario-amplio.yaml)
conserva universo, mensajes, fechas, datos y restricciones; cambia solo ID y límites:
60 llamadas al modelo, 90 herramientas, 1200 segundos, reserva temporal de 90 segundos
y contexto serializado de 1048576 bytes por activación. El perfil permanece OpenAI
`gpt-6-luna`, `medium`, salida máxima 16000. Hasta 360 llamadas por condición.

Esta ampliación es una condición nueva, no un resultado del piloto de 18 llamadas.
El escenario original y sus comandos se conservan debajo. No hay compactación del
contexto ni garantía de consumir todo el presupuesto; también aplican límites del proveedor.
La reserva sigue siendo dos llamadas de consolidación y una de respuesta.

Ejecución autorizada con estos comandos, cada destino nuevo y estado independiente:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal run benchmarks/intencion-persistente-v1/scenario-amplio.yaml --condition baseline --data artifacts/price-review-adjusted-v3/data.json --output artifacts/intencion-amplia-baseline-v1
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal run benchmarks/intencion-persistente-v1/scenario-amplio.yaml --condition deliberative --data artifacts/price-review-adjusted-v3/data.json --output artifacts/intencion-amplia-deliberative-v1
```

La ejecución completó seis activaciones por condición, en doce intentos, sin reintentos.
Los [hallazgos](findings-amplio.md) conservan consumos, continuidad comprobada y límites
de interpretación; no atribuyen calidad financiera al cierre operativo.

## Pregunta y condiciones

¿Conservar el mandato auténtico y cargar una agenda compacta ayuda a retomar
investigaciones, resolver incertidumbres y revisar prioridades entre procesos?
Se contrasta el paquete mandato + agenda + instrucciones; no sus contribuciones aisladas.

El [escenario](../../../benchmarks/intencion-persistente-v1/scenario.yaml) conserva
las 50 identidades, 100.000 USD, máximo de diez posiciones, disponibilidad anual
estimada de 120 días y restricciones del escenario histórico revisado. Se acorta a
enero–junio de 2023: seis activaciones mensuales; mensajes auténticos en enero y abril,
cuatro activaciones temporales. No se añaden estímulos ni se programa qué investigar.

| Condición | Contexto inicial | Instrucciones |
|---|---|---|
| baseline | Índice y mensaje de activación | Generales y financieras vigentes |
| deliberative | Lo anterior, mandato auténtico y agenda | Lo anterior y deliberacion.md |

Cada campaña empieza con su propio estado nuevo. Solo la condición deliberativa tiene
agenda inicial vacía. No copiar memoria ni cartera de la campaña anterior. Las
condiciones se ejecutan con el mismo código, datos, perfil, herramientas, calendario,
mensajes y límites; después su memoria puede divergir por las acciones elegidas.

Referencia de perfil: OpenAI `gpt-6-luna`, razonamiento `medium`, `max_output_tokens=16000`.
Por activación: 18 llamadas al modelo, 30 herramientas, 300 segundos, reserva final
de 45 segundos y contexto serializado de 262144 bytes. Hasta 108 llamadas por condición;
informar también del consumo real. No aumentar salida o reservas entre condiciones.

## Contexto, autoridad y recuperación

`mandato.md`, fuera de `estado/`, contiene mensajes auténticos en orden cronológico
hasta la fecha de activación incluida. No resume ni incorpora respuestas del agente.
Solo modificaciones explícitas sustituyen restricciones previas. La agenda es memoria
revisable del agente, no autorización. Las herramientas no escriben fuera del estado.

Mandato: texto no vacío de hasta 16 KiB UTF-8; agenda: hasta 8 KiB, vacía permitida.
Faltas, texto inválido o exceso se rechazan antes de llamar al modelo, sin truncar ni
resumir. El manifiesto conserva condición y texto/hash del contexto inicial; la
conversación y las capturas del proveedor muestran su entrega. Se preservan el índice
automático y la recuperación selectiva existentes.

El controlador congela `condition.json` y su hash junto a las entradas. `resume` no
admite cambiar condición. Las campañas antiguas sin ese archivo siguen siendo baseline,
sujetas a las comprobaciones previas de identidad. El mandato se reconstruye desde
el escenario congelado antes de cada nuevo intento; no se acumulan copias de mensajes.
Al reconocer una ejecución completada se contrasta el mandato esperado y la agenda del
checkpoint con su manifiesto antes de confirmar el cursor.

Hay dos oportunidades de consolidación y una respuesta final, sin escritura obligatoria.
Guardar durante la investigación reduce dependencia del cierre; una caída no recupera
intenciones nunca escritas. No hay transacción multiarchivo ni nueva política de reintentos.

## Preparación y ejecución manual posterior

Desde la raíz Git, comprobar sin red el escenario y el perfil configurado:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal validate benchmarks/intencion-persistente-v1/scenario.yaml
.\.venv\Scripts\python.exe -c "from research_benchmarks.longitudinal import runtime_identity; p=runtime_identity()['profile']; expected={'provider':'openai','model':'gpt-6-luna','reasoning_effort':'medium','max_output_tokens':16000}; print({k:p.get(k) for k in expected}); assert all(p.get(k)==v for k,v in expected.items()), 'Perfil distinto: corregir antes de ejecutar ambas condiciones'"
Get-FileHash -Algorithm SHA256 -LiteralPath artifacts/price-review-adjusted-v3/data.json
```

Dataset común previamente revisado: `artifacts/price-review-adjusted-v3/data.json`,
SHA-256 `2b65121feae3ae0f2784584f53af6649856d988997eda6eb402f0a71f2b58745`.
La [revisión de precios](../colaboracion-historica-v1/price-review.md) conserva las
convenciones y la excepción AVB. No editarlo, regenerarlo ni sustituirlo silenciosamente.
Si falta, recuperar el archivo original; no usar una descarga nueva como si fuese idéntica.

Los comandos siguientes **llaman a proveedores** y quedan para ejecución posterior:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal run benchmarks/intencion-persistente-v1/scenario.yaml --condition baseline --data artifacts/price-review-adjusted-v3/data.json --output artifacts/intencion-persistente-baseline-v1
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal run benchmarks/intencion-persistente-v1/scenario.yaml --condition deliberative --data artifacts/price-review-adjusted-v3/data.json --output artifacts/intencion-persistente-deliberative-v1
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal resume artifacts/intencion-persistente-deliberative-v1
```

Ambos destinos deben ser nuevos. `--data` evita una nueva exportación remota de Findata;
el controlador comprueba cobertura local antes de activar A. No utilizar el subcomando
`preflight` para esta comprobación: ese comando exporta Findata. La web permanece viva.
Tras iniciar una campaña, no cambiar código, perfil, instrucciones, límites ni dataset
para recuperarla. Conservar todos los intentos y errores. No ejecutar estos comandos
como parte de una edición documental o de los checks locales.

## Rúbrica y evidencia

Revisar cada condición y después compararlas. Para cada conclusión reconstruir
**intención previa → contexto disponible → acción → evidencia → cambio persistido**
mediante manifiesto, entradas reales al modelo, herramientas y snapshots. Un texto
coherente o un archivo leído no demuestra por sí solo que la evidencia se haya utilizado.

| Dimensión | Pregunta de revisión |
|---|---|
| Intención | ¿Retoma preguntas anteriores sin un recordatorio específico? |
| Progreso | ¿Resuelve o acota incertidumbres frente a copiarlas? |
| Prioridades | ¿Mantiene o cambia prioridades con motivos pertinentes? |
| Amplitud | ¿Explora alternativas materiales y explica su selección? |
| Eficiencia | ¿Qué recursos dedica a análisis, recuperación y mantenimiento? |
| Trazabilidad | ¿Los cambios tienen evidencia y referencias recuperables? |

Informar casos favorables, contrarios y no observables; bloqueos resueltos y persistentes;
trabajo planeado, intentado, completado y detenido por presupuesto. Comparar llamadas,
herramientas, tiempos y tokens observados; coste monetario desconocido queda desconocido.
No imponer una puntuación agregada ni premiar escrituras, empresas, notificaciones,
cambios de opinión u operaciones. No operar puede ser correcto. El silencio no prueba
que todas las preguntas estén resueltas.

El piloto con una trayectoria por condición es exploratorio. Web viva, entrenamiento
del modelo, revisiones de datos, supervivencia y disponibilidad estimada limitan el
aislamiento; filtrar published_at no garantiza contenido históricamente válido.
No afirmar causalidad aislada, calidad inversora, alfa ni mejora estable. La aceptación
técnica y la revisión semántica se informan por separado. No hay hallazgos del piloto
hasta ejecutarlo. La condición de 18 llamadas sigue sin ejecutarse; la ampliación tiene
su [registro de hallazgos](findings-amplio.md). Los tests controlados solo acreditan contratos técnicos.
