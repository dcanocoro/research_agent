# Documentación de Research Agent

Research Agent estudia mecanismos de conocimiento, investigación y revisión para el
futuro FinMate. El [baseline vigente](baseline.md) identifica el estado que se toma
como referencia para próximos experimentos, su configuración y evidencias disponibles.
La [estrategia](strategy.md) fija la agenda; la arqueología caracteriza un corte
histórico de FinMate y E001/E002 son antecedentes recuperables desde Git.

## Cinco referencias principales

| Documento | Qué resuelve |
|---|---|
| [Visión y propósito](purpose.md) | Qué producto buscamos y qué hipótesis estudia el laboratorio |
| [Estrategia](strategy.md) | Qué investigar, en qué orden y con qué criterios de avance |
| [Arquitectura](architecture.md) | Qué está implementado, quién lo posee y cuáles son sus límites |
| [Experimentos](experiments.md) | Cómo comparar mecanismos y qué conclusiones permite la evidencia |
| [Desarrollo](development.md) | Instalar, actualizar dependencias, ejecutar, verificar y entregar |

Para diseñar, empezar por visión y estrategia; para programar, seguir arquitectura,
productores, consumidores y pruebas del área afectada. [AGENTS.md](../AGENTS.md)
establece las reglas de colaboración; el [README](../README.md) ofrece el arranque rápido.
No hace falta releer todo en cada tarea.

## Registros y referencias

| Registro | Pregunta que conserva |
|---|---|
| [Baseline](baseline.md) | ¿Qué implementación y evidencias usamos como referencia? |
| [Decisiones](decisions/README.md) | ¿Qué elegimos, por qué y qué queda abierto? |
| [Experimentos y hallazgos](experiments/README.md) | ¿Qué contrastamos y qué aprendimos con qué evidencia? |
| [Entregas](deliveries/README.md) | ¿Qué se cambió y verificó en un corte concreto? |
| [Referencias de FinMate](finmate-references.md) | ¿Dónde investigar el producto y las bibliotecas compartidas? |

Cada tema tiene una referencia propietaria; los registros enlazan esa referencia sin
copiarla. Las entregas conservan su fecha: sus siguientes pasos pueden ser históricos.
La prioridad vigente se consulta en estrategia, no en la última campaña recordada.

## Cómo leer las afirmaciones

- **Visión y propuesta:** dirección a contrastar; no capacidad ni autorización de cambio.
- **Implementación:** código, schemas y configuración efectiva; no prueba de calidad financiera.
- **Hallazgo:** observación fechada con base, evidencia y límites; interpretación separada.
- **Decisión:** elección explícita con estado y justificación; no consecuencia automática de un check.

Hoy existe solo A, con herramientas y estado de archivos por experimento; instrucciones,
materiales y ejecuciones están separados. CLI permite crear o continuar una prueba.
Las campañas se ejecutan desde `research_benchmarks`, separado del núcleo.
La CLI carga guía financiera básica. El [entorno longitudinal](experiments/colaboracion-historica-v1/protocol.md)
añade cartera ficticia y activaciones históricas opcionales; A0–A3 y DCF no están implementados. Los documentos de E001/E002 no están en el árbol
actual; el registro experimental explica cómo recuperarlos desde Git.
Las rutas a FinMate suponen repositorios hermanos y no son imports de ejecución.
La documentación de sus fuentes puede diferir del wheel instalado: verificar antes
de atribuir capacidades. Estado revisado el 2026-10-24.
