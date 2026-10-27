# Entrega: benchmark piloto

Fecha: 2026-10-20. Base Git: `eb673ef` y diff local de esta entrega, sin commit ni publicación.

Se añade un controlador local que valida definiciones, prepara experimentos, ejecuta
la CLI existente por sesión y reúne evidencia nativa. El [protocolo](../experiments/benchmark-pilot-v1/protocol.md)
define B1, E2, F3 y G2, ocho sesiones y revisión humana. Los
[comandos](../development.md#campañas) permiten validar, ejecutar un caso o
regenerar pasos sin proveedor. No cambia ciclo, prompts, bibliotecas compartidas o Audit.

Verificación local:

- `python -m pytest -q tests`: 65 passed, incluidos 21 checks del benchmark. Se probaron
  los cuatro pilotos con servicios simulados y CLI/AgentA/RunRecorder en procesos
  distintos, conservación de archivos, fallos, interrupción y capturas incompletas.
- `python -m mypy src/research_agent --follow-imports=silent`: sin errores, 18 fuentes.
- `python -m research_agent.benchmark validate benchmarks/pilot-v1`: cuatro casos y ocho
  sesiones; la prueba offline bloquea imports de servicios y del producto.
- `python scripts/check_docs.py`: 25 Markdown, 470 enlaces locales, cero errores.
- `git diff --check`: sin errores.

Sin campaña real, Excel, jueces LLM, puntuación semántica ni conclusión de calidad
financiera. El siguiente paso operativo es una invocación explícita de `run` y revisión
humana de su archivo completo. No se presume disponibilidad o estabilidad de servicios
remotos a partir de los checks locales.
