# Registro de experimentos y hallazgos

La [metodología](../experiments.md) define cómo comparar y la
[estrategia](../strategy.md) establece la prioridad. Los escenarios ejecutables de [scenarios](../../scenarios)
son estímulos y checks, no campañas realizadas ni resultados semánticos.

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
| E001 | ¿A conserva conocimiento de NVIDIA y lo recupera tras reiniciar? | Concluido: sin expediente; primera entrega fallida, segunda por presupuesto. [Protocolo](E001-nvidia-casefile/protocol.md), [hallazgos](E001-nvidia-casefile/findings.md) |
| E002 | ¿Presupuesto visible, guardado provisional y cierre con escritura permiten conservar y continuar? | Concluido: dos revisiones, recuperación observada y consolidación parcial. [Protocolo](E002-persistent-research/protocol.md), [hallazgos](E002-persistent-research/findings.md) |

E001/E002 conservan protocolos y hallazgos del modo de expedientes retirado. No son
evidencia del estado de archivos adoptado el 2026-10-18. Para un contraste nuevo,
crear un experimento separado con la [CLI vigente](../development.md#ejecutar-a-nuevo-experimento-o-continuación).
