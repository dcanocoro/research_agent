# Decisiones arquitectónicas

Registrar aquí solo elecciones duraderas que afecten conceptos, fronteras, contratos
o garantías. No hay ADRs locales registrados en este corte. La
[estrategia](../strategy.md) orienta la agenda; no implica que un modelo esté aceptado.

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
