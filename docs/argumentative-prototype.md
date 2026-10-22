# Expediente argumentativo experimental

Implementación local desde 2026-10-22, optativa y sin aceptación financiera.
El modo Markdown sigue siendo el predeterminado. El contrato de archivos de ADR-0001
se conserva para ese modo; el encargo del prototipo introduce una excepción
experimental en A1, sin elegir la arquitectura final de FinMate.

## Estado y autoridad

```text
experimento/
  experimento.json                  # modo y perfil fijados al crear
  instrucciones/expediente.md       # solo A1; instrucciones operativas
  estado/                          # Markdown, fuentes publicadas y materiales
  conocimiento/expediente.sqlite    # autoridad del expediente A1
  ejecuciones/<run>/                # respuesta, trazas y capturas
```

`KnowledgeStore`, en `src/research_agent/knowledge.py`, posee tablas de revisiones y
causas de impacto. Usa `sqlite3`, sin wheel nuevo ni cambios de Findata/FinMate.
Cada operación abre y cierra su conexión. Cada lote usa transacción inmediata y
rollback completo ante rechazo. Las revisiones son inmutables y tienen identidad,
versión, tipo, retirada, motivo, nombre del run y fecha UTC. La versión del schema
es 1; no hay migración/importación del antiguo CaseStore ni conversión de Markdown.

Los tipos son `assessment`, `hypothesis`, `argument`, `evidence` y `relation`.
Una referencia identifica `{id, revision}`. Argumentos conservan premisas, inferencia
y conclusión (hipótesis/evaluación); relaciones conectan elementos mediante
`supports`, `objects` o `depends_on`. Esta última va del dependiente al fundamento.
Evidencia exige observación, fuente relativa con `#localizador` y metadatos
fecha/periodo/moneda/unidades (null cuando falten). Solo admite fuentes existentes
en `entradas/` o `materiales/`; comprueba localización del archivo, no la verdad del
pasaje ni que el localizador sea semánticamente correcto.

## Herramientas y revisión

| Herramienta | Entradas y resultado |
|---|---|
| `knowledge_query` | `kind` (vacío=todos), `text`, `offset`, `limit`; elementos actuales no retirados y `next_offset`. |
| `knowledge_read` | `id`, `revision` (0=actual); revisión y causas pendientes para ella. |
| `knowledge_history` | `id`, `offset`, `limit`; revisiones en orden ascendente y `next_offset`. |
| `knowledge_impact` | `id`; dependientes potencialmente afectados, sin modificar conclusiones. |
| `knowledge_apply` | `changes`, hasta 50; cada cambio contiene `id`, `kind`, `expected_revision`, `retired`, `reason`, `data`. Devuelve revisiones creadas y pendientes. |

Reparación del 2026-10-22: query busca una subcadena literal tanto en ID como en
contenido, sin distinguir mayúsculas; no combina palabras ni hace búsqueda semántica.
Para un ID conocido, usar read directamente con revision=0; text vacío lista el tipo.
Un conflicto indica la versión actual y pide recuperarla antes de reconsiderar el
lote, sin reintento automático. Los datos y schemas de argumentos son compatibles.

El prompt operativo de A1 exige conservar avances materiales (incluida evaluación
inicial) y fundamentos con estructura mínima. Markdown es presentación o notas. Si
no se completa una actualización, el agente debe señalar en índice y respuesta qué
ID quedó desactualizado y qué falta aplicar; no presenta la nota de contingencia
como una revisión formal. Es disciplina instruida, no validación semántica del runtime.

Al crear, `expected_revision=0`; al revisar se exige la versión vigente. El lote puede
referenciar elementos creados dentro del mismo lote. Conserva referencias a revisiones
históricas; si se utiliza un fundamento superado, queda pendiente de revisión. No
admite cambios de tipo, referencias inexistentes o nuevas referencias a retirados.
Las retiradas mantienen versiones anteriores y propagan impacto por los caminos previos.
Retirar exige repetir el contenido anterior: no permite reescribirlo al darlo de baja.

Se rechazan ciclos de fundamentación (premisas→argumento→conclusión, referencias y
dependencias). Soporte y objeción son relaciones de debate: pueden coexistir y no
certifican una inferencia. Se usan también para señalar impactos potenciales.
Actualizar un fundamento conserva las conclusiones dependientes y registra causas
para sus revisiones actuales. Revisar un elemento supera sus marcas antiguas;
no demuestra que el agente las haya resuelto bien. Los lotes conservan marcas
conservadoras si cambian simultáneamente fundamento y dependiente: revisar después
de examinar el resultado, sin afirmar consistencia semántica por un commit exitoso.
Actualizar solo las revisiones referenciadas de una relación ya revisada no vuelve
a invalidar automáticamente su conclusión; evita un ciclo de marcas puramente contable.

Los adaptadores son asíncronos sin awaits internos: validación y commit terminan
sin delegar un escritor a threads. La cancelación puede preceder al lote o llegar
después de su commit, sin dejar escrituras pendientes tras cerrar. Siguen sujetos
al tamaño máximo del lote y al bloqueo SQLite; no son un motor lógico ni un sandbox
contra otros procesos que accedan directamente al disco.

## Captura y recuperación

Cada snapshot de A1 añade `conocimiento-inicial.sqlite`/`conocimiento-final.sqlite`,
sus exportaciones JSON y sendos `conocimiento-*-hashes.json`. La exportación lógica
incluye revisiones y causas de impacto, con texto UTF-8 y orden estable. El backup
SQLite y la exportación se toman sobre la misma copia consistente. No se cargan en
el contexto del modelo: la recuperación requiere las herramientas del expediente.

`verify_capture(run)` verifica hashes, integridad SQLite y equivalencia lógica, en
solo lectura. Para inspeccionar, abrir una copia SQLite con `mode=ro` o el JSON.
Para recuperar el estado en otro experimento, usar la copia verificada; no hay
comando de restauración automática ni sustitución de un experimento en marcha.
La compacción conserva estas capturas y sus hashes; una captura incompleta retiene
los ficheros nativos. El perfil Markdown conserva su formato y sus lectores históricos.

El [protocolo](experiments/longitudinal-v2/protocol.md) posee el contraste y las rúbricas.
