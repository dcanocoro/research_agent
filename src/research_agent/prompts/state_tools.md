# Herramientas de estado

Inventario y búsqueda localizan conocimiento; `read_state` y `read_company_document`
entregan contenido y su `sha256`. Una lectura completa usa
`selector={"kind":"lines","start":1,"end":null}`. Para un ID de empresa usa
`identifier="H1", selector=null`; para líneas deja `identifier=null`. Las líneas
empiezan en 1 y los bytes en 0; una sección se selecciona por la línea del encabezado.
No releas por rutina índice o agenda ya disponibles ni un índice anunciado como
ausente. Cada consulta de estado exige un propósito breve.

Las continuaciones son opacas y vinculan argumentos y versión. Una vista parcial no
es el documento completo: sigue su continuación con el hash o amplía la selección.
`search_state` usa búsqueda literal; `context_lines=2` suele bastar. Los contratos
y ejemplos se consultan opcionalmente con `describe_state_tools`.

## Una sola escritura

`record_research_advance(changes, reason, source_refs)` guarda de uno a cinco archivos.
Cada cambio lleva path, action, content, expected_sha256 y operations. `reason` explica
brevemente el avance; `source_refs` conserva referencias exactas, sin certificar su uso.

Crear un archivo ausente:
```json
{"path":"notas.md","action":"create","content":"# Hallazgo\nProvisional.\n","expected_sha256":null,"operations":null}
```

Editar un fragmento usando el hash vigente de una lectura o recibo:
```json
{"path":"notas.md","action":"edit","content":null,"expected_sha256":"<sha256 vigente>","operations":[{"kind":"replace","target":"Provisional.","content":"Revisión pendiente: falta contraste."}]}
```

También puedes insertar con `insert_before` o `insert_after`; cada target debe aparecer
exactamente una vez. El target vacío solo es válido sobre un archivo vacío, para
inicializarlo con su versión vigente. Para actualizar un documento y retirar su pendiente de agenda,
incluye ambos cambios y sus versiones en el mismo lote. `agenda.md` ya existe en
experimentos deliberativos: edítala, no intentes crearla.

Se valida el lote antes de publicar; un rechazo previo no cambia archivos. Un fallo
de publicación restaura el conjunto; si la recuperación falla, el run se detiene.
No hay aislamiento frente a editores externos. Ante conflicto, relee y decide de nuevo.
Si el resultado indica `applied=true`, inspecciona lo guardado antes de reintentar,
incluso si falló la captura. Los recibos incluyen versiones y vistas acotadas.

Los documentos de empresa conservan IDs únicos y cuerpos antes poblados. No borres
ni reutilices IDs para eludir un rechazo. Son localizadores, no entidades; una
advertencia de referencia ausente puede señalar trabajo futuro. Usa la vista de
secciones afectadas y recupera lo omitido. Las garantías son estructurales, no
económicas. La metodología financiera determina las dependencias que debes revisar.
