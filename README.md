# Research Agent

Laboratorio para descubrir qué mecanismos de conocimiento, investigación y revisión
necesita el futuro FinMate. La aspiración es mantener evaluaciones de inversión
fundamentadas y revisables; su arquitectura se decidirá mediante experimentos.

**Pregunta vigente:** cómo convertir investigación y cálculos en una evaluación
revisable que permita decidir, manteniendo fundamentos y continuidad. La
[estrategia](docs/strategy.md) conserva alcance y criterios; los
[hallazgos](docs/experiments/README.md) distinguen lo observado de lo pendiente.
El [baseline del 18 de octubre](docs/baseline.md) es una referencia histórica.

Hoy implementa A: modelo → herramienta → modelo → respuesta, con estado Markdown,
JSON, TXT y CSV, materiales automáticos e instrucciones y ejecuciones separadas.
Permite empezar una prueba vacía o continuar su estado; Git es manual.
No incorpora un motor DCF preimplementado, cartera o grafo obligatorio. E001/E002 son antecedentes históricos.
La [capacidad Python opcional](docs/experiments/python-operators-v1/protocol.md)
permite construir cálculos y modelos acotados mediante `--python`, con contratos
recuperables y procesos locales; es una POC sin sandbox de seguridad.

El proyecto vive fuera de FinMate. Reutiliza bibliotecas compartidas instaladas desde
un wheel local; sus fuentes permanecen en FinMate. No importa `finmate`, `engine` o `api`.

## Empezar

La [documentación](docs/README.md) ofrece un mapa de visión, estrategia,
arquitectura, experimentos, campañas y desarrollo, con registros de decisiones, hallazgos y entregas.
Las instrucciones para trabajar en este repositorio están en [AGENTS.md](AGENTS.md).

Con el entorno y `.env` preparados según [desarrollo e instalación](docs/development.md):

```powershell
.\.venv\Scripts\python.exe -m research_agent "Investiga NVIDIA" --experiment ./artifacts/nvidia-conservacion --new --run-name investigacion-inicial
.\.venv\Scripts\python.exe -m research_agent "Continúa desde lo conservado" --experiment ./artifacts/nvidia-conservacion --continue --run-name revision-documental
```

Los comandos reales pueden consumir servicios LLM, Tavily y PostgreSQL según la tarea.
Workspace y archivo de ejecuciones deben estar separados. Para consultas de historial,
exportación, campañas y pruebas, seguir [desarrollo y operación](docs/development.md).

La CLI carga guía financiera básica; no representa todavía el A0 sin guía
específica de la [matriz propuesta A0–A3](docs/experiments.md). Una ejecución completada
o un check aprobado no demuestra suficiencia financiera ni rentabilidad.

Consolidación documental: 2026-10-31. [Entregas y comprobaciones fechadas](docs/deliveries/README.md).
