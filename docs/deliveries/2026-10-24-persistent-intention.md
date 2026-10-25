# Entrega — Intención persistente experimental

Fecha: 2026-10-24. Base Git: `907880e`, árbol limpio al empezar. Cambios locales sin
commit. Implementación del plan aprobado; no se ejecutan campañas ni servicios remotos.

## Cambio

Condición deliberativa opcional sobre A: mandato auténtico externo, agenda automática,
instrucciones copiadas y captura del contexto inicial. El controlador congela la
condición y reconstruye los mensajes disponibles por fecha, también al recuperar
intentos. Se mantienen herramientas, recuperación selectiva, política de cierre y
baseline sin mandato. La API directa sin experimento gestionado incorpora la guía
del paquete; los experimentos gestionados exigen su copia explícita.

El [protocolo](../experiments/intencion-persistente-v1/protocol.md) contiene el escenario
de seis activaciones, la rúbrica y los comandos para dos campañas independientes.
La [decisión](../decisions/0003-intencion-persistente.md) registra la elección experimental.
Se corrigen referencias desactualizadas a la campaña histórica, preservando sus capturas.

## Verificación

- Suite completa: **135 passed** en 109,79 s, con proveedores controlados. Continuidad entre procesos, recuperación
  de materiales tras traslado, límites UTF-8, autoridad, cierre, fallos y recuperación
  sin duplicar efectos; compatibilidad baseline y rechazo de contexto incorrecto.
- Mypy sin errores sobre los 26 archivos fuente; `pip check` sin conflictos.
- Enlaces locales sin errores y `git diff --check` correcto.
- Escenario validado: 50 empresas y seis activaciones. Universo, límites y mensajes
  dentro del intervalo coinciden con el escenario histórico revisado.
- Preflight local sobre el dataset existente: `ready=true` para las 50 empresas;
  SHA-256 `2b65121feae3ae0f2784584f53af6649856d988997eda6eb402f0a71f2b58745`.
- Perfil configurado leído sin red: OpenAI `gpt-6-luna`, razonamiento `medium`, salida
  máxima 16.000 tokens, coincidente con el protocolo.

Comandos de regresión y enlaces: los de [desarrollo](../development.md#verificación-proporcionada-al-cambio).
La comprobación del dataset llamó directamente a `preflight(config, data)` con archivos
locales; no al subcomando que exporta Findata. Los subprocess de pruebas usaron clientes
controlados y las capturas nativas.

## Límites y siguiente paso

Las condiciones están implementadas y preparadas, no ejecutadas con el LLM real.
No se acredita iniciativa, progreso analítico, calidad financiera ni rentabilidad.
El siguiente encargo puede ejecutar ambas campañas y revisar las cadenas de evidencia
de la rúbrica, conservando intentos y limitaciones de web viva. No se cambió FinMate,
el wheel, los datos originales ni el archivo histórico; tampoco se hizo commit o push.
