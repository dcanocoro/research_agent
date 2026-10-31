# Experimentos y evaluación

> Metodología y líneas de contraste. Revisión: 2026-10-18.
> La prioridad está en estrategia; protocolos y resultados se registran por separado.

## Qué comparar primero

El [baseline vigente](baseline.md) es A con estado de archivos por experimento,
materiales automáticos y consolidación sin publicación obligatoria. La ejecución de
NVIDIA del 2026-10-18 tiene un [registro retrospectivo](experiments/baseline-nvidia-2026-10-18/findings.md).
Es una observación exploratoria sin control ni rúbrica fijada antes de ejecutarla;
no prueba superioridad, continuidad semántica ni rentabilidad.

La [arqueología](finmate-concept-model/modelo-conocimiento-actual.md) caracteriza un
corte histórico de FinMate. E001/E002 son [antecedentes](experiments/README.md#antecedentes-e001-y-e002)
del modo de expedientes retirado. Los siguientes encargos podrán contrastar
conservación, interpretación y revisión sobre materiales controlados, cambiando un
factor cada vez. Las familias narrativa, argumentativa y financiero-argumentativa
son candidatos por comparar, no variantes implementadas ni sistemas que debamos construir.

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

La [suite longitudinal v1](experiments/longitudinal-v1/protocol.md) define tres nuevas
historias (ASML, NVIDIA y Ford), con seis sesiones cada una, corpus sintético publicado
por etapas y rúbricas previas. Está generada, sin ejecutar ni implementar M1/M2.
El piloto anterior se conserva en Git; las restricciones de la suite de corpus y consultas son declaradas,
no límites técnicos impuestos por el controlador.

El [benchmark piloto v1 histórico](experiments/benchmark-pilot-v1/protocol.md) definió cuatro casos
con sesiones en procesos nuevos, entradas publicadas entre sesiones y herramientas
reales. Su controlador prepara archivos, invoca la CLI y recoge evidencia; no cambia
el ciclo de A ni usa jueces automáticos. Tiene verificación local con servicios
simulados, sin campaña real. Web y PostgreSQL siguen siendo variables externas.

Las campañas actuales usan `python -m research_campaigns`, separado del núcleo,
con las definiciones de `campaigns/`. La integración local con Experience Audit y
sus escenarios se retiraron el 2026-10-24. Los checks mecánicos no evalúan por sí
solos la veracidad o calidad financiera.

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
colaboran. No existen selectores A0–A3 implementados. Hoy la CLI añade la guía
financiera básica. En CLI, `--instructions` añade archivos solo con `--new`; las
continuaciones utilizan las copias de `instrucciones/`, que pueden editarse explícitamente.
La ejecución
actual no equivale a A0, ni la guía ligera representa necesariamente el tratamiento
financiero completo propuesto para A2/A3.

Para comparar, habría que definir textos exactos, selección mutuamente excluyente y
captura de la condición efectiva. Mantener iguales herramientas, modelo, datos,
presupuesto y tarea. No añadir simultáneamente expediente, políticas y nuevos cálculos:
no podríamos atribuir la diferencia. Esta documentación no implementa esos cambios.

Esta matriz estudia instrucciones. No confundirla con las familias de modelos de
conocimiento: son factores distintos, que conviene estudiar por separado.

## Ejemplo de representación por contrastar

El estado actual no exige schema financiero ni carpeta de casos. El modo `cases` fue
retirado; sus antecedentes se describen en [arquitectura](baseline.md#antecedente-retirado-modo-de-expedientes).
La siguiente convención histórica es una alternativa textual, no el mapa físico actual:

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

La base para próximos experimentos es el [baseline](baseline.md), con sus límites
observados. Los experimentos futuros necesitan su protocolo y autorización propios;
esta agenda no autoriza ejecutar campañas ni implementar toda la matriz.
