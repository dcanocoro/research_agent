# Registro de experimentos y hallazgos

La [metodología](../experiments.md) define cómo comparar y la
[estrategia](../strategy.md) establece la prioridad. No hay protocolos ni hallazgos
locales registrados aquí todavía. Los escenarios ejecutables de [scenarios](../../scenarios)
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
