# V7: investigación continua con datos reales

Fecha: 2026-10-30. Campaña autorizada expresamente por el usuario tras implementar V7.
Diseño fijado antes del lanzamiento. Estado inicial nuevo; una ejecución continua,
sin sesiones artificiales, corpus congelado, evidencia introducida ni universo recortado.

## Pregunta y condiciones

¿Puede V7 convertir 200 llamadas ordinarias en expedientes, evaluaciones y una comparación
útil para decidir qué inversiones merecen atención, conservando fundamentos a través de
renovaciones? Usa PostgreSQL Findata en transacciones de solo lectura, web y extracción
Tavily, aritmética y Python opcional habilitado. No se modifican runtime ni prompts
durante la ejecución. No hay cartera conectada ni ejecución de órdenes reales.

Perfil efectivo esperado: OpenAI `gpt-6-luna`, razonamiento medium, salida 16000.
Límites: 200 llamadas ordinarias, 300 herramientas, 3600 s globales, 300 s por operación,
umbral 262144 / máximo 524288 bytes. Autor revisiones cada diez llamadas de investigación
y revisiones externas intermedia/final tienen presupuesto adicional y comparten tiempo.
La política real y todos los intentos se conservan en captura nativa; 200 no es total LLM.

El preflight verifica servicios, perfil, Python, modo de transacción y muestra cobertura
sin seleccionar empresas para el investigador. Fecha de arranque: 30 de octubre de 2026.
Los precios almacenados observados llegan al 9 de octubre: no son cotizaciones del día.
Se mantienen fechas, monedas, unidades, procedencia y ausencias; no se ingieren datos.

## Ejecución y evidencia

La CLI continua acepta datos reales al omitir `--simulation`; el lanzador de pilotos
`research_campaigns run` exige dataset congelado y no sirve para este encargo. Se usa
la CLI nativa mediante un lanzador local que reutiliza creación, captura e inspección
de campañas, sin cambiar el runtime ni añadir una modalidad al agente.

Definición: mandato, petición y rúbrica de esta carpeta. El destino nuevo es
`artifacts/inversion-real-v7/piloto-200-llamadas`; lanzador y preflight en su padre.
`campaign.json` identifica `mode=continuous` y `source_mode=live` explícitamente;
`research_campaigns report` puede regenerar su informe, sin afirmar compatibilidad
con validate/run/resume de pilotos congelados. El estado fresco se prepara antes de
lanzar la CLI con `--continue`; no es continuación de una investigación anterior.

Se conservan hashes de código, instrucciones, definición y wheel instalado, perfil,
comando, preflight, todas las tentativas y errores. Las respuestas reales de servicios
se archivan en materiales; la BD y web no se congelan ni serán idénticas al repetir.
Los artefactos son locales, ignorados por Git y no portables por el enlace a esta ruta.

## Evaluación

La [rúbrica](rubrica.md) se fija antes de ejecutar y no se entrega al investigador.
Examinar estados y fuentes, además de informes de revisión. Captura completa y checks
numéricos no acreditan calidad económica. Agotar llamadas significa interrupción por
presupuesto; la etiqueta failed del runner no se cambia para declarar el mandato cumplido.
Los hallazgos distinguirán observación, interpretación, hipótesis y límites.

Se evalúa V7 en entorno vivo, sin control V6 equivalente. Cambian datos, universo, web,
mandato y presupuesto respecto al piloto V6. No permite atribuir mejoras a V7 ni medir
rentabilidad, y no es backtest. Una respuesta de insuficiencia puede ser correcta;
no se exige comprar, producir cuotas de expedientes ni fabricar valoración.
