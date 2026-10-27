# Entrega — resultados al cruzar el umbral

Fecha: 2026-10-26. Base: `2201d77` más los cambios locales previos del modo continuo
en bytes. Encargo explícito: corregir la entrega y volver a ejecutar la campaña.

## Cambio

En `run_continuous`, el tamaño de un resultado se compara con `max_context_bytes`
en investigación y consolidación. Superar `consolidation_threshold_bytes` no sustituye
el contenido por una referencia: la siguiente iteración activa la consolidación.
Se conserva el límite duro y la comprobación antes de llamar al proveedor. No cambian
prompts, herramientas, paginación, modelo, datos ni límites globales.

El [protocolo](../experiments/contexto-continuo-v1/protocol.md) identifica la repetición
con estado nuevo. Los [hallazgos](../experiments/contexto-continuo-v1/findings.md)
conservan observaciones y límites de la comparación; una repetición no acredita
causalidad ni calidad financiera general.

## Verificación

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

## Límites

Se corrige la entrega observada, no la selección de investigaciones ni las ausencias
del corpus. Las capturas/eventos siguen creciendo en RAM y disco. El máximo en bytes
sigue siendo local, no una garantía de tamaño remoto. No hay commit ni push.
