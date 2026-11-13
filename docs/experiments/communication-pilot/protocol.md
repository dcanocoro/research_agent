# Piloto de comunicación de progreso — 2026-11-11

## Autorización y objetivo

El usuario autoriza lanzar simultáneamente tres ejecuciones y detener el trabajo
tras comprobar su arranque. Piloto exploratorio, sin evaluación automática ni
seguimiento hasta el cierre. Comparar ausencia de comunicación, hook temporal y
comunicador independiente sobre el mismo encargo.

## Encargo común

Investiga Microsoft (MSFT) y explica cómo han evolucionado su crecimiento, rentabilidad, generación de caja y deuda en los tres últimos ejercicios anuales completos disponibles. Comprueba la comparabilidad de periodos, moneda y unidades. Identifica los factores económicos materiales y las principales incertidumbres, distinguiendo datos confirmados, cálculos, interpretaciones y supuestos. Utiliza las herramientas disponibles y conserva los avances útiles y sus fuentes en el estado del experimento. Entrega una conclusión breve y fundada sobre la evolución del negocio y lo que queda sin resolver. No inventes datos ni una valoración y no realices decisiones de cartera.

## Condiciones

- Tres procesos CLI nativos: `off`, `hook`, `communicator`, cada uno con estado
  nuevo y directorio independiente; sin memoria compartida.
- Régimen acotado: 30 llamadas LLM por ejecución, incluidas consolidación, cierre
  y solicitudes de publicación del hook; hasta 60 herramientas por ejecución.
- Comunicador: hasta cinco inferencias adicionales, 30 segundos por inferencia.
  Máximo agregado: 95 llamadas gestionadas; los límites son techos, no objetivos.
- Timeout global de cada investigación: 3600 segundos, con 60 para finalización.
  Timeout y presupuesto por llamada del proveedor: 180 segundos mediante variables
  del proceso, sin cambiar `.env`. Perfil de modelo configurado igual en los tres.
- Sin continuo, Progress, B, nota de continuidad, Python ni DCF Lab.
- Mismas instrucciones base, herramientas estándar, código y pregunta. Fuentes
  Findata de solo lectura y web en vivo: datos no congelados y respuestas variables.
  No atribuir causalidad ni superioridad a una única tentativa por condición.

## Revisión posterior prevista

Revisar utilidad, fidelidad al corte temporal, redundancia, oportunidades omitidas
y retraso de las actualizaciones; evaluar por separado calidad y cierre de la
investigación. Registrar errores y coste adicional del comunicador. No premiar el
número de mensajes ni interpretar integridad técnica como calidad financiera.
No se ha realizado esa evaluación ni se declara una variante ganadora.

## Captura y disponibilidad

Salida local ignorada: `artifacts/communication-pilot-20261111-181851`.
Conserva petición y límites comunes, `launch.json`, driver y logs por proceso;
cada condición conserva manifiesto, eventos, respuesta y registros de comunicación.
`artifacts/` no es evidencia portable. El manifiesto efectivo registra modelo,
configuración y fingerprints; el arranque no demuestra finalización exitosa.
