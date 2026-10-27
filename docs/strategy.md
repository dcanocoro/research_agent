# Estrategia de investigación

> Agenda revisada el 2026-10-25 con el encargo de metodología financiera aceptado por el usuario.
> Orienta próximos encargos; no autoriza por sí sola implementaciones o migraciones.

## Encargo vigente: bucle continuo con contexto acotado

El 2026-10-26 el usuario aprobó implementar el [modo continuo](experiments/contexto-continuo-v1/protocol.md)
de A con mandato persistente, presupuesto local inicialmente en tokens y reconstrucción desde archivos.
El primer contraste mantiene fija la fecha simulada y no cambia el calendario longitudinal.
El alcance es implementación y verificación local con clientes simulados; no autoriza
proveedores ni campañas reales. La conservación semántica y la selección de trabajo siguen
pendientes de observar. No elige arquitectura definitiva para FinMate.

El encargo posterior del 2026-10-26 sustituye el tokenizer por tamaño UTF-8 y prepara
un piloto manual con mandato, dataset local congelado, rúbrica y límites. Autoriza
implementación y preparación local. El piloto se ejecutó posteriormente de forma manual.
Tras revisar sus resultados, el usuario autorizó el 2026-10-26 corregir la entrega de
resultados al cruzar el umbral y repetir la campaña con las mismas entradas y estado
nuevo. El [protocolo](experiments/contexto-continuo-v1/protocol.md) conserva el contraste;
ambos intentos alcanzaron 60 llamadas y seis renovaciones. Los
[hallazgos](experiments/contexto-continuo-v1/findings.md) confirman la desaparición de la
redirección adicional de lecturas, con continuidad parcial y problemas de revisión entre
documentos. No se autoriza por ello una ejecución indefinida ni aceptación semántica.

## Antecedente: metodología financiera longitudinal

El 2026-10-25 el usuario aprobó integrar una metodología financiera y una convención
mínima de conocimiento por empresa en los prompts por defecto. El
[protocolo](experiments/analisis-financiero-v1/protocol.md) conserva el contraste frente
al deliberativo anterior, con control congelado, misma base técnica y estados nuevos.
El alcance incluye implementación y comprobaciones locales sin proveedores; no autoriza
campañas ni pruebas con LLM real. La aceptación semántica queda pendiente. La metodología
y la representación se contrastan juntas, sin elegir arquitectura para FinMate.

## Antecedente: intención persistente

El usuario aprobó preparar la [condición de intención persistente](experiments/intencion-persistente-v1/protocol.md)
con mandato auténtico, agenda automática y disciplina de continuidad sobre A. La
[decisión experimental](decisions/0003-intencion-persistente.md) conserva el alcance:
implementación y comprobaciones locales, sin ejecutar proveedores ni la campaña real.
El piloto comparará seis activaciones por condición con datos congelados y web viva;
su utilidad semántica sigue pendiente. No se elige la arquitectura final de FinMate.

Posteriormente el usuario autorizó ejecutar con 60 llamadas y 20 minutos por activación.
Ambas condiciones completaron seis activaciones; los [hallazgos preliminares](experiments/intencion-persistente-v1/findings-amplio.md)
registran continuidad del contexto y cierres autónomos, sin demostrar progreso superior.
El escenario de 18 llamadas no se ejecutó. La siguiente revisión debe valorar el trabajo
pendiente y sus bloqueos antes de atribuir la limitación a falta de recursos.

## Antecedente: colaboración longitudinal

Actualizado el 2026-10-24 por aprobación explícita del plan del usuario. Construir
el entorno longitudinal de 50 empresas y hasta 10 posiciones para observar memoria,
revisión e iniciativa. Se acepta disponibilidad anual estimada de 120 días naturales,
sin atribuir resultados de alfa. El [protocolo](experiments/colaboracion-historica-v1/protocol.md)
y la [decisión](decisions/0002-simulacion-longitudinal.md) conservan el alcance.
La [revisión de precios](experiments/colaboracion-historica-v1/price-review.md) habilita
el dataset ajustado con las excepciones declaradas. La prueba corta histórica real
está completada; también se completaron las 24 activaciones de dos años. El
[informe local](../artifacts/campana-historica-completa-v1/informe-ejecucion.md),
ignorado y no portable, documenta continuidad, pérdida parcial del mandato y contaminación
temporal web; no prueba alfa. Ese encargo no incorporó mecanismos cognitivos ni evaluador. El baseline anterior y los
antecedentes siguientes no se reescriben como resultados de este encargo.

## Prioridad anterior y antecedentes

**Contrastar conservación y continuidad con un estado de archivos por experimento.**
El [baseline acordado](baseline.md), basado en el plan aceptado el 2026-10-18, sustituye el almacén de expedientes por un único estado
editable, materiales automáticos, instrucciones separadas y archivo por run. Git es
manual; una prueba puede empezar vacía o continuar su propio estado. La
[decisión local](decisions/0001-estado-por-experimento.md) y la
[arquitectura](architecture.md) fijan el alcance. No se elige la arquitectura final
ni se aceptan semánticamente las evaluaciones por este cambio de representación.

El [mapa conceptual](finmate-concept-model/modelo-conocimiento-actual.md) y su
[anexo](finmate-concept-model/estructuras-y-campos.md) siguen como referencia.
[E001](experiments/README.md#antecedentes-e001-y-e002) y
[E002](experiments/README.md#antecedentes-e001-y-e002) conservan los resultados del
candidato anterior. La nueva representación tiene verificación local controlada y
una ejecución real de NVIDIA con [hallazgos retrospectivos](experiments/baseline-nvidia-2026-10-18/findings.md).
No se ha ejecutado una comparación controlada ni una continuación real de ese estado;
la revisión ante contradicción sigue sin observarse.
Las variantes A0–A3 siguen siendo posteriores.

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

E001 se ha ejecutado: sus [hallazgos](experiments/README.md#antecedentes-e001-y-e002)
registran ausencia de guardado en ambos procesos y truncamiento del primer cierre.
E002 se ha ejecutado: sus [hallazgos](experiments/README.md#antecedentes-e001-y-e002)
registran dos revisiones y recuperación tras reiniciar, con consolidación incompleta.
El plazo de consolidación se corrigió después y solo tiene comprobación local. La
representación nueva conserva esa corrección, pero elimina la publicación obligatoria.
El siguiente contraste deberá evaluar consolidación y recuperación con archivos,
sin presentar los resultados de E002 como evidencia del mecanismo nuevo. No se ha
repetido E002. El run nuevo de NVIDIA es una observación del baseline de archivos,
no una repetición comparable de E002 ni una campaña controlada.

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
