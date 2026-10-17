# Visión y propósito

> Dirección de producto e hipótesis de investigación. Revisión: 2026-10-17.
> No modifica el comportamiento del agente ni los contratos de FinMate.

## Para qué existe FinMate

FinMate aspira a acompañar el proceso inversor: comprender los objetivos y restricciones
del usuario, investigar empresas, elaborar evaluaciones justificadas y relacionarlas
con su cartera. A largo plazo, contempla una gestión cada vez más autónoma y supervisada.
Esa autonomía requerirá garantías de riesgo, permisos, ejecución y evaluación propias;
no forma parte de los primeros experimentos de este laboratorio.

La unidad de valor buscada es una **evaluación de inversión auditable que evoluciona
con la evidencia**. El expediente vivo conserva qué sabemos, qué interpretamos, qué
desconocemos, por qué sostenemos un juicio y qué nos haría revisarlo. Su significado
y sus conceptos aún deben precisarse; no implica un schema o almacenamiento elegido.
La [visión de FinMate](../../FinMate/docs/product/vision.md) y sus
[capacidades](../../FinMate/docs/product/capabilities.md) documentan aquel producto.

## Para qué existe Research Agent

Research Agent es el laboratorio para descubrir qué combinación de autonomía,
herramientas, instrucciones y memoria permite mantener ese conocimiento con calidad
y un coste proporcionado. Su núcleo es general; las finanzas son la primera especialización.

FinMate ha explorado entidades, operadores, argumentación y persistencia que aportan
conocimiento y garantías, pero también pueden introducir coordinación innecesaria.
Preservar una capacidad no exige conservar su implementación. Cada mecanismo debe
justificarse por el problema que resuelve, la alternativa más sencilla y cómo comprobar
su aportación. La arquitectura resultante será una conclusión revisable.

Hoy solo está implementado A: ciclo de modelo y herramientas, memoria Markdown,
Findata de solo lectura, Tavily, aritmética y captura experimental. Un modo opcional
añade expedientes versionados con Markdown y referencias, como candidato experimental.
No administra cartera ni ejecuta inversiones; no dispone de DCF o vigilancia
programada. El contrato vigente está en [arquitectura](architecture.md).

## Qué queremos contrastar

La hipótesis principal es que un estado explícito y persistente, acompañado de una
disciplina de investigación y revisión, permite evaluaciones más coherentes y útiles
que responder sin continuidad. Queda abierto cuánto debe estructurarse y si la
argumentación ayuda durante el razonamiento, al conservarlo o en ambas situaciones.

Una segunda hipótesis es que ese progreso mejore las decisiones y, eventualmente,
los resultados de inversión. Necesita evidencia diferente:

| Nivel | Qué habría que demostrar | Qué no basta |
|---|---|---|
| Análisis y revisión | Fundamento, fidelidad numérica, materialidad y continuidad | Un informe ordenado o muchos argumentos |
| Juicio y decisión | Uso adecuado de precio, alternativas, incertidumbre, riesgo y contexto del usuario | Una explicación coherente de la empresa |
| Resultados de inversión | Mejora frente a referencias, considerando horizonte, costes y riesgo | Un caso acertado o una campaña aprobada |

## Distinciones que orientan el diseño

Fuente, observación, interpretación, supuesto, cálculo, evaluación y decisión personal
tienen significados distintos, aunque compartan un archivo. Por ejemplo, mayores
ventas de NVIDIA son una observación; que sostengan sus márgenes es una hipótesis;
que la acción resulte atractiva exige además expectativas y precio; aumentar una
posición depende del usuario y su cartera. Citar las ventas no demuestra toda esa cadena.

La investigación debe abordar incertidumbres capaces de cambiar la evaluación,
ponderando su consecuencia económica y el coste de resolverlas. Lo menos documentado
no es necesariamente lo más material. Una consulta breve puede cerrarse sin expediente.

El [plan de investigación](strategy.md) establece la secuencia: comprender el estado
actual de FinMate, contrastar alternativas y después estudiar persistencia, transiciones
y presentación. [Experimentos](experiments.md) explica cómo evaluar esas hipótesis.
