# Rúbrica: operadores Python v1

Uso futuro con el [protocolo](protocol.md). Sin evaluación con LLM realizada.

| Dimensión | Criterio observable |
|---|---|
| Elección de capacidad | El procedimiento responde a una necesidad de la pregunta y usa el operador apropiado. Resolver con aritmética sencilla también es válido. |
| Exactitud | Coincide con las referencias del corpus (tolerancia relativa 1e-8 para números); las ausencias y decisiones por umbral son exactas. |
| Contrato | Interfaz válida, resultado JSON y criterios/supuestos explícitos cuando se requieren. |
| Fundamento | Conserva fuente, periodo, moneda/unidades y distingue datos de estimaciones. No inventa entradas. |
| Interpretación | Explica qué permite concluir el cálculo, sin atribuir al éxito técnico calidad económica o recomendación de inversión. |
| Eficiencia | Número de intentos/correcciones, duración, llamadas y tokens observables; se contabilizan errores y documentación consultada. |

Calificar cada dimensión semántica como satisfecha, parcial o incumplida y justificar
con pasajes o referencias de las capturas. No sumar dimensiones como si produjeran
una probabilidad de acierto. Informar por separado éxito técnico y corrección analítica.

Éxito al primer intento: el primer código solicitado para esa necesidad ejecuta y
produce el resultado correcto. Consultar antes el contrato consume recursos, pero
no cuenta como un intento de código. El objetivo de hasta tres intentos no permite
omitir fallos ni declarar correcto un cálculo que no lo sea.
