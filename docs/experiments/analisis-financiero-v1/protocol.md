# Análisis financiero longitudinal v1

> Lectura histórica: los comandos `research_benchmarks`, las utilidades de
> `scripts/` y varias definiciones de campañas se retiraron del checkout. Se
> conservan como condiciones del corte, no como instrucciones ejecutables actuales.
> La operación vigente está en la [guía de campañas](../../campaigns.md).

Estado: implementación y verificaciones locales; contraste y aceptación semántica
**sin ejecutar**. Encargo aprobado el 2026-10-25. No acredita calidad financiera ni
una arquitectura elegida para FinMate.

## Pregunta e intervención

¿La metodología financiera y una convención mínima de conocimiento persistente
permiten desarrollar evaluaciones económicas acumulativas más útiles que la condición
deliberativa anterior? Se contrasta el paquete completo, sin aislar metodología de
representación. Se conserva el mismo A, sus herramientas, mandato protegido y captura.

Los documentos por empresa separan modelo económico, valoración y evaluación vigente.
Al iniciar una evaluación que previsiblemente tendrá continuidad, su ubicación por empresa
es obligatoria; su creación es progresiva, sin archivos vacíos ni expediente para consultas
superficiales. La revisión coordinada de prompts los unifica en español y exige consultar
los dependientes relevantes de una hipótesis modificada, revisarlos, justificar ausencia
de impacto o dejar revisión pendiente identificable. `oportunidades.md` separa comparaciones
y `cartera.md` opcional conserva razonamiento de asignación sin sustituir herramientas. La agenda
representa trabajo pendiente; el índice permite localizar conocimiento. Las dependencias
son referencias textuales con ruta e ID, sin grafo, parser ni propagación automática.

## Condiciones congeladas

- **Control:** los tres textos efectivos de la campaña deliberativa ampliada, preservados
  en control (`campaigns/analisis-financiero-v1/control`; referencia local histórica).
- **Intervención:** los tres prompts nuevos por defecto del paquete, copiados al crear
  una campaña nueva. Congelar revisión de código y sus hashes antes de ejecutar ambos brazos.
- Ambos usan `--condition deliberative`, empiezan con estados y carteras nuevos y no
  comparten memoria. La campaña anterior es antecedente, no el brazo control futuro.

La procedencia (`campaigns/analisis-financiero-v1/control-provenance.json`; referencia local histórica)
registra hashes y seis manifiestos locales verificados: todos contienen el mismo texto
efectivo y coinciden con los archivos históricos leídos como UTF-8. Las diferencias de
hash inicialmente observadas entre algunas plantillas y copias eran de finales de línea,
no de contenido efectivo. Las copias versionadas contienen el texto exacto de los manifiestos
codificado UTF-8/LF, sin payloads privados. La evidencia original completa sigue local e
ignorada; los textos de control y sus hashes sí son portables.

El escenario (`campaigns/analisis-financiero-v1/scenario.yaml`; referencia local histórica) deriva del
ampliado anterior cambiando únicamente su ID: enero–junio de 2023, seis activaciones,
mismos mensajes, 50 empresas, 100.000 USD ficticios, máximo diez posiciones y lag anual
estimado de 120 días. Límites por activación: 60 llamadas, 90 herramientas, 1200 segundos,
reserva temporal 90 segundos y 1048576 bytes de contexto. Misma reserva de dos llamadas
de consolidación y una respuesta. No se requiere consumir todo el presupuesto.

Perfil fijado para ambos brazos: OpenAI `gpt-6-luna`, razonamiento `medium`, salida máxima
16000. No se modifica configuración automáticamente. Registrar y contrastar perfil,
código, wheel, instrucciones y límites efectivos antes y durante ambos brazos; no
actualizarlos entre campañas. La identidad del runtime existente impide reanudar bajo
otra configuración. No se recupera el chat entre activaciones.

Dataset común: `artifacts/price-review-adjusted-v3/data.json`, SHA-256
`2b65121feae3ae0f2784584f53af6649856d988997eda6eb402f0a71f2b58745`.
Es local e ignorado: si falta o difiere, recuperar el original; no regenerarlo silenciosamente.
La [revisión de precios](../colaboracion-historica-v1/price-review.md) conserva sus límites.

## Preparación local y comandos posteriores

Desde la raíz Git, este check no construye clientes ni consulta datos remotos:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal validate benchmarks/analisis-financiero-v1/scenario.yaml
```

La opción `--instructions-dir` acepta un conjunto completo que sustituye las plantillas;
no se acumula mediante `--instructions`. En condición deliberativa exige exactamente
`agente.md`, `deliberacion.md` e `investigacion-financiera.md`, no vacíos y UTF-8, sin
subcarpetas ni entradas adicionales. La validación precede a la identidad del runtime
y construcción de clientes. Sin opción se copian los prompts nuevos. Para baseline
un conjunto explícito requiere únicamente los dos archivos no deliberativos.

Los comandos siguientes **llaman a proveedores y quedan sin ejecutar**. Requieren
verificar previamente el perfil fijado, hash del dataset y una misma revisión técnica:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal run benchmarks/analisis-financiero-v1/scenario.yaml --condition deliberative --instructions-dir benchmarks/analisis-financiero-v1/control --data artifacts/price-review-adjusted-v3/data.json --output artifacts/analisis-financiero-control-v1
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal run benchmarks/analisis-financiero-v1/scenario.yaml --condition deliberative --data artifacts/price-review-adjusted-v3/data.json --output artifacts/analisis-financiero-intervencion-v1
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal resume artifacts/analisis-financiero-intervencion-v1
```

Los destinos deben ser nuevos. `resume` usa las instrucciones copiadas y congeladas;
no admite seleccionar otro conjunto y rechaza cambios. No modificar capturas anteriores.
No usar `preflight` como check documental: exporta Findata. `--data` reutiliza el dataset
local; la web sigue viva y sus resultados pueden diferir entre condiciones.

## Pruebas pequeñas y aceptación semántica pendiente

Los casos preparados (`campaigns/analisis-financiero-v1/semantic-cases.json`; referencia local histórica)
son un corpus sintético por etapas, no un schema ejecutable del controlador. No se ha
implementado otro runner. Una prueba posterior requerirá un transporte controlado:
publicar exclusivamente las fuentes de la etapa actual, impedir web y datos externos,
arrancar cada activación en un proceso nuevo y conservar estado solo dentro de su brazo.
El corpus completo y la rúbrica quedan fuera de las instrucciones y memoria del agente;
no revelar estímulos futuros ni respuestas esperadas. Mantener modelo y presupuesto
idénticos entre brazos y archivar entradas, herramientas, respuesta y snapshots.

La [rúbrica](rubric.md) es exclusiva del revisor. La prueba sintética puede revisar
creación, recuperación sin recordatorio específico, contradicción, redundancia,
dependencia pendiente y bloqueo con una alternativa investigable. No se ejecuta como
parte de esta entrega, tampoco con un LLM real.

La integración local H1 → V1 → evaluación usa dos procesos: guarda un escenario de
20 USD, recibe un cambio de EPS supuesto de 2 a 1 USD, consulta los tres documentos y
conserva el escenario revisado de 10 USD y su evaluación, con materiales de cálculo.
Otra rama conserva revisión pendiente de valoración y evaluación antes de fallar.

Los tests de clientes programados comprueban composición de instrucciones, operaciones
de archivos y cálculo, referencias a materiales, recuperación tras reiniciar, revisión
pendiente durable y conservación tras fallo. Las acciones están prescritas por el test:
no prueban que un LLM las elija ni entienda sus fundamentos.

## Interpretación y límites

Revisar evidencia → hipótesis → valoración → evaluación → cambio persistido,
contrastando fundamentos, materialidad, fidelidad numérica, comparaciones y progreso
de pendientes. Informar también casos contrarios y no observables, errores, cierres y
reintentos. Registrar recursos y coste solo cuando sean observables.

La evidencia será prometedora si recupera y usa fundamentos, corrige lo afectado sin
inventar cifras, conserva incertidumbre y hace progresar preguntas materiales con coste
proporcionado. Un fallo de continuidad o valoración no se compensa con más documentos.
No exigir operaciones ni cambios de opinión. Una única pareja es exploratoria; no
establece superioridad estable, causalidad por componente ni rentabilidad.

Persisten precios ajustados, disponibilidad estimada, revisiones, universo seleccionado,
conocimiento previo del modelo y web viva: `published_at` no garantiza contenido
históricamente válido. El simulador no ofrece lectura de documentos web completos.
No se incorpora DCF, motor de reglas, base de datos ni modificación de herramientas.
No confundir checks locales con aceptación semántica o resultados de inversión.

## Procedencia y disponibilidad

Consolidación del 2026-10-31: se conserva el registro documental fechado y sus
condiciones; no se repitió la ejecución ni se recuperaron capturas ausentes. La preparación o implementación descrita no demuestra que se haya ejecutado el contraste
controlado propuesto. Las observaciones reales relacionadas se identifican por separado
en el [registro experimental](../README.md). Las rutas locales citadas son procedencia
histórica y pueden no existir en el checkout o quedar en un archivo externo de ubicación
no fijada. Si no están disponibles los originales, sus cifras y verificaciones son
afirmaciones del registro previo, no resultados nuevamente comprobados en esta revisión.
