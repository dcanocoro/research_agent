# Research Agent

Laboratorio para investigar qué combinación de autonomía, herramientas, instrucciones
y memoria mejora el análisis y la revisión de conclusiones. Hoy implementa el agente A:
modelo → herramienta → modelo → respuesta, con memoria Markdown y primera especialización
financiera mediante Findata y Tavily. No incorpora DCF, cartera o grafo obligatorio.

El proyecto vive fuera de FinMate. Reutiliza bibliotecas compartidas instaladas desde
un wheel local; sus fuentes permanecen en FinMate. No importa `finmate`, `engine` o `api`.

## Empezar

La [documentación](docs/README.md) reúne propósito, arquitectura, dependencias,
experimentos, operación y referencias. Las instrucciones para trabajar en este
repositorio están en [AGENTS.md](AGENTS.md).

Con el entorno y `.env` preparados según [instalación](docs/dependencies.md):

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

Estado documentado: 2026-10-16. [Entrega y comprobaciones de este corte](docs/deliveries/2026-10-16-documentation.md).
