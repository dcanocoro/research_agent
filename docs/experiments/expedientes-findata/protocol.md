# Expedientes con FinData en una sesión

Dos repeticiones emparejadas de Progress abierto con y sin nota, con dos
procesos concurrentes. Una sesión por recorrido, 120 llamadas gestionadas
como máximo, umbral común de 400.000 bytes y renovación anticipada por
cambio de compromiso desactivada en ambos brazos abiertos.

El objetivo JSON con mode open distingue el cierre de cada avance del cierre
global. El evaluador propone otro compromiso material o justifica un bloqueo
global. El contrato anterior conserva su cierre por suficiencia. Se conserva
la posibilidad de cerrar por límites operativos.

La cartera es sintética y las observaciones proceden de FinData de solo
lectura. El mandato limita el análisis a observaciones disponibles hasta
el 5 de noviembre de 2026. La base se consulta en vivo y la fecha de corte
se aplica por instrucción, con las respuestas de herramientas capturadas.

[El lanzador](../../../campaigns/expedientes-findata/ejecutar.py) recibe un
destino nuevo. Pausa la segunda pareja si falla un proceso de la primera.
Revisar expedientes y trazas a las llamadas 30, 60, 90 y 120 o hasta el
cierre. Distinguir avances materiales, trabajo repetido y trabajo retomado
tras renovar. Si faltan renovaciones comparables, dejar abierto el efecto
de la nota.
