# Entrega documental — 2026-10-16

## Base y alcance

Proyecto: `C:\Users\Daniel\Proyectos\research_agent`.
Base Git al inicio: `e5856d5b749afc8600a644559abf820d46cd3b06`, sin cambios locales.
Petición: documentar propósito, arquitectura, relación con FinMate, reglas de trabajo
y reflexiones estratégicas aportadas por el usuario.

Se contrastaron código local, composición, prompts, herramientas, tests, empaquetado
compartido y entrypoints de Audit. Se consultaron las referencias y entregas enlazadas
en el [mapa de FinMate](../finmate-references.md). No se copiaron secretos ni capturas privadas.

## Resultado

- README de arranque y [índice](../README.md) con una referencia propietaria por tema.
- [AGENTS local](../../AGENTS.md), adaptado a un agente externo con dependencias instaladas.
- [Propósito](../purpose.md) y [experimentos](../experiments.md) que incorporan las reflexiones:
  expediente evolutivo, materialidad, puente económico, estructura de memoria y variantes A0–A3.
- [Arquitectura](../architecture.md), [dependencias](../development.md) y
  [operación](../development.md) que describen capacidades y límites actuales.

Quedan explícitos: distribución frente a paquete; editable frente a wheel; fuentes
compartidas en FinMate; actualización deliberada; memoria frente a historial y archivo;
guía financiera actual frente al A0 propuesto; implementación frente a evaluación semántica.

Se documenta el uso de salida absoluta para consultas de Audit: actualmente los comandos
de archivo y `lab` no resuelven del mismo modo las rutas relativas. No se cambia el runner.

## Verificación de este cambio

- Diez archivos Markdown revisados: 80 enlaces locales comprobados, sin destinos ausentes.
  La comprobación cubre existencia de archivos, no disponibilidad futura del repositorio hermano.
- Sin espacios al final de línea ni archivos sin salto final, incluidos documentos nuevos.
- Ayudas de `research_agent` y `experience_audit lab` ejecutadas correctamente en la `.venv` local.
- Ejemplo YAML validado con `LabScenario`; cinco ejemplos de comandos de Audit aceptados
  por su parser sin ejecutar campañas, consultar archivos privados o llamar a proveedores.
- Los módulos instalados `experience_audit.commands` y `experience_audit.lab_runner`
  coinciden byte a byte con las fuentes referenciadas de FinMate en este corte.
- `git diff --check` correcto. Revisión del diff del README y del contenido documental nuevo.
  La suite de runtime no se repite por tratarse de documentación; sus resultados históricos
  están en las entregas originales, sin atribuirlos a esta ejecución.

No se modifican runtime, prompts, dependencias instaladas, escenarios ni fuentes de
FinMate. No se ejecutan campañas reales, lecturas financieras o evaluaciones semánticas.
Las entregas históricas enlazadas conservan su fecha y no se presentan como aceptación
repetida. No hay revisión independiente de este cambio. No se hace commit, push o despliegue.

## Siguiente paso recuperable

Definir con el usuario un protocolo longitudinal pequeño, fuentes congeladas y rúbrica;
decidir después qué cambio mínimo permite contrastarlo. La matriz A0–A3 y la convención
de expediente son propuestas, no implementaciones ni mandato de construirlas todas.
