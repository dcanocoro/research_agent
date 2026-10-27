# Research Agent

Laboratorio para descubrir qué mecanismos de conocimiento, investigación y revisión
necesita el futuro FinMate. La aspiración es mantener evaluaciones de inversión
fundamentadas y revisables; su arquitectura se decidirá mediante experimentos.

**Prioridad actual:** contrastar conservación y continuidad con un estado de archivos
por experimento, a partir de la [arqueología de FinMate](docs/finmate-concept-model/modelo-conocimiento-actual.md).
El [baseline](docs/baseline.md) fija la referencia actual y sus límites; la
[estrategia](docs/strategy.md) define alcance y criterios de avance.

Hoy implementa A: modelo → herramienta → modelo → respuesta, con estado Markdown,
JSON, TXT y CSV, materiales automáticos e instrucciones y ejecuciones separadas.
Permite empezar una prueba vacía o continuar su estado; Git es manual.
No incorpora DCF, cartera o grafo obligatorio. E001/E002 son antecedentes históricos.

El proyecto vive fuera de FinMate. Reutiliza bibliotecas compartidas instaladas desde
un wheel local; sus fuentes permanecen en FinMate. No importa `finmate`, `engine` o `api`.

## Empezar

La [documentación](docs/README.md) reúne cinco referencias: visión, estrategia,
arquitectura, experimentos y desarrollo, con registros de decisiones, hallazgos y entregas.
Las instrucciones para trabajar en este repositorio están en [AGENTS.md](AGENTS.md).

Con el entorno y `.env` preparados según [desarrollo e instalación](docs/development.md):

```powershell
.\.venv\Scripts\python.exe -m research_agent "Investiga NVIDIA" --experiment ./artifacts/nvidia-conservacion --new --run-name investigacion-inicial
.\.venv\Scripts\python.exe -m research_agent "Continúa desde lo conservado" --experiment ./artifacts/nvidia-conservacion --continue --run-name revision-documental
.\.venv\Scripts\python.exe -m research_campaigns validate campaigns/longitudinal-v1
```

Los comandos reales pueden consumir servicios LLM, Tavily y PostgreSQL según la tarea.
Workspace y archivo de ejecuciones deben estar separados. Para consultas de historial,
exportación, campañas y pruebas, seguir [desarrollo y operación](docs/development.md).

La CLI carga guía financiera básica; no representa todavía el A0 sin guía
específica de la [matriz propuesta A0–A3](docs/experiments.md). Una ejecución completada
o un check aprobado no demuestra suficiencia financiera ni rentabilidad.

Revisión documental: 2026-10-18. [Entregas y comprobaciones fechadas](docs/deliveries/README.md).
