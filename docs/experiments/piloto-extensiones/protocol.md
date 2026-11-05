# Piloto de extensiones en continuo

Cuatro condiciones con 60 llamadas gestionadas como máximo por recorrido.
A sin revisión, A con revisión general y nota, A con Progress y objetivo fijo,
y A con revisión general, nota y B preparado. B reserva 18 llamadas. A y
el controlador disponen de 42 en ese brazo. Cada condición tiene dos
repeticiones independientes en cada uno de los dos casos. Techo de 960 llamadas.

Los casos sintéticos de Lumen Redes usan documentos congelados. Renovación
parte de doce partes y dos documentos de cierre. Revisión arranca de un
expediente común y recibe una corrección. El umbral común de renovación es de 400.000 bytes presupuestados, una aproximación a 100.000 tokens. El máximo local sigue en 524.288 bytes. El primer intento con 20.000 bytes quedó pausado tras cuatro errores de contexto inicial y cero llamadas.
El uso efectivo de la nota y de B se comprueba en trazas. Los límites de
tiempo de las llamadas se fijan a 180 segundos en el proceso de campaña.

## Rúbrica previa

Evaluar respuesta y expediente con etiquetas de brazo ocultas. Asignar
de 0 a 2 por dimensión (ausente o errónea, parcial, completa).

- Cifras y procedencia. 24/120 = 20 % reportado y (24−6)/120 = 15 %
  normalizado. La corrección afecta al numerador. En Renovación, reconciliar
  también los doce partes con el cierre y la nota de auditoría.
- Juicio. Usar el 15 % como punto de partida condicionado para 2026,
  identificar qué podría cambiarlo y distinguir el ajuste del tratamiento contable.
- Estado. Guardar fuentes, cálculo y conclusión vigente sin dejar la tesis
  anterior como válida. En Revisión, actualizar evaluacion.md.

Conservar por separado consumo por rol y fase, tiempo, paradas y errores.
Agrupar revisión y nota impide estimar sus contribuciones individuales.
Dos repeticiones y dos casos sintéticos proporcionan evidencia exploratoria.

## Ejecución

[El lanzador](../../../campaigns/piloto-extensiones/ejecutar.py) prepara con
--prepare y ejecuta después el plan guardado en el mismo destino. Cuatro
bloques con dos procesos concurrentes, orden de arranque rotado y salidas
aisladas. Un código de salida no nulo pausa la campaña al terminar el bloque.
