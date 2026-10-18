# 2026-10-17 — Conservación del conocimiento y E002

Base Git: `5ae4e5d4651eff2dd8c17f6d8f2bc88c7570c815`. Implementación local sin commit/push.
Contrato: [conservación y cierre](../architecture.md#conservación-y-cierre-de-la-investigación).
Protocolo y evidencia: [E002](../experiments/README.md#antecedentes-e001-y-e002).

## Qué cambió y por qué

- El prompt pide una revisión provisional temprana y actualizaciones materiales;
  respuesta breve, sin plantilla obligatoria ni guardado automático de la respuesta.
- El ciclo comunica presupuesto y separa investigación, consolidación con escritura y
  respuesta. Con defaults: hasta 15, 2 y una llamada. Filtra catálogo y despacho efectivo.
- La reserva temporal deja escribir antes del cierre. Un texto temprano sin publicación
  se conserva como borrador y ofrece consolidación dentro de los límites.
- `AgentResult.persistence` y la CLI informan publicaciones comprobadas desde disco,
  excluyendo huérfanos y otros productores, y separan entrega de respuesta de persistencia.
  Vanilla conserva su política y códigos operativos; el núcleo sigue sin dominio financiero.

Almacén, cuatro herramientas y wheel compartido se conservan. No se modificaron FinMate,
proveedores, modelo o límite de salida. Las capturas E001 y su protocolo permanecen intactos.

## Verificación

- Antes de E002: **49 tests passed**. Después de la corrección temporal posterior:
  **50 tests passed**. Cubren fases por llamadas/tiempo/herramientas/contexto, rechazo
  de búsquedas en consolidación, guardado y conflicto, borradores, fallo posterior de
  entrega, verificación de disco, huérfanos, productores, replay, reinicio y fronteras.
- Mypy: sin incidencias en 16 archivos locales; los imports sin marcadores del wheel
  mantienen los overrides ya documentados. `pip check`: sin requisitos rotos.
- Enlaces locales afectados: sin destinos rotos nuevos. Se mantienen 107 destinos
  rotos anteriores, principalmente en la arqueología importada; no se comprobaron todos
  los anchors. `git diff --check`: sin errores de whitespace.

## Ejecución real y alcance de la aceptación

Dos procesos, una sola secuencia, presupuesto global sin ampliaciones. Ambos entregaron
respuesta y publicaron una revisión; el segundo leyó y actualizó el mismo expediente.
La aceptación técnica y la recuperación inicial se observan. La aceptación semántica
es parcial: hubo investigación posterior no incorporada a las revisiones.

Se detectó un error: el candidato ejecutado aplicaba 15 segundos de consolidación
incluso al entrar por llamadas con minutos disponibles. Las dos fases agotaron ese
plazo. Tras acabar ambas intervenciones se corrigió para reservar 30 segundos de
respuesta y utilizar el resto disponible, sin ampliar las dos llamadas de consolidación.
La corrección final se probó localmente; **no se volvió a ejecutar con proveedores**.
Los [hallazgos](../experiments/README.md#antecedentes-e001-y-e002) identifican
versiones ejecutadas, corrección posterior, IDs, hashes y límites numéricos observados.

Evidencia completa en `artifacts/E002-persistent-research/attempt-01/`, local, ignorada
y no portable. Incluye código congelado, configuración, fuentes, presupuestos,
transiciones, errores, respuestas y estado. La revisión semántica fue interna; no hubo
revisión independiente, migración, despliegue ni prueba de resultados de inversión.
