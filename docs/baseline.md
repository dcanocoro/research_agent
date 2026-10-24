# Baseline de Research Agent — 2026-10-18

Estado: referencia elegida por el usuario para próximos experimentos. No implica
aceptación financiera ni elección de la arquitectura final de FinMate.

## Identidad de la referencia

Código de referencia: `20afee95ed6e99f9ba25394abfa30b3293ce461b`.
Esta revisión documental no cambia el comportamiento del agente. El árbol al comenzar
la revisión ya tenía eliminados los cuatro documentos de E001/E002 y `src/research_agent/py.typed`;
se conservan esos cambios. Por ello, el commit por sí solo no describe todo el árbol
actual: comprobar también `git status` y el diff antes de fijar un contraste nuevo.

| Distribución local | Versión / identidad observada |
|---|---|
| Research Agent | `0.1.0`, instalación editable |
| Findata y bibliotecas compartidas | `0.1.0`; wheel SHA-256 `70cd4a370e1ca4690631f104291a7cc3281acbf6972e43b3c14cb18fe7662e4f` |
| tzdata | `2026.2` |

Las huellas siguientes se comprobaron contra los paquetes instalados y coinciden con
las del manifiesto del run de NVIDIA. Se calculan como en `bootstrap.py`, sobre rutas
relativas y contenidos `.py`/`.md`; no incluyen documentación externa al paquete,
datos, `.env`, `py.typed` ni toda la distribución de dependencias.

| Paquete | `configuration.code_sha256` |
|---|---|
| research_agent | `c46f109a2f580585628fa8c57cd72f77829e08038cf3294920ffa1908c3b6be6` |
| findata | `7275d76edaa6fcab438f7998519e8c4845d6bf649bd4f25d54c9cb4e2bd74018` |
| infra | `c7d497c24c68e256af539fbc572ec51ba2745efe99ffc14b51d8b9b5c6f3cb42` |
| runtime_contracts | `d3a95ffa862398dee65b408fb76c159113f63b547478d6430271c34e32521677` |

## Contrato que se compara

- Un solo A, con ciclo modelo/herramientas y un máximo de una herramienta por llamada.
  La respuesta final es texto sin herramienta; escribir conocimiento es una acción distinta.
- Estado UTF-8 por experimento, materiales originales automáticos, instrucciones copiadas
  y archivo por run. `--new` aísla; `--continue` reutiliza archivos con una instancia nueva.
  Solo `indice.md` entra automáticamente; el resto se lee bajo demanda.
- Defaults de 18 llamadas al modelo, 30 herramientas, 300 segundos y 256 KiB de contexto
  serializado. Hasta dos llamadas de consolidación y una de respuesta; guardado opcional.
  Esos máximos no obligan a consumir todo el presupuesto.
- Las distinciones financieras viven en prompts y documentos narrativos; no hay schema
  que valide causalidad, comparabilidad de cifras, hipótesis o condiciones de revisión.
- Git manual. No hay versión automática por run, publicación de expedientes, grafo,
  DCF, cartera, recuperación automática del chat o variantes A0–A3.

Los contratos completos pertenecen a [arquitectura](architecture.md), la operación a
[desarrollo](development.md) y la decisión a [ADR-0001](decisions/0001-estado-por-experimento.md).
La integración local con Audit se retiró el 2026-10-24. La captura propia y la
separación de campañas se describen en la [entrega del portado](deliveries/2026-10-24-simplification-main.md).
Las verificaciones históricas siguientes no se han repetido como campañas reales.

## Configuración observada y evidencia

La ejecución real `investigar Nvidia` usó OpenAI `gpt-6-luna`, razonamiento `medium`,
perfil `lab`, salida máxima 4000 y los límites anteriores. Es una configuración observada,
no un valor fijo impuesto por el repositorio: el perfil procede del entorno compartido.
Los prompts efectivos fueron las copias general y financiera, sin instrucciones adicionales.

| Prompt | SHA-256 del texto efectivo |
|---|---|
| agente.md | `f0c1258ad811508ced28b5dc3bbda5e45582908dc568c53db6bcaf516c4fa38b` |
| investigacion-financiera.md | `208e977ce4b990bf8591bf7db551b707f4d3d32d89ca7a9d7f3e23ce61646f70` |

Los [hallazgos del run](experiments/baseline-nvidia-2026-10-18/findings.md) separan
ejecución, persistencia e interpretación. Sus capturas completas son locales e ignoradas;
este documento no las exporta ni permite reproducir sus datos solo con los hashes.

| Nivel | Evidencia disponible |
|---|---|
| Checks deterministas | 44 pruebas locales, mypy y dependencias; integración simulada de Audit |
| Integración real inicial | Un run NVIDIA, 18 llamadas, 17 herramientas, 14 materiales y dos Markdown |
| Continuidad entre procesos | Probada con datos controlados; no ejecutada sobre este estado real |
| Calidad semántica | Revisión posterior interna, parcial; sin rúbrica previa ni comparación controlada |
| Revisión ante contradicción / resultados de inversión | No observados |

## Cómo utilizarlo en el próximo experimento

Fijar previamente mensaje, condición, materiales, prompts, modelo, presupuesto y rúbrica.
Conservar revisión y diff del código, versión/hash del wheel y manifiestos efectivos.
Una ruta nueva reproduce aislamiento; no congela PostgreSQL, la web o el proveedor LLM.
Para atribuir diferencias, usar materiales idénticos y cambiar un factor cada vez.
No llamar a nuevos servicios para comprobar documentación ni reutilizar el estado de
NVIDIA salvo que la continuidad sea parte explícita del encargo.

Los hallazgos observados sugieren contrastar incorporación de evidencia disponible,
explicaciones causales y condiciones de revisión, antes de añadir entidades. Son
hipótesis para próximos protocolos, no cambios implementados ni campañas autorizadas.

`pyproject.toml` aún declara `py.typed`, ausente en el árbol actual por un borrado previo.
Los checks locales pasan sin él; no se afirma publicación de wheel ni cumplimiento del
contrato PEP 561 para consumidores externos. Resolverlo antes de distribuir el paquete.
