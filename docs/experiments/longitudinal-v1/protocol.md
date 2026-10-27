# Tres escenarios longitudinales — v1

Estado: escenarios preparados, sin ejecutar. Fecha: 2026-10-20.
Encargo limitado a generar las tres historias del documento aportado por el usuario.
No implementa M1/M2, variantes A0–A3, nuevos agentes, cambios de herramientas ni campaña.

## Catálogo

| Escenario | Definición | Rúbrica | Secuencia de seis sesiones |
|---|---|---|---|
| S1 ASML | [YAML](../../../campaigns/longitudinal-v1/S1/case.yaml) | [Revisión](../../../campaigns/longitudinal-v1/S1/rubric.md) | Inicio, priorización, dos consultas, contradicción, precio, recuperación. |
| S2 NVIDIA | [YAML](../../../campaigns/longitudinal-v1/S2/case.yaml) | [Revisión](../../../campaigns/longitudinal-v1/S2/rubric.md) | Inicio, ruido, hipótesis, deterioro, evidencia mixta, historia. |
| S3 Ford | [YAML](../../../campaigns/longitudinal-v1/S3/case.yaml) | [Revisión](../../../campaigns/longitudinal-v1/S3/rubric.md) | Inicio, perímetro, ausencia documental, nueva fecha, premisa falsa, cierre. |

La [suite](../../../campaigns/longitudinal-v1/suite.yaml) declara S1→S2→S3:
18 sesiones. El piloto anterior se conserva como antecedente separado; no se cambian
su catálogo ni sus capturas. Esta suite es la nueva propuesta para el encargo, sin
alterar por ello la estrategia general o aceptar mecanismos.

## Universo y decisiones de diseño

Todos los documentos, datos, precios, emisores auxiliares y acontecimientos son
sintéticos. Se usan nombres de empresas reales para delimitar problemas económicos;
ninguna cifra pretende describirlas actualmente. No se han buscado fuentes reales.
El reloj de las historias es 2030; los ejercicios son convencionales del benchmark,
incluido NVIDIA. No existe evidencia posterior a la sesión publicada en su estado.

Los primeros mensajes se mantienen abiertos. El contexto solo delimita universo,
fuentes y continuidad; no añade disciplinas M1/M2 ni una plantilla de expediente.
La base ofrece información suficiente para iniciar y deja lagunas explícitas. Las
conclusiones esperadas son propiedades del razonamiento, no una postura bursátil única.
La investigación es selección, lectura y contraste dentro del corpus; esta versión
no mide descubrimiento autónomo en la web ni cobertura de documentos financieros reales.

Cada caso dispone de sus propios archivos. La publicación se fija en cada `case.yaml`:
solo entran los documentos de esa sesión y los anteriores. La rúbrica y documentos
futuros no se publican al agente. En ASML 03 se publican catálogo y seis opciones;
leer el catálogo no consume consulta, abrir o buscar contenido de cada opción distinta
sí consume una de las dos. Se evalúa por trayectoria, no por declaración del agente.
Lecturas de memoria, índice y base anterior no consumen ese cupo documental.

En Ford 03 se inyecta una constancia de indisponibilidad y una alternativa limitada.
No se fabrica un evento técnico de herramienta: recuperación ante fallos de transporte
queda fuera de observación. Las fechas de publicación y corte separan lo conocido en
cada momento. Ford mantiene el horizonte original hasta 2031-12-31 incluso después
de publicar el corte de junio.

## Compatibilidad y límites operativos

Se reutiliza `benchmark-v1`, sin campos nuevos ni cambios de código. El controlador
existente inicia procesos independientes por sesión, continúa archivos sin chat y
conserva respuesta, herramientas y estados para revisión. Véase el
[protocolo del controlador](../benchmark-pilot-v1/protocol.md) y la
[operación](../../development.md#campañas).

El corpus queda fijado en archivos versionables; el runner congela los referenciados
al preparar una campaña. Esto NO desactiva herramientas remotas: la restricción de
corpus y el máximo de dos consultas son instrucciones de tarea, sin enforcement en el
runner actual. Una futura ejecución deberá registrar cualquier uso externo como
contaminación/incumplimiento y no tratarla como comparación controlada válida.
No se resuelve esa limitación implementando mecanismos en este encargo.

Los límites técnicos actuales de A no cambian. No se ha elegido modelo, repetición,
presupuesto monetario ni condición experimental. El factorial de 72 ejecuciones del
documento adjunto es trabajo posterior; generar estos casos no lo prepara ni autoriza
operativamente. Antes de comparar condiciones habrá que fijar los prompts efectivos,
configuración, fuentes, límites y control de acceso equivalentes.

## Evaluación prevista, sin resultados

Las tres rúbricas fijan seis dimensiones: investigación, calidad del juicio, revisión,
memoria, incertidumbre y eficiencia. Se revisan por sesión, con criterios concretos,
referencias numéricas y fallos materiales. Usar observado/parcial/fallo/N/O y evidencia
recuperable, sin puntuación global ni pesos inventados. No exigir una recomendación
concreta; premiar límites justificados, no cambios de opinión o cantidad de fuentes.

Examinar estados intermedios junto a respuestas y trayectoria para distinguir guardado,
recuperación, fidelidad y uso. Si un proceso no entrega o la captura falla, conservarlo
y separar lo no observable de un fallo financiero. La rúbrica no se suministra al agente.
No hay juez automático, hallazgos, baseline ejecutado ni aceptación semántica.

## Verificación de preparación

Revisión estructural offline del catálogo, referencias locales y `git diff --check`.
No ejecutar `run`, la CLI del agente, modelos, web ni bases de datos para esta tarea.
La validación estructural no acredita que los escenarios discriminen mecanismos:
esa cuestión requiere una ejecución futura autorizada y revisión de evidencia.
