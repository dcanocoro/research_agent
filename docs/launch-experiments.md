# Preparar, lanzar y revisar experimentos

## Organización y revisión general

El [mapa de módulos](modules.md) describe rutas y activación actuales.
En continuo, `--general-review off` desactiva las llamadas periódicas y finales de
revisión general. Por defecto permanece activada. Repetir la elección en cada run;
Progress usa su propio evaluador y desactiva la revisión general. La opción explícita
requiere `--continuous`; `--general-review on` con Progress se rechaza antes de crear clientes.
Los checkpoints, límites y persistencia permanecen activos. El mecanismo V8 ha sido
retirado; sus instrucciones históricas no son comandos vigentes.

## 1. Preparar la pregunta y las entradas

Define qué quieres comprobar y qué resultado te permitiría valorarlo. Elige una
carpeta en `campaigns/` y edita sus archivos antes de lanzar:

| Nombre | Qué prueba hoy | Entradas |
|---|---|---|
| `regimenes` | Continuidad E2, renovación de contexto y revisión general | [Mandato](../campaigns/regimenes/mandato.md) y [petición](../campaigns/regimenes/peticion.md) |
| `progreso` | Compromisos verificables con continuo opcional | [Mandato](../campaigns/progreso/mandato.md), [petición](../campaigns/progreso/peticion.md) y [objetivo](../campaigns/progreso/objetivo.json) |
| `multiagente` | A investiga y encarga a B integrar conocimiento | [Mandato](../campaigns/multiagente/mandato.md) y [petición](../campaigns/multiagente/peticion.md) |

El mandato fija el encargo duradero y sus restricciones; la petición indica por
dónde empezar. Las tres pruebas usan el mismo motor. En multiagente, B trabaja
secuencialmente con el material recibido; no investiga fuentes nuevas.

## 2. Lanzar

Desde la raíz del repositorio, con `.env` configurado y el entorno virtual activo:

```powershell
python -m research_agent --name regimenes --continuous --max-calls 100 --output artifacts/prueba-regimenes --new
python -m research_agent --name progreso --continuous --max-calls 100 --output artifacts/prueba-progreso --new
python -m research_agent --name multiagente --continuous --max-calls 100 --output artifacts/prueba-multiagente --new
```

Estos comandos consumen llamadas reales. `--name` carga los archivos de la carpeta;
`--output` es el destino exacto y debe ser nuevo con `--new`. Puedes lanzar los tres
en terminales distintas usando salidas distintas; comparten límites del proveedor.
No cambies código, configuración o entradas mientras se ejecutan.

El presupuesto incluye investigación y revisiones. Multiagente exige 100 llamadas:
70 para A/controlador y 30 protegidas para B, sin transferir a A las sobrantes.
El timeout global predeterminado es 24 horas. No hay máximo global de herramientas;
se conservan timeouts por operación y límites internos de B.

`--name progreso` activa el nuevo mecanismo de [compromisos](experiments/progress/protocol.md).
También puede ejecutarse sin `--continuous`. El valor predeterminado es 100 llamadas
totales y hasta 15 de A por tramo (`--progress-step-calls`). Para una petición libre:

```powershell
python -m research_agent "Evalúa Microsoft como inversión" --experiment artifacts/progress-01 --new --run-name msft --progress
```

Sin `--objective`, una llamada genera criterios que quedan fijos y se recuperan al
continuar. Con `--objective PATH`, se usa el JSON explícito. Progress no se combina
todavía con B. No añade herramientas de valoración; para cálculos Python opcionales
se conserva `--python` y sus límites existentes.

Si una evaluación agota el presupuesto interno del proveedor, aumentar únicamente
el timeout del runtime no elimina ese límite. Para una repetición con hasta 180
segundos por llamada, configurar ambos valores en la terminal de lanzamiento:

```powershell
$env:LLM_TIMEOUT_SECONDS = "180"
$env:LLM_CALL_BUDGET_SECONDS = "180"
python -m research_agent --name progreso --continuous --max-calls 100 --output artifacts/progreso-timeout-180 --new
```

Comprobar `configuration.timeout_seconds` y `configuration.call_budget_seconds`
en el manifiesto efectivo. Estos valores no amplían las 100 llamadas ni garantizan
que el proveedor complete la evaluación; conservar el intento fallido y usar otra salida.

## 3. Continuar o empezar otra prueba

Para retomar el mismo conocimiento, conserva nombre y salida y sustituye `--new`
por `--continue`. El presupuesto de llamadas vuelve a empezar:

```powershell
python -m research_agent --name multiagente --continuous --max-calls 100 --output artifacts/prueba-multiagente --continue
```

Se reutilizan archivos y se recupera el estado operativo compatible, no toda la
conversación anterior. Para un contraste nuevo, usa otra salida con `--new`.

## 4. Revisar y registrar lo observado

La CLI imprime la carpeta del run. Revisa `resultado.json` (estado, motivo de parada
y consumo), `manifiesto.json` (configuración e instrucciones), `respuesta.md` y
`eventos.jsonl`. El conocimiento queda en `estado/`; los compromisos y evaluaciones en
`progreso/` del run, y los encargos de B en `control-integracion/`. Las capturas V8
históricas permanecen en `evaluacion-objetivo/` y no se migran.

Comprueba si conserva el hilo, resuelve carencias y guarda avances coherentes.
Una pausa por presupuesto no significa investigación completada. Para comparar,
controla entradas, modelo, presupuesto y criterios; conserva también fallos e
interrupciones. Resume observaciones y límites según la [metodología](experiments.md)
y el [registro experimental](experiments/README.md). `artifacts/` es local e ignorado:
su ruta no sustituye un informe portable. Más pasos o archivos no prueban mejor análisis.

Para campañas gestionadas con definiciones y varios casos, consulta
[Campañas](campaigns.md); esta guía describe el lanzamiento manual por nombre.
