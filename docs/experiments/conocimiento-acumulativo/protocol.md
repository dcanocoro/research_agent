# Conocimiento financiero acumulativo con Progress

[La campaña](../../../campaigns/conocimiento-acumulativo/ejecutar.py) compara
Progress continuo con y sin nota. Dos repeticiones emparejadas, dos procesos
concurrentes y orden de arranque invertido. Cada recorrido tiene 80 llamadas
para el estado inicial y 80 para revisarlo. Techo agregado de 640.
Umbral de renovación de 400.000 bytes, pasos de Progress de 15 llamadas
y presupuestos temporales del proveedor y transporte de 180 segundos.

Preparar el destino nuevo con `--prepare` y ejecutar el mismo lanzador con
ese destino. El controlador congela fuentes, objetivos y mandato con hashes,
conserva los manifiestos efectivos y toma una instantánea de cada estado
inicial. Solo después deposita la segunda tanda. Cada brazo conserva su
workspace. Una salida CLI con error pausa el avance de la pareja.

## Rúbrica privada

Presentar respuesta y expedientes con etiquetas de brazo ocultas. Puntuar
cada dimensión de 0 a 2 (errónea o ausente, parcial, completa).

- Detección. Identificar la subida de tipos, la cobertura omitida y los
  aplazamientos de Vector. Distinguir deuda nominal, exposición efectiva
  y sensibilidad comercial.
- Exactitud. Nébula pasa de 60 a 30 M EUR expuestos y de 1,2 a 0,6 M EUR
  de impacto anualizado. Prisma mantiene 80 M EUR al 4% hasta 2029.
  Vector desplaza 9 de 36 M EUR de hitos de 2026 a 2027, sin cancelación
  demostrada ni efecto preciso sobre margen.
- Propagación. Comparar instantánea inicial y estado final. Revisar los
  activos y el factor común. Mantener el supuesto anterior solo como
  histórico y conservar las conclusiones todavía fundadas.
- Cartera. El sector pesa inicialmente 22% frente a límite de 25%.
  Distinguir riesgo directo e indirecto y condicionar cambios de
  asignación a valoración y evidencia pendiente.

Después de puntuar, examinar eventos y trazas con etiquetas visibles.
Registrar primera conclusión correcta, primera persistencia y cierre,
llamadas por fase, tokens disponibles y errores. En cada renovación,
anotar el pendiente anterior y si la siguiente actuación lo retoma,
repite comprobaciones o reintroduce una premisa corregida. Distinguir
renovación dentro de una fase de continuación desde el expediente.
Sin renovaciones comparables con trabajo pendiente, el efecto de la
nota queda sin resolver.
