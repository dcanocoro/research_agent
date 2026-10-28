# Operador Python: transform

Contrato: python-operators-v1.

Preparación de datos: limpieza explícita, agrupación y alineación de series,
conversión de estructuras y variables derivadas. No inventes valores ausentes ni
mezcles periodos, monedas o unidades. Explica las conversiones o filas descartadas.

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
import pandas as pd

def run(inputs, parameters):
    left = pd.DataFrame(inputs["revenue"])
    right = pd.DataFrame(inputs["cash_flow"])
    table = left.merge(right, on="period", how="outer").sort_values("period")
    records = table.astype("object").where(pd.notna(table), None).to_dict(orient="records")
    return {"rows": records, "missing_policy": "outer join; missing is null"}
```

Entradas (`inputs`):

```json
{"revenue": [{"period": "2023", "revenue": 100}], "cash_flow": [{"period": "2024", "fcf": 15}]}
```

Parámetros (`parameters`):

```json
{}
```

Serializa los objetos de entrada y parámetros anteriores como texto en `inputs_json`
y `parameters_json`. Usa `input_refs_json="{}"` y `source_refs=[]` para este ejemplo sintético.


## Ejemplo de argumentos de herramienta

```json
{
  "operator": "transform",
  "code": "import pandas as pd\n\ndef run(inputs, parameters):\n    left = pd.DataFrame(inputs[\"revenue\"])\n    right = pd.DataFrame(inputs[\"cash_flow\"])\n    table = left.merge(right, on=\"period\", how=\"outer\").sort_values(\"period\")\n    records = table.astype(\"object\").where(pd.notna(table), None).to_dict(orient=\"records\")\n    return {\"rows\": records, \"missing_policy\": \"outer join; missing is null\"}\n",
  "inputs_json": "{\"revenue\": [{\"period\": \"2023\", \"revenue\": 100}], \"cash_flow\": [{\"period\": \"2024\", \"fcf\": 15}]}",
  "input_refs_json": "{}",
  "parameters_json": "{}",
  "source_refs": []
}
```
