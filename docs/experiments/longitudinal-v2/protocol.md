# Longitudinal v2 — expediente argumentativo experimental

Estado: preparado e integrado, sin campaña real. Fecha: 2026-10-22.
Encargo aceptado: endurecer benchmark, construir prototipo y verificar offline.
No autoriza ejecutar campañas ni adoptar este mecanismo en FinMate.

## Pregunta y controles

¿Aporta un expediente con identidad, revisiones y operaciones explícitas mejores
revisiones y continuidad que la memoria Markdown con M1 + M2, a coste proporcionado?
El contraste futuro compara A0 (`markdown`) y A1 (`argumentative`) sobre el mismo A.
La guía financiera, M1 + M2 y límites son comunes; A1 añade solo instrucciones de
operación del expediente. El tratamiento incluye representación, herramientas y
validaciones; esta primera comparación no atribuirá resultados a cada pieza aislada.

La [suite](../../../benchmarks/longitudinal-v2/suite.yaml) fija tres casos de seis
sesiones, con fuentes íntegramente sintéticas y reloj 2030. Conserva v1 intacta.

| Caso | Definición y rúbrica privada | Dificultad añadida |
|---|---|---|
| ASML | [Caso](../../../benchmarks/longitudinal-v2/S1/case.yaml), [rúbrica](../../../benchmarks/longitudinal-v2/S1/rubric.md) | Cartera creciente, menor conversión próxima y mayor concentración, con efecto aislado del precio. |
| NVIDIA | [Caso](../../../benchmarks/longitudinal-v2/S2/case.yaml), [rúbrica](../../../benchmarks/longitudinal-v2/S2/rubric.md) | Piloto y despliegue competitivo, logística y calendarios con distintos horizontes. |
| Ford | [Caso](../../../benchmarks/longitudinal-v2/S3/case.yaml), [rúbrica](../../../benchmarks/longitudinal-v2/S3/rubric.md) | Reexpresión de liquidez y flujos con deuda y perímetro Credit intactos. |

Las rúbricas identifican fuentes disponibles por sesión, dependencias privadas,
alternativas admisibles, controles numéricos y errores materiales. Quedan fuera del
estado y del contexto del agente, igual que los documentos todavía no publicados.
Ambas representaciones pueden resolver las tareas: no se exige un grafo para aprobar.

## Condiciones efectivas

Cada condición empieza vacía y aislada; las sesiones de un caso continúan sus propios
archivos y, en A1, su SQLite. Cada sesión arranca un proceso nuevo, sin restaurar chat,
respuestas anteriores ni trazas del evaluador como memoria suplente.

Perfil `closed-corpus`: archivos, aritmética y conocimiento en A1. No se construyen
clientes Tavily ni motor Findata. `entradas/` está protegida contra escrituras del
agente. En ASML 03, leer o buscar contenido de cada documento distinto del catálogo
consume una de dos consultas; releerlo o paginarlo no consume otra. El catálogo y la
memoria no consumen cupo. Una búsqueda transversal que excedería el cupo se rechaza
antes de leer contenido, aunque el texto buscado no aparezca. La cuota es por sesión.

Presupuesto igual por sesión: 18 llamadas, 30 herramientas, 300 segundos, 45 segundos
de umbral de cierre y 262144 bytes de contexto. Las operaciones SQLite consumen
llamadas de herramienta y su schema consume contexto en A1; no se compensan esos costes.

El perfil LLM no se elige en esta entrega. Una campaña controlada exigirá un JSON con
`provider`, `model`, `reasoning_effort` y `max_output_tokens` idéntico en ambas condiciones.
`reasoning_effort` puede ser null; Gemini requiere null en este campo. Se construye un
perfil independiente del entorno, con defaults compartidos del wheel para transporte
(30 s por intento, 45 s por llamada, hasta 3 intentos; sin verbosity/thinking adicional).
Los manifiestos por run conservan el perfil completo efectivo y el hash del wheel.
Congelar también código, prompts, fuentes y rúbricas; cualquier diferencia material
invalida atribuir el resultado exclusivamente al mecanismo. No incorporar respuestas
esperadas, entidades precargadas ni dependencias del evaluador al expediente.

## Captura y revisión futura

Conservar respuesta, contexto efectivo, resultados originales/entregados, errores y
snapshots de archivos. A1 conserva además copia SQLite consistente y exportación
lógica inicial/final, verificadas por hash y comparadas entre sí. Las revisiones,
relaciones y causas de revisión pendiente forman parte de la evidencia. El archivo
compacto conserva estos ficheros y sigue leyendo campañas anteriores.

Evaluar por sesión, trayectoria y estado final: juicio financiero, consistencia,
precisión de revisión, memoria/trazabilidad y eficiencia/complejidad. Registrar
observado/parcial/fallo/N/O y evidencia concreta; sin nota global. Un elemento pendiente
no demuestra error financiero, ni su ausencia demuestra validez del razonamiento.
Una buena respuesta y un mal estado se registran separadamente.

La evaluación local del 2026-10-21 está en
`artifacts/evaluacion-campanas-2026-10-21.md`, fuera de Git: es un antecedente local,
no evidencia portable. Describe una tentativa por condición y límites de salida
4000/16000 distintos; sus notas son retrospectivas. No demuestra superioridad causal
de M1 + M2. El nuevo control se elige por encargo, no por declarar ganadora esa campaña.

La siguiente tarea deberá ejecutar primero A0 y revisar si las dificultades resultan
observables y plausibles. Si se modifica el benchmark, versionar y volver a congelar
antes de comparar A1; no reutilizar selectivamente resultados de definiciones previas.
La repetición, modelo concreto y presupuesto monetario se fijarán antes de esa campaña.
Una señal prometedora será mejora reproducible en revisión, consistencia o historia,
sin degradación material del juicio y con coste aceptable; aún no se ha observado.

## Verificación y límites

Validación de catálogo, cálculos de referencia revisados, pruebas con clientes
simulados y SQLite temporales, tipado, dependencias, enlaces y diff. No se ejecuta
el benchmark con proveedores ni se consultan bases remotas. No hay hallazgos de
discriminación, superioridad semántica, coste real, rentabilidad o adopción en FinMate.
La entrega solo acredita capacidad operativa local; véase la
[entrega](../../deliveries/2026-10-22-argumentative-prototype.md).
