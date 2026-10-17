# Experimentos y evaluación

> Metodología y líneas de contraste. Revisión: 2026-10-17.
> La prioridad está en estrategia; protocolos y resultados se registran por separado.

## Qué comparar primero

La [estrategia](strategy.md) comienza por reconstruir el modelo conceptual de FinMate.
Después se compararán candidatos narrativo, argumentativo y financiero-argumentativo
con los mismos ejemplos y operaciones. Son familias propuestas de representación del
conocimiento, no variantes de A implementadas ni tres sistemas que debamos construir.

El primer contraste puede hacerse con expedientes de ejemplo y transiciones manuales
o procedimientos pequeños, antes de conectar un LLM. No evaluarlo solo por su aspecto:
probar construcción, incorporación de evidencia, contradicción, revisión longitudinal,
coexistencia de tesis y recuperación histórica. Las vistas y un caso de decisión de
cartera sirven como pruebas conceptuales de información necesaria; no requieren
implementar interfaz, cartera u órdenes en el laboratorio.

| Dimensión | Observación que buscar |
|---|---|
| Expresividad y simplicidad | Qué se representa y qué abstracciones exige |
| Continuidad y trazabilidad | Si se recuperan fundamentos y estados anteriores sin redescubrirlos |
| Actualización | Si una revisión corrige lo afectado y conserva contradicciones e incertidumbres |
| Utilidad para agente y usuario | Si se puede leer, modificar y derivar una vista comprensible |
| Calidad financiera y coste | Si conecta evidencia con consecuencias económicas y qué recursos consume |

La estructura que facilita registrar una evaluación no demuestra que esa evaluación
sea correcta. Las disciplinas de razonamiento y la representación física son factores
posteriores que deben aislarse. El [registro experimental](experiments/README.md)
define cómo fijar cada protocolo y conservar hallazgos, fallos y límites.

## Qué podemos ejecutar hoy

El directorio [scenarios](../scenarios) contiene investigación de empresa, comparación
de periodos, continuidad de memoria, fallo documental y agotamiento de recursos.
Sus YAML fijan mensajes y checks, pero los escenarios que usan fuentes remotas no
congelan automáticamente PostgreSQL ni la web. Los casos sintéticos se identifican.

Experience Audit ejecuta mensajes secuenciales con una instancia por escenario y un
workspace aislado. Conserva definiciones, intervenciones, resultados y evidencia.
Los checks mecánicos comprueban ejecución, texto, uso de herramienta o archivos;
no evalúan por sí solos la veracidad o calidad financiera.

La [operación](development.md) describe contrato, comandos y consulta. Este documento
posee el diseño experimental, no el funcionamiento del runner.

## Pregunta central

¿Qué mecanismos ayudan a obtener una investigación material, fundada y revisable,
y cuáles añaden coste o rigidez sin mejora demostrable? Una respuesta favorable al
agente simple no refutaría todas las estructuras de FinMate; una respuesta ordenada
de FinMate tampoco demostraría su superioridad. Comparar mecanismos identificables.

La hipótesis de [propósito](purpose.md) propone probar más estructura en el conocimiento
retenido antes de imponer una secuencia rígida de ejecución. Argumentar puede ayudar
a razonar o a representar la conclusión: son intervenciones distintas.

## Línea posterior: matriz de instrucciones

| Variante propuesta | Argumentación explícita obligatoria | Guía financiera específica |
|---|---|---|
| A0 autónomo | No | No |
| A1 argumentativo | Sí | No |
| A2 financiero y argumentativo | Sí | Sí |
| A3 financiero | No | Sí |

Son cuatro condiciones experimentales del mismo agente, no cuatro agentes que
colaboran. No existen selectores A0–A3 implementados. Hoy CLI y Audit añaden la guía
financiera básica; `--instructions` agrega instrucciones, no las reemplaza. La ejecución
actual no equivale a A0, ni la guía ligera representa necesariamente el tratamiento
financiero completo propuesto para A2/A3.

Para comparar, habría que definir textos exactos, selección mutuamente excluyente y
captura de la condición efectiva. Mantener iguales herramientas, modelo, datos,
presupuesto y tarea. No añadir simultáneamente expediente, políticas y nuevos cálculos:
no podríamos atribuir la diferencia. Esta documentación no implementa esos cambios.

Esta matriz estudia instrucciones. No confundirla con las familias de modelos de
conocimiento: son factores distintos, que conviene estudiar por separado.

## Ejemplo de representación por contrastar

No hay schema o carpeta de casos obligatoria en A. Una convención a probar sería:

```text
workspace/cases/nvidia/
  assessment.md   evaluación vigente, fundamentos, incertidumbres y revisión
  research.md     investigación, hipótesis, argumentos, objeciones y cálculos
  sources.md      fuentes consultadas/usadas y referencias recuperables
```

`assessment.md` respondería a la pregunta actual y distinguiría lo que sabemos de lo
que suponemos. Puede incluir escenarios o relación con el precio si existe soporte;
no debe fabricar valoración porque haya un apartado. No hay DCF implementado.
`research.md` conserva el fundamento que permite revisar la conclusión; `sources.md`
permite rastrearlo. Referenciar una fuente no prueba que se haya leído o usado bien.
El índice de memoria apuntaría a esos archivos en vez de cargar todo automáticamente.

Primero probar la utilidad de la convención con las herramientas actuales. Solo
formalizar contratos adicionales si permite una mejora observable de recuperación,
revisión o validación. Una consulta breve no tiene por qué producir un expediente.

## Recorrido longitudinal para un protocolo futuro

1. Proporcionar un conjunto fechado de datos y documentos. Pedir una evaluación inicial
   con fundamentos, límites y una incertidumbre material para la pregunta.
2. Pedir que elija una siguiente investigación y explique qué resultado cambiaría su
   evaluación. Distinguir relevancia económica de mera falta de evidencia.
3. Introducir evidencia nueva, incluida evidencia contradictoria o periodos incompatibles.
   Pedir revisión de fundamentos, escenarios y conclusión hasta donde permitan los datos.
4. Comprobar qué memoria consultó, qué corrigió, qué mantuvo y por qué. Evaluar también
   la entrega final y la siguiente acción propuesta, conservando el estado anterior.

Las hipótesis relevantes son económicas: demanda, márgenes sostenibles, competencia,
reinversión, caja, riesgo o precio. Contar argumentos a favor/en contra de comprar no
sustituye conectar esos mecanismos con sus consecuencias y la incertidumbre.

## Controles y rúbrica antes de ejecutar

- Congelar mensajes, instrucciones, herramientas, límites, configuración y condición;
  conservar revisión y hashes de código, schemas y wheel compartido.
- Para comparación controlada, usar transportes/documentos/datos congelados. Si se usan
  proveedores reales, archivar resultados exactos, fecha y limitaciones; registrar que
  el entorno externo puede variar. Repetir varias tentativas, sin descartar las fallidas.
- Iniciar cada condición con memoria idéntica y workspace distinto. Solo compartir
  memoria entre intervenciones que formen parte explícita del mismo caso longitudinal.
- Aplicar una rúbrica previa: fundamento, distinción de hechos/supuestos, materialidad,
  fidelidad numérica, incertidumbre, revisión ante contradicción, entrega y siguiente acción.
- Registrar tiempo, llamadas, errores y coste solo cuando sea observable; desconocido
  permanece desconocido. Valorar ganancia marginal frente a recursos y evidencia previa.

Separar en el informe: estado operativo, checks mecánicos, juicio semántico y límites
de captura. Una respuesta calibrada puede concluir insuficiencia; cambiar de opinión
no es automáticamente aprender, ni mantenerla automáticamente fallar. Mayor longitud,
más fuentes o más argumentos no son métricas suficientes de progreso.

## Qué conclusiones permitiría

Un experimento puede evidenciar mejor razonamiento o revisión en esas condiciones.
La calidad de una decisión exige además alternativas, precio, riesgo y contexto del
usuario; el agente actual no administra cartera. Rentabilidad superior requiere otra
evaluación: muchas decisiones, tiempo, benchmarks, costes, control de riesgo y ausencia
de información futura. No inferirla de una campaña local o un dossier coherente.

El siguiente paso de investigación es el análisis conceptual definido en
[estrategia](strategy.md). Sus resultados permitirán elegir una comparación y fijar
su protocolo y rúbrica antes de implementar los mecanismos mínimos. No hay aquí
autorización implícita para construir toda la agenda.
