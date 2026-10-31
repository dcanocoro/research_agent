# Autorregulación v3 y renovación menos frecuente

Fecha: 2026-10-27. Base Git: `99ac7e9`; cambios locales sin commit.
Encargo: incorporar en español las orientaciones de progreso, conocimiento,
recuperación y coherencia de la propuesta v3, y reducir las recomposiciones.

## Cambio y alcance

Los tres prompts existentes refuerzan reflexión sobre progreso durante el trabajo,
construcción ordinaria de explicaciones e hipótesis, recuperación según la pregunta y
corrección de afirmaciones obsoletas. La consolidación guarda solo lo pendiente y puede
terminar antes de consumir sus cuatro llamadas. Son instrucciones al mismo A, sin
activación obligatoria del harness ni herramientas nuevas.

Las definiciones v3 (`campaigns/contexto-continuo-v3/scenario.json`; referencia local histórica) elevan el
umbral de 196608 a 262144 bytes, manteniendo máximo de 524288 y presupuestos de 60
llamadas, 90 herramientas y 1200 segundos. Mandato, petición, perfil y dataset permanecen
iguales; la rúbrica añade autorregulación. Los intentos anteriores conservan sus copias.
El [protocolo](../experiments/contexto-continuo-v1/protocol.md#v3--autorregulación-mediante-instrucciones-y-renovación-menos-frecuente)
registra alcance, hipótesis, límites y comandos.

Se preparó sin servicios el destino local ignorado
`artifacts/contexto-continuo-v3/piloto`, con memoria y cartera nuevas e instrucciones
v3 copiadas. Su presupuesto inicial es 171306 bytes, incluida reserva de salida de
128000; el margen de arranque de 2048 también cabe bajo el umbral. El proveedor no
se ha consultado ni la campaña se ha ejecutado. Estos artefactos no son evidencia portable.

## Verificación y límites

Las pruebas del piloto cubren ambas definiciones con datos sintéticos y red prohibida,
incluyendo propagación del umbral al comando y congelación de instrucciones. Los límites
pequeños de las pruebas del ciclo se ajustaron al mayor tamaño de los prompts, manteniendo
las comprobaciones de entrega al cruzar el umbral, máximo, paginación y renovación.

Resultados locales:

- Suite completa: 193 pruebas pasaron y una detectó que la prueba sintética de tres
  renovaciones necesitaba más llamadas con el umbral v3. Se amplió su presupuesto de
  10 a 14 llamadas, sin modificar los límites de la campaña.
- Tras esa corrección, las 46 pruebas de ciclo continuo y preparación del piloto pasaron.
  No se repitió el resto de la suite, que había pasado.
- Mypy: sin incidencias en 29 archivos. `pip check`: dependencias compatibles.
- Preparación y `continuous check` del piloto real local: correctos, sin proveedor.
- 75 enlaces locales revisados: sin ausencias nuevas; siguen ausentes dos referencias
  previas al informe local de la campaña histórica, ajenas a este cambio.
- `git diff --check`: correcto.

La orientación de tres o cuatro renovaciones en 60 llamadas queda por observar; no es
una cuota ni un resultado demostrado. Instrucciones y umbral cambian juntos, de modo que
el contraste evaluará el conjunto. Menos mantenimiento no demuestra mejor análisis.
