# Referencias de Progress y recuperación de truncamientos

Fecha: 2026-11-07. Base: `64d0861`. Cambios sin commit ni cambios en el wheel.

## Problema y cambio

Las [tentativas del baseline](../experiments/expedientes-findata/baseline-150.md)
fallaron por copia incorrecta de hashes y una escritura truncada con repetición de
texto. Progress asigna ahora identificadores locales a documentos visibles y resuelve
sus versiones en código. Los informes válidos mantienen ruta y hash para consumidores
y continuaciones existentes; los inputs y respuestas crudas permiten reconstruir la
resolución. No se aceptan ids de otra vista ni referencias a documentos omitidos.

La reparación de informes inválidos se aplica a objetivos finitos y abiertos, una
vez por evaluación y dentro del presupuesto. La validación da el campo afectado.

El motor descarta truncamientos antes de despacho y pide un paso nuevo a la política,
con salida menor. No repite herramientas ni acepta argumentos parciales. Una recuperación
por episodio, tres por ejecución, preservando presupuestos y el error original si
la recuperación vuelve a truncarse. La composición clasifica errores del proveedor;
el núcleo no importa Infra. No se aumenta el límite de 16000 tokens.

## Verificación

Pruebas locales de Progress, recuperación, arquitectura, continuo y nota. Cubren
resolución exacta, rechazo entre vistas, reparación, persistencia de la evaluación
válida, ausencia de escrituras duplicadas y respeto al presupuesto. Se actualiza una
aserción antigua sobre el mensaje de configuración de B al contrato vigente, sin
cambiar B. Comprobación de enlaces locales nuevos y `git diff --check`.

Los checks no acreditan calidad financiera. Se autoriza repetir la pareja de 150
llamadas con las mismas entradas y estados nuevos; las tentativas anteriores se
conservan. Después de arrancar, detener el trabajo sin monitorización de resultados.

Resultado local: 95 pruebas aprobadas (39 de núcleo/Progress y 56 de continuo/nota).
Destino de la repetición: `C:/Users/canoc/Proyectos/research_agent/artifacts/expedientes-findata-baseline-150-repeticion-20261107-122229`.
