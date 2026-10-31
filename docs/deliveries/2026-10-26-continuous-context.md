# Entrega — bucle continuo con contexto acotado

Esta entrega reúne tres cortes del 2026-10-26: implementación inicial en tokens,
sustitución por bytes y preparación offline, y corrección de entrega con repetición.
Las verificaciones se conservan por corte; el runtime vigente usa bytes.

Fecha: 2026-10-26. Base Git: `d5386ad60d68dd35957991fd62b67d1d1f23f419`.
Encargo: implementar el plan aprobado y verificar localmente, sin proveedores ni campañas.
Contrato y preguntas: [protocolo](../experiments/contexto-continuo-v1/protocol.md).

## Cambios

Modo `--continuous` y `AgentRequest.continuous` sobre A, mandato obligatorio, texto
intermedio, recursos globales opcionales y timeout finito por operación. Consolidación
de hasta cuatro llamadas y reconstrucción desde mandato, petición, metadatos, índice
y agenda. Entrega por referencias cuando los resultados no caben; historial incremental
separado de la ventana activa. No cambia el calendario, el modo acotado ni el wheel.

Dependencia local tiktoken 0.14.0 y constraints de su dependencia regex. Conteo estimado
en tokens con margen y salida reservada; no es un conteo remoto exacto. El modelo
configurado localmente, `gpt-6-luna`, no tiene mapping: rechazo explícito antes de llamar
al proveedor. Los clientes programados usan un modelo reconocido, sin inferencia real.

## Verificaciones

- 22 pruebas nuevas: tres reconstrucciones con recuperación de agenda, presupuestos,
  Unicode, continuaciones opacas, resultados grandes, consolidación, interrupciones,
  CLI crear/continuar, fecha fija y ausencia de duplicación de órdenes sintéticas.
- Ciclo, persistencia y modo continuo: 86 passed y 1 skipped (symlinks no permitidos
  por el host), con clientes locales.
- Mypy en ambos paquetes: sin errores. `pip check`: sin requisitos rotos.
- La suite completa no puede recolectar `test_longitudinal.py`: el wheel instalado
  carece de `findata.read.historical`. No se sustituyó ese módulo ni se cambió el wheel.
- Resto de la suite, excluyendo únicamente ese archivo: 131 passed y 1 skipped
  en 99,17 segundos; incluye las 22 pruebas nuevas y regresiones de fronteras.
- Comprobador documental: 250 ocurrencias de enlaces ausentes preexistentes (111 pares
  únicos). Comparación contra HEAD, leída en memoria: ningún error de enlace introducido.
- `git diff --check`: sin errores.

El intérprete base del venv carece de librería estándar. Los checks utilizan temporalmente
`PYTHONHOME` apuntando al runtime Python 3.12 del bundle local de Codex; no se editó el
intérprete ni las bibliotecas compartidas. No se realizaron commits ni publicaciones.

## Límites

La aceptación es técnica, no financiera ni semántica. La ventana calculada está acotada;
el conteo real del proveedor no se ha contrastado y las capturas/eventos acumulados del
proceso no tienen un límite total. Una continuación explícita abre otra ejecución con
nuevo presupuesto y utiliza solo lo conservado; no garantiza recuperar razonamiento
que nunca se escribió. Campañas, compatibilidad del tokenizer con el modelo configurado
y reparación del entorno compartido quedan fuera de esta entrega.

## Presupuesto en bytes y preparación offline

Fecha: 2026-10-26. Base Git: `2201d77c22f7ae53974d98e7efdfc3d94f617892` más
los cambios locales de esta entrega, sin commit. Encargo: sustituir el tokenizer y
preparar el escenario para ejecución manual, sin lanzar la campaña.

### Cambio y contrato

`ByteCounter` sustituye tiktoken por tamaño de JSON UTF-8 con margen y reserva de
salida heurística. CLI y contratos usan bytes explícitos; las opciones antiguas en
tokens se rechazan. No se cambia el modelo ni el wheel. La salida máxima del LLM
conserva su unidad de tokens; el consumo real disponible permanece en sus trazas.

El [protocolo](../experiments/contexto-continuo-v1/protocol.md) posee escenario, límites,
comandos y aceptación; sus definiciones (`campaigns/contexto-continuo-v1`; referencia local histórica) incluyen
mandato, petición, configuración y rúbrica externa. Una preparación offline reutiliza
validadores, simulador y CLI existentes, crea estado nuevo y congela las entradas.
No añade otro ciclo de ejecución ni modifica el lanzador longitudinal.

La simulación permite omitir la herramienta web con `allow_web: false`; su ausencia
conserva la web anterior. El piloto usa datos locales congelados y no abre PostgreSQL.
El directorio local `artifacts/contexto-continuo-v1/` se ignora expresamente; no se
retiran de Git las capturas históricas que ya estaban versionadas.

### Verificación

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

### Límites y siguiente paso

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

## Corrección de entrega y repetición autorizada

Fecha: 2026-10-26. Base: `2201d77` más los cambios locales previos del modo continuo
en bytes. Encargo explícito: corregir la entrega y volver a ejecutar la campaña.

### Cambio

En `run_continuous`, el tamaño de un resultado se compara con `max_context_bytes`
en investigación y consolidación. Superar `consolidation_threshold_bytes` no sustituye
el contenido por una referencia: la siguiente iteración activa la consolidación.
Se conserva el límite duro y la comprobación antes de llamar al proveedor. No cambian
prompts, herramientas, paginación, modelo, datos ni límites globales.

El [protocolo](../experiments/contexto-continuo-v1/protocol.md) identifica la repetición
con estado nuevo. Los [hallazgos](../experiments/contexto-continuo-v1/findings.md)
conservan observaciones y límites de la comparación; una repetición no acredita
causalidad ni calidad financiera general.

### Verificación

- 37 pruebas del modo continuo y preparación pasan, con clientes programados.
- El caso que cruza el umbral conserva el contenido y entra en consolidación; el
  que excede el máximo mantiene la referencia y no envía un presupuesto excesivo.
- Un documento de 32843 bytes se recupera entero mediante dos páginas, cruzando
  el umbral y conservando offsets y contenido.
- Mypy: sin errores en los 29 archivos de fuente.
- Suite completa: **185 passed**, 153,42 segundos, sin proveedores ni bases remotas
  en las pruebas.

La comprobación de entradas previa al lanzamiento confirmó igualdad de configuración,
mandato, petición, rúbrica, instrucciones, dataset, perfil y wheel registrado. La campaña
original se conserva y el nuevo intento no hereda sus archivos ni sus operaciones.
El resultado operativo de la ejecución real se recoge en los hallazgos del protocolo.

La repetición terminó con retorno 0 y `interrupted: call_limit`, sin errores de captura.
El hash agregado antes/después de todos los archivos del piloto original coincide.
`pip check` y `git diff --check` pasan. El comprobador documental conserva los mismos
tres enlaces ausentes al informe histórico anterior; no introduce errores nuevos.

### Límites

Se corrige la entrega observada, no la selección de investigaciones ni las ausencias
del corpus. Las capturas/eventos siguen creciendo en RAM y disco. El máximo en bytes
sigue siendo local, no una garantía de tamaño remoto. No hay commit ni push.
