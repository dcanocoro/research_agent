# E002 — Conservación durante la investigación y recuperación tras reinicio

Estado del protocolo: fijado antes de ejecutar. Fecha: 2026-10-17.
Los resultados y desviaciones se registrarán en `findings.md` después de ejecutar.

## Pregunta, intervención y límites de inferencia

¿Conserva A una evaluación provisional útil y la recupera un proceso nuevo cuando
dispone de presupuesto visible, instrucciones de persistencia y un cierre con escritura?
Se introduce conjuntamente el prompt revisado y la política de consolidación del
[modo cases](../../architecture.md#conservación-y-cierre-de-la-investigación).
El contraste con [E001](../E001-nvidia-casefile/findings.md) será descriptivo:
no aísla el efecto individual de las instrucciones, información de presupuesto o reserva.
Fuentes y proveedores son reales, no congelados entre experimentos.

## Secuencia y condiciones fijadas

Un único intento con directorios inicialmente nuevos. Dos procesos CLI separados,
mismo workspace, almacén y archivo, sin resumen, ID o material añadido manualmente:

1. Mensaje exacto: `Investiga NVIDIA`.
2. Mensaje exacto: `Continúa la investigación de NVIDIA a partir de lo que conservaste. Explica qué evaluación recuperas, qué sigue pendiente y decide cómo continuar.`

Modo `cases`, prompts instalados general, financiero y de expediente. Sin instrucciones
adicionales. Mantener el perfil configurado del planificador como `lab`; comprobar
modelo efectivo y máximo de salida 4000 antes de ejecutar. No modificar configuración
para mejorar los resultados. Si el entorno difiere del corte anterior, declararlo.

Presupuesto por intervención: 18 llamadas al modelo, 30 herramientas, 300 segundos y
256 KiB de contexto. Hasta 15 llamadas de investigación, 2 de consolidación y una
reservada para respuesta. La consolidación se adelanta por tiempo, herramientas o
contexto. En la ventana final de 45 segundos puede usar hasta 15 segundos, conservando
30 para respuesta; puede disponer de menos si se llega tarde. Reservar 32 KiB de contexto
con los límites actuales. No hay ampliaciones, recortes silenciosos ni intentos ilimitados.

Durante consolidación solo se ofrecen y ejecutan `list_cases`, `read_case`,
`list_case_revisions`, `read_artifact` y `save_case`. Un texto temprano sin publicación
se conserva como borrador y ofrece consolidación, sin transformarlo automáticamente
en conocimiento. Un guardado confirmado permite pasar a respuesta. Esta debe ser breve,
con objetivo de hasta 400 palabras; no se modifica el máximo de salida del proveedor.

Preflight: claves configuradas y una lectura PostgreSQL en transacción de solo lectura.
No ingestas, migraciones ni escrituras financieras. La presencia de claves no prueba
disponibilidad; los errores posteriores también son evidencia. No repetir intervenciones
ni cambiar presupuestos tras un fallo. E001 y sus capturas permanecen intactos.

## Evidencias y reproducibilidad

Conservar en `artifacts/E002-persistent-research/attempt-01/` los procesos, workspace,
almacén, runs, borradores, respuestas, fuentes, errores y capturas. Antes de ejecutar,
copiar y hashear código, prompts, tests y protocolo; registrar revisión Git, diff,
dependencias instaladas, bibliotecas del wheel y hash del wheel original si se localiza.
Los manifiestos de run registran configuración efectiva, schemas y política de cierre.

Los eventos `lab.budget` y `lab.phase.*` permiten observar recursos y transiciones.
`result.json.persistence` se obtiene leyendo revisiones publicadas del almacén con el
run productor, verificando Markdown y referencias. Diferenciar `confirmed`, `unconfirmed`
y `verification_failed`; registrar aparte `response_delivered`. Un evento de intento
o una afirmación del modelo no acreditan persistencia. Conservar snapshots de estado
antes/después y no promover revisiones huérfanas.

Las capturas completas permanecen locales e ignoradas; no son evidencia portable.
Publicar IDs, hashes y resumen sin credenciales. La revisión semántica será interna,
realizada por el mismo agente desarrollador, sin presentarla como independiente.

## Criterios previos de aceptación

| Nivel | Comprobación |
|---|---|
| Técnico | La primera intervención publica una revisión íntegra y recuperable; no basta con respuesta o trazas. Comprobar también el resultado de persistencia de la segunda. |
| Continuidad | El segundo proceso consulta el expediente, recupera evaluación, fundamentos y pendientes, y trabaja sobre ellos sin fingir memoria ni reconstruir todo por ausencia de estado. |
| Semántico | Lo conservado representa de forma útil lo investigado: hechos, supuestos, inferencias, referencias, incertidumbres y cambios. Revisar una muestra explícita de cifras y fuentes. |

Usar `observado`, `parcial`, `fallo` o `N/O`, con base y límites. Un archivo vacío o un
texto de relleno no satisface aceptación semántica. Guardar no prueba calidad financiera;
mantener o cambiar la evaluación no es por sí solo éxito. No exigir compra, venta o DCF.
Un fallo de entrega puede coexistir con persistencia confirmada. El coste monetario
permanece desconocido si no hay base para calcularlo.

Examinar cuándo guarda, qué incorpora y si quedan acciones de investigación posteriores
sin consolidar; una escritura no garantiza actualización completa. Si la segunda
investigación no necesita cambiar la conclusión, evaluar la justificación y qué evidencia
nueva quedó conservada. No añadir entidades como consecuencia automática del resultado.
