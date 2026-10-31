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
UnitOfWork. A dirige un ciclo convencional de modelo/herramienta y escribe Markdown, JSON, TXT
y CSV en un estado acotado, con materiales originales y archivo de runs separados. Ambos pueden conservar evidencia, pero no comparten entidades,
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
| [Runner nativo lab histórico](../../FinMate/experience_audit/lab_runner.py) | Referencia del contrato retirado de este laboratorio; no dependencia de ejecución |

Ante una diferencia entre guía y ejecución, revisar fuentes, tests y versión instalada.
Cambios en Findata/Infra/Audit se realizan en FinMate y se incorporan mediante una
actualización deliberada del wheel, según [dependencias](development.md).

## Extracción y evidencia histórica

La [entrega local de extracción documental](deliveries/2026-10-16-documentation.md)
conserva procedencia y verificaciones del traslado. Los originales externos estaban en
`FinMate/artifacts/research-lab/2026-10-15/delivery.md` y
`FinMate/artifacts/research-agent/2026-10-16/delivery.md`; son referencias históricas,
no evidencia distribuida aquí.

La [arqueología conceptual](finmate-concept-model/modelo-conocimiento-actual.md)
explica conceptos, ciclos y consumidores del corte del 17 de octubre. Su
[anexo de estructuras](finmate-concept-model/estructuras-y-campos.md) conserva campos
y restricciones declaradas; se mantiene separado porque permite descender al detalle
sin repetirlo en el mapa conceptual. Ninguno define el runtime vigente de A.

Las rutas navegables de esta página y de la arqueología son **referencias externas**
al checkout hermano de FinMate. Su ausencia se informa por separado de errores
internos del laboratorio; no se reconstruye su contenido ni se cambia la referencia
histórica para hacer pasar una comprobación. Los informes externos pueden depender
de capturas privadas ausentes. No se consultaron datos privados ni servicios para
esta consolidación.
