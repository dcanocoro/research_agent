# Campañas de investigación

Las definiciones viven en `campaigns/`; el código de preparación, ejecución y revisión
vive en `src/research_campaigns/`. Una definición es la receta; una campaña es una
ejecución concreta en una carpeta nueva. Solo A investiga: el controlador prepara
entradas, lanza su CLI y conserva evidencia. El núcleo no importa el controlador.

## Definir una campaña

Crear `campaigns/nombre/` con exactamente una entrada:

| Entrada | Modalidad | Contenido |
|---|---|---|
| `suite.yaml` | Casos con documentos | Lista de `case.yaml`; cada caso define contexto, competencias, dificultad, rúbrica y sesiones con mensaje y publicaciones. |
| `scenario.yaml` | Histórica | Fechas, universo, efectivo, posiciones, disponibilidad anual estimada, mensajes fechados, límites y revisión de precios. |
| `scenario.json` | Continua | Fecha fija, dataset por hash, perfil esperado, web desactivada y presupuestos continuos; acompañar con `mandato.md`, `peticion.md` y `rubrica.md`. |

Ejemplos: [suite](../campaigns/longitudinal-v1/suite.yaml),
[histórica](../campaigns/intencion-persistente-v1/scenario-amplio.yaml) y
[continua](../campaigns/contexto-continuo-v3/scenario.json). Los archivos alternativos
como `scenario-amplio.yaml` son referencias: para lanzarlos con esta interfaz, crear
un directorio de definición separado con el nombre de entrada `scenario.yaml`.

Las suites usan `schema_version: campaign-suite-v1`. Las modalidades histórica y
continua conservan sus esquemas específicos. Las publicaciones son archivos UTF-8
bajo `entradas/`, sin sobrescribir entradas anteriores. Los casos están aislados;
entre sesiones se conservan archivos, sin restaurar el chat.

Antes de ejecutar, fijar pregunta, condiciones, controles y rúbrica en el protocolo
de `docs/experiments/`. Un escenario no demuestra que una campaña se haya ejecutado.

## Comandos

Desde la raíz, con el entorno instalado:

```powershell
.\.venv\Scripts\python.exe -m research_campaigns validate campaigns/longitudinal-v1
.\.venv\Scripts\python.exe -m research_campaigns run campaigns/longitudinal-v1 --case S2 --output artifacts/mi-campana
.\.venv\Scripts\python.exe -m research_campaigns report artifacts/mi-campana

.\.venv\Scripts\python.exe -m research_campaigns validate campaigns/analisis-financiero-v1 --data RUTA/data.json
.\.venv\Scripts\python.exe -m research_campaigns run campaigns/analisis-financiero-v1 --data RUTA/data.json --condition deliberative --output artifacts/mi-historica
.\.venv\Scripts\python.exe -m research_campaigns resume artifacts/mi-historica

.\.venv\Scripts\python.exe -m research_campaigns run campaigns/contexto-continuo-v3 --data RUTA/data.json --output artifacts/mi-continua
```

`validate` solo lee definiciones y, con `--data`, verifica datos locales. No crea una
campaña ni consulta servicios. `run` prepara y ejecuta el agente real; `--output`
es el destino exacto, debe ser nuevo y estar separado de fuentes y definición.

`--case` corresponde a suites. `--condition baseline|deliberative` y
`--instructions-dir` corresponden a históricas; el directorio sustituye el conjunto
completo de instrucciones. Sin `--data`, la histórica exporta Findata en solo lectura.
La continua exige dataset local y verifica hash, perfil y presupuesto inicial antes
de lanzar. No hay sustitución automática del modelo.

`resume` solo admite campañas históricas nuevas: comprueba configuración, fuentes,
instrucciones y datos congelados. Recupera una activación completa o restaura el
checkpoint para repetir una interrumpida, conservando el intento y estado fallidos.
Las suites y continuas no ofrecen reanudación automática.

Retornos: 0 para operación completada; 1 para ejecución incompleta o interrumpida;
2 para entradas o configuración inválidas. Son resultados operativos.

## Revisar los resultados

```text
mi-campana/
  README.md
  campaign.json
  definicion/
  instrucciones/
  estado/
  ejecuciones/
  simulador/       # Si corresponde
  recuperacion/    # Checkpoints históricos
```

Las suites sitúan `instrucciones/`, `estado/` y `ejecuciones/` bajo `casos/ID/`.
Abrir primero **`README.md`**: describe condiciones y cierre, sesiones, consumo
observado, respuestas, snapshots, diagnósticos y conocimiento vigente. La simulación
se consulta desde `simulador/state.json`, con posiciones, órdenes y comunicaciones.

`campaign.json` es el único registro de control: versión, modalidad, configuración,
hashes, comprobaciones, progreso e intentos. Se escribe atómicamente antes y después
del lanzamiento. Los mensajes y documentos originales quedan en `definicion/`;
las instrucciones efectivas, en `instrucciones/`. La captura nativa de cada ejecución
conserva petición, manifiesto, resultado, respuesta, eventos, snapshots y trazas.
Los checkpoints necesarios para recuperar no sustituyen esos snapshots.

El informe se actualiza durante la campaña y puede regenerarse con `report`; solo
escribe `README.md`, comprueba capturas y señala ausencias sin reescribir evidencia.
Una interrupción abrupta puede dejar el informe desactualizado. Los consumos ausentes
se muestran como desconocidos. No hay puntuación ni juicio semántico automáticos.

No se generan índices de pasos, conversiones compactas ni copias JSON de informes
finales del simulador. stdout se retira en ejecuciones satisfactorias y los logs
vacíos se omiten; los diagnósticos no vacíos se conservan.

## Límites y formatos retirados

Los pilotos continuos admiten `objective.json` opcional junto a `scenario.json`.
Se valida y congela en `definicion/`, se entrega mediante `--objective` y se incluye
en la comprobación de contexto inicial. `campaign.json` conserva definición, hash y
política V8. La comprobación rechaza inputs alterados y la inspección detecta un run
con otro objetivo. No se añade `resume` al piloto continuo: una continuación manual
es otro run; después de una tentativa `check` sigue exigiendo un piloto nuevo.

Los informes muestran llamadas del evaluador, última cobertura completa y estado de
la evaluación actual, además de fallos, parciales y omisiones. Su lectura estructural
no evalúa calidad semántica. Véase el [protocolo V8](experiments/objetivos-v8/protocol.md).

La reorganización del 2026-10-27 no modifica los artefactos anteriores y no ofrece
compatibilidad de comandos, lectura compacta ni reanudación de campañas antiguas.
Los ejemplos fechados de protocolos y entregas conservan su sintaxis histórica;
esta guía posee la operación vigente.

`artifacts/` es local e ignorado por Git. Para trasladar evidencia, conservar la
carpeta completa revisando datos privados. Captura íntegra, cierre operativo,
calidad semántica y resultados de inversión son comprobaciones diferentes.
