# Entrega — presupuesto en bytes y piloto manual

Fecha: 2026-10-26. Base Git: `2201d77c22f7ae53974d98e7efdfc3d94f617892` más
los cambios locales de esta entrega, sin commit. Encargo: sustituir el tokenizer y
preparar el escenario para ejecución manual, sin lanzar la campaña.

## Cambio y contrato

`ByteCounter` sustituye tiktoken por tamaño de JSON UTF-8 con margen y reserva de
salida heurística. CLI y contratos usan bytes explícitos; las opciones antiguas en
tokens se rechazan. No se cambia el modelo ni el wheel. La salida máxima del LLM
conserva su unidad de tokens; el consumo real disponible permanece en sus trazas.

El [protocolo](../experiments/contexto-continuo-v1/protocol.md) posee escenario, límites,
comandos y aceptación; sus [definiciones](../../campaigns/contexto-continuo-v1) incluyen
mandato, petición, configuración y rúbrica externa. Una preparación offline reutiliza
validadores, simulador y CLI existentes, crea estado nuevo y congela las entradas.
No añade otro ciclo de ejecución ni modifica el lanzador longitudinal.

La simulación permite omitir la herramienta web con `allow_web: false`; su ausencia
conserva la web anterior. El piloto usa datos locales congelados y no abre PostgreSQL.
El directorio local `artifacts/contexto-continuo-v1/` se ignora expresamente; no se
retiran de Git las capturas históricas que ya estaban versionadas.

## Verificación

- Suite completa: **183 passed**, 161,10 segundos; incluye regresiones, límites,
  preparación y una ejecución CLI con respuestas programadas que atraviesa tres
  renovaciones con prompts reales y reserva de salida de 16000 tokens.
- Mypy: sin errores en 29 archivos de fuente. `pip check` y `git diff --check`: correctos.
- Instalación editable actualizada desde el pyproject sin cambiar el wheel compartido.
- Piloto preparado en `artifacts/contexto-continuo-v1/piloto` y comprobación `READY`
  offline: 50 empresas con cobertura, presupuesto inicial 166514 bytes (35012 de
  entrada, margen y 128000 de reserva), por debajo del umbral 196608. Cartera vacía,
  fecha 2023-01-01 y cero runs. Dataset copiado por hash, sin reutilizar estado antiguo.
- Sintaxis de `run-pilot.ps1`: comprobada con el parser de PowerShell sin ejecutarlo.
- Enlaces locales: tres errores preexistentes por un informe histórico ausente.
  Comparación contra HEAD en memoria: ningún error introducido.

No se usan modelos, bases remotas ni campañas reales. Las pruebas de preparación
prohíben conexiones remotas; Windows asyncio puede utilizar un par de sockets de
loopback interno. No hay commit ni push. Las comprobaciones no prueban continuidad
semántica del modelo real.

## Límites y siguiente paso

La preparación confirma cobertura local, perfil, semilla y congelación; no acredita
disponibilidad del proveedor ni conservación semántica. El modelo Luna no requiere
ya un mapping de tokenizer. Los datos retrospectivos y la reserva heurística no
garantizan fidelidad histórica ni capacidad remota. Las listas de eventos/trazas
del proceso siguen sin un límite total de RAM; el primer intento dura como máximo
20 minutos y una ampliación requiere revisar recursos y resultados.

Ejecutar manualmente el script del protocolo sobre el piloto preparado y aplicar
la rúbrica a al menos tres renovaciones con investigación posterior. Si no se alcanza
esa exposición, conservar el intento como insuficiente. No hay resultado financiero,
hallazgo semántico ni decisión arquitectónica derivados de esta entrega.
