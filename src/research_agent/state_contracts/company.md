# Expedientes — contrato state-tools-v6.1

Capa financiera fina sobre las primitivas de estado: no tiene almacén propio, LLM
oculto, acceso a BD, propagación económica ni sello de análisis completo. Comparte
los límites, versiones, rutas y errores del contrato de `read_state`/`edit_state`,
consultable con `describe_state_tools(tool="read_state")`.

`symbol` es un identificador ya resuelto por A: ASCII alfanumérico con puntos o guiones
interiores; respeta la escritura existente y rechaza colisiones de mayúsculas, nombres
reservados y rutas. `dimension` es modelo, valoracion o evaluacion. Solo opera en
`empresas/<symbol>/<dimension>.md`. Ausente significa no conservado, no no investigado.

- `inspect_company(symbol,purpose,cursor)`: devuelve dimensiones presentes/ausentes,
  versiones, encabezados ATX e IDs iniciales reconocibles (por ejemplo H1, V1).
  Informa IDs duplicados; no demuestra integridad semántica o ausencia de riesgos.
- `read_company_document(symbol,dimension,purpose,selector,identifier,expected_sha256,cursor)`:
  selector o identifier, exclusivamente uno; el otro null. Un ID requiere un único
  encabezado. Si está repetido o no se reconoce, usa líneas. La sección incluye sus
  subsecciones y las continuaciones requieren versión y selección originales.
- `update_company_document(symbol,dimension,purpose,action,content,expected_sha256,operations,reason,source_refs)`:
  action=create requiere content, expected_sha256=null y operations=null. action=edit
  requiere content=null, hash esperado y operaciones exactas. Motivo no vacío y lista
  explícita de referencias (puede ser vacía). Conserva IDs reconocidos y rechaza
  duplicados tanto al crear como al revisar. Rechaza vaciar el cuerpo recuperable de
  un ID previamente poblado, incluyendo cambios en la jerarquía de encabezados.
  Puede reparar IDs duplicados externos conservando una única aparición por ID.
  No puede comprobar si el significado de un ID ha cambiado.
  No crea las otras dimensiones ni modifica dependencias. Las referencias se conservan
  sin certificar su existencia, admisibilidad histórica o fundamento económico.

## Resultado recuperable V6

La escritura devuelve `changed_ids`, `validation` y `recovered_sections` con texto
original, selector de sección y marca `partial`. La vista usa exactamente los límites
ATX de `read_state`; incluye subsecciones. El hash superior identifica el resultado.
Hasta veinte IDs y referencias locales se muestran; campos `*_omitted` indican lo
no entregado. Usa `inspect_company` y `read_company_document` con el hash devuelto
para ampliar la vista. El límite serializado incluye todo el envoltorio.

`validation.empty_ids` informa encabezados nuevos o preexistentes sin cuerpo; no
obliga a rellenar campos. Una sección con solo encabezados y blancos no tiene cuerpo.
`unresolved_references` comprueba referencias literales `#ID` y
`empresas/SIMBOLO/dimension.md#ID`; estados missing_id, ambiguous_id o
unavailable_document son advertencias. Las referencias futuras son legítimas si A
las declara pendientes. `source_refs` se conserva sin validar: esta comprobación
no cubre citas abreviadas, URLs, unidades, inferencias ni pendientes obsoletos.

La misma política protege los escritores generales del workspace cuando se registran
las herramientas V5. No se permite usar un alias para saltarse estas comprobaciones.
No hay transacción entre archivos ni aislamiento frente a editores externos.

La respuesta de escritura distingue cambio aplicado y captura fallida. Lecturas y
mapas son paginables y versionados; el payload completo cabe en 32 KiB. No hay
transacciones multiarchivo. Para localizar consecuencias usa búsqueda literal por
ruta#ID, también fuera de la empresa. A decide qué revisar y redacta el pendiente.
Usa la fecha simulada para el significado financiero; los eventos conservan hora real.

## Ejemplo ejecutable con StateOperations

```python
from research_agent.state_tools import StateOperations
ops = StateOperations(workspace)
created = ops.update_company_document("ACME", "modelo", "Conservar hipótesis", "create", "### H1 — Margen\nSupuesto provisional.\n", None, None, "Inicio del modelo", [])
view = ops.read_company_document("ACME", "modelo", "Revisar H1", None, "H1", created["sha256"], None)
updated = ops.update_company_document("ACME", "modelo", "Revisar incertidumbre", "edit", None, view["sha256"], [{"kind": "replace", "target": "Supuesto provisional.", "content": "Supuesto pendiente de contraste; no confirmado."}], "Falta evidencia", [])
hits = ops.search_state(".", "empresas/ACME/modelo.md#H1", "Localizar consecuencias", 2, None)
```

Plantilla opcional: encabezado con ID estable; observación/fuentes; interpretación;
supuestos o cálculos; incertidumbre; condición de revisión; dependencias y pendientes.
No exige rellenar campos ni crear un expediente para una consulta breve.
