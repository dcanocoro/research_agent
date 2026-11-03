**Se usa con los mismos comandos de antes.** El cambio está en el código interno: acotado, continuo y B utilizan ahora el mismo motor.

| Modalidad | Cómo se activa | Comportamiento |
|---|---|---|
| Acotada | Sin opciones adicionales | Atiende una petición y responde dentro de sus límites |
| Continua E2 | `--continuous --mandate RUTA` | Continúa investigando, renueva contexto y revisa avances |
| Con objetivos | Añadir `--objective RUTA_JSON` | Sustituye la revisión general por evaluación de criterios |
| Con B | Añadir `--knowledge-agent prepared` | A puede encargar a B integrar conocimiento; exige 100 llamadas totales |

`--experiment` sigue indicando **la carpeta donde guardar estado y ejecuciones**.

### 1. Primero: probar sin consumir llamadas reales

Desde PowerShell:

```powershell
cd C:\Users\Daniel\Proyectos\research_agent

.\.venv\Scripts\python.exe -m pytest -q tests/test_runtime_architecture.py
```

Estas seis pruebas comprueban el motor común, la ejecución básica sin cargar extensiones, la compatibilidad de la identidad E2 y la captura de cancelaciones.

Para comprobar también los comportamientos existentes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_agent.py tests/test_continuous.py tests/test_e2.py tests/test_durable_knowledge.py tests/test_v8.py
```

Usan clientes controlados, sin proveedores LLM ni bases remotas.

### 2. Una ejecución real acotada

Requiere la configuración habitual del proveedor y las herramientas en `.env`. **Este comando sí consume llamadas reales.**

```powershell
.\.venv\Scripts\python.exe -m research_agent `
  "Explica brevemente el modelo de negocio de Microsoft y señala las incertidumbres principales." `
  --experiment artifacts/prueba-refactor-acotado `
  --new --run-name inicial
```

La carpeta debe ser nueva. Para continuar usando su conocimiento guardado:

```powershell
.\.venv\Scripts\python.exe -m research_agent `
  "Revisa lo guardado y explica qué falta por comprobar." `
  --experiment artifacts/prueba-refactor-acotado `
  --continue --run-name revision
```

Continuar reutiliza archivos e instrucciones; **no restaura toda la conversación anterior**.

### 3. Una prueba continua pequeña

Crea un mandato fuera de `estado/` y `ejecuciones/`:

```powershell
New-Item -ItemType Directory -Force artifacts/pruebas-refactor | Out-Null

"Investiga el modelo de negocio de Microsoft. Conserva evidencia, incertidumbres y pendientes. No fuerces una valoración." |
  Set-Content -Encoding utf8 artifacts/pruebas-refactor/mandato.md
```

Después:

```powershell
.\.venv\Scripts\python.exe -m research_agent `
  "Comienza por identificar los principales negocios y sus fuentes de ingresos." `
  --experiment artifacts/prueba-refactor-continuo `
  --new --run-name inicial `
  --mandate artifacts/pruebas-refactor/mandato.md `
  --continuous --max-calls 10 --max-tools 15 `
  --continuous-timeout-seconds 300
```

Las diez llamadas incluyen investigación y revisiones. Al alcanzar el presupuesto puede terminar con `interrupted: call_limit`: es una pausa por recursos, no una certificación de tarea completada.

Para probar B, utiliza **otro directorio nuevo**, añade `--knowledge-agent prepared` y cambia el presupuesto a `--max-calls 100`. Se reservan 30 llamadas para B; las que B no utiliza no pasan a A. Activarlo permite la delegación, pero no obliga a A a delegar.

### 4. Qué revisar al terminar

La CLI imprime la carpeta de ejecución. Dentro encontrarás:

- `respuesta.md`: respuesta producida.
- `resultado.json`: estado, motivo de parada y llamadas utilizadas.
- `manifiesto.json`: instrucciones, herramientas y composición efectiva en `extensions`.
- `eventos.jsonl`: lo sucedido durante la ejecución.

El conocimiento editable queda en `estado/`. En continuo, `conversacion-completa.jsonl` conserva el transcript; los encargos de B quedan en `control-integracion/`.

Empezaría por **las seis pruebas de arquitectura y una ejecución acotada nueva**. Después probaría el continuo pequeño. Los comandos y límites están documentados en la [guía de desarrollo](C:/Users/Daniel/Proyectos/research_agent/docs/development.md).