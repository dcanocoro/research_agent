# Operadores Python programables v1

Estado: implementación y verificación local; contraste controlado con LLM preparado, sin ejecutar.
Fecha: 2026-10-27.

Encargo posterior del usuario: repetir V4 con Python activado. La
[observación real V4](findings-v4.md) está ejecutada y revisada; no equivale al
contraste sintético controlado descrito aquí, que sigue sin ejecutar.

## Pregunta e hipótesis

¿Permitir procedimientos Python acotados ayuda a resolver preguntas cuantitativas
con exactitud y coste proporcionado? Se espera resolver una necesidad en un intento
o hasta dos correcciones. Es una hipótesis por observar, no una garantía ni un
motivo para aceptar un cálculo incorrecto.

## Implementación y límites acordados

La [arquitectura](../../architecture.md#operadores-python-opcionales) describe la
capacidad. Por preferencia del usuario, esta POC usa procesos locales sin Docker,
con filtros preventivos y sin aislamiento de seguridad ni límite duro de memoria.
No crea acceso alternativo a Findata, un motor DCF validado, un registro de funciones
o un nuevo ciclo de planificación. La instalación es opcional y requiere `--python`.

Los cuatro [contratos](../../../src/research_agent/python_contracts/calculate.md)
definen interfaz y ejemplos. Las pruebas locales ejecutan los ejemplos con referencias
independientes y cubren el ciclo mediante clientes simulados. No demuestran elección
autónoma de herramientas, utilidad económica ni rendimiento de inversión.

## Contraste futuro, pendiente de ejecución

Usar las cuatro tareas del [corpus sintético](fixtures.json) y la [rúbrica](rubric.md).
Crear un experimento nuevo por tarea, condición y repetición; sin memoria compartida.
Control: sin `--python`. Intervención: con `--python`. Mantener las herramientas
restantes idénticas, las mismas instrucciones actualizadas en ambas condiciones,
modelo/perfil, pregunta, datos y límites. Python será la única diferencia de capacidad.

No usar web ni bases vivas: construir A con herramientas de archivos y, solo en la
intervención, las herramientas Python. Es una composición local para el contraste;
la CLI habitual puede tener fuentes externas y no equivale a este entorno congelado.
La primera entrega prepara el corpus y protocolo, sin añadir un runner de campañas.

Repetir cada caso tres veces por condición (24 ejecuciones). Usar el mismo perfil
efectivo en todas, sin cambiar de proveedor/modelo entre intentos: congelar antes su
identidad, temperatura si existe y máximo de salida. Límites por ejecución: 12
llamadas de modelo, 15 herramientas, 180 segundos y cierre reservado de 45 segundos.
El worker mantiene sus propios 30 segundos. El modelo no recibe referencias esperadas
ni rúbrica: solo pregunta y datos. Conservar también fallos y agotamientos de presupuesto.

Antes de la campaña, congelar revisión/diff, hashes de corpus, contratos, instrucciones,
schemas, entorno y configuración. No ejecutar contra capturas o estado históricos.
Los resultados locales en `artifacts/` no serán evidencia portable por sí solos.

## Aceptación y medición

La aceptación técnica exige casos numéricos correctos, referencias recuperables,
errores precisos y procesos terminados ante límites/cancelación. El contrato exige
criterios en evaluate y supuestos en model; comprobar su estructura no acredita su
sentido económico.

Para cada necesidad, registrar primer intento correcto, correcciones, exactitud,
tratamiento de ausencias/unidades, duración, llamadas y tokens reportados. Derivar
coste solo si existe información suficiente. Vincular intentos mediante revisión
de la conversación; no inventar una agrupación automática por función.

Una ejecución con éxito y un resultado incorrecto cuenta como fallo analítico.
Valorar si el resultado cambia una conclusión fundada o resuelve la pregunta.
Comparar resultados y coste por tarea; esta muestra es exploratoria y no basta
para afirmar superioridad general. La reutilización automática queda fuera de v1.
Registrar hallazgos únicamente después de ejecutar y revisar las capturas.
