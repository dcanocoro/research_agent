# Reorganización documental — 2026-10-17

## Base y alcance

Base Git: `efbb4c1228675a6371a21db91dd5e041546bd837`.
Cambio previo ajeno: `.env.example` eliminado; se conserva esa eliminación.
Encargo: mejorar organización, contenido y legibilidad sin ampliar innecesariamente
la documentación ni ejecutar la agenda experimental.

Se sintetizan tres textos aportados por el usuario: los guidelines de reorganización,
«FinMate — Rediseño del modelo de conocimiento y reconstrucción experimental de la
arquitectura» y «FinMate — Contexto histórico y aprendizajes para el rediseño arquitectónico».
Son propuestas y antecedentes, no pruebas nuevas sobre FinMate. No se copian adjuntos
completos ni rutas privadas como dependencias documentales.

## Cambios

- Cinco referencias centrales: visión, estrategia, arquitectura, experimentos y desarrollo.
  Se conservan nombres estables y se integran las dependencias en desarrollo.
- [Estrategia](../strategy.md) como referencia de prioridad: arqueología del estado,
  alternativas conceptuales, operaciones, persistencia, transiciones y reconstrucción.
  A0–A3 pasa a línea posterior; ningún modelo se declara elegido.
- Distinción entre estado de dominio, conversación, memoria y evidencia experimental.
  Registros mínimos de decisiones y experimentos, sin ADRs o hallazgos ficticios.
- README, índice y AGENTS orientados a lectura selectiva y continuidad. El mapa de
  FinMate queda como apéndice; en la entrega anterior solo se redirige el enlace de
  dependencias a su nueva ubicación, conservando su contenido histórico.

## Verificación y límites

Contraste estático de contratos, composición, CLI, prompts y herramientas locales.
Verificados 14 archivos Markdown y 111 enlaces locales sin destinos ausentes; sin
espacios al final de línea, errores de UTF-8, bloques de código abiertos o archivos
sin salto final. `git diff --check` correcto.
La existencia de enlaces a FinMate no comprueba de nuevo sus capacidades o campañas.
No hay revisión independiente ni aceptación semántica en este trabajo documental.

No se modifican runtime, prompts, escenarios, bibliotecas o entorno instalado.
No se llaman proveedores o bases remotas ni se repite la suite de runtime.
No se realiza commit, push o despliegue.

## Siguiente paso recuperable

El próximo encargo de investigación es la arqueología conceptual descrita en
[estrategia](../strategy.md): modelo actual, relaciones y ciclos de vida, diagnóstico
fundado y preguntas abiertas. Esta entrega prepara ese trabajo; no lo da por realizado.
