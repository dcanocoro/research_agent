# Research Agent: agente A

> Estado: implementación local de investigación sin DCF. Fecha: 2026-10-16.
> Evidencia: [entrega](../FinMate/artifacts/research-lab/2026-10-15/delivery.md).

Agente general con ciclo modelo → herramienta → modelo → respuesta y memoria Markdown.
Reutiliza Findata, Infra y trazas. No importa `finmate`, `engine` ni `api`, tampoco
indirectamente durante ejecución o auditoría. Solo A: sin workflows ni subagentes.

## Instalar y ejecutar

Python >=3.11, verificado con 3.12. Proyecto extraído a
`C:\Users\Daniel\Proyectos\research_agent`. Desde esta carpeta:

```powershell
.\.venv\Scripts\python.exe -m research_agent "Investiga NVIDIA sin DCF" --workspace ./artifacts/workspace --runs ./artifacts/runs
.\.venv\Scripts\python.exe -m experience_audit lab ./scenarios --output ./artifacts/audit
.\.venv\Scripts\python.exe -m pytest -q tests
```

La distribución `research-agent` está instalada en editable en su `.venv`; el paquete
compartido `findata` está instalado desde un wheel, sin enlaces editables a FinMate.
Su fuente (Findata, Infra, Audit y contratos) permanece en `../FinMate`.
Para actualizarlo, construir allí un wheel nuevo e instalarlo explícitamente en esta
`.venv`. La configuración local `.env` contiene solo ajustes y credenciales de datos,
modelos y Tavily, y no debe versionarse. `.env.example` contiene marcadores sin secretos.

Para recrear el entorno, instalar el wheel local de la distribución compartida (no un
paquete homónimo de un índice público), luego `pip install -e .` y las herramientas
`pytest`, `mypy`, `types-PyYAML`, `types-jsonschema`. Los wheels iniciales y la evidencia
están en `../FinMate/artifacts/experience-audit-validation/relocation-2026-10-16/`.
El controlador PostgreSQL debe corresponder al esquema de `DATABASE_URL`.

Workspace y runs deben ser disjuntos. La CLI usa los prompts generales/financieros
incluidos; `--instructions` añade Markdown explícito. `--conversation` identifica
la conversación, pero entre procesos solo persiste la memoria Markdown; no restaura
un chat. Cada escenario de Audit conserva una instancia para sus intervenciones.

Proveedor y modelo proceden de `LLM_PLANNER_*`, con perfil efectivo `lab`. Las
credenciales y `DATABASE_URL` siguen la configuración de Findata. Sus lecturas v2
requieren PostgreSQL. No se crean tablas, migran bases, ingieren datos ni escriben
registros financieros. La consulta aplica transacción de solo lectura y timeout.

Para trasladar esta carpeta, instalar antes la distribución compartida `findata`
que contiene Infra, observabilidad, Audit y `runtime_contracts`; después instalar
el proyecto trasladado. No se modifica `sys.path` ni se buscan recursos en el checkout
padre. Distribuciones independientes de cada biblioteca quedan fuera de v1.

## Componentes y herramientas

`AgentA.run` recibe mensaje, conversación, workspace e instrucciones y devuelve
estado operativo, respuesta, motivo de cierre, contadores y referencias. El paquete
contiene contratos, registro de funciones, workspace, recorder, composición y
adaptaciones a Findata/Tavily. Los prompts son recursos Markdown instalables.

Herramientas: búsqueda de empresas, ficha, financieros, tendencias, búsqueda web,
extracción de documentos, archivos Markdown, lectura de artefactos y aritmética
determinista. No hay SQL libre, shell, Python arbitrario ni DCF. La calculadora
conserva entradas y referencias; no demuestra comparabilidad ni respaldo semántico.

Se preservan unidades, periodos, moneda, procedencia y ausencias. Resultados grandes
se guardan completos y se leen mediante `read_artifact`. Lecturas UTF-8: hasta 32 KiB,
con offsets en bytes y continuación. Escrituras: solo Markdown dentro del workspace.
Se rechazan escapes, streams Windows, enlaces y junctions; no es un sandbox contra
otro proceso que altere simultáneamente el sistema de archivos.

Defaults por intervención: 18 llamadas lógicas, 30 herramientas, 300 segundos,
una llamada y 45 segundos reservados para cierre. Contexto máximo: 256 KiB. Sin
compactación automática: cuando ya no cabe, se registra interrupción sin recortes
silenciosos. Solo el índice de memoria se carga automáticamente, hasta 8 KiB.

## Memoria, trazas y auditoría

El workspace editable conserva Markdown. El archivo externo por ejecución contiene
manifest con configuración, prompts y schemas, eventos, transcript, respuesta,
resultados de herramientas y snapshots inicial/final.

Los eventos LLM existentes conservan sus nombres `engine.llm`, `engine.llm_call`
y `engine.llm_attempt` sin duplicación; su nombre histórico no implica dependencia
del motor. Eventos `lab.*` describen herramientas, archivos y terminación. OpenTelemetry
permanece instalado, sin configurar exportadores. La captura local es secuencial:
no ejecutar campañas concurrentes dentro de un proceso con su configuración global.

Los YAML tienen contrato propio `lab-v1`: ID, título, `messages`, `instructions`
opcionales, `memory`, `requirements`, `limits` y `checks`. Requisitos: `llm`,
`postgresql`, `tavily`. Checks: `completed`, `answer_contains`, `tool_used`,
`file_contains`; `step` selecciona una intervención desde 1. Cada escenario tiene
workspace aislado; sus mensajes comparten memoria e historial.

Audit reutiliza Archive, hashes, consulta, exportación, visor e informes. No arranca
servicios del producto ni simula usuarios, SSE o revisiones. Checks y finalización
son mecánicos: la calidad financiera requiere revisión separada. Tentativas y fallos
permanecen archivados; una cancelación conserva estado incompleto.

```powershell
.\.venv\Scripts\python.exe -m experience_audit history
.\.venv\Scripts\python.exe -m experience_audit show <execution-id> --full
.\.venv\Scripts\python.exe -m experience_audit export <execution-id> --format json --full
.\.venv\Scripts\python.exe -m experience_audit report <ruta-al-run.json>
.\.venv\Scripts\python.exe -m pytest -q tests
```

La batería incluye investigación real, periodos incompatibles, memoria, fallo
documental y recursos agotados. Fuentes sintéticas se identifican expresamente.
Las capturas completas y datos privados permanecen en almacenamiento local ignorado.
