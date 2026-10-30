# Campaña V5: mismo escenario, 100 llamadas ordinarias

Fecha: 2026-10-28. Estado inicial: autorizada por el usuario, preparación y ejecución
real de una campaña con la implementación V5. No es un contraste causal ni un backtest.

Resultado posterior: ejecutada, detenida tras 11 llamadas en la primera consolidación.
Los [hallazgos](findings.md) conservan el fallo y sus límites; no alcanzó 100 llamadas.

## Pregunta y condiciones

Observar si A adopta las herramientas de estado y expediente, qué entrega recibe,
cómo conserva y recupera fundamentos tras renovar contexto y qué revisiones realiza.
Separar adopción, integridad mecánica, calidad de contexto y calidad financiera.

Referencia: última ejecución V4 con Python,
`artifacts/contexto-continuo-v4/piloto-python-v1`. Se conservan por hash mandato,
petición, rúbrica, universo y dataset. La definición nueva está en
[campaigns/contexto-continuo-v5](../../../campaigns/contexto-continuo-v5/scenario.json).

- Fecha fija: 2023-01-01; 50 empresas; 100.000 USD ficticios; diez posiciones máximas.
- Datos congelados SHA-256 `4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`.
- Web desactivada, sin exportar ni consultar la BD remota. Estado, agenda y cartera nuevos.
- OpenAI `gpt-6-luna`, medium, salida máxima 16000, mismos parámetros efectivos.
- Código e instrucciones actuales, perfil V5 y Python opcional habilitado como en V4.
  No se añade una instrucción para forzar el uso de las herramientas.
- 100 llamadas de investigación más consolidación. Revisiones cada diez llamadas
  de investigación, adicionales según la política vigente. No significa 100 llamadas
  totales al proveedor ni obliga a completar el presupuesto si hay otro límite/error.
- 150 herramientas: aumento proporcional desde 90/60 para evitar corte prematuro.
  Mismo tiempo máximo de 1200 segundos, contexto 524288 bytes y umbral 262144.

Se parte de estado nuevo, sin continuar los análisis de V4. Se conservan todos los
intentos anteriores. El presupuesto inicial se recalcula con V5, simulación y Python
realmente registrados. No se cambia el ciclo ni el controlador del laboratorio.

## Captura y evaluación

El lanzador local se conserva en `artifacts/contexto-continuo-v5/ejecutar.py` y utiliza
el preparador e inspector nativos. La captura completa vive en
`artifacts/contexto-continuo-v5/piloto-100-llamadas`; es local e ignorada por Git.

Aplicar la rúbrica V4 conservada. Sus referencias a 60 llamadas son antecedentes;
registrar el presupuesto nuevo y el número real, sin imponer una cuota de renovaciones.
Además registrar con referencias a eventos/resultados:

- Herramientas V5 ofrecidas y elegidas, propósitos, consulta opcional de contratos,
  lecturas selectivas, búsquedas, creaciones y revisiones; distinguir escritores antiguos.
- Errores, conflictos, continuación/paginación, captura y cambios aplicados.
- Empresas/dimensiones conservadas, IDs y referencias; recuperación después de renovar.
- Cálculos Python, fuentes y reservas presentes en los documentos; distinguir cálculos
  ejecutados de procedimientos propuestos y fuentes citadas de inferencias justificadas.
- Llamadas por fase, herramientas, tiempo, uso reportado y RAM observada desde fuera
  del proceso cuando sea posible. Las muestras no prueban estabilidad ni son límite duro.

Una pausa `call_limit` es interrupción controlada. El registro general puede etiquetarla
`failed` porque exige completitud del mandato: no atribuir esa etiqueta automáticamente
a un fallo instrumental. Conservar estado final, trazas y motivos reales de cierre.

## Límites

Cambian herramientas, instrucciones y presupuesto frente a V4. Una única ejecución
no atribuye causalidad ni demuestra superioridad, calidad financiera o rentabilidad.
El dataset es retrospectivo, la disponibilidad histórica es parcialmente estimada y
el modelo puede conocer acontecimientos posteriores. No es un backtest limpio.
Los hallazgos se documentarán después de leer las capturas; no se anticipan resultados.

## Repetición tras corregir la recuperación de errores

Autorizada expresamente el 2026-10-28 después de eliminar el cierre automático ante
errores de herramienta en consolidación. Se conserva el primer intento de 11 llamadas.
La corrección y sus pruebas están en la
[entrega](../../deliveries/2026-10-28-consolidation-tool-errors.md).

La repetición usa `artifacts/contexto-continuo-v5/repeticion-100-llamadas`, con estado
y cartera nuevos. Conserva por hash las instrucciones del primer V5, además de
mandato, petición, rúbrica y dataset. Mantiene modelo y todos los límites de V5.
El aviso técnico de consolidación explica ahora que los errores se pueden corregir;
es parte de la intervención y queda capturado, no un nuevo encargo financiero.

Se observará especialmente si el agente recibe un error y actúa después de él,
cuánto presupuesto consume, si conserva conocimiento antes de renovar y si lo recupera.
No se forzará un error ni una herramienta durante la ejecución real. El informe
distinguirá ausencia de errores de recuperación demostrada y checks mecánicos de
calidad del análisis. Se registrará la exposición real, aunque no alcance 100 llamadas.

Resultado posterior: alcanzó 100 llamadas ordinarias y seis revisiones adicionales,
con diez renovaciones y captura completa. El [informe de funcionamiento](findings-repeticion.md)
conserva errores, recuperación, comprobaciones numéricas y límites semánticos.
