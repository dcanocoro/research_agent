# NVIDIA — Observación inicial del baseline de archivos

Fecha: 2026-10-18. Registro retrospectivo de la ejecución solicitada por el usuario.
No hubo protocolo ni rúbrica fijados antes del run. No asigna un ID E003 ni presenta
esta observación como contraste controlado. Referencia técnica: [baseline](../../baseline.md).

## Ejecución y evidencia

- Petición exacta: `investigar Nvidia`. Experimento inicialmente vacío.
- Run: `ccc663aa-5f32-4b0b-9287-757a3854f2c4`, 11:43:58–11:45:19, Europe/Madrid.
- OpenAI `gpt-6-luna`, razonamiento `medium`, salida máxima 4000. Sin instrucciones
  añadidas a las copias general y financiera. Las huellas del código coinciden con el baseline.
- `completed / budget`: 18 llamadas al modelo, 17 herramientas, unos 81,37 segundos.
  El límite de llamadas provocó el cierre; quedaba tiempo y no se agotaron las 30 herramientas.
- Evidencia completa local en `artifacts/nvidia-investigacion-2026-10-18/ejecuciones/2026-10-18-investigar-nvidia/`.
  Estado en `estado/`, con `indice.md`, `nvidia-panorama.md` y 14 JSON en `materiales/`.
  La ruta es relativa a la raíz del repo, está ignorada y no constituye evidencia portable.

| Archivo | SHA-256 |
|---|---|
| manifiesto.json | `a02a727181119dbd361e16ed72a34c337954384552e54b51a021cc2debd5fd5e` |
| resultado.json | `5402fb373da1311032f53a4f0952a55d061ea5f5bbc25fa540c2301938eacf3d` |
| estado-final.json | `53a228a82d41815d913e833b3e578aa5f6561c8bd25921e8d98440b643957886` |

## Observaciones

Las 15 acciones de investigación fueron: listado inicial, cuatro lecturas/búsquedas
Findata, dos búsquedas web, cuatro extracciones sobre tres URLs y cuatro cálculos.
Los materiales se guardaron automáticamente. En consolidación escribió primero el
índice y después el panorama; la última llamada entregó texto sin herramientas.

Se comprobaron los 16 contenidos del estado frente al snapshot final, hashes de los
14 materiales y de las 18 capturas del modelo. No hay fallos de herramienta ni errores
de captura registrados. El Git propio del experimento figura ausente antes y después.
No se ha ejecutado una continuación real de este experimento.

La revisión semántica posterior del mismo asistente desarrollador encontró:

- Uso de aritmética determinista, cautelas sobre periodos, distinción negocio/precio
  y una discrepancia entre capitalización y acciones por precio dejada sin resolver.
- Caída del margen y cargo H20 conservados como hechos separados, sin desarrollar
  su relación causal o una condición explícita que permitiera revisar la interpretación.
- Caja y capex incluidos entre los pendientes de extracción del filing, aunque ya había
  cifras del proveedor disponibles; no distingue claramente ausencia y falta de contraste.
- Pendientes amplios sin priorización por su posible efecto sobre la evaluación.
- Referencias abreviadas en prosa y explicaciones mezcladas con rutas en `source_refs`;
  los cálculos son recuperables, pero no hay validación automática del soporte de entradas.
- Ninguna interpretación provisional guardada durante la fase de investigación: el
  conocimiento narrativo se escribió solo al consolidar. El índice precedió al documento,
  dejando una ventana aproximada de 13 segundos con un enlace aún no satisfecho.

## Interpretación y límites

El run demuestra conservación de materiales y entrega de una síntesis recuperable.
Su razonamiento observable tiene comprobaciones útiles, pero la conexión causal,
priorización y uso de evidencia disponible son parciales. No acredita superioridad,
continuidad semántica, actualización correcta ante contradicción o rentabilidad.
Una pregunta abierta permite un panorama breve; no se exige DCF o recomendación.

La inferencia de que mejorarían instrucciones de investigación o representación del
conocimiento es una hipótesis. No puede atribuirse este resultado al modelo, al presupuesto
o a un mecanismo individual con una tentativa sin control. Conservar los materiales
antes de usar este run como entrada de un contraste nuevo.
