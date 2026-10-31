# V8: repetición de investigación continua con datos reales

Fecha: 2026-10-31. Autorización: el usuario solicita ejecutar otra campaña como V7
y conservarla. Protocolo fijado antes del lanzamiento; estado nuevo, sin evidencia
introducida ni empresas seleccionadas para el investigador.

## Condiciones

Repetir el [mandato V7](../inversion-real-v7/mandato.md), con fecha de arranque actual,
misma petición y rúbrica externa. La diferencia es el mecanismo de objetivos V8 y
su [objetivo fijo](objective.json), derivado del mandato. Sus siete criterios pesan
igual y permanecen congelados. La rúbrica externa no se entrega al investigador ni
se sustituye por distancia. Una insuficiencia fundada sigue siendo una conclusión
válida; no se exige comprar ni fabricar una valoración.

Findata PostgreSQL en transacciones de solo lectura, web y documentos Tavily,
aritmética y Python habilitado. Sin simulador, cartera conectada, órdenes reales,
ingestas ni migraciones. El preflight comprueba perfil, servicios, Python y fechas
disponibles; sus muestras no se incorporan al estado ni seleccionan empresas.

Perfil esperado: OpenAI `gpt-6-luna`, razonamiento medium, salida máxima 16000.
200 llamadas ordinarias acumuladas (investigación y consolidación), 300 herramientas,
3600 segundos acumulados de ejecución; 300 segundos por operación. Contexto máximo
524288 y umbral 262144 bytes. Timeout y presupuesto del proveedor: 180 segundos desde
el inicio, como la última tentativa V7; difiere de sus dos primeras tentativas de 45 s.
Autorrevisión cada diez llamadas de investigación y evaluación V8 cada veinte son
adicionales al máximo ordinario y comparten deadline. No se modifica código ni prompts
durante la campaña. El contador de revisión/evaluación se reinicia si hay otro run.

## Ejecución y conservación

Usar la CLI nativa sin `--simulation` y con `--objective`. El lanzador local reutiliza
creación, ejecución, inspección e informe de `research_campaigns`, como V7; el comando
de pilotos congelados no sirve para este entorno vivo. Destino nuevo:
`artifacts/inversion-real-v8/piloto-200-llamadas`. Conservar definición, instrucciones,
objetivo, perfil, identidad del wheel/código, preflight, comandos, logs, materiales,
snapshots, evaluaciones y trazas. `campaign.json` declara `source_mode=live`.

Si aparece un fallo operativo recuperable, conservar la tentativa y continuar desde
archivos descontando llamadas ordinarias, herramientas y tiempo ya usados. No restaurar
chat, repetir deliberadamente herramientas ni aumentar los máximos. Conservar cualquier
desviación y no usar reinicios para eludir un error persistente. Los límites agotados
cierran la campaña; `interrupted: call_limit` no equivale a mandato cumplido y no se
reescribe como `completed` para mejorar el resultado.

El informe local conserva todas las tentativas y sus presupuestos. Los artefactos son
locales e ignorados por Git; no son evidencia portable por enlazarlos. La definición
y los hallazgos documentales omiten credenciales y payloads privados.

## Evaluación

Revisar resultado, fidelidad escogida, continuidad, respuesta al feedback, cobertura
y consumo disponible. Distinguir lo observado del juicio del evaluador y de una
interpretación humana. Conservar fallos JSON, paquetes parciales y omisiones.

No es un contraste causal V7/V8: cambian tiempo, fuentes vivas y criterios explícitos,
y V7 tuvo reinicios y correcciones. No es backtest ni prueba de rentabilidad. Los
hallazgos se redactan después de ejecutar, con alcance y límites reales de la captura.
