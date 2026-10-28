# Observación V4 con operadores Python

Fecha: 2026-10-27. Estado: ejecución real autorizada por el usuario y revisada.
Esta observación usa el mandato de investigación V4; no es el contraste sintético
controlado del [protocolo](protocol.md), que sigue pendiente.

## Resultado principal

**A utilizó Python autónomamente dos veces y ambas funciones ejecutaron correctamente
al primer intento.** Los resultados se incorporaron al conocimiento persistente.
Se observó uso del ejecutor y del contrato calculate, con Python básico; no se
observaron imports de bibliotecas científicas, otros operadores ni modelos DCF.

## Condiciones y captura

Se preservó el intento anterior en `artifacts/contexto-continuo-v4/piloto` y se creó
`artifacts/contexto-continuo-v4/piloto-python-v1` con memoria, agenda y cartera nuevas.
Mandato, petición, rúbrica, configuración de escenario y dataset son idénticos por
hash a los del intento anterior. El dataset mantiene SHA-256
`4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`.
Se usaron código y prompts actuales, sin una indicación adicional para forzar Python.
Por tanto, no se aísla el efecto del ejecutor frente al de las instrucciones.

Perfil: OpenAI `gpt-6-luna`, razonamiento medium, máximo de salida 16000.
Fecha simulada 2023-01-01, web desactivada y sin consultas a BD remota.
Se mantuvieron 60 llamadas ordinarias, 90 herramientas, 1200 segundos, contexto
máximo 524288 bytes y umbral 262144. El presupuesto inicial recalculado con las
herramientas Python fue 175837 bytes, incluida la reserva de salida de 128000.
La activación queda comprobada en el manifiesto: `python_operators.enabled=true`
y schemas de `run_python` y `describe_python_operator` presentes.

Run: `b8f18e55-d63c-454f-bb0b-0a1e02916427`. La
[captura local](../../../artifacts/contexto-continuo-v4/piloto-python-v1/README.md)
y el [resumen verificable](../../../artifacts/contexto-continuo-v4/piloto-python-v1/resumen-uso-python.json)
requieren conservar los artefactos: son evidencia local, no portable por estar enlazada.
El lanzador local `artifacts/contexto-continuo-v4/ejecutar-python-v1.py` conserva la
composición usada; añadió `--python` sin modificar el controlador ni el ciclo de A.

## Uso observado

| Ejecución | Operador | Entradas | Procedimiento | Tiempo |
|---|---|---|---|---|
| Primera | calculate | AAPL y AMZN, ejercicios 2019–2021 | Márgenes operativo, de caja operativa y FCF; capex/flujo operativo; FCF/flujo operativo; CAGR de ingresos y resultado operativo | 1,219 s |
| Segunda | calculate | ADBE, ejercicios 2019–2021 | Los mismos indicadores, aplicados a Adobe | 1,125 s |

No hubo consulta a `describe_python_operator`, que es opcional. Ambas funciones
definieron `run(inputs, parameters)`, recibieron objetos mediante `inputs_json` y
devolvieron JSON. Usaron entradas inline con fuentes explícitas; `input_refs_json`
quedó vacío. No necesitaron correcciones. Los dos tiempos suman 2,344 segundos y
corresponden al ejecutor, sin atribuirles las llamadas al modelo que generaron código.

Referencias relativas a la carpeta de campaña:

- Primera ejecución: `ejecuciones/2026-10-27-piloto/trazas/herramienta-0192.json`;
  resultado en `estado/materiales/2026-10-27-piloto-10-run-python.json`.
- Segunda ejecución: `ejecuciones/2026-10-27-piloto/trazas/herramienta-0223.json`;
  resultado en `estado/materiales/2026-10-27-piloto-14-run-python.json`.
- Código y entradas exactas: `execution_ref` terminado en
  `resultado-herramienta-0031.json` y `resultado-herramienta-0037.json`.

Los documentos finales `estado/oportunidades.md`, `estado/agenda.md` y
`estado/empresas/ADBE/modelo.md` utilizan los indicadores y referencian los materiales.
`oportunidades.md` compara las tres empresas y limita expresamente la interpretación:
los agregados y crecimientos retrospectivos no explican por sí solos causalidad,
sostenibilidad o atractivo de inversión.

## Comprobación y cierre

Recalculados independientemente con Decimal los **51 indicadores**: coinciden con
las salidas dentro de tolerancia relativa/absoluta 1e-12. Los cocientes se comprobaron
como numerador/denominador por 100 y los CAGR con raíz cuadrada de la relación entre
extremos, para dos intervalos anuales. También se contrastaron las **45 entradas
financieras** con las observaciones anuales de los materiales citados, verificando
empresa, año y métrica, con conversión uniforme de USD a millones de USD.
Esto valida la aritmética y la transcripción de estos datos, no su calidad económica
ni el aislamiento temporal del dataset.

La ejecución duró **488,16 segundos**; el lanzamiento completo, 493,45 segundos.
Se contabilizaron 63 llamadas al modelo: 38 de investigación, 22 de consolidación y
3 revisiones adicionales; 58 herramientas y 6 renovaciones. Cero herramientas
fallidas y cero errores de captura; inspector nativo: captura completa.
El agente pausó con `interrupted: call_limit`, sin completar el mandato. El registro
general de campaña lo etiqueta `failed` porque exige `agent_status=completed`;
esa etiqueta no describe un fallo de Python o de captura.

La evidencia demuestra adopción autónoma del ejecutor y uso posterior de sus resultados
en este intento. No demuestra utilidad de NumPy/pandas/SciPy, reutilización de código,
modelado cuantitativo avanzado, mejora causal frente a V4 anterior ni resultados de
inversión. Es una observación real favorable al funcionamiento y adopción inicial;
el contraste controlado del protocolo sigue pendiente.
