# Documentación de Research Agent

> Estado: índice del proyecto externo. Revisión: 2026-10-16.
> Autoridad: código local, contratos de las bibliotecas instaladas y evidencia fechada.

Research Agent permite investigar agentes con herramientas y memoria. La primera
especialización es financiera; no impone un grafo, expediente o valoración para responder.

## Orden de lectura

1. [Propósito, reflexión e hipótesis](purpose.md): por qué existe y qué no sabemos aún.
2. [Arquitectura implementada](architecture.md): clases, flujo, herramientas y límites.
3. [Dependencias de FinMate](dependencies.md): distribuciones, wheel, configuración y actualizaciones.
4. [Experimentos y evaluación](experiments.md): escenarios actuales, propuestas A0–A3 y continuidad.
5. [Desarrollo y operación](development.md): ejecutar, comprobar y conservar resultados.
6. [Referencias de FinMate](finmate-references.md): dónde investigar contratos y antecedentes.
7. [Entrega documental del 16 de octubre](deliveries/2026-10-16-documentation.md).

Las instrucciones de colaboración están en [AGENTS.md](../AGENTS.md). El
[README inicial](../README.md) proporciona el arranque rápido.

## Cómo interpretar estas páginas

| Tipo de información | Referencia propietaria | Qué acredita |
|---|---|---|
| Capacidad actual | Arquitectura y código enlazado | Existencia de un recorrido, no su calidad financiera |
| Propósito e hipótesis | Propósito | Dirección de investigación, no comportamiento obligatorio |
| Dependencia o instalación | Dependencias | Relación con bibliotecas; verificar el entorno efectivo |
| Protocolo experimental | Experimentos | Qué controlar y observar; no resultados anticipados |
| Resultado fechado | Entrega y artefactos citados | Lo observado en esa ejecución, con sus límites |

Se conserva una referencia por tema. Los antecedentes de FinMate se enlazan, no se
copian como contratos locales. La documentación de la fuente compartida puede ser
más reciente que el wheel instalado: contrastar antes de atribuir una capacidad.

## Estado a este corte

- Agente A con ciclo autónomo, memoria Markdown, Findata, Tavily y aritmética.
- Proyecto externo `research-agent`, paquete `research_agent`; bibliotecas comunes en FinMate.
- CLI y campañas de Experience Audit sin backend, navegador ni expediente del producto.
- Sin DCF, cartera, órdenes, vigilancia programada, grafo obligatorio ni variantes A0–A3.
- La entrada habitual carga guía financiera básica; no es el futuro A0 sin guía específica.

Las referencias entre repositorios suponen carpetas hermanas `research_agent` y
`FinMate`. Es una comodidad documental, no una ruta de importación en ejecución.
