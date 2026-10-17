# Research Agent

Laboratorio para descubrir qué mecanismos de conocimiento, investigación y revisión
necesita el futuro FinMate. La aspiración es mantener evaluaciones de inversión
fundamentadas y revisables; su arquitectura se decidirá mediante experimentos.

**Prioridad actual:** comprender el modelo conceptual vigente de FinMate antes de
comparar alternativas de estado. El [plan](docs/strategy.md) define alcance y criterios
de avance; esta reorganización documental todavía no realiza ese análisis.

Hoy implementa el agente A: modelo → herramienta → modelo → respuesta, con memoria
Markdown y herramientas financieras y web. No incorpora DCF, cartera o grafo obligatorio.

El proyecto vive fuera de FinMate. Reutiliza bibliotecas compartidas instaladas desde
un wheel local; sus fuentes permanecen en FinMate. No importa `finmate`, `engine` o `api`.

## Empezar

La [documentación](docs/README.md) reúne cinco referencias: visión, estrategia,
arquitectura, experimentos y desarrollo, con registros de decisiones, hallazgos y entregas.
Las instrucciones para trabajar en este repositorio están en [AGENTS.md](AGENTS.md).

Con el entorno y `.env` preparados según [desarrollo e instalación](docs/development.md):

```powershell
.\.venv\Scripts\python.exe -m research_agent "Investiga NVIDIA sin DCF" --workspace ./artifacts/workspace --runs ./artifacts/runs
$auditRoot = Join-Path $PWD.Path "artifacts/audit"
.\.venv\Scripts\python.exe -m experience_audit lab ./scenarios --output $auditRoot
```

Los comandos reales pueden consumir servicios LLM, Tavily y PostgreSQL según la tarea.
Workspace y archivo de ejecuciones deben estar separados. Para consultas de historial,
exportación, escenarios y pruebas, seguir [desarrollo y operación](docs/development.md).

La CLI y Audit cargan guía financiera básica; no representan todavía el A0 sin guía
específica de la [matriz propuesta A0–A3](docs/experiments.md). Una ejecución completada
o un check aprobado no demuestra suficiencia financiera ni rentabilidad.

Revisión documental: 2026-10-17. [Entregas y comprobaciones fechadas](docs/deliveries/README.md).
