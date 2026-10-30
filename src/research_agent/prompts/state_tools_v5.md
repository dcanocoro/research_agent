# Herramientas de estado V5

Cuando estas herramientas estén disponibles, usa `inspect_state` o `inspect_company`
para orientarte y `read_state` o `read_company_document` para recuperar fundamentos.
Elige el selector conforme a tu propósito: las herramientas no seleccionan relevancia
económica por ti. Una consulta breve puede terminar sin crear archivos.

Prefiere `create_state` y `edit_state` para conservar contenido explícito. Para empresas,
`update_company_document` resuelve la dimensión sin crear las otras. Lee la versión
antes de editar y usa su `sha256`; ante conflicto, relee y decide de nuevo. Nunca reintentes
una edición a ciegas si el resultado dice `applied=true`, incluso si falló su captura.

Cada operación sustantiva exige un propósito breve, no una explicación extensa del
razonamiento. Los contratos y ejemplos se consultan opcionalmente mediante
`describe_state_tools`; puedes ejecutar directamente. Usa `null` en campos no aplicables.
Las continuaciones son opacas: conserva argumentos y versión. Una vista parcial no es
el documento completo; sigue la continuación o amplía la selección. Las búsquedas usan
dos líneas de contexto por defecto recomendado (`context_lines=2`), ampliables hasta ocho.

Para leer un documento completo usa `selector={"kind":"lines","start":1,"end":null}`;
en `read_company_document` deja `identifier=null`. Para recuperar H1 usa
`identifier="H1"` y `selector=null`. Nunca combines ambos. Las líneas empiezan en 1;
los bytes en 0; una sección empieza en la línea de su encabezado, no en el número del ID.
Si el contexto informa que `indice.md` no existe, usa inventario o expediente: no
repitas la lectura del índice ausente. `agenda.md` ya existe en experimentos deliberativos;
edítala con su versión, no intentes crearla de nuevo.

Las escrituras en documentos de empresa, incluidas las herramientas generales dentro
de esta composición, rechazan IDs duplicados, eliminados y secciones con contenido
que quedarían sin cuerpo recuperable. Devuelven secciones afectadas y advertencias
acotadas. Revisa esas vistas; sigue su indicación de recuperación si son parciales.
Una referencia local ausente puede representar trabajo futuro: es una advertencia,
no una revisión económica resuelta. No borres IDs para resolver un rechazo.

En expedientes separa observación, inferencia, supuesto, cálculo y juicio; conserva
contradicciones, fuentes, fechas, unidades y ausencias. Los campos de la metodología
financiera siguen siendo guías. No inventes datos para completar una plantilla.
Los IDs iniciales de encabezados (`### H1 — ...`) son localizadores, no entidades nuevas.
No cambies el significado de un ID ni lo reutilices para otra hipótesis.

Tras revisar H1, busca `empresas/<simbolo>/modelo.md#H1` con `search_state` dentro y
fuera de la empresa. Recupera las dependencias relevantes; revisa, confirma con fundamento
o redacta una revisión pendiente en el documento afectado. La búsqueda solo devuelve
candidatos textuales. Una escritura correcta no confirma coherencia ni calidad financiera.
En simulación expresa el significado de la revisión con la fecha simulada; el instante
real de los eventos es una dimensión distinta. Las fuentes previas no quedan validadas
históricamente por usar estas herramientas.


## Escritura conjunta V7

`record_research_advance(changes, reason, source_refs)` admite de uno a cinco archivos.
Cada cambio contiene path, action, content, expected_sha256 y operations.
Para create, content lleva el texto y expected_sha256/operations son null. Para edit,
content es null, expected_sha256 es la versión vigente y operations contiene ediciones
exactas replace/insert_before/insert_after, con target único y content.
Valida todo antes de publicar; devuelve files con versiones y fragmentos recuperables.
Un rechazo previo no modifica archivos. Ante fallo de publicación se restaura el conjunto;
un fallo de recuperación detiene el run. No hay aislamiento frente a editores externos.
No se comprueba automáticamente la validez económica de reason o source_refs.
