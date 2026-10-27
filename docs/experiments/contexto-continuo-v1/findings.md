# Contexto continuo v1 — piloto original y repetición con entrega corregida

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
