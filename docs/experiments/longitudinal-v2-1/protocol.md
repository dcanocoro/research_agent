# Longitudinal v2.1 — recuperación y uso material del expediente

> Disponibilidad revisada el 2026-10-22: solo `longitudinal-v2-1` permanece
> en el árbol actual. Las rutas históricas de v1, v2 y la prueba corta se consultan
> con `git show c75dd01:benchmarks/NOMBRE/ARCHIVO`; los comandos históricos
> correspondientes requieren recuperar esa definición. Esta nota no cambia
> el protocolo ni afirma que se haya ejecutado una campaña nueva.

Estado: preparado para ejecución manual, sin campaña nueva. Fecha: 2026-10-22.
Encargo: corregir recuperación, precisar la operación de A1 y reparar la ambigüedad
de ASML; no ejecutar proveedores ni modificar campañas previas.

## Base y cambio

Los [hallazgos v2](../longitudinal-v2/findings.md) separan fallo de recuperación de
pérdida de datos. `knowledge_query` ahora busca subcadenas literales, sin distinguir
mayúsculas, en ID o contenido. El contrato de argumentos y los datos SQLite no
cambian. Un conflicto indica ID, versión actual y recuperación mediante
knowledge_read antes de reconsiderar el lote; no hay reintento automático.

El prompt A1 pide registrar evaluación y fundamentos materiales con estructura
mínima, recuperación directa por ID conocido y notas de contingencia explícitas
si SQLite no pudo actualizarse. No obliga a escribir ante ruido ni impone cuotas.
Es una instrucción del modelo, no un bloqueo de respuestas ni garantía de adopción.
Markdown sigue disponible, sin sincronización automática.

La [suite longitudinal-v2-1](../../../benchmarks/longitudinal-v2-1/suite.yaml) conserva
tres casos y 18 sesiones. Solo cambian el ID de suite y la ficha ASML `cartera.md`:
pedidos adicionales por 8 y aplazamientos por 6 se expresan explícitamente en miles
de millones EUR. Así quedan sustentados los controles de cartera 48, Alfa 20/48,
programación 2030 de 18 y posterior de 30. El resto de estímulos, rúbricas, cupos y
presupuestos coincide byte por byte con v2. La suite v2 y sus campañas se conservan.

## Prueba corta antes de comparar

argumentative-continuity-v1 (`benchmarks/argumentative-continuity-v1/suite.yaml`)
prepara un caso sintético de cuatro sesiones: crear evaluación, recuperar tras
reiniciar, incorporar corrección y comparar revisión anterior/vigente. Es una prueba
operacional dirigida, no evidencia de autonomía financiera ni comparación A0/A1.
Publica solo dos documentos y mantiene proceso nuevo por sesión.
Su rúbrica privada (`benchmarks/argumentative-continuity-v1/C1/rubric.md`)
requiere revisar operaciones y contenido, no solo completed o existencia de SQLite.

Ejecutar manualmente, desde la raíz, con el perfil elegido por el usuario:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks run benchmarks/argumentative-continuity-v1 --condition A1 --profile perfil-benchmark.json --output artifacts/benchmark
```

Si la operación corta funciona, comparar nuevas campañas de ambas condiciones:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks run benchmarks/longitudinal-v2-1 --condition A0 --profile perfil-benchmark.json --output artifacts/benchmark
.\.venv\Scripts\python.exe -m research_benchmarks run benchmarks/longitudinal-v2-1 --condition A1 --profile perfil-benchmark.json --output artifacts/benchmark
```

Cada invocación crea campaña y estado independientes. Congelar el mismo perfil,
código, prompts comunes, wheel y definiciones antes de comparar. Las campañas v2
son antecedentes, no el control emparejado de v2.1. Las copias de instrucciones en
experimentos anteriores permanecen intactas: continuar uno viejo no carga el prompt
nuevo automáticamente. No copiar estados entre condiciones.

## Aceptación y límites

Pruebas locales deterministas cubren búsqueda por ID/contenido, filtros, paginación,
retirada y recorrido en cuatro procesos: creación, recuperación, conflicto con
rollback, lectura vigente, reintento y comparación histórica. Se conserva la prueba
CLI con modelo simulado. La evaluación real de adopción y calidad sigue pendiente.

Aplicar las mismas dimensiones del protocolo v2 y registrar además adopción efectiva,
recuperación de IDs, resolución de conflictos y divergencias SQLite/Markdown. No
premiar entidades por cantidad; no interpretar una búsqueda vacía como amnesia.
Conservar errores y tentativas. No hay umbral automático de superioridad ni decisión
de adoptar el mecanismo en FinMate.
