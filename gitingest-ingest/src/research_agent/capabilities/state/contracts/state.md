# Contrato de estado — state-tools-e1

Las rutas son relativas al estado; materiales originales son de solo lectura.
Las consultas exigen purpose no vacío. Los resultados entregados se limitan a 32 KiB
y el original se conserva como artefacto. Una vista parcial requiere continuación.
Las garantías son estructurales, sin certificación semántica o financiera.

## Recuperación

- inspect_state(path,purpose,cursor): inventario o mapa de encabezados ATX fuera de
  bloques de código. Las continuaciones vinculan inventario y versiones.
- read_state(path,purpose,selector,expected_sha256,cursor): bytes, líneas o sección.
  Líneas desde 1, bytes desde 0; sección por línea del encabezado. Documento completo:
  {"kind":"lines","start":1,"end":null}. Primera lectura sin versión/cursor; para
  continuar utiliza el sha256 devuelto, los mismos argumentos y el cursor opaco.
- search_state(path,query,purpose,context_lines,cursor): búsqueda literal sin distinguir
  mayúsculas, ordenada por ruta y línea; hasta 50 coincidencias por página.
  context_lines entre 0 y 8, normalmente 2. Extractos largos son explícitamente parciales.
- describe_state_tools(tool): contrato opcional de una herramienta disponible en la fase.

Un hash vincula bytes, no una interpretación. Las secciones no prueban cobertura.
Las lecturas pueden continuar dentro de una línea larga. Un cambio de argumentos,
inventario o versión invalida su continuación; recupera de nuevo lo necesario.

## Única escritura

record_research_advance(changes,reason,source_refs) acepta 1–5 archivos distintos.
Cada cambio tiene path, action, content, expected_sha256 y operations:

- create: content explícito, expected_sha256=null, operations=null; solo archivo ausente.
- edit: content=null, expected_sha256 vigente, operations no vacías. Cada operación
  tiene kind (replace, insert_before, insert_after), target único y content.

Se conserva UTF-8 y texto exacto; hasta 128 KiB por archivo y 8 KiB para agenda.md.
JSON debe ser válido. No hay borrados, reemplazo ciego ni modificación de materiales.
Todas las validaciones preceden a publicación. Ante conflicto de versión o target
ambiguo, el lote se rechaza. El target vacío tiene una única coincidencia solo en
un archivo vacío y permite inicializarlo con su versión vigente. El diario queda fuera del estado editable, en ejecuciones.
Un fallo de publicación restaura el conjunto; si falla la recuperación, el run se detiene.
No ofrece aislamiento frente a editores externos.

El resultado devuelve applied y files con versiones anteriores/nuevas, bytes y vistas
parciales. Si applied=true y falla la captura, inspecciona el estado antes de reintentar.
Las secciones de empresa conservan IDs únicos y cuerpos poblados; vistas y advertencias
literales no prueban coherencia económica ni validez de reason o source_refs.

## Ejemplo local ejecutable

Con workspace (Workspace) y runs (Path fuera del estado) proporcionados:
```python
from research_agent.storage.transactions import record_advance
from research_agent.capabilities.state.operations import StateOperations
ops = StateOperations(workspace)
created = record_advance(workspace, runs, [
    dict(path="notas.md", action="create", content="# Hallazgo\nProvisional.\n",
         expected_sha256=None, operations=None)
], "Guardar un hallazgo", [])
view = ops.read_state("notas.md", "Revisar", dict(kind="lines", start=1, end=None), None, None)
edited = record_advance(workspace, runs, [
    dict(path="notas.md", action="edit", content=None, expected_sha256=view["sha256"],
         operations=[dict(kind="replace", target="Provisional.", content="Revisión pendiente.")])
], "Precisar el estado", [])
assert edited["files"][0]["applied"]
```
