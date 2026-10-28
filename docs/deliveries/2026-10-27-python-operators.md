# Entrega: operadores Python programables

Fecha: 2026-10-27. Base Git: `ec331a812b6963d1c8a7ca680b16dc02b46ba116`,
con cambios previos de revisión periódica ya presentes y conservados. Sin commit.

## Cambio

Implementada la [POC](../experiments/python-operators-v1/protocol.md) aprobada:
`--python` / `build_agent(..., python_enabled=True)`, documentación bajo demanda y
ejecución asíncrona en procesos locales con NumPy, pandas, SciPy y numpy-financial.
Cuatro contratos permiten cálculos, preparación de datos, evaluación por reglas y
modelos con supuestos explícitos. No se cambia el ciclo de A ni el wheel compartido.

Los tres campos `*_json` transportan objetos con claves libres como texto validado:
adaptación al schema estricto del adaptador OpenAI instalado, sin modificarlo.
Las funciones reciben diccionarios normales y devuelven objetos JSON.
Las referencias JSON/CSV se resuelven en el host y se conserva una copia exacta
de las entradas con código, configuración y fuentes, antes de ejecutar.
Materiales y resultados extensos utilizan captura y paginación existentes.

Se actualizaron los tres prompts propietarios, manteniendo instrucciones antiguas
congeladas. Dependencias científicas opcionales instaladas y fijadas para el entorno
local verificado. Corpus sintético y rúbrica preparados sin ejecutar un LLM.

## Verificación local

- `tests/test_python_operators.py`: **38 passed**, incluidos los cuatro ejemplos,
  referencias independientes, errores, pipes acotadas, terminación/cancelación,
  schemas cerrados, CLI, simulación, continuación y modo continuo.
- mypy: sin errores en los 33 módulos de A/campañas; `pip check`: sin conflictos.
- Regresión final de agente, modo continuo, metodología financiera y persistencia:
  **116 passed** con clientes controlados.
- Wheel construido sin dependencias: incluye worker, integración y cuatro contratos.
- Suite general: **235 passed, 4 failed, 10 errors**. Los fallos/errores corresponden
  a campañas ausentes: `longitudinal-v1`, `intencion-persistente-v1` y
  `contexto-continuo-v1`. No se fabricaron ni restauraron esos materiales.
  Este recorrido general precedió al ajuste final de transporte JSON; las pruebas
  específicas corresponden a la versión final.
- Comprobador documental: 20 enlaces a campañas/materiales ausentes del checkout;
  los 29 enlaces añadidos/nuevos se verificaron separadamente sin errores.
  `git diff --check` sin errores.

## Límites y continuidad

POC local expresamente sin sandbox ni límite duro de memoria. Los filtros reducen
usos accidentales y no garantizan contención frente a código que los eluda. En Windows
se lanza el intérprete real, evitando dejar un worker detrás del launcher del venv;
la limpieza drena las tuberías tras terminarlo para no bloquear el cierre.

No se ejecutaron proveedores, consultas a bases remotas ni campañas reales. Los
clientes usados en integración son simulados y la base de composición se sustituye
por SQLite local sin lecturas financieras. La corrección de fixtures y del lifecycle
no demuestra razonamiento autónomo, calidad financiera o rentabilidad. El siguiente
paso de evaluación es el contraste del protocolo, pendiente de encargo de ejecución.
