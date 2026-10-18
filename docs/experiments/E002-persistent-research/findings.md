# E002 — Expediente conservado y recuperación tras reinicio

Estado: concluido con persistencia y continuidad observadas, aceptación semántica parcial.
Fecha: 2026-10-17. Diseño previo: [protocolo](protocol.md).

## Resultado principal

Las dos intervenciones entregaron respuesta y publicaron una revisión del mismo
expediente. La primera guardó una interpretación provisional en su quinta acción;
la segunda recuperó esa revisión al empezar y la actualizó con información documental.
Hay dos revisiones íntegras y recuperables, con productores distintos y antecedentes.

La conservación no fue completa: ambas investigaciones obtuvieron información después
de guardar que no llegó a incorporarse al expediente. Las dos consolidaciones agotaron
un límite temporal aplicado incorrectamente por la implementación ejecutada. El
fallo se corrigió después de terminar ambas intervenciones y se verificó localmente;
no se ha repetido el experimento ni se presenta esa corrección como validada en vivo.

## Base, configuración y evidencias

- Base Git: `5ae4e5d4651eff2dd8c17f6d8f2bc88c7570c815`, con el candidato E002 local sin commit.
- Corte fijado el 2026-10-17 a las 17:54:55 UTC en
  `artifacts/E002-persistent-research/attempt-01/environment.json` y `frozen_source/`.
  `sequence-code-verified.json` comprueba que los 26 archivos congelados permanecieron
  iguales durante los dos procesos. La corrección posterior se identifica aparte.
- SHA-256 del protocolo previo: `dc1b1c3c792373d92e934f6a6125c991e4944cbd9557af73a44f1d433ff79b14`.
- Wheel Findata sin modificaciones ni reinstalación:
  `70cd4a370e1ca4690631f104291a7cc3281acbf6972e43b3c14cb18fe7662e4f`.
- Perfil comprobado: OpenAI, `gpt-6-luna`, razonamiento `medium`, salida máxima 4000.
  Mismos límites globales de E001: 18 llamadas, 30 herramientas, 300 segundos, 256 KiB.
- Preflight satisfactorio para claves y lectura PostgreSQL. No hubo ingestas,
  migraciones ni escrituras financieras. Las condiciones externas no están congeladas.
- Evidencia local completa en `artifacts/E002-persistent-research/attempt-01/`:
  `runs/`, `cases/`, `workspace/`, procesos, configuración, código congelado,
  `mechanical-review.json`, `state-review.json` y `post-run-correction.json`.
  Está ignorada por Git y no es evidencia portable; los IDs y hashes permiten localizarla
  mientras se conserve el archivo local. No se exportan credenciales ni payloads privados.

## Ejecuciones

Mensajes exactos y procesos nuevos según el protocolo, sin añadir resúmenes manuales.

| Intervención | Run ID | Estado / cierre | Llamadas / herramientas | Duración | Persistencia |
|---|---|---|---|---|---|
| Investiga NVIDIA | `b62a5327-02a0-4041-8166-3131f6eba317` | `completed / budget` | 18 / 16 | 88,66 s | `confirmed`, respuesta entregada |
| Continuación tras reinicio | `8ed34d00-8e77-4db5-9f89-923e18a8adff` | `completed / budget` | 17 / 15 | 123,52 s | `confirmed`, respuesta entregada |

Las 31 llamadas a herramientas conservaron 29 artefactos distintos. Todos los hashes
de artefactos comprobados coinciden. Hay un rechazo de `save_case`, explicado abajo.
No hubo `LLMTruncated` en estas entregas; las respuestas fueron breves. No se infiere
que el problema de truncamiento esté resuelto para otras tareas.

### Primera intervención

1. Lista expedientes, identifica la empresa, consulta ficha y observaciones financieras.
2. En la quinta acción publica una primera revisión: negocio, cifras del proveedor,
   cautelas, referencias y preguntas pendientes. Es provisional y no pretende valorar la acción.
3. Continúa con búsqueda web, tres extracciones y seis cálculos. Obtiene evidencia del
   informe anual sobre concentración en Data Center y restricciones de exportación.
4. Tras 15 llamadas de investigación entra en consolidación. Lee el expediente y la
   siguiente llamada al modelo agota el plazo de fase. Pasa a respuesta sin publicación adicional.
5. Entrega una respuesta que identifica exactamente la revisión guardada y reconoce
   que los hallazgos documentales posteriores aún no se han incorporado.

Distribución de llamadas: 15 investigación, 2 consolidación (una sin respuesta por
timeout de fase), 1 respuesta. La primera evaluación sobrevive aunque la actualización falle.

### Continuación

1. Lista y lee el expediente antes de buscar fuentes. Recupera la evaluación y sus pendientes;
   no recorre carpetas vacías ni necesita volver a obtener todas las observaciones anteriores.
2. Busca y extrae el informe trimestral SEC para el periodo terminado el 26-jul-2026.
   Calcula el peso trimestral de Data Center y el margen operativo.
3. Un primer guardado se rechaza porque una referencia carece de `.json`. La siguiente
   acción corrige el listado de referencias y publica una revisión del mismo expediente,
   conservando la revisión inicial como antecedente.
4. Sigue investigando concentración, suministro, caja y perspectivas. Vuelve a leer su
   revisión y entra en consolidación al alcanzar 15 llamadas de investigación.
5. La llamada de consolidación agota el plazo. La respuesta final distingue lo guardado
   de los hallazgos adicionales que todavía requieren una nueva revisión.

Distribución: 15 llamadas de investigación, 1 de consolidación fallida y 1 de respuesta.
No se reintentó la intervención ni se usó la llamada global sobrante para ampliar la fase.

## Estado persistente comprobado

Expediente: `35d1d4eb-a776-4172-9a2e-879a4f5e2b48`, activo `NVDA`.

| Revisión | Productor | Contenido | SHA-256 del Markdown |
|---|---|---|---|
| `45dbc6d7-a814-4f0d-a6c2-905273c22b1f` | Primera intervención | 4.645 bytes; cuatro referencias | `f8b38b2939ff23ed96e80e941dfb0fa089310ca0a279ce0a4e2833d7ac0dab40` |
| `545b97d6-0dc2-4016-87a6-537931ec1c80` | Continuación | 7.044 bytes; siete referencias | `d9c9e649c3b5b9089c17bc45920b1c009a64f4dfc1c7ee676fa810dd427979f2` |

La segunda apunta a la primera y es la vigente. Se verificaron contenido, historia,
productor y resolución de referencias declaradas en cada revisión. Los snapshots
inicial/final muestran vacío → primera revisión → segunda revisión. No hay restos
no publicados. La memoria auxiliar del workspace no fue necesaria para esta continuidad.

La confirmación técnica comprueba las referencias de la revisión, no recursivamente
toda la semántica o las referencias internas de cada cálculo. Tampoco acredita que
se haya incorporado toda la evidencia obtenida después del último guardado.

## Desviación temporal y corrección posterior

El protocolo permite dedicar como máximo 15 segundos a consolidar cuando se entra en
la ventana final de 45, reservando 30 para respuesta. El código ejecutado aplicó un
tope fijo de 15 segundos incluso cuando la transición se debía al límite de llamadas
y quedaban varios minutos. En la primera consolidación quedaban aproximadamente
230 segundos globales: una lectura consumió parte de los 15 y la llamada siguiente
se interrumpió. La segunda consolidación también terminó por timeout del modelo.

Esta aplicación anticipada del tope fue un error de implementación, no una decisión
del modelo de rechazar el guardado. Las oportunidades de escritura existían, pero el
plazo las limitó innecesariamente. No se puede asegurar que con más tiempo hubiera
publicado una actualización correcta; eso permanece sin observar.

**Después de ambos procesos**, se sustituyó ese plazo por `deadline - reserva_respuesta`.
Si quedan 45 segundos permite hasta 15 de consolidación; si se entra antes por llamadas
o contexto, permite utilizar el tiempo disponible manteniendo 30 para responder.
No cambia los presupuestos globales ni las dos llamadas máximas de consolidación.
Se añadió un test específico con reloj controlado. El código final pasa 50 pruebas,
mypy y dependencias; el candidato ejecutado había pasado 49 pruebas.

`post-run-correction.json` identifica los únicos archivos congelados que cambiaron
después: `agent.py` y el test añadido. No se modificó el protocolo, las capturas o
resultados anteriores. **La corrección final tiene verificación local y no prueba real**;
se respetó la única secuencia autorizada, sin repetir para obtener un resultado favorable.

## Evaluación interna y límites

Evaluación del mismo agente desarrollador, no revisión independiente.

| Nivel | Resultado | Base y límites |
|---|---|---|
| Técnico | Observado | Dos revisiones íntegras, confirmadas desde disco, con productores distintos; dos respuestas entregadas. |
| Continuidad | Observado, alcance acotado | La continuación lee la primera revisión, recupera su conclusión provisional y pendientes y actualiza el mismo expediente. No prueba continuidad de todos los hallazgos no guardados. |
| Semántico | Parcial | Las revisiones distinguen observaciones, interpretación, precio y decisión; conservan fuentes y límites. Queda información posterior fuera del expediente. |
| Revisión ante contradicción | N/O | No se introdujo una contradicción controlada ni se evaluó exhaustivamente la actualización de dependencias. |

Muestra comprobada en el extracto SEC `3f36ef...5301e.json`: ingresos trimestrales
96.221, Data Center 89.023 y resultado operativo 63.734, todos en millones de USD.
Las divisiones ejecutadas producen aproximadamente 92,5 % y 66,2 %, coherentes con la
segunda revisión. El material está marcado como extracción parcial, no revisión integral
del filing. No se certifican todas las cifras, mecanismos económicos o inferencias.

Limitaciones de procedencia observadas: los dos cálculos conservan `source_refs` sin
la extensión `.json`; el modelo corrigió esa referencia en el listado del expediente
tras el rechazo, pero no reescribió los artefactos de cálculo. La cifra aritmética es
reproducible; la referencia anidada requiere normalización manual para recuperar su fuente.
La revisión también menciona un cociente comparativo aproximado no ejecutado mientras
afirma omitirlo. Son límites de disciplina numérica, no errores del versionado.

La primera revisión usa periodos normalizados del proveedor y advierte límites de fecha;
no se ha auditado su correspondencia exhaustiva con fechas fiscales de filings. La
segunda añade evidencia más reciente y conserva antecedentes. No realiza DCF ni
concluye atractivo bursátil o recomendación personal.

Comparado descriptivamente con E001, hay conservación y recuperación donde antes no
había revisiones. Cambiaron juntos prompt y cierre, y las fuentes remotas pudieron
variar: no se atribuye el avance a un componente individual. El coste monetario no se
calculó; llamadas, tiempos y capturas sí son observables.

## Siguiente cuestión

El siguiente contraste debería comprobar la consolidación con el plazo corregido y
la incorporación de evidencia posterior al primer guardado, manteniendo revisión
semántica y captura de errores de referencias. No hace falta añadir entidades para
explicar el fallo observado. No se ejecutó ese contraste adicional ni se adopta una
arquitectura definitiva a partir de estas dos intervenciones.
