# Investigación autónoma: 1.000 llamadas

Preparación del 2026-11-01; campaña no ejecutada en esta entrega.
Una ejecución nueva de A en continuo de `experiment/fileAgent` con el [mandato literal del usuario](mandato.md)
y una [petición de arranque](peticion.md) sin empresa asignada. El workspace empieza
vacío: no se importa conocimiento de otras campañas.

Desde la raíz Git, con el entorno y credenciales del laboratorio ya disponibles:

```powershell
.\campaigns\investigacion-autonoma-1000\ejecutar.ps1
```

El [script](ejecutar.ps1) fija OpenAI gpt-6-luna, medium, salida máxima 16000,
timeout/presupuesto de proveedor 180 s y UTF-8; restaura las variables de proceso
al terminar y no edita .env. Usa Python opcional, Findata de solo lectura y web reales.
Techo de 1000 llamadas LLM gestionadas totales, incluidas consolidación y revisiones;
2000 herramientas, 300 s por operación y contexto máximo/renovación 524288/262144 bytes.
No fija timeout global ni reintenta una ejecución fallida. Los reintentos internos
del proveedor quedan en las trazas y no incrementan el contador gestionado.
El script usa `--max-total-calls 1000` además de `--max-calls 1000`: en esta rama
la segunda opción limita únicamente investigación/consolidación. El techo total
reserva una llamada para la revisión final y evita exceder 1000 con las revisiones.
Se conserva el controlador por fases de File Agent, sin incorporar E2.

El destino por defecto es `artifacts/investigacion-autonoma-1000`, que debe ser nuevo.
Para elegir otro destino:

```powershell
.\campaigns\investigacion-autonoma-1000\ejecutar.ps1 -Output artifacts/investigacion-autonoma-1000-otro
```

Esto lanza otro experimento completo, con presupuesto nuevo: no es una recuperación
ni debe usarse como reintento silencioso. Las instrucciones efectivas y el mandato
quedan en la captura nativa. No modificar código ni entradas durante la ejecución.

Consultar `estado/` y `ejecuciones/` bajo el destino: manifiesto, resultado, respuesta
cuando exista, eventos, conversación completa, revisiones y snapshots. No se genera
`campaign.json` ni informe agregado; se usa directamente la CLI nativa, como en los
casos fijos. Esta receta no es una definición para `research_campaigns run/validate`.
La CLI puede retornar 0 con `interrupted: call_limit`; no acredita cumplimiento.
Un fallo operativo puede cerrar antes de 1000 llamadas y conserva lo capturado.

El [protocolo](../../docs/experiments/investigacion-autonoma-1000/protocol.md)
fija la revisión posterior y los límites de interpretación. No hay objetivo JSON,
recomendación final obligatoria, pausas planificadas ni intervención humana intermedia.
