# Continuar la consolidación después de errores de herramienta

Fecha: 2026-10-28. Encargo explícito del usuario tras la
[campaña V5 interrumpida](../experiments/herramientas-estado-v5/findings.md).
Se conserva el intento original y los cambios locales anteriores.

## Cambio

Se elimina la condición de `run_continuous` que terminaba toda la ejecución con
`consolidation_failed` ante cualquier resultado de herramienta con `ok=false`.
El resultado pasa al historial y a la siguiente llamada del modelo, como en
investigación. El aviso de consolidación explica que puede corregirlo usando las
llamadas restantes. No hay reintento automático ni repetición oculta de escrituras.

Cada intento sigue descontando presupuesto. Se mantienen las cuatro llamadas máximas
por consolidación, la renovación al responder o agotarlas y los límites globales de
llamadas, herramientas, tiempo y contexto. Las excepciones operativas y cancelaciones
conservan su tratamiento. Un error de herramienta no se convierte en éxito ni acredita
que se haya conservado el conocimiento.

No se cambia la validación de anclas ni se interpreta NUL como un comodín para un
archivo vacío. El agente puede recibir el rechazo y escoger una escritura válida.

## Verificación

Pruebas con clientes controlados, sin proveedores ni BD remota:

Resultado: **107 pruebas aprobadas** de continuo, herramientas V5 y preparación del
piloto. Mypy sobre agente y campañas, enlaces de las cuatro referencias documentales
afectadas y `git diff --check`: aprobados.

- Lectura fallida en consolidación: el modelo recibe el error y la historia previa,
  guarda la agenda, renueva y continúa investigando.
- Reproducción de V5: agenda vacía, hash correcto y ancla NUL inexistente; se mantiene
  el rechazo, pero la llamada siguiente puede guardar mediante `write_file`.
- Cuatro herramientas fallidas consumen las cuatro llamadas y se renueva, sin bucle
  ilimitado ni requisito de escritura exitosa.
- Si el error agota el límite global de llamadas o herramientas, se pausa por ese
  límite y conserva el resultado fallido en la historia.
- Escritura aplicada con fallo de captura: el modelo recibe `applied=true`, puede
  inspeccionar el archivo y no hay repetición automática de la escritura.

La verificación local no equivale a repetir la campaña real ni demuestra continuidad
semántica o mejora financiera. El resultado de 11 llamadas del primer intento permanece
como evidencia del comportamiento anterior.
