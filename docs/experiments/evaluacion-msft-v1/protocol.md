# Evaluación decisoria de Microsoft — primera campaña

Fecha: 2026-10-31. El usuario autoriza implementar la dirección hacia una evaluación
útil para decidir y ejecutar una campaña; fija literalmente esta pregunta:

> Evaluar si Microsoft merece una inversión a cinco años al precio de referencia, frente a esperar, con fundamentos, escenarios, riesgos y condiciones de revisión

## Diseño previo

Un investigador, un objetivo fijo, Microsoft como empresa fijada por el usuario y
estado nuevo. Sin cribado del universo ni objetivo de cartera. La pregunta es el texto
exacto de `peticion.md` y de `objective.json → description`; las condiciones viven en
mandato y protocolo. El preflight fijará un precio fechado real de Findata sin tratarlo
como cotización vigente; muestras y diagnósticos permanecen fuera del estado.

El resultado de trabajo es `empresas/MSFT/evaluacion.md`: juicio provisional con
fundamentos, escenarios y cálculos reproducibles, relación con precio, riesgos,
condiciones de revisión y bloqueos específicos. No se crea una plantilla vacía ni
se exige comprar. Insuficiencia genérica no satisface el objetivo de evaluación.

La implementación añade dirección explícita por llamada con objetivo, vista versionada
del juicio activo hasta 4 KiB al arrancar, renovar o cambiar, y 16 KiB de margen de
semilla por debajo del umbral para objetivos con documento de evaluación. La agenda
publicable se limita a 8 KiB antes de cualquier mutación, incluidas operaciones conjuntas;
se recomienda 4 KiB y detalle en documentos referenciados. No se migra estado previo.

El evaluador separado conserva criterios fijos y distancia binaria como indicador
auxiliar. Añade juicio de utilidad decisoria, impedimentos con IDs/tipo/impacto/fuentes,
impedimentos resueltos y valoración de la adaptación frente a la revisión anterior.
Tipos: evidencia, cálculo, interpretación, coherencia y preferencia del usuario.
El investigador elige herramientas y método; debe explicitar qué hará distinto cuando
un método no resuelve el impedimento y qué resultado observable espera. Las revisiones
posteriores comprueban la adaptación, no solo la declaración de autocrítica.

## Condiciones y conservación

Presupuesto fijado antes del lanzamiento: **100 llamadas ordinarias**, 200 herramientas,
2400 segundos globales acumulados y 300 segundos por operación. Perfil esperado:
OpenAI `gpt-6-luna`, razonamiento medium, salida 16000; timeout y presupuesto del
proveedor 180 s. Contexto máximo/umbral 524288/262144 bytes. Autorrevisión cada diez
llamadas de investigación y evaluador cada veinte, adicionales al máximo ordinario
y dentro del tiempo global. Python habilitado; aritmética disponible. Findata de
solo lectura y web/extracción reales; sin ingestas, migraciones, cartera u órdenes.

Destino nuevo: `artifacts/evaluacion-msft-v1/campana-100-llamadas`. Lanzador local sobre
CLI nativa y registro de campañas, sin simulador ni modalidad nueva. Conservar
instrucciones, objetivo, definición, perfil, identidad de fuentes/wheel, comandos,
preflight, snapshots, eventos, materiales, respuesta, evaluaciones y fallos. Máximo
tres tentativas solo ante timeout recuperable, descontando todos los presupuestos;
no alterar runtime, prompts o conocimiento manualmente durante el contraste.

La campaña conserva el comportamiento continuo: alcanzar cobertura cero pide cierre,
no fuerza otra llamada ni termina automáticamente. Los límites son máximos, no éxito.
Una pausa por presupuesto no es cumplimiento; una evaluación positiva del LLM no es
validación financiera independiente. Los artefactos son locales e ignorados, no portables
por enlazarlos. No se realizan commits ni cambios en FinMate.

## Aceptación y límites

Verificación local previa: límite de agenda UTF-8 y rechazo conjunto sin publicación,
contrato de impedimentos, feedback acotado, pregunta exacta, recuperación/actualización
del juicio y regresión del continuo y lectores. Sin proveedores en los tests.

Después de ejecutar, examinar si existe una evaluación que conecte fundamentos,
escenarios, precio y juicio; qué bloqueos materiales se resolvieron; si el feedback
produjo adaptaciones útiles; consumo de consolidación y errores. Revisar cifras y
fuentes escogidas y declarar el alcance. No premiar número de documentos ni una caída
de distancia aislada. Cambian tarea, instrucciones y mecanismo frente a V8 real:
esta campaña exploratoria no identifica causalmente una mejora ni prueba rentabilidad.

## Ejecución y correcciones posteriores

Los [hallazgos](findings.md) registran 100 llamadas ordinarias y cierre por presupuesto,
con evaluación provisional y recálculo de escenarios pendiente. La captura del run
conserva el código de arranque. Tras cerrar, sin repetir proveedores, se corrigió la
recuperación de revisiones parciales y se permitió incluir hasta 16 KiB del documento
activo en el paquete evaluador manteniendo el máximo total de 64 KiB. La vista de
contexto del investigador sigue en 4 KiB y distancia solo con evaluaciones completas.
Las correcciones posteriores tienen pruebas locales y no se atribuyen a esta campaña.
