# Estado — contrato state-tools-v6.1

Propósito: localizar y editar texto explícito del workspace existente. `purpose` es una
frase breve no vacía; no concede permisos. Solo Markdown, JSON, TXT y CSV; máximo dos
niveles de carpetas. Se rechazan enlaces, junctions y escapes. `materiales/` es de solo
lectura. No hay inferencia semántica, resumen LLM ni ejecución financiera.

## Consultas

`describe_state_tools(tool)` recupera opcionalmente el contrato de una operación V5
del registro efectivo, incluida la propia descripción. Rechaza herramientas ausentes
en el perfil o fase. No requiere propósito ni es un paso previo obligatorio.

- `inspect_state(path, purpose, cursor)`: directorio → archivos con bytes/hash;
  archivo → versión y encabezados ATX con línea/offset/nivel/ID. No reconoce Setext
  ni encabezados dentro de código cercado. Títulos de más de 256 caracteres se marcan
  parciales; recuperar el original mediante líneas. `cursor=null` inicia la consulta.
- `read_state(path, purpose, selector, expected_sha256, cursor)`: selector cerrado
  `{kind,start,end}`. `bytes`: offsets UTF-8, cero inicial, fin exclusivo o null hasta
  final; no partir caracteres. `lines`: numeración desde uno, fin inclusivo o null.
  `section`: start es la línea de un encabezado, end=null; incluye subsecciones hasta
  el próximo encabezado de nivel igual o superior. La respuesta identifica la selección,
  bytes entregados, versión, encabezado de contexto y continuación. Primera llamada
  admite expected_sha256=null; continuación requiere el hash y mismos selectores.
- `search_state(path, query, purpose, context_lines, cursor)`: búsqueda literal sin
  distinguir mayúsculas, orden ruta/línea; context_lines=2 recomendado, rango 0..8.
  Máximo 50 coincidencias por página; el presupuesto puede reducirlo. Los contextos
  largos se marcan parciales y se recuperan por líneas con el hash entregado.

Los cursores son opacos y ligados a argumentos/versiones. Un cambio exige reiniciar.
La respuesta completa, con su envoltorio JSON, no excede 32 KiB. El resultado original
de cada llamada se archiva; `artifact_ref` se recupera con `read_artifact`, bajo la
misma identidad de workspace. No hay selección de campos JSON o filas de artefactos.

## Mutaciones

- `create_state(path, content, purpose)`: solo ruta ausente; rechaza colisión. Publicación
  exclusiva mediante enlace duro temporal en el mismo filesystem; un sistema que no
  lo soporte falla sin recurrir a sobrescritura. Tamaño máximo 128 KiB UTF-8.
- `edit_state(path, expected_sha256, operations, purpose)`: lista no vacía de
  `{kind,target,content}`. kind=`replace`, `insert_before` o `insert_after`.
  Cada target aparece exactamente una vez, contando solapamientos. Se aplican en orden
  en memoria; solo se publica si todas pasan y el documento resultante es válido.
  JSON se valida antes de guardar. Se conservan bytes ajenos, Unicode y CRLF.

La respuesta informa applied, hashes, número de operaciones y diff acotado; diff_partial
avisa del recorte. El diff no es un historial restaurable. No se conservan automáticamente
todas las versiones intermedias. La mutación se contabiliza antes de la captura posterior:
si esta falla, `applied=true` significa que debes inspeccionar la versión actual antes
de reintentar. Los errores incluyen version_conflict, ambiguous_target, invalid_selector,
invalid_cursor, continuation_changed o una excepción de ruta/formato/publicación.

Un bloqueo por raíz serializa escritores cooperantes del proceso, incluyendo las
escrituras antiguas; se vuelve a comprobar el hash antes de publicar. No es un CAS
universal frente a editores externos, ni transacción multiarchivo. Las herramientas
antiguas siguen disponibles y permiten reemplazo completo sin precondición de versión.

En composición V5/V6, todas las escrituras de `empresas/<simbolo>/{modelo,valoracion,evaluacion}.md`
pasan la validación de expediente, también `write_file`, `write_markdown`, `create_state`
y `edit_state`. Rechazan IDs duplicados o eliminados y pérdida del cuerpo de un ID
previamente poblado. El núcleo Workspace recibe esta política desde las herramientas;
Workspace sin esa composición y editores externos no la aplican. Ver el contrato de empresa.

## Ejemplo ejecutable con StateOperations

```python
from research_agent.state_tools import StateOperations
ops = StateOperations(workspace)
created = ops.create_state("notas.md", "# Observación\nMargen provisional.\n", "Conservar el límite")
read = ops.read_state("notas.md", "Recuperar el fundamento", {"kind": "lines", "start": 1, "end": None}, created["sha256"], None)
edited = ops.edit_state("notas.md", read["sha256"], [{"kind": "replace", "target": "provisional", "content": "pendiente de contraste"}], "Precisar la incertidumbre")
```

Disponibles durante investigación y consolidación, sin herramientas en revisión
periódica. La documentación es opcional; no se exige leerla antes de ejecutar.
