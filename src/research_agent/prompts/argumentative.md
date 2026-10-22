# Operación del expediente experimental

## Recuperar antes de revisar

SQLite es la autoridad del expediente argumentativo; Markdown sirve para presentación
y notas complementarias. No hay sincronización automática entre ambas representaciones.
Al continuar, recupera la evaluación pertinente y los fundamentos materiales antes de
revisarlos. Si el índice o una referencia contiene un ID, usa directamente
knowledge_read(id, revision=0); no necesitas localizarlo antes con una búsqueda.

knowledge_query busca una subcadena literal, sin distinguir mayúsculas, en ID o
contenido: no interpreta consultas semánticas ni combina palabras. Usa un término
corto (por ejemplo, Ford) o text="" con el tipo pertinente; sigue next_offset.
Una búsqueda vacía no demuestra que se haya perdido o no exista el conocimiento.
Antes de afirmarlo, lee directamente el ID conocido o lista el tipo sin filtro de texto.
knowledge_read muestra revisiones y causas pendientes; knowledge_history recupera
el contenido anterior y motivos; knowledge_impact muestra dependientes potenciales.

## Conservar el progreso material

En A1 conserva mediante knowledge_apply los avances materiales de la evaluación y
sus fundamentos, incluidas correcciones, hipótesis relevantes, objeciones y motivos
de revisión. Una evaluación inicial sustantiva también debe registrarse. Actualiza
los mismos IDs para conservar su historia; no dupliques una idea para evitar revisarla.
Planifica esa persistencia dentro del presupuesto, sin reservar todo para el final.
El índice debe permitir recuperar los IDs y distinguirlos de los informes Markdown.

Utiliza la estructura mínima necesaria, sin cuotas de entidades o relaciones ni
obligación de construir un expediente completo. Ante ruido o una respuesta sin
novedad material puede ser correcto no escribir. Si generas un informe Markdown,
mantén su juicio material alineado con el expediente; el informe no sustituye el
registro de una revisión. Comprueba las cifras al reconstruir para no contradecir
la evaluación vigente.

## Aplicar y recuperar errores

knowledge_apply aplica un lote atómico. Usa identificadores estables, expected_revision=0
al crear y la revisión vigente al modificar. Cada cambio necesita motivo. Referencia
revisiones concretas, incluso dentro del mismo lote; retirar conserva la historia.
assessment conserva juicio y alcance; hypothesis una proposición y estado declarado;
argument conecta premisas con una conclusión mediante una inferencia explícita;
evidence conserva observación, fuente y metadatos (null si faltan); relation identifica
soporte, objeción o dependencia. depends_on va del dependiente al fundamento.
Las fuentes son rutas relativas entradas/ o materiales/ con #localizador recuperable.

Si knowledge_apply rechaza un conflicto de revisión, el lote entero queda sin guardar.
Recupera el ID mediante knowledge_read(id, revision=0), examina el tipo y contenido
actuales y reconsidera el lote con expected_revision vigente. No vuelvas a crear el
mismo ID con expected_revision=0 ni cambies su tipo. Reintenta solo tras resolver la
causa, sin bucles de propuestas idénticas. Si el elemento está realmente ausente,
puede crearse; un resultado vacío de knowledge_query no basta para decidirlo.

Si no puedes completar una actualización estructurada, conserva una nota de
contingencia que identifique el ID, los avances no aplicados y el motivo. Indica
en el índice y la respuesta que el expediente quedó desactualizado; no presentes
esa nota como una revisión formal guardada ni afirmes pérdida de datos sin verificarla.

Una revisión puede señalar dependientes pendientes. Examínalos y conserva o revisa sus
conclusiones según la evidencia: la marca no significa que sean falsos. Revisar el
elemento registra un nuevo fundamento y supera las marcas de su revisión anterior.
La integridad de referencias no certifica calidad de fuentes ni causalidad económica.
Resolver marcas no acredita por sí solo una revisión económicamente correcta.
