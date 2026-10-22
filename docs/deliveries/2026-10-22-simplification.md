# Simplificación del laboratorio

Fecha: 2026-10-22. Base Git: `c75dd01`; cambios locales sin commit.

## Cambio

Las campañas pasan de `research_agent.benchmark*` a `src/research_benchmarks/`:
catálogo, controlador, extracción y compactación. El comando actual es
`python -m research_benchmarks`; sus definiciones siguen en `benchmarks/`.
La lectura de evidencia compacta permanece en `research_agent.archive`, para que
el agente recupere resultados históricos sin importar el controlador de campañas.
El manifiesto de campaña registra hashes de ambos paquetes.

Se retiran los escenarios, pruebas e instrucciones operativas de Experience Audit.
El wheel compartido sigue instalado sin modificaciones; la prueba de frontera
bloquea imports de Audit y del paquete de campañas durante una ejecución simulada.
Los registros nuevos usan siempre los nombres españoles y captura local propia.
Las capturas anteriores no se reescriben. No se mantiene el formato alternativo ni
el contrato de ejecución externa de Audit.

`AgentA.run` conserva ciclo y reservas; apertura y captura final se concentran en
`_prepare` y `_finish`. `ExperimentConfig` centraliza los modos persistentes y la
CLI lee una vez el archivo de configuración de ejecución, pasando opciones explícitas.
Cada herramienta declara ejecución, materiales y disponibilidad en consolidación;
su validador se prepara al registrarla. SQLite registra métodos directamente,
conserva operaciones sin escritores tardíos y aporta una función de captura con
fase explícita. Los clientes y fixtures comunes de pruebas viven en `tests/support.py`.

La [arquitectura](../architecture.md#organización-del-código) y la
[operación](../development.md#benchmark-piloto) describen el estado resultante.
No se modifican prompts, corpus, rúbricas, presupuestos ni el schema de conocimiento.

## Verificación

Base previa: 96 pruebas aprobadas. Resultado local tras el cambio:

- `pytest -q tests -x`: 100 pruebas aprobadas en 107,25 segundos. Se retira una prueba
  específica de Audit y se añaden cinco casos sobre configuración y herramientas.
- Mypy: sin errores en los 23 archivos de ambos paquetes.
- Dependencias: `pip check` sin requisitos rotos.
- Los cuatro catálogos se validan offline desde `python -m research_benchmarks`;
  la instalación editable descubre ambos paquetes y la ayuda de la CLI funciona.
- Documentación: 36 Markdown, 530 enlaces locales, sin errores; `git diff --check` limpio.

Se conserva el alcance de continuidad por procesos, cancelación, cierres, fidelidad
de compactación y fallos de captura. La prueba de CLI comprueba lectura única y
propagación de configuración; la de herramientas verifica conservación y consolidación
con un nombre nuevo. La validación offline del catálogo no construye servicios.

No se ejecutan campañas con proveedores ni consultas a bases remotas. No se mide
rendimiento ni calidad financiera. La instalación editable se actualiza para descubrir
el nuevo paquete; no se modifica FinMate ni el wheel compartido.
