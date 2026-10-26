# Rúbrica de revisión semántica — análisis financiero v1

Estado: preparada, sin aplicación ni resultados. Solo para el revisor; no cargar como
instrucción ni material del agente. Corpus: [casos](../../../benchmarks/analisis-financiero-v1/semantic-cases.json).

| Caso | Evidencia que debe revisar la persona evaluadora |
|---|---|
| Creación | Explica ingresos, retención y riesgos; distingue hechos de supuestos; conserva conocimiento útil en los documentos de empresa al prever continuidad, sin crear archivos vacíos ni premiar su número. |
| Recuperación | Consulta y usa fundamentos persistidos sin reconstruir el análisis ni recibir el chat anterior; mantiene incertidumbres y selecciona trabajo pertinente. |
| Contradicción | Vincula la novedad con H1, consulta sus dependientes antes de cerrar la actualización, revisa V1 y la evaluación dependiente; conserva causas del cambio y fundamentos no afectados. |
| Redundancia | Reconoce que repetir una fuente no añade evidencia ni justifica fortalecer una hipótesis; no se exige escribir ni cambiar de opinión. |
| Dependencia pendiente | Marca la valoración anterior como pendiente o superada cuando pierde su fundamento; no conserva 20/10 USD como valor vigente sustentado; relaciona agenda y documentos. |
| Bloqueo instrumental | Explica exactamente por qué no puede comparar valor y precio; evita búsquedas agotadas y avanza en concentración o mecanismos económicos sin fabricar valoración. |

Referencia numérica sintética para el revisor: EPS inicial 20 millones USD / 10 millones
de acciones = 2 USD; escenario 2 × 10 = 20 USD/acción. Tras el cambio, supuesto 1 × 10 =
10 USD/acción; no es beneficio observado ni valor intrínseco validado. BETA: 1 × 15 =
15 USD/acción, con riesgos y supuestos diferentes. La aritmética debe ejecutarse mediante
herramientas, conservar sus materiales y respetar las bases comparables. La ausencia de
DCF no bloquea estos escenarios simples. No exigir una conclusión de compra.

Para cada dimensión registrar favorable, contrario o no observable y citar run, entrada,
herramienta/material y snapshot concretos. Revisar calidad del modelo económico,
trazabilidad, revisión selectiva, comparación de oportunidades y avance de incertidumbres.
Una llamada a read_file no demuestra uso del conocimiento; una cita no prueba inferencia.

Separar observación de interpretación, bloqueo de datos de limitación de herramientas y
fallo operativo de fallo semántico. Comparar recursos observados y carga de mantenimiento;
no usar un agregado de archivos, llamadas, operaciones o rentabilidad como nota de éxito.
No fabricar puntuaciones ni omitir intentos fallidos. No atribuir causalidad aislada a la
metodología o a la representación: se han cambiado conjuntamente.
