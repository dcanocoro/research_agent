# Operador Python: calculate

Contrato: python-operators-v1.

Cálculos deterministas y estadísticos sobre datos disponibles. Permite ratios,
crecimientos, agregaciones, correlaciones y otros procedimientos definidos por
el agente. Usa la herramienta aritmética `calculate` para operaciones sencillas.
Identifica fórmula, unidades y tratamiento de denominadores cero.

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
import numpy as np

def run(inputs, parameters):
    revenues = np.asarray(inputs["revenue"], dtype=float)
    operating = np.asarray(inputs["operating_income"], dtype=float)
    if np.any(revenues == 0):
        raise ValueError("revenue contains zero")
    return {"operating_margin": (operating / revenues).tolist(),
            "unit": "fraction", "periods": inputs["periods"]}
```

Entradas (`inputs`):

```json
{"revenue": [100, 120], "operating_income": [20, 30], "periods": ["2023", "2024"]}
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
  "operator": "calculate",
  "code": "import numpy as np\n\ndef run(inputs, parameters):\n    revenues = np.asarray(inputs[\"revenue\"], dtype=float)\n    operating = np.asarray(inputs[\"operating_income\"], dtype=float)\n    if np.any(revenues == 0):\n        raise ValueError(\"revenue contains zero\")\n    return {\"operating_margin\": (operating / revenues).tolist(),\n            \"unit\": \"fraction\", \"periods\": inputs[\"periods\"]}\n",
  "inputs_json": "{\"revenue\": [100, 120], \"operating_income\": [20, 30], \"periods\": [\"2023\", \"2024\"]}",
  "input_refs_json": "{}",
  "parameters_json": "{}",
  "source_refs": []
}
```
