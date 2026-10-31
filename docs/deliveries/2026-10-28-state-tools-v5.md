# Estado y expedientes de empresa V5

Esta entrega reúne la implementación V5 y la corrección posterior de recuperación
de errores en consolidación. Sus verificaciones corresponden a momentos distintos;
los [hallazgos](../experiments/herramientas-estado-v5/findings.md) conservan ambos intentos reales.

Fecha: 2026-10-28. Base Git: `4e88d2a`, con propuesta e índices documentales locales
previos conservados. Encargo: implementar el plan V1 aprobado, con verificación local
y sin ejecutar campañas con proveedores. El [diseño](../experiments/herramientas-estado-v5/protocol.md)
conserva el contexto; la [arquitectura](../architecture.md#herramientas-de-estado-v5--2026-10-28)
describe los contratos efectivos.

## Cambio

Nueve herramientas nuevas: orientación, lectura por bytes/líneas/sección, búsqueda
contextual, creación exclusiva, edición exacta, orientación/lectura/revisión de una
dimensión de empresa y descripción opcional de contratos. Propósito explícito, hashes
del contenido leído, continuaciones ligadas a versiones y respuestas nuevas de hasta
32 KiB serializados. Los diffs completos se archivan y la vista puede ser parcial.

Las mutaciones se contabilizan antes de capturar; una captura fallida informa del
cambio aplicado y su versión. Workspace conserva rutas, permisos, UTF-8, límites y
publicación atómica. El bloqueo por raíz cubre escritores cooperantes del proceso;
no ofrece aislamiento frente a editores externos ni transacciones multiarchivo.

Los experimentos nuevos usan V5 por defecto. Los existentes sin configuración mantienen
legacy; su adopción explícita añade una guía sin reemplazar instrucciones y conserva
la transición. La configuración y los contratos efectivos se capturan en cada run;
se anuncian cambios de contratos en continuaciones. La API directa mantiene legacy
por defecto. Las herramientas anteriores conservan nombres y schemas.

`research_campaigns` usa el perfil efectivo en composición y presupuesto inicial,
permite elegir legacy en nuevas campañas y congela la configuración para reanudar.
No se cambian datos, campañas históricas ni el wheel compartido.

## Verificación local

- Suite completa: **294 pruebas aprobadas** (`python -m pytest -q tests --tb=short`).
- 41 pruebas específicas de V5 aprobadas: integridad, conflictos, colisiones,
  selectores, Unicode/CRLF, JSON, paginación, entrega serializada, captura fallida,
  perfiles/adopción, contratos y ejemplos ejecutables.
- Caso H1/V1 con cliente controlado: revisión explícita, búsqueda de dependencia,
  pendiente conservado y recuperación después de renovación real del contexto.
- 75 pruebas de persistencia, metodología y preparación del piloto aprobadas.
- Mypy sobre agente y campañas y `pip check`: aprobados.
- `git diff --check`: aprobado.
- Wheel local construido sin índice ni dependencias: contratos y guía V5 presentes.

Las pruebas de transporte que dependían de definiciones retiradas usan ahora fixtures
sintéticos temporales, conservando sus comprobaciones de publicación, aislamiento,
argumentos y renovación. No se recrean campañas ni se presentan como evidencia histórica.
El control financiero congelado se prueba expresamente con perfil legacy.

El comprobador documental global no queda aprobado: aparecen referencias históricas
a campañas, artefactos y archivos del repositorio hermano ausentes. En la comparación
final hay 46 referencias rotas únicas tanto en `HEAD` como en el árbol actual, ninguna
introducida por V5. La disponibilidad del repositorio hermano cambió durante los checks;
no se modifica ni se restauran sus archivos desde este encargo.

## Límites y siguiente paso

La capa de empresa reconoce localizadores de encabezados y conserva referencias;
no verifica su fundamento financiero, admisibilidad histórica ni significado del ID.
No crea dimensiones vacías, selecciona investigaciones, propaga conclusiones ni declara
un expediente coherente. No hay almacén de versiones intermedias restaurables.

Esta entrega acredita mecánica e integración local. Un contraste controlado autorizado
deberá evaluar utilidad del contexto, elección autónoma de herramientas y calidad de
revisión; no se ejecuta aquí ni se infiere mejora financiera o causal.

## Corrección posterior: errores recuperables en consolidación

Fecha: 2026-10-28. Encargo explícito del usuario tras la
[campaña V5 interrumpida](../experiments/herramientas-estado-v5/findings.md).
Se conserva el intento original y los cambios locales anteriores.

### Cambio

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

### Verificación

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
