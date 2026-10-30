# Campaña V5 — detención en la primera consolidación

Fecha: 2026-10-28. Estado: ejecución real finalizada por interrupción temprana.
El [protocolo](protocol.md) fijó el escenario V4, estado nuevo, Python, V5 y 100 llamadas
ordinarias. **Solo se realizaron 11 llamadas; no se alcanzó el límite solicitado.**
No se corrigió el runtime ni se repitió el intento para ocultar esta observación.

## Condiciones y evidencia

Mandato, petición, rúbrica y dataset coinciden por hash con la última V4 con Python.
El dataset conserva SHA-256 `4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`.
Fecha fija 2023-01-01, 50 empresas, 100.000 USD ficticios y cartera nueva; sin web
ni consultas a BD remota. Modelo `gpt-6-luna`, medium, salida máxima 16000.
El manifiesto confirma V5 y Python habilitados. Presupuesto inicial efectivo: 184979
bytes, con reserva de salida de 128000; umbral 262144 y máximo 524288.

Run: `640c90fa-d9eb-4e97-85e5-71cea9bd9053`.
[Captura local](../../../artifacts/contexto-continuo-v5/piloto-100-llamadas/README.md) y
[resumen verificable](../../../artifacts/contexto-continuo-v5/piloto-100-llamadas/resumen-observacion.json).
Son artefactos locales ignorados por Git: el enlace no los convierte en evidencia portable.

| Observación | Resultado |
|---|---|
| Límite configurado | 100 llamadas ordinarias, revisiones adicionales; 150 herramientas; 1200 segundos |
| Llamadas realizadas | 11: 10 investigación, 1 consolidación, 0 revisión |
| Herramientas | 10 exitosas, 1 rechazada |
| Renovaciones | 0; exposición insuficiente para la rúbrica de continuidad |
| Tiempo | 40,006 s de ejecución según eventos; 46,125 s del lanzamiento completo |
| Cierre | Agente `interrupted: consolidation_failed`; registro de campaña `failed` |
| Captura | Completa según inspector nativo; cero errores de captura |
| Estado editable | Ninguna escritura de conocimiento; agenda inicial sigue vacía |
| Materiales | Seis originales conservados automáticamente |
| Cartera | 100.000 USD, sin posiciones, órdenes ni comunicaciones; fecha intacta |
| Uso reportado | 170974 tokens de entrada y 1582 de salida; 122181 de entrada cacheada; 11 intentos de proveedor |

## Qué ocurrió

La primera operación fue `inspect_state`, que devolvió `agenda.md` existente y vacía
(0 bytes, SHA-256 del contenido vacío). A comenzó una comparación de AAPL y AMZN,
consultó universo, cartera, perfiles y fundamentales; recuperó resultados con
`read_artifact`. No utilizó Python ni las operaciones específicas de empresa.

Al entrar en consolidación intentó conservar la investigación con `edit_state` sobre
la agenda. Envió el hash correcto del archivo vacío, pero una sustitución cuyo objetivo
era el carácter NUL (`\u0000`), inexistente en el documento. La herramienta rechazó
el objetivo con `ambiguous_target`; el mensaje cubre tanto ausencia como ambigüedad.
El rechazo conserva el archivo: no hubo escritura parcial ni conflicto de versión.

La [traza exacta](../../../artifacts/contexto-continuo-v5/piloto-100-llamadas/ejecuciones/2026-10-28-piloto/trazas/herramienta-0064.json)
conserva argumentos y respuesta. El texto propuesto para la agenda está en esos
argumentos, **no** en el estado editable. No confundir ese borrador archivado con
conocimiento persistido y recuperable en la siguiente ventana de A.

La política del ciclo continuo vigente en ese intento finalizaba la ejecución
ante cualquier resultado no exitoso de una herramienta en consolidación. Por ello
el modelo no recibió otra oportunidad para corregir el ancla o elegir un escritor
compatible. El límite de 100 llamadas, las herramientas y el tiempo no fueron la causa.

## Interpretación y límites

**Observado:** adopción inicial de orientación V5 y un intento de edición con propósito
explícito. La validación protegió el estado y la captura conservó el fallo. La combinación
de una operación inválida elegida por A y la política de cierre impidió continuar.

**No demostrado:** utilidad de la lectura selectiva, expedientes acumulativos,
recuperación tras renovación, revisión de dependencias, calidad financiera o mejora
frente a V4. No hubo exposición suficiente ni un control equivalente; tampoco hubo
valoración calculada o decisión de inversión evaluable.

Se preservó una muestra externa de RAM del lanzador y sus descendientes: suma de RSS
382832640 bytes y memoria privada 338001920 bytes. Una muestra no establece pico,
estabilidad ni consumo propio de A; sumar RSS puede contar páginas compartidas dos veces.
El resumen conserva por separado el uso reportado en trazas, sin inferir precio o coste.

## Siguiente intervención propuesta

Antes de otra campaña larga, resolver dos puntos mediante un encargo explícito y
pruebas locales: cómo inicializar con versión un archivo ya existente pero vacío,
y si los errores recuperables de herramienta deben permitir corrección dentro del
presupuesto de consolidación. Las herramientas antiguas permiten escribir la agenda,
pero no ofrecen la precondición de versión de V5. No se introduce una excepción que
trate NUL como comodín ni se flexibiliza silenciosamente la unicidad de los objetivos.

Una repetición posterior debe conservar este intento, declarar cualquier cambio de
schema/instrucciones/política y comenzar con un estado nuevo. Este hallazgo no acepta
una modificación del ciclo ni una arquitectura nueva por sí solo.

Encargo posterior del usuario, 2026-10-28: eliminar el cierre automático ante errores
de herramienta en consolidación. La [entrega](../../deliveries/2026-10-28-consolidation-tool-errors.md)
registra la corrección y sus pruebas locales. No modifica los resultados de este
intento ni constituye una repetición de la campaña.
