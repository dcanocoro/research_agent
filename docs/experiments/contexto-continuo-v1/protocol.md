# Contexto continuo v1

Estado: protocolo preparado; campaña con proveedor sin ejecutar.
Fecha: 2026-10-26. Encargo: implementación y verificación local autorizadas.

## Pregunta e hipótesis

¿Puede el mismo A conservar el mandato y avanzar a través de varias reconstrucciones
de contexto utilizando sus archivos? Hipótesis a contrastar: índice y agenda, recuperados
con mandato y petición inicial, permiten retomar fundamentos e intenciones sin una cola
de conversación ni un resumen adicional. La hipótesis no se considera demostrada por tests.

## Condición implementada

Un solo A en modo continuo; texto intermedio no finaliza el encargo. Ventana estimada
de 32.000 tokens, umbral de 24.000 y salida reservada según perfil, con margen del 10 %
sobre entrada. Hasta cuatro llamadas de consolidación, descontadas del presupuesto total.
Memoria de archivos existente; índice y agenda automáticos, recuperación adicional selectiva.
La [arquitectura](../../architecture.md#modo-continuo-experimental--2026-10-26) posee el contrato
y [desarrollo](../../development.md#ejecutar-el-modo-continuo-experimental) los comandos.

El contador es local y estimado; no acredita el número exacto de tokens del proveedor.
Modelos sin mapping se rechazan sin fallback. La configuración local `gpt-6-luna` no
está reconocida por tiktoken 0.14.0; una campaña requerirá resolver explícitamente esa
compatibilidad antes de elegir o ejecutar un modelo, sin sustituirlo silenciosamente.

La fecha histórica permanece fija. Para el futuro contraste histórico, partir de un
simulador congelado, sin avances durante la ejecución. Comprar registra órdenes pendientes;
no simula ejecuciones inmediatas. No se estudian aquí calendario, rentabilidad o alfa.

## Verificación local y trazabilidad

Clientes programados, workspace temporal y cartera sintética; sin modelos ni bases
remotas. Probar tres renovaciones, recuperación de agenda escrita, permanencia del
mandato/petición, límite antes de cada llamada, Unicode, resultados por referencia,
continuaciones opacas, cuatro llamadas de consolidación, errores, cancelación, límites
globales y reanudación sin repetición de órdenes. Contrastar también regresiones del modo
acotado y fronteras de importación.

Conservar manifiesto, eventos, conversación incremental, ventana final, resultados originales,
snapshots y trazas. Cada reconstrucción registra tamaño antes/después, cambios de archivos
y recursos consumidos. Preservar también cierres sin progreso, excesos y fallos de captura.

## Evaluación semántica posterior

Antes de autorizar campaña, fijar revisión de código, wheel, modelo/perfil, tokenizer,
mandato, instrucciones, estado inicial, dataset/fecha, presupuesto total y rúbrica.
Usar entradas y recursos iguales al comparar una segunda política de contexto; cambiar
un solo mecanismo. Esta implementación prepara una política, no una comparación ya realizada.

Revisar si recupera la pregunta activa, distingue hechos de supuestos, conserva intentos
fallidos y fundamentos, elige nuevas acciones por materialidad y evita redescubrimientos.
Medir coste por avance y repeticiones; más llamadas, escrituras u operaciones no son éxito.
No fijar todavía una campaña ni inventar puntuaciones o resultados de inversión.

La aceptación técnica exige continuidad acotada y evidencia recuperable. Una propuesta
arquitectónica futura requiere hallazgos semánticos y decisión explícita, separados de checks.
