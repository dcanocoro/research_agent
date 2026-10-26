# Entrega — bucle continuo con contexto acotado

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
