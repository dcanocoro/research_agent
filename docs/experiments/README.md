# Registro de experimentos y hallazgos

La [metodología](../experiments.md) define cómo comparar y la
[estrategia](../strategy.md) establece la prioridad. Las definiciones ejecutables de [benchmarks](../../campaigns)
son estímulos y rúbricas, no campañas realizadas ni resultados semánticos.

Crear una carpeta `E001-nombre-breve/` cuando exista un contraste concreto:

- `protocol.md`: estado (propuesto, en curso o concluido), pregunta, hipótesis,
  variantes, operaciones, entradas, controles, presupuestos, repeticiones y rúbrica.
  Indicar de antemano qué resultado justificaría una decisión. Fijar revisión antes
  de ejecutar y registrar cualquier desviación sin sobrescribir el protocolo original.
- `findings.md`: base y ejecuciones, resultados observados, interpretación, fallos,
  límites de captura, incertidumbres y decisión propuesta o siguiente comparación.
  Separar resultado operativo, checks y juicio semántico; enlazar el ADR si se acepta.

No crear resultados vacíos como si se hubiera ejecutado. Conservar también intentos
fallidos y revisiones anteriores. Identificar revisión de código, configuración,
wheel, entradas y artefactos con hashes o referencias recuperables. Una ruta local en
`artifacts/` no constituye evidencia portable: declarar disponibilidad y restricciones
si las capturas no pueden compartirse. No incorporar secretos o payloads privados.

Mantener aquí una fila por experimento cuando exista: ID, pregunta, estado, enlaces
a protocolo/hallazgos y decisión asociada. Un experimento puede concluir sin recomendar
un cambio arquitectónico; una entrega de ingeniería no sustituye sus hallazgos.

| ID | Pregunta | Registro |
|---|---|---|
| Contexto continuo v1 | ¿A conserva intención y avanza a través de reconstrucciones con ventana acotada? | [Protocolo](contexto-continuo-v1/protocol.md) y [hallazgos](contexto-continuo-v1/findings.md); original y repetición ejecutados, bloqueo técnico corregido; continuidad semántica parcial. [V3](contexto-continuo-v1/protocol.md#v3--autorregulación-mediante-instrucciones-y-renovación-menos-frecuente): instrucciones reforzadas y umbral mayor, sin campaña ejecutada. |
| Análisis financiero v1 | ¿Metodología y conocimiento Markdown mejoran el análisis acumulativo? | [Protocolo](analisis-financiero-v1/protocol.md) y [rúbrica](analisis-financiero-v1/rubric.md); implementación local, contraste y aceptación semántica sin ejecutar. |
| Intención persistente v1 | ¿Mandato y agenda ayudan a mantener intención y producir progreso? | [Protocolo](intencion-persistente-v1/protocol.md); condición ampliada de 60 llamadas: seis activaciones completadas por condición. [Hallazgos preliminares](intencion-persistente-v1/findings-amplio.md); condición de 18 llamadas sin ejecutar. |
| Colaboración histórica v1 | ¿Cómo colabora A durante meses con iniciativa y cartera ficticia? | [Protocolo](colaboracion-historica-v1/protocol.md); 24 activaciones completadas. Informe local (`../../artifacts/campana-historica-completa-v1/informe-ejecucion.md`; no disponible en este checkout), ignorado y no portable; web temporalmente contaminada, sin prueba de alfa. |
| Longitudinal v1 | ¿Cómo combina A investigación, revisión y memoria en tres historias exigentes? | Tres escenarios de seis sesiones generados; [protocolo](longitudinal-v1/protocol.md). Corpus sintético y rúbricas previas; sin ejecutar. |
| Benchmark piloto v1 | ¿Qué hace A ante contradicción, continuidad, ruido y fuentes fallidas? | Cuatro casos preparados; [protocolo](benchmark-pilot-v1/protocol.md). Verificación local con servicios simulados; sin campaña real ni aceptación semántica. |
| Baseline NVIDIA 2026-10-18 | ¿Qué dejó la primera ejecución del estado de archivos? | Observación exploratoria concluida; [hallazgos retrospectivos](baseline-nvidia-2026-10-18/findings.md). Sin protocolo previo ni control. |
| E001 | ¿A conserva conocimiento de NVIDIA y lo recupera tras reiniciar? | Histórico: sin expediente; recuperación desde Git indicada abajo. |
| E002 | ¿Presupuesto visible y cierre con escritura permiten conservar y continuar? | Histórico: dos revisiones y recuperación observada, consolidación parcial; recuperación desde Git indicada abajo. |

## Antecedentes E001 y E002

Sus cuatro documentos no están en el árbol de trabajo actual. No se han restaurado
como parte de la revisión del baseline. Los resúmenes de las entregas de
[expedientes](../deliveries/2026-10-17-casefile.md) y
[conservación](../deliveries/2026-10-17-persistent-research.md) permanecen disponibles.
Para consultar las versiones históricas sin modificar archivos:

```powershell
git show 20afee9:docs/experiments/E001-nvidia-casefile/protocol.md
git show 20afee9:docs/experiments/E001-nvidia-casefile/findings.md
git show 20afee9:docs/experiments/E002-persistent-research/protocol.md
git show 20afee9:docs/experiments/E002-persistent-research/findings.md
```

Estos registros describen el modo de expedientes retirado. No son evidencia del estado
actual de archivos. Crear un experimento separado con la
[CLI vigente](../development.md#ejecutar-a-nuevo-experimento-o-continuación) para un
contraste nuevo y seguir el [baseline](../baseline.md) para fijar las condiciones.
