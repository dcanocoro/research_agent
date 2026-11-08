# Baseline de 150 llamadas: tentativas del 2026-11-07

## Observación

Se lanzaron dos estados nuevos con el mandato y objetivo actuales de Expedientes
FinData, Progress abierto y continuo, sin/con nota, techo de 150 llamadas cada uno.
La captura local original es `artifacts/expedientes-findata-baseline-150-20261107-105604`.
Sin nota terminó en 34 llamadas con `progress_evaluation_invalid`, después de cuatro
renovaciones y escrituras de tres expedientes e índice. Dos evaluaciones consecutivas
fueron rechazadas por referencias; el último informe copió un hash de MSFT de dos
formas distintas. Con nota terminó en 14 llamadas con `LLMTruncated`, sin renovación,
nota ni expedientes escritos. El proveedor registró `max_output_tokens` al alcanzar
16000 tokens; el final de los argumentos de escritura contiene texto repetido.

## Interpretación y límites

La primera captura muestra fragilidad al pedir al modelo que copie hashes. La segunda
muestra una respuesta incompleta que no fue recuperada. No permiten comparar utilidad
de la nota ni acreditar calidad financiera. Las capturas completas son locales e
ignoradas; este relato no sustituye los originales para repetir una auditoría.

## Repetición autorizada

Tras las correcciones de referencias y recuperación, repetir una ejecución por brazo
con las mismas entradas y límites, en estados nuevos. Conservar las tentativas
originales. El Python base de `.venv` carece de biblioteca estándar; se usa el runtime
Python 3.12 de la aplicación con las dependencias instaladas del proyecto mediante
`PYTHONPATH`. No se modifica el wheel ni se cambia el modelo. El resultado de la nueva
tanda queda pendiente; no inferir éxito de su lanzamiento.

Destino nuevo preparado para la repetición: `C:/Users/canoc/Proyectos/research_agent/artifacts/expedientes-findata-baseline-150-repeticion-20261107-122229`.

La repetición terminó por presupuesto en ambos brazos; véase la [revisión de trayectorias y notas](baseline-150-findings.md).
