# Contexto continuo v1

Estado: piloto original y repetición con entrega corregida ejecutados; ver [hallazgos](findings.md).
Fecha: 2026-10-26. Encargo: sustituir el tokenizer y preparar el escenario, con
verificación local. Encargo posterior explícito: corregir la entrega y repetir el piloto
con proveedor, conservando la ejecución original. No implica aceptación semántica.

## Pregunta e hipótesis

¿Puede el mismo A conservar el mandato y avanzar a través de varias reconstrucciones
de contexto utilizando sus archivos? Hipótesis: índice y agenda, recuperados con mandato
y petición inicial, permiten retomar fundamentos e intenciones sin una cola de conversación
ni un resumen adicional. Los tests no demuestran esta hipótesis semántica.

## Condición implementada

Un solo A en modo continuo; el texto intermedio no finaliza el encargo. El presupuesto
local mide JSON tipado en bytes UTF-8: `ceil(input_bytes * 1.10) + max_output_tokens * 8`.
Los ocho bytes por token máximo de salida son una reserva heurística, no un conteo de
tokens ni una garantía sobre el payload remoto. Se conserva el consumo real informado
por el proveedor cuando existe. Se retira tiktoken como requisito; no se cambia de modelo.

Los valores generales son máximo 524288 bytes y umbral 262144; el piloto fija el umbral
en 196608 para observar renovaciones antes. Ambos incluyen margen y reserva. Se permiten
hasta cuatro llamadas de consolidación, descontadas del presupuesto total. El umbral
dispara consolidación, pero no oculta un resultado que cabe bajo el máximo. Solo superar
el máximo reemplaza la entrega por referencia. Si un intercambio no cabe, se pausa
preservando evidencia. Memoria de archivos existente, índice y agenda
automáticos y recuperación adicional selectiva. Las escrituras de consolidación son opcionales.

La [arquitectura](../../architecture.md#modo-continuo-experimental--2026-10-26) posee el contrato;
[desarrollo](../../development.md#ejecutar-el-modo-continuo-experimental), la interfaz general.

## Escenario congelado del piloto

Las [definiciones](../../../benchmarks/contexto-continuo-v1) contienen
[configuración](../../../benchmarks/contexto-continuo-v1/scenario.json),
[mandato](../../../benchmarks/contexto-continuo-v1/mandato.md),
[petición](../../../benchmarks/contexto-continuo-v1/peticion.md) y
[rúbrica](../../../benchmarks/contexto-continuo-v1/rubrica.md).

- Fecha única: 2023-01-01, sin avance de calendario. Universo de 50 empresas, 100000 USD
  ficticios, máximo diez posiciones, cartera y memoria nuevas. Las órdenes quedan pendientes.
- Pregunta: elegir investigaciones útiles sobre candidatas a inversión a cinco años,
  conservando fundamentos y límites. No se exige comprar ni recorrer todo el universo.
- Perfil: OpenAI `gpt-6-luna`, `medium`, salida máxima 16000; sin sustitución automática.
- Límites globales: 60 llamadas, 90 herramientas y 1200 segundos; timeout por operación
  de 300 segundos. La consolidación consume estos mismos recursos.
- Presupuesto de contexto: máximo 524288 y umbral 196608 bytes; reserva de salida de
  128000 bytes. Se valida la semilla efectiva más 2048 bytes de margen de arranque.
- Fuentes: dataset local existente, SHA-256
  `4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`.
  Copia conservada en `artifacts/analisis-financiero-intervencion-v1/simulador/data.json`.
  Se reutilizan únicamente sus datos, nunca estado, cartera, memoria o instrucciones antiguos.
- Web desactivada mediante `allow_web: false`: no se ofrece `search_web`. Las otras
  simulaciones conservan la web por defecto. No hay exportación Findata ni acceso a BD
  durante preparación o campaña; el LLM real se usa solo al lanzar manualmente el piloto.

La fuente contiene 25400 precios y 6619 observaciones fundamentales. El hash identifica
esta copia concreta, no el archivo original de otro protocolo cuyo hash era distinto.
Conserva limitaciones de precios ajustados retrospectivos y fundamentales revisados o con
disponibilidad estimada. El filtrado histórico no elimina el conocimiento previo del modelo.
Esto no es un backtest limpio ni una evaluación de alfa. El dataset permanece local e
ignorado: las definiciones son portables, los datos requieren transferencia explícita.

## Preparación y ejecución manual

Desde la raíz Git, este comando no crea clientes, no consulta servicios y rechaza un
destino existente o un dataset con otro hash:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks.continuous prepare artifacts/contexto-continuo-v1/piloto --source-data artifacts/analisis-financiero-intervencion-v1/simulador/data.json
.\.venv\Scripts\python.exe -m research_benchmarks.continuous check artifacts/contexto-continuo-v1/piloto
```

La preparación valida cobertura de datos, perfil y contexto inicial con los schemas
efectivos; copia mandato/petición/rúbrica/configuración, instrucciones actuales y dataset;
crea `agente/estado/` y `simulador/` nuevos; y registra hashes y runtime instalado en
`preparacion.json`. `preflight.json` distingue preparación local de aceptación del proveedor.
`command.json` contiene el comando completo con rutas absolutas y límites. Se usa
`--continue` porque el experimento ya está creado, aunque todavía no tiene runs.

El siguiente comando **llama al proveedor y ejecuta el piloto**. No forma parte de los
checks locales; el script comprueba primero la congelación y se niega a reutilizar un intento:

```powershell
& ./benchmarks/contexto-continuo-v1/run-pilot.ps1
```

Para otro destino, usar `-Pilot RUTA` tras prepararlo. No pasar estas definiciones al
lanzador `longitudinal run`: mantiene activaciones acotadas y otro schema. No borrar
intentos para repetirlos. Los cambios de código, dependencias, perfil o entradas exigen
un destino nuevo. La comprobación no autentica los manifiestos frente a edición deliberada
ni confirma disponibilidad del servicio remoto.

## Evaluación y siguiente fase

Revisar con la rúbrica externa las trazas y archivos antes/después de cada renovación.
Exigir al menos tres renovaciones y trabajo posterior a la tercera; si los límites se
alcanzan antes, registrar exposición insuficiente, sin declarar éxito. No forzar contenido
de relleno ni alterar el umbral a mitad del intento para fabricar renovaciones.

Separar aceptación técnica, conservación semántica y progreso material. Revisar mandato,
pregunta activa, fundamentos, intentos agotados, recuperación selectiva, revisión y repetición.
Conservar referencias a eventos/calls y archivos que sostengan cada juicio. Registrar
coste/uso solo cuando sea observable, y no confundir cantidad de acciones con avance.

Si el piloto ofrece exposición y continuidad suficientes, preparar otro intento de mayor
duración con presupuesto y criterio fijados antes. No se ha autorizado ni configurado
una ejecución indefinida. La repetición autorizada mantiene los límites originales.
El volumen en disco y las listas de eventos/trazas en RAM no
tienen límite total: observar memoria del proceso antes de ampliar a horas. No hay espera
autónoma ni reinicio automático. La recuperación entre procesos con `--continue` es una
prueba separada y solo conserva lo escrito, no razonamiento perdido.

## Verificación local y trazabilidad

Clientes programados, workspaces temporales y cartera sintética, sin modelos ni bases
remotas. Probar renovaciones, recuperación de agenda, mandato/petición, UTF-8 y continuaciones
opacas, límite antes de cada llamada, paginación, consolidación, errores y cancelación.
La preparación se prueba con red prohibida, hash incorrecto, deriva de perfil/entradas,
rechazo de sobrescritura y ausencia de web; el modo acotado mantiene sus regresiones.

Conservar manifiesto, eventos, `conversacion-completa.jsonl`, ventana final, resultados
originales, snapshots y trazas. Cada reconstrucción registra tamaños en bytes antes/después,
archivos modificados y recursos consumidos. No reinterpretar capturas antiguas en tokens.
Una propuesta arquitectónica futura necesita hallazgos y decisión explícita, separados de checks.

## Repetición autorizada: entrega al cruzar el umbral

La campaña original queda intacta en `artifacts/contexto-continuo-v1/piloto`.
El nuevo intento usa `artifacts/contexto-continuo-v1/piloto-entrega-maximo-v2`;
se prepara con el dataset del simulador original y las mismas definiciones. Antes de
lanzarlo se comprueba igualdad de configuración, mandato, petición, rúbrica, instrucciones,
datos, perfil y wheel registrado, con memoria y cartera nuevas. El único cambio de
comportamiento es comparar la entrega con el máximo en ambas fases. Las herramientas
conservan su límite de entrega directa de 32 KiB y su paginación.

Registrar errores, referencias sin contenido, lectura efectiva de las páginas, renovaciones
y avance semántico, además de llamadas/uso. Una sola repetición con un modelo real no
demuestra causalidad ni superioridad general. Los [hallazgos](findings.md) separan las
observaciones de cada intento y la interpretación.

## V3 — Autorregulación mediante instrucciones y renovación menos frecuente

Encargo del 2026-10-27: incorporar en español las orientaciones sobre progreso,
conocimiento, recuperación y coherencia, y reducir la frecuencia de recomposición.
Implementado y verificado localmente; campaña v3 sin ejecutar. Las
[definiciones v3](../../../benchmarks/contexto-continuo-v3/scenario.json) conservan
mandato, petición, dataset, perfil, fecha, máximo de contexto y presupuestos del piloto.
La [rúbrica ampliada](../../../benchmarks/contexto-continuo-v3/rubrica.md) añade criterios
de autorregulación. Las definiciones v1 y las copias de los intentos anteriores se conservan.

Los prompts vigentes de agente, deliberación y análisis financiero refuerzan revisión
del progreso durante el trabajo, interpretación y conservación ordinarias, recuperación
intencional y corrección de afirmaciones afectadas. La consolidación debe guardar solo
lo pendiente y terminar en cuanto permita continuar. No se añade reflexión obligatoria
desde el harness, herramienta ni planificador; esos mecanismos siguen fuera de v3.
Los experimentos nuevos reciben estas plantillas; las instrucciones ya copiadas en
experimentos existentes no se actualizan automáticamente.

El umbral v3 sube de 196608 a **262144 bytes**, el valor general ya existente;
el máximo permanece en 524288. La repetición v2 reconstruyó semillas de aproximadamente
169–170 KB, incluida la reserva de salida de 128000 bytes. El umbral anterior dejaba
unos 27 KB para crecer; el nuevo permite unos 92 KB antes de considerar el aumento por
los prompts v3. Se pretende acercar la frecuencia a tres o cuatro renovaciones en 60
llamadas, sin garantizarla: depende del contenido generado y recuperado. No se impone
una cuota ni se suprime una renovación necesaria. Se conserva el máximo de cuatro
llamadas por consolidación y todas las protecciones de tamaño.

Este encargo cambia dos factores: instrucciones y umbral. Una futura comparación con v2
evaluará el conjunto; no podrá atribuir por separado sus efectos. Registrar progreso,
coherencia, repeticiones y coste, además del número efectivo de renovaciones. Menos
renovaciones no acredita mejor investigación y puede aumentar el contexto reenviado.

Preparación y comprobación **sin proveedores** en un destino nuevo:

```powershell
.\.venv\Scripts\python.exe -m research_benchmarks.continuous prepare artifacts/contexto-continuo-v3/piloto --definition benchmarks/contexto-continuo-v3 --source-data artifacts/analisis-financiero-intervencion-v1/simulador/data.json
.\.venv\Scripts\python.exe -m research_benchmarks.continuous check artifacts/contexto-continuo-v3/piloto
```

El lanzador existente admite ese destino mediante `-Pilot`; ejecutarlo llama al proveedor.
Esta entrega no ejecuta la campaña ni modifica capturas históricas.
