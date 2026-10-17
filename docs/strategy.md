# Estrategia de investigación

> Agenda de referencia a 2026-10-17, sintetizada de los documentos aportados por el usuario.
> Orienta próximos encargos; no autoriza por sí sola implementaciones o migraciones.

## Prioridad actual

**Contrastar un primer expediente mínimo sobre la arqueología disponible.** El
[mapa conceptual](finmate-concept-model/modelo-conocimiento-actual.md) y su
[anexo](finmate-concept-model/estructuras-y-campos.md) reconstruyen el corte de FinMate
que se toma como referencia. El usuario ha autorizado implementar y explorar el
candidato [E001](experiments/E001-nvidia-casefile/protocol.md): Markdown versionado,
metadatos mínimos y cuatro herramientas, con investigación y continuación de NVIDIA.
Es una elección experimental local, no una arquitectura final ni una aceptación
semántica general de toda la arqueología. Las variantes A0–A3 siguen siendo posteriores.

El punto de partida es distinguir cuatro preguntas:

| Perspectiva | Pregunta | Ejemplo |
|---|---|---|
| Modelo conceptual | ¿Qué significa y qué relaciones necesita el conocimiento? | Evaluación, fundamento y condición de revisión |
| Representación y persistencia | ¿Cómo se identifica, valida, conserva y recupera? | Markdown, JSON, tablas, grafos o combinación |
| Transiciones | ¿Cómo se investiga y modifica ese estado? | Un agente propone una revisión y se valida su aplicación |
| Presentación | ¿Cómo lo entiende y utiliza una persona? | Vista de evaluación vigente y cambios desde la anterior |

Diseñar desde el estado no obliga a crear cuatro subsistemas. Las vistas y las
operaciones sirven para contrastar el modelo desde el principio. Una card no define
por sí sola una entidad; un operador existente tampoco prueba que su entrada deba
conservarse como concepto independiente.

## Secuencia y criterios de avance

| Fase | Trabajo mínimo | Evidencia para decidir el siguiente paso |
|---|---|---|
| 1. Reconstruir el modelo actual | Conceptos, relaciones, ciclos de vida y consumidores, con referencias al código | Revisión humana de la fidelidad del mapa y de los problemas identificados |
| 2. Formular alternativas | Modelos narrativo, argumentativo y financiero-argumentativo como candidatos, con los mismos ejemplos | Selección de conceptos y preguntas que merecen comparación |
| 3. Contrastar operaciones | Construir, incorporar evidencia, contradecir, revisar, recuperar historia y producir vistas | Hallazgos sobre capacidades, pérdidas y complejidad; selección de un candidato provisional |
| 4. Probar representación física | Implementación mínima de las opciones que el candidato necesite | Lectura, edición, validación, historial y recuperación comprobados con coste conocido |
| 5. Estudiar transiciones | Conectar A y comparar disciplinas de investigación y revisión | Campañas longitudinales con integridad y calidad evaluadas por separado |
| 6. Reconstruir progresivamente | Adaptar ejecución, persistencia y presentación por capacidades | Comprobación y reversión de cada sustitución antes de ampliar el alcance |

Las fases admiten retroalimentación. No requieren implementar todas las alternativas
ni una reescritura completa. La elección de un modelo o una sustitución material
requiere decisión humana; los prototipos y campañas necesitan un encargo concreto.

## Referencia del encargo de arqueología

Partir del [mapa de referencias](finmate-references.md) y seguir productores,
persistencia y consumidores reales. Estudiar usuario e intenciones; empresa y
expediente; tesis, hipótesis, argumentos y evidencia; evaluaciones y valoraciones;
necesidades e intentos de investigación; decisiones, posiciones e historia.
Son áreas a investigar, no un inventario confirmado de entidades obligatorias.

Para cada concepto, documentar significado, identidad, relaciones, ciclo de vida,
quién lo crea o modifica, dónde se guarda y quién lo consume. Acompañarlo de un
ejemplo recuperable y referencias verificables al código. Señalar ausencias y
definiciones ambiguas, especialmente entre tesis, hipótesis, argumento y evaluación.

Seguir un recorrido concreto desde una intención hasta una investigación, evidencia,
evaluación persistida y revisión posterior, hasta donde exista. Examinar también qué
leen las vistas y acciones. Identificar duplicaciones, pérdidas de contexto y qué
estados anteriores se pueden reconstruir realmente; un hash no conserva su contenido.

El encargo de referencia cubre tres piezas, reunidas en la arqueología enlazada:

- Modelo actual: conceptos y relaciones, con evidencia de implementación.
- Mapa de ciclos de vida: diagramas y ejemplos de lectura, modificación y consumo.
- Diagnóstico: problemas observados, garantías que protegen los mecanismos e hipótesis
  de simplificación. Clasificar algo como prescindible no autoriza eliminarlo.

Cerrar con incertidumbres y comparaciones propuestas. La revisión humana confirma
que el mapa describe fielmente el sistema antes de seleccionar alternativas.
No se realiza aquí ese análisis ni se modifica FinMate.

E001 se ha ejecutado: sus [hallazgos](experiments/E001-nvidia-casefile/findings.md)
registran ausencia de guardado en ambos procesos y truncamiento del primer cierre.
El siguiente contraste propuesto estudia cuándo persistir, antes de añadir entidades;
no se ha ejecutado ni implica autorización para modificar la política silenciosamente.

## Cómo usar los antecedentes

Los textos históricos aportados recuerdan riesgos útiles: coordinar más no garantiza
mejor análisis; una mejora local puede impedir la entrega por coste o timeout; una
referencia válida no prueba una inferencia; memoria útil, historial y trazas cumplen
funciones distintas. También señalan que autonomía e integridad necesitan evaluarse
por separado, y que una agregación de argumentos no es una probabilidad calibrada.

Son pistas para buscar evidencia. Los recuentos de campañas, explicaciones causales
y resultados recordados no se adoptan como hallazgos locales sin localizar revisión,
configuración, artefactos y límites originales. El mapa histórico de FinMate facilita
la búsqueda; el código y los registros fechados determinan qué puede afirmarse.

## Criterio para elegir mecanismos

Antes de añadir o retirar estructura, explicar qué operación o garantía permite,
qué fallo evita, qué alternativa más sencilla existe y cómo medir beneficio y coste.
Comparar actualizaciones longitudinales y recuperación, además del ejemplo inicial.
La ausencia de una necesidad multiusuario en A no demuestra que desaparezca del producto.

Las preguntas abiertas incluyen qué necesita identidad e historial, cuánto texto libre
es suficiente, qué estructura financiera aporta valor y qué responsabilidades deberán
asumir el agente y la aplicación. Conservar los hallazgos en el
[registro experimental](experiments/README.md) y las elecciones duraderas en
[decisiones](decisions/README.md). No convertir un resultado en una decisión implícita.
