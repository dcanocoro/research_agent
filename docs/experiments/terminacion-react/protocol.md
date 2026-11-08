# Terminación inteligente del ReAct acotado

Fecha: 2026-11-08. Estado: montaje preparado; sin campaña ni resultados semánticos.

Actualización posterior: [piloto y lanzamiento paralelo](execution-2026-11-08.md).
Tanda finalizada: [resultados y límites de la revisión](findings.md).
La autorización del usuario cambia la ejecución a tres procesos, uno por condición;
el resto del diseño y la preparación original se conservan.
Encargo: comparar suficiencia por instrucciones y checkpoint externo en tareas
acotadas, manteniendo el experimento fuera del paquete del agente.

## Pregunta y condiciones

¿Reduce el autocontrol el trabajo prescindible sin empeorar la resolución? ¿Añade el
checkpoint una mejora que compense sus llamadas y latencia? V0 es A acotado actual,
V1 añade solo instrucciones de suficiencia y V2 añade a V1 un evaluador aislado.
V0 no es el baseline histórico del 18 de octubre ni una variante de FinMate.

Los tres reutilizan `BoundedPolicy` y el motor único. La subclase experimental
`TerminationPolicy` vive en `research_campaigns`, consumidor de A. No hay selector
nuevo, import inverso, modificación de AgentA ni cambio de instrucciones estándar.
La estructura nueva permite ejecutar y retirar el checkpoint sin contaminar otras
campañas; los runners existentes no proporcionan este contraste sobre la política
acotada. Se reutilizan herramientas, transporte, límites, captura y persistencia.

Sin continuo, Progress, objetivo generado, nota, revisión general, mandato ni B.
Todos usan mismo perfil principal y evaluador (clientes con conversación separada),
archivos y aritmética locales. El cliente del checkpoint usa un alias de perfil
distinto para evitar la caché de clientes de Infra; conserva proveedor, modelo y
ajustes del principal, con salida limitada a1500 tokens. La guía financiera actual permanece común. Corpus
sintético congelado, fuentes ficticias, corte 2026-10-31, sin datos remotos.
Esta primera tanda controla el acceso a evidencia; validar después con herramientas
reales requerirá otro protocolo y no está implícito en preparar este montaje.

La captura se adapta localmente a los contratos histórico y actual de Infra,
sin parchear módulos globales ni modificar A. La preparación del contexto inicial
reproduce el acotado sin mandato; las tres condiciones usan esta misma preparación.
La equivalencia de ejecución V0 se comprueba con el mismo adaptador de captura.

## Presupuestos y cierre

18 llamadas máximas de A, 30 herramientas, 600 segundos de tiempo total y reserva
temporal de cierre de 45 segundos. El timeout mayor que el predeterminado es común
y explícito: busca reducir confusión entre latencia y suficiencia. Se conserva la
política acotada: hasta15 llamadas de investigación, hasta2 de consolidación y1
de respuesta; puede responder voluntariamente antes. Límites de contexto y tiempo
pueden adelantar el cierre. No se suprime consolidación ni se obliga a guardar.

En V2 se revisa tras6 y12 llamadas de A solo si sigue investigando, después de una
respuesta de herramienta completa y antes de la siguiente llamada de A. Un cierre
voluntario anterior no provoca revisión. El evaluador recibe petición y conversación
visible completa, sin truncado añadido, sin rúbrica ni conocimiento futuro. No ve
razonamiento interno oculto ni documentos que A no haya recuperado. No tiene herramientas.
No inspecciona automáticamente el workspace. El input exacto queda archivado.

Devuelve CONTINUE o REQUEST_FINISH con razón breve. REQUEST_FINISH cambia a respuesta
sin herramientas, sin nueva consolidación, y usa una llamada de A aún disponible.
La razón no se inyecta como evidencia. Se conserva esta diferencia deliberada con
el cierre ordinario para medir también sus posibles pérdidas de persistencia.
No equivale a aprobación del resultado ni orden humana. Si la respuesta falla o es
inválida, continuar sin reintento. La cancelación se propaga y conserva su causa.
Cada evaluación tiene hasta30 segundos y no invade los45 segundos protegidos;
si no cabe, se omite con motivo. A y checkpoints comparten el deadline global.

V2 añade hasta2 intentos LLM al techo de A: máximo20 llamadas gestionadas; las
llamadas internas/reintentos del transporte se revisan en trazas y no se presentan
como si fueran cero coste. Se registran intentos fallidos, fases, roles y tiempo.
El coste total de V2 incluye el evaluador; tokens/dinero ausentes son desconocidos.

## Casos, repetición y piloto

La [definición](../../../campaigns/terminacion/README.md) contiene12 casos y rúbricas
previas: cuatro simples (extracción, crecimiento, ausencia de precio, corrección),
cuatro intermedios (márgenes, caja no recurrente, periodos/perímetros, liquidez),
cuatro de alcance amplio acotado (calidad del crecimiento, concentración, valoración
insuficiente y recuperación corregida). No hay mandato abierto indefinido.

Cada trabajo comienza con workspace independiente: índice idéntico entre condiciones
y corpus del caso en `materiales/corpus.md`, protegido por la regla existente de
materiales de solo lectura. Las rúbricas se quedan fuera del workspace y del prompt.
No hay contaminación por memoria entre condiciones o repeticiones.

El plan predeterminado es12×3×3=108 trabajos, orden por bloques de caso/repetición
con semilla1729 y orden de condiciones aleatorio; la semilla controla el orden, no
la aleatoriedad del proveedor. Sin paralelismo ni reintentos automáticos. Conservar
todos los intentos y errores. No atribuir diferencias causales a una única respuesta.

Antes de la tanda: piloto independiente de S2 y O4 con una repetición por condición,
para comprobar cierre, captura y si se alcanzan los checkpoints. Los casos sencillos
pueden acabar antes de6; eso es un resultado válido. Si ningún caso amplio alcanza
un checkpoint, registrar falta de exposición: no concluir que V2 carece de valor.
Revisar dificultad o cobertura en una versión nueva antes de la tanda, sin obligar
al agente a consumir llamadas para activar el mecanismo. No incorporar el piloto
a las estimaciones de una tanda redefinida.

## Evaluación y criterio de avance

La [rúbrica general](../../../campaigns/terminacion/rubric.md) fija revisión ciega de
respuestas y revisión de trayectoria por prefijos, por separado del controlador V2.
El montaje prepara paquetes; no ejecuta el juez independiente. Conservar scores,
razones y discrepancias, adjudicando cierres dudosos mediante revisión humana.

Medir suficiencia, errores materiales, terminación prematura, justificación/limitaciones,
primer punto o intervalo suficiente, acciones posteriores clasificadas y recursos.
No contar persistencia útil como desperdicio por definición. No usar hallazgos futuros
para juzgar la suficiencia de un prefijo. Calidad y cierre prematuro tienen prioridad.

Comparar V1 conV0 yV2 conV1 por caso/repetición y por grupo, mostrando dispersión y
regresiones. No recomendar adopción con regresiones materiales sin revisar y repetir.
Preferir el mecanismo más simple si la complejidad no aporta ganancia observable.
La muestra es exploratoria; no prueba significación estadística, calidad financiera
en producción ni rentabilidad. El checkpoint y los jueces pueden equivocarse.

## Operación, recuperación y retirada

Los comandos de validar, preparar, lanzar y regenerar informe están en la definición.
Solo `run` construye clientes LLM. La preparación congela entradas y fingerprints de
código/wheel; el primer lanzamiento fija el perfil efectivo. Cada run conserva prompts,
schemas, capturas y configuración efectiva. Cambios incompatibles exigen nueva campaña.
Una continuación del runner ejecuta trabajos no intentados, sin restaurar chats ni
repetir fallos. Los directorios parciales permanecen para auditoría.

Para retirar el experimento, eliminar su paquete `research_campaigns/termination`,
definición `campaigns/terminacion`, prueba dedicada y referencias afectadas, conservando
protocolo/hallazgos si ya hay evidencia. No hay cambios de A que revertir. Las capturas
en `artifacts/` son locales e ignoradas; no sustituyen futuros hallazgos portables.
