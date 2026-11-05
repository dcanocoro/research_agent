# Operador Python: evaluate

Contrato: python-operators-v1.

Aplicación de criterios explícitos sobre datos: umbrales, puntuaciones y
comparaciones multicriterio. Exige `parameters.criteria` como objeto no vacío.
Explica el sentido y unidades de cada criterio y el tratamiento de ausencias.
El resultado es una evaluación computacional; no equivale a recomendar invertir.

## Interfaz y entorno comunes

Invoca `run_python(operator, code, inputs_json, input_refs_json, parameters_json, source_refs)`.
Todos los argumentos se envían. Los tres campos `*_json` son textos que codifican
objetos JSON; usa el texto `"{}"` si no los necesitas y `[]` para fuentes vacías.
Esto mantiene compatibilidad con schemas estrictos del proveedor sin limitar las
claves de tus datos. La función recibe diccionarios decodificados, no esos textos.
El código define exactamente `def run(inputs, parameters):` y devuelve un objeto
JSON. Puede contener imports permitidos y funciones auxiliares; no sentencias de
trabajo a nivel de módulo, clases, decoradores o funciones asíncronas.

Bibliotecas: `math`, `statistics`, `numpy`, `pandas`, `scipy` y
`numpy_financial`. Importa con sus alias habituales dentro del código. Usa
`.tolist()`, `.to_dict(orient="records")`, `float(...)` e `int(...)` para
convertir resultados científicos a JSON. No devuelvas DataFrame, ndarray,
fechas Python, NaN o infinito: representa las ausencias explícitamente con
`None` y explica el tratamiento.

`inputs_json` codifica datos inline. `input_refs_json` codifica nombres adicionales con
rutas JSON o CSV del workspace, incluidas `materiales/...`. Los nombres no pueden
repetirse entre ambos objetos. El host resuelve los archivos antes de ejecutar:
JSON mantiene su estructura completa, incluidos los envoltorios de materiales;
CSV es una lista de registros con valores de texto que debes convertir.
No hay selección automática de campos. Ejemplo:
`"input_refs_json": "{\"finanzas\": \"materiales/resultado.json\"}"`; entonces consulta
`inputs["finanzas"]` según el schema real de ese material.
`source_refs` identifica los fundamentos, sin probar que sean correctos.

Límites: código 32 KiB UTF-8; entradas y parámetros resueltos 1 MiB; salida
1 MiB; 30 segundos incluyendo arranque; un hilo numérico. Cada ejecución empieza
sin variables de ejecuciones anteriores. No hay límite estricto de memoria.
No uses archivos, red, procesos, instalación de paquetes, reflexión, evaluación
dinámica ni APIs de lectura/escritura de las bibliotecas. No hay `print`: devuelve
los datos. Los filtros son preventivos; este proceso local no es un sandbox.

## Revisión y recuperación

Una llamada valida y ejecuta. Si falla, usa el tipo y línea del error para una
corrección puntual, hasta dos correcciones adicionales; después simplifica o declara
el límite. El runtime no realiza reintentos automáticos.

El resultado contiene `result`, parámetros, fuentes, configuración y
`execution_ref`, que recupera código y entradas exactas mediante `read_artifact`.
Se conserva también como material original de solo lectura. Para resultados
extensos sigue el `material_ref`/ `artifact_ref` y la paginación en bytes.
Para encadenar operaciones usa el material anterior como entrada y selecciona su
campo `result` explícitamente. Guarda en el conocimiento solo lo que aporte a
la investigación, enlazando sus fundamentos.

Que el código termine no demuestra exactitud económica. Conserva periodos, moneda,
unidades, procedencia y ausencias; comprueba resultados con casos sencillos y
órdenes de magnitud. No uses Python para obtener datos externos.

## Ejemplo completo

Código:

```python
def run(inputs, parameters):
    criteria = parameters["criteria"]
    rows = []
    for company in inputs["companies"]:
        margin = company["margin"]
        rows.append({"symbol": company["symbol"],
                     "passes": None if margin is None else margin >= criteria["minimum_margin"]})
    return {"rows": rows, "unit": "fraction", "missing_policy": "unknown"}
```

Entradas (`inputs`):

```json
{"companies": [{"symbol": "A", "margin": 0.2}, {"symbol": "B", "margin": null}]}
```

Parámetros (`parameters`):

```json
{"criteria": {"minimum_margin": 0.15}}
```

Serializa los objetos de entrada y parámetros anteriores como texto en `inputs_json`
y `parameters_json`. Usa `input_refs_json="{}"` y `source_refs=[]` para este ejemplo sintético.


## Ejemplo de argumentos de herramienta

```json
{
  "operator": "evaluate",
  "code": "def run(inputs, parameters):\n    criteria = parameters[\"criteria\"]\n    rows = []\n    for company in inputs[\"companies\"]:\n        margin = company[\"margin\"]\n        rows.append({\"symbol\": company[\"symbol\"],\n                     \"passes\": None if margin is None else margin >= criteria[\"minimum_margin\"]})\n    return {\"rows\": rows, \"unit\": \"fraction\", \"missing_policy\": \"unknown\"}\n",
  "inputs_json": "{\"companies\": [{\"symbol\": \"A\", \"margin\": 0.2}, {\"symbol\": \"B\", \"margin\": null}]}",
  "input_refs_json": "{}",
  "parameters_json": "{\"criteria\": {\"minimum_margin\": 0.15}}",
  "source_refs": []
}
```
