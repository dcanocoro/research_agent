# Decisiones arquitectónicas

Registrar aquí solo elecciones duraderas que afecten conceptos, fronteras, contratos
o garantías. La
[estrategia](../strategy.md) orienta la agenda; no implica que un modelo esté aceptado.

- [ADR-0001 — Estado de archivos por experimento](0001-estado-por-experimento.md):
  aceptada el 2026-10-18 para el laboratorio, con Git manual.

- [ADR-0002 — Simulación longitudinal](0002-simulacion-longitudinal.md):
  aceptada el 2026-10-24; disponibilidad estimada, universo y separación de estados.

- [ADR-0003 — Intención persistente](0003-intencion-persistente.md): aceptada el
  2026-10-24 como condición experimental; mandato protegido y agenda automática,
  sin aceptación semántica ni campaña real.

Usar `0001-nombre-breve.md`, con número consecutivo y este contenido mínimo:

```markdown
# ADR-0001 — Título de la elección
Estado: Propuesta | Aceptada | Sustituida
Fecha: YYYY-MM-DD

## Contexto
Problema, operación o garantía necesaria.

## Decisión y alternativas
Elección, alcance y opción más sencilla considerada.

## Justificación
Evidencia enlazada, interpretación y motivo de la elección.

## Consecuencias
Beneficios, costes, incertidumbres y condición para reconsiderar.
```

Elegir un único estado. Una decisión material pasa a `Aceptada` tras la aceptación
humana; no basta que un experimento termine. Si otra la sustituye, conservar la anterior
y enlazar ambas. No crear ADRs por ajustes rutinarios ni copiar hallazgos completos.
Cuando existan, enlazar aquí número, título y estado para facilitar su consulta.
