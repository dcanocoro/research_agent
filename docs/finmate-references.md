# Referencias de FinMate

> Mapa de lectura, no dependencia de ejecución. Revisión: 2026-10-16.

Las rutas suponen proyectos hermanos. Si se traslada uno, pueden dejar de abrirse
sin afectar al agente instalado. La documentación de FinMate describe su checkout;
contrastarla con el wheel efectivo antes de atribuir una capacidad a Research Agent.

## Visión y arquitectura para entender el contraste

| Referencia en FinMate | Para qué leerla aquí |
|---|---|
| [Índice](../../FinMate/docs/README.md) y [AGENTS](../../FinMate/AGENTS.md) | Orientación y criterio original del que se adapta el AGENTS local |
| [Visión](../../FinMate/docs/product/vision.md) y [capacidades](../../FinMate/docs/product/capabilities.md) | Separar aspiración, producto vigente y experimento |
| [Arquitectura](../../FinMate/docs/architecture/overview.md) y [mapa de datos](../../FinMate/docs/architecture/data-map.md) | Propiedad del estado, productores y consumidores |
| [Contrato de Engine](../../FinMate/engine/ARCHITECTURE.md) | Entender ciclo, resoluciones y efectos que A no reutiliza |
| [Expediente](../../FinMate/docs/architecture/thesis-review.md) y [fuentes](../../FinMate/docs/architecture/thesis-inputs.md) | Revisiones, fundamentos y procedencia del producto; antecedentes, no schemas de A |

FinMate dirige su ejecución mediante Engine y persiste efectos validados mediante
UnitOfWork. A dirige un ciclo convencional de modelo/herramienta y escribe Markdown
en un workspace acotado. Ambos pueden conservar evidencia, pero no comparten entidades,
estados de tesis o mecanismos de persistencia del dominio. No sustituir uno por otro
solo porque sus salidas se parezcan.

## Bibliotecas compartidas y su autoridad

| Referencia | Qué resuelve |
|---|---|
| [Declaración de distribución](../../FinMate/pyproject.toml) | Qué instala hoy el wheel llamado `findata` |
| [Clientes LLM](../../FinMate/docs/architecture/llm-clients.md) | Perfiles, replay, errores, captura y proveedores |
| [Infraestructura](../../FinMate/docs/architecture/infrastructure.md) | Configuración y composición compartidas |
| [Operación Findata](../../FinMate/docs/operations/findata.md) | PostgreSQL, datos y restricciones de lectura |
| [Experience Audit](../../FinMate/docs/operations/experience-audit.md) | Archivo, consulta, informes y distinción de variantes |
| [ADR 0004: contratos compartidos](../../FinMate/docs/architecture/decisions/0004-shared-runtime-contracts.md) | Separación de contratos técnicos respecto a Engine |
| [Runner nativo lab](../../FinMate/experience_audit/lab_runner.py) | Contrato efectivo `lab-v1`, checks y ejecución sin producto |

Ante una diferencia entre guía y ejecución, revisar fuentes, tests y versión instalada.
Cambios en Findata/Infra/Audit se realizan en FinMate y se incorporan mediante una
actualización deliberada del wheel, según [dependencias](dependencies.md).

## Extracción y evidencia histórica

- [Guía de extracción](../../FinMate/docs/development/research-agent.md): ubicación,
  instalación y frontera entre proyectos.
- [Entrega de implementación de A, 2026-10-15](../../FinMate/artifacts/research-lab/2026-10-15/delivery.md):
  implementación, verificaciones y límites del corte original.
- [Entrega de extracción, 2026-10-16](../../FinMate/artifacts/research-agent/2026-10-16/delivery.md):
  renombrado, instalación y verificaciones del traslado.
- [Flujo de desarrollo de FinMate](../../FinMate/docs/development/workflow.md):
  antecedente del criterio de documentación y entrega adaptado aquí.

Estos informes son históricos, no contrato vigente ni pruebas repetidas hoy. Los
artefactos privados e ignorados a los que aludan pueden no estar presentes en otra máquina.
La [entrega local](deliveries/2026-10-16-documentation.md) registra este cambio documental.
