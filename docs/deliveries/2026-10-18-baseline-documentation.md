# 2026-10-18 — Documentación y referencia del baseline

Base Git: `20afee95ed6e99f9ba25394abfa30b3293ce461b`. Se conservan los borrados previos
de los cuatro documentos E001/E002 y `src/research_agent/py.typed`. No hay cambios
de comportamiento, prompts, bibliotecas instaladas, wheel compartido o datos remotos.

## Cambios

- [Baseline](../baseline.md) con contrato, código, huellas, configuración observada,
  checks y límites semánticos; referencias desde README, índice, estrategia y AGENTS.
- [Hallazgos retrospectivos de NVIDIA](../experiments/baseline-nvidia-2026-10-18/findings.md),
  sin inventar protocolo previo ni presentar la revisión interna como independiente.
- Metodología actualizada: E002 deja de ser el siguiente encargo. La CLI conserva
  instrucciones copiadas; escribir conocimiento y entregar respuesta son operaciones distintas.
- Recuperación histórica de E001/E002 desde Git; sus borrados no se revierten.
- 282 destinos de enlaces de la arqueología corregidos al repositorio hermano FinMate.
  Se identifican metadatos originales ausentes. No se alteran conclusiones del corte histórico
  ni se valida de nuevo toda su semántica frente al checkout actual de FinMate.
- `scripts/check_docs.py`: comprobación local de archivos y anclas, sin red ni dependencias nuevas.

## Verificación

- 44 pruebas pytest aprobadas, incluido Audit instalado con servicios simulados y frontera
  de imports en subprocess. Mypy sin incidencias en los 15 archivos fuente; `pip check` correcto.
- Enlaces locales y anclas de README, AGENTS y todo `docs/` sin errores; `git diff --check`.
- Huellas actuales de Research Agent, Findata, Infra y runtime_contracts iguales a las del
  run NVIDIA. También se comprobaron resultado, manifiesto y snapshot final por sus hashes.
- Sin nuevas ejecuciones LLM/Tavily/PostgreSQL, commit, push o reinstalación de bibliotecas.

La consistencia documental y los checks locales no equivalen a aceptación semántica ni
reproducibilidad de proveedores remotos. El paquete declara `py.typed`, pero el archivo
fue eliminado previamente; el baseline recoge esa diferencia y no acredita el empaquetado
tipado para distribución. La siguiente campaña necesita entradas, condición y rúbrica fijadas.
