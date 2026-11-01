# Tres casos fijos para los siguientes experimentos

Fecha: 2026-10-31. Preparación autorizada; sin campañas reales ejecutadas en esta entrega.

## Encargos estables

Cada experimento utiliza exactamente tres ejecuciones, una por caso, sin ejecuciones
adicionales de control. Los textos aprobados se conservan en:

- [Analista abierto](../../../campaigns/casos-fijos/analista.md): selección autónoma
  de prioridades y comparación de oportunidades a cinco años.
- [Microsoft](../../../campaigns/casos-fijos/microsoft.md): evaluación de inversión
  centrada en una empresa, escenarios, precio y condiciones de revisión.
- [Infraestructura de IA](../../../campaigns/casos-fijos/sector-ia.md): investigación
  sectorial sobre creación y captura de valor, relaciones y explicaciones rivales.

Comparten un [mandato](../../../campaigns/casos-fijos/mandato.md) de autonomía,
persistencia, procedencia, cálculo y Findata de solo lectura. Los prompts se mantienen
iguales entre experimentos. Dentro de un lote solo cambian petición inicial, nombre
identificador y directorio aislado. No se suministra `objective.json`: se conserva
la revisión externa del continuo sin objetivo.

## Condiciones comunes

Las condiciones siguientes describen la preparación original con V5. La
[ablación E1](../e1-simplificacion/protocol.md) conserva encargos y presupuestos,
pero cambia herramientas e instrucciones sobre el mismo agente; su protocolo
declara esa intervención y los timeouts efectivos.

Una ejecución nueva por caso, sin conocimiento previo ni intercambio de estado.
Mismo intérprete, perfil LLM configurado, instrucciones vigentes, herramientas V5 y
Python habilitado. Cada proceso conserva su propia copia nativa de instrucciones.
Fuentes reales disponibles en Findata y web, sin congelar datos ni simular fechas.

Por caso: máximo de 100 llamadas ordinarias, 200 herramientas y 300 segundos por
operación; máximo/umbral de contexto de 524288/262144 bytes. Autorrevisiones y revisiones
externas son llamadas adicionales conforme al runtime vigente. No hay timeout global
adicional; siguen aplicándose los límites del proveedor y de cada operación.
Los presupuestos son máximos, no garantía de consumirlos ni de resolver el encargo.

El [lanzador](../../../scripts/run_fixed_cases.py) inicia los tres procesos antes de
esperar resultados, conserva las entradas efectivas y separa logs y capturas.
La [guía de campañas](../../campaigns.md#tres-casos-fijos-en-paralelo) contiene el comando,
ubicación de resultados y comportamiento ante fallos y cancelación.

## Interpretación y límites

Estos casos son cargas de trabajo reutilizables, no tres repeticiones del mismo caso
ni un contraste causal entre condiciones. Una sola ejecución por caso y fuentes web
y financieras cambiantes limitan la atribución de diferencias entre experimentos.
Cada experimento debe declarar su intervención y criterios de evaluación antes de
lanzar, conservando estos prompts y las condiciones efectivas.

Separar consumo, cierre operativo e integridad de captura de calidad semántica,
coherencia económica y utilidad. No se generan puntuaciones automáticas ni se
interpreta agotar las 100 llamadas como cumplimiento. No hay resultados financieros
validados ni hallazgos experimentales en esta preparación.
