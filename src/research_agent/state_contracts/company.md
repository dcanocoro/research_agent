# Documentos de empresa — state-tools-e1

Son vistas del mismo estado. Las rutas son empresas/<simbolo>/<dimension>.md, con
dimension modelo, valoracion o evaluacion. El símbolo debe ser ASCII inequívoco,
sin escapes ni colisiones entre grafías que solo difieran en mayúsculas.
No se crean las otras dimensiones automáticamente.

- inspect_company(symbol,purpose,cursor): existencia, versiones, encabezados e IDs.
  Ausente significa no conservado, no demuestra que nunca se investigara.
- read_company_document(symbol,dimension,purpose,selector,identifier,expected_sha256,cursor):
  elige selector o identifier, dejando el otro en null. Para H1: identifier="H1",
  selector=null. Para documento completo: identifier=null y selector de líneas desde 1.
  Un ID debe localizar exactamente un encabezado ATX fuera de bloques de código.
  Las continuaciones y vistas parciales siguen el contrato de read_state.

Los IDs son localizadores, no conceptos validados. Duplicados se informan al leer;
un estado externo corrupto no se repara automáticamente.

La escritura se realiza con record_research_advance sobre la ruta explícita. Antes de
publicar, se rechazan IDs duplicados, eliminados y vaciado del cuerpo de una sección
antes poblada. Las comprobaciones no detectan un cambio de significado del ID ni
certifican fuentes, cifras o hipótesis. Devuelve changed_ids, recovered_sections,
sus omisiones y advertencias literales sobre referencias locales. Una referencia
futura ausente no impide guardar ni demuestra una revisión resuelta.

Tras cambiar H1, busca sus dependientes por ruta e ID y aplica la revisión financiera:
actualizar, confirmar con fundamento o marcar revisión pendiente. Usa el mismo lote
para cambios relacionados en documentos y agenda; sus versiones son independientes.

## Ejemplo local ejecutable

Con workspace y runs proporcionados:
```python
from research_agent.advances import record_advance
from research_agent.state_tools import StateOperations
ops = StateOperations(workspace)
path = "empresas/ACME/modelo.md"
record_advance(workspace, runs, [
    dict(path=path, action="create", content="### H1 — Margen\nProvisional.\n",
         expected_sha256=None, operations=None)
], "Guardar hipótesis", [])
view = ops.read_company_document("ACME", "modelo", "Revisar H1", None, "H1", None, None)
record_advance(workspace, runs, [
    dict(path=path, action="edit", content=None, expected_sha256=view["sha256"],
         operations=[dict(kind="replace", target="Provisional.", content="Pendiente de contraste.")])
], "Precisar incertidumbre", [])
```
