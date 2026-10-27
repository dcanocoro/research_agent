# Revisión previa del piloto

La persona revisora lee las trazas y los archivos, no solo la última respuesta.
Esta rúbrica queda fuera del estado y las instrucciones que recibe A.

## Aceptación técnica

- Exigir al menos tres eventos `lab.context.renewed` con una llamada de investigación
  posterior a la tercera renovación. Menos: exposición insuficiente, no éxito ni fracaso semántico.
- Comprobar presupuesto local en bytes antes de cada llamada, historial recuperable,
  resultados originales, motivo de pausa y ausencia de errores de captura.
- Comprobar fecha fija, cartera inicialmente vacía y órdenes pendientes sin ejecuciones.
- Un límite global devuelve una pausa controlada, no una investigación completada.
- Registrar llamadas, tiempo, uso real del proveedor cuando exista y tamaño de capturas.
  Observar RAM desde fuera del proceso; no inferir consumo estable del límite de contexto.

## Revisión semántica de cada renovación

Registrar para cada criterio: conservado, parcial, perdido o no observable, con referencia
al evento/call y archivo anterior y posterior. No agregar una puntuación sin evidencia.

| Criterio | Evidencia que buscar |
|---|---|
| Mandato | Mantiene fecha, universo, horizonte, restricciones y finalidad de investigación |
| Pregunta e intención | Recupera la incertidumbre activa y la siguiente acción, o justifica cambiarlas |
| Fundamentos | Recupera cifras, periodos, unidades, procedencia, supuestos y cálculos relevantes |
| Fallos y bloqueos | Conserva intentos agotados y condiciones para reabrirlos |
| Recuperación | Usa índice/agenda y lee los archivos pertinentes antes de apoyarse en ellos |
| Revisión | Explica correcciones y mantiene coherentes los documentos afectados |
| Materialidad | La acción posterior aporta comprensión o reduce una incertidumbre relevante |
| Repetición | Distingue comprobación justificada de redescubrimiento sin novedad |

## Decisión posterior

Separar éxito mecánico de continuidad semántica y avance económico. El piloto habilita
valorar una ejecución más larga si hay exposición suficiente, captura íntegra y continuidad
sin pérdidas materiales no reparadas. Un bloqueo bien conservado puede ser correcto;
repetirlo indefinidamente no demuestra autonomía útil. Conservar fallos e inconclusos.

No hay brazo control, repetición estadística, prueba de alfa ni backtest limpio. El dataset
es retrospectivo, su disponibilidad histórica es parcial y el modelo puede conocer el futuro.
Una reanudación tras cerrar el proceso se evalúa aparte de las renovaciones dentro del run.
