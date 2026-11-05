# Recursos y cierre de B preparado

Base Git: `dfe6a15`. Corrección del mecanismo actual en la misma rama, sin variante adicional ni cambios
en FinMate. Se mantiene el comando con `--knowledge-agent prepared` y 100 llamadas.
La [entrega anterior](2026-11-02-b-prepared-original.md) conserva su corte histórico.

## Observación y elección

La captura local `artifacts/analista-b-prepared-100/ejecuciones/2026-11-02-analista/resultado.json`
registra `interrupted / call_limit`, 100 llamadas LLM (76 A, 24 B) y 94 herramientas.
El resumen de recuperación aportado por el usuario describe cuatro intentos de seis
llamadas, nueve encargos pendientes y publicaciones parciales. Esta corrección no
modifica la captura original ni convierte sus escrituras en integraciones cerradas.

Se eligen 15 llamadas por intento frente a las seis anteriores: once para trabajo
ordinario y cuatro para verificar, publicar, declarar y corregir una declaración
rechazada. Se amplía la reserva total de B de 24 a 30, dejando 70 para A/controlador.
Con consumo máximo caben dos intentos completos; consumos menores permiten más.
La reserva no usada no se transfiere a A. Esta es una elección operativa, no una
prueba de suficiencia o mejora financiera. Registrar encargos sigue siendo posible
sin recursos inmediatos: la cola durable conserva el pendiente.

## Contrato corregido

Cada inicio exige las 15 llamadas, 24 herramientas y 181 segundos disponibles.
El hijo tiene hasta 180 segundos. El trabajo ordinario no consume los últimos 60;
el cierre conserva 15 segundos para declarar. La última llamada/herramienta, o esos
últimos 15 segundos, solo ofrecen `finish_integration`. Un timeout ordinario permite
pasar al cierre. La respuesta en texto no sustituye esa herramienta. No se garantiza
cierre si el proveedor falla, el plazo vence o el modelo no cumple: permanecen
pendientes y recibos recuperables, sin fabricar una declaración semántica.

`pending` exige pendientes explícitos y versiones actuales de todas las publicaciones,
incluidas las heredadas de intentos anteriores. `integrated` sigue exigiendo recibos
y ausencia de trabajo material pendiente. Los lotes conservan validación previa,
ámbito, hashes y recuperación transaccional; no se añade validación financiera.

Se archiva el contexto de A al registrar cada encargo: petición, acciones y resultados
disponibles. La vista selecciona los intercambios más recientes dentro de 12 KiB y
permite recuperar la captura completa. El paquete sube a 64 KiB, conserva mandato,
encargo, vistas de estado/evidencia y declaraciones anteriores, con recortes explícitos
y recuperación. Los registros anteriores sin origen no se inventan. Se conservan
cola, namespaces, bloqueos de evidencia/conflicto y reintentos explícitos.

Los experimentos nuevos congelan el prompt actualizado; continuar conserva sus
instrucciones anteriores y aplica el control del runtime. No hace falta otro comando.

## Verificación

60 pruebas locales de B, agente acotado y E2 pasan con clientes controlados.
Incluyen reserva completa, consumo global de las 30 llamadas, cola sin recursos,
cierre con publicación parcial y pendientes, declaración final restringida,
respuesta textual insuficiente, recuperación de contexto y timeout ordinario.
Mypy pasa en 45 archivos; `pip check` y `git diff --check` sin errores.

La suite completa se detiene al recopilar `tests/campaigns/test_price_review.py`: falta
`scripts/review_historical_prices.py`, también ausente en la base Git. Se verifica
el resto excluyendo únicamente ese archivo: 410 pruebas pasan en 365,96 segundos.

Comprobados 94 enlaces locales/anclas de los cuatro documentos afectados: sin
roturas internas. Existe una referencia externa previa ausente en
`docs/development.md` hacia la decisión compartida de FinMate
(`../../FinMate/docs/architecture/decisions/0004-shared-runtime-contracts.md`).
No se modifica ese repositorio ni se presenta esa referencia como validada.

No se ejecuta campaña,
no se consulta ningún proveedor o base remota, y no se hace commit ni push.
La aceptación semántica de la integración queda pendiente de la ejecución manual.
