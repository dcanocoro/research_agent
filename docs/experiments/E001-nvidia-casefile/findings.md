# E001 — Hallazgos de investigación y continuación de NVIDIA

Estado: concluido con pérdida de continuidad y entrega inicial fallida. Fecha: 2026-10-17.
Diseño previo: [protocolo](protocol.md). No se han repetido intervenciones ni ampliado
sus presupuestos. Las dos intervenciones se ejecutaron en procesos diferentes.

## Resultado principal

El modo de expedientes está implementado y sus operaciones funcionan con pruebas
controladas, pero **ninguna intervención real llamó a `save_case` ni escribió memoria**.
La primera falló al generar la respuesta de cierre; la segunda reconoció la ausencia
de antecedentes, investigó de nuevo y entregó una respuesta limitada por presupuesto.
No se ha construido un expediente real de NVIDIA ni demostrado continuidad del
conocimiento. Este resultado no refuta la representación Markdown: no llegó a utilizarse
su operación de guardado en la ejecución real.

## Base y evidencia recuperable

- Checkout base: `9ef7627cfb2c347cffc4a6caaa4e44d34fa736d2`, con implementación local sin commit.
- Corte previo: `artifacts/E001-nvidia-casefile/attempt-01/environment.json`, preparado
  el 2026-10-17 a las 17:23:54 UTC. Incluye copia y hashes de código, pruebas, prompts,
  protocolo, dependencias, bibliotecas instaladas y diff. La documentación de hallazgos
  y entrega se añadió después; no cambia el código usado entre intervenciones.
- SHA-256 del protocolo previo: `707be60e58ddf2cf55801d73ce54edada703bc925d52a53e78bda2815b7e9400`.
- Wheel Findata localizado y conservado sin reinstalar ni modificar:
  `70cd4a370e1ca4690631f104291a7cc3281acbf6972e43b3c14cb18fe7662e4f`.
- Perfil efectivo: OpenAI, `gpt-6-luna`, razonamiento `medium`, máximo de salida 4000
  tokens. Límites de A: 18 llamadas, 30 herramientas, 300 segundos y 256 KiB de contexto.
- Preflight: claves presentes y lectura PostgreSQL satisfactoria. No hubo ingestas,
  migraciones ni escrituras financieras. Los checks de claves no demuestran disponibilidad
  del servicio; las llamadas posteriores sí muestran integración en este intento.
- Directorio local completo: `artifacts/E001-nvidia-casefile/attempt-01/`, con `runs`,
  `workspace`, `cases`, `frozen_source`, resultados de procesos y revisión mecánica.
  Está ignorado por Git: no es evidencia portable. Este documento conserva el resumen
  verificable por IDs; para reproducir la revisión detallada se necesita el archivo local.

## Operación y comprobaciones mecánicas

| Intervención | Run ID | Estado / cierre | Llamadas / herramientas | Duración de A |
|---|---|---|---|---|
| `Investiga NVIDIA` | `518d6601-f233-43ad-9021-b3e9caa1a64c` | `failed / operational_failure`, error `LLMTruncated` | 18 / 17 | 104,41 s |
| Continuación exacta del protocolo | `be75a4ef-b130-4241-81f6-88bdb2caecc8` | `completed / budget` | 18 / 17 | 82,18 s |

No hubo errores de herramienta en las 34 llamadas ejecutadas. Se conservaron 30
artefactos de contenido distinto; todos los archivos de artefactos comprobados coinciden
con su hash. Las referencias de la respuesta final del segundo proceso resuelven
artefactos existentes. Esto acredita integridad y recuperación, no verdad o soporte
de cada inferencia.

En ambos procesos, `state_before.json` y `state_after.json` muestran `heads={}` y
`unpublished_files=[]`. `workspace_after.json` es `{}`: no hay notas ni índice persistido.
No se intentó guardar una revisión ni se produjo rechazo de guardado.

La primera intervención ejecutó: buscar expedientes (1), buscar empresa (1), ficha (1),
financieros (1), tendencia (1), cálculos (2), búsquedas web (5) y lecturas documentales (5).
La segunda ejecutó: buscar expedientes (1), listar carpetas (4), ficha (1), financieros (1),
búsquedas web (2), cálculos (4) y lecturas documentales (4). No hubo `read_case`,
`list_case_revisions`, `save_case`, `write_markdown` ni `read_artifact`.

**Truncamiento del primer cierre.** La captura del proveedor
`765fcbf8-20e1-4abe-a10f-ba58f7f4f31c.json.gz` registra `tool_choice=none`,
`status=incomplete` e `incomplete_details.reason=max_output_tokens`: 4000 tokens de
salida, incluidos 1578 de razonamiento. Hay texto parcial en esa captura, pero el
cliente devolvió `LLMTruncated`; no se publicó como respuesta ni como expediente.
No fue un timeout ni agotamiento del contexto. Se conserva el parcial sin presentarlo
como entrega final.

Con una herramienta por respuesta del modelo, estas 18 llamadas dejaron 17 acciones
y una llamada final sin herramientas. El límite de 30 herramientas no llegó a ser
vinculante; tampoco lo fueron los 300 segundos. La reserva actual protege una respuesta
final, no una oportunidad adicional de guardar conocimiento.

## Revisión semántica acotada

Revisión realizada por el mismo agente desarrollador sobre capturas, resultados y
respuesta. No hubo evaluador independiente ni aceptación general de calidad financiera.

| Dimensión | Resultado | Evidencia y límites |
|---|---|---|
| Alcance y materialidad | Parcial | El segundo proceso conecta crecimiento con sostenibilidad de márgenes, demanda y concentración; declara pendientes importantes. No resuelve el atractivo de la acción. |
| Fundamento | Parcial | Distingue resultados realizados, perspectivas y evaluación provisional. Cita extractos y cálculos recuperables. Las fuentes principales son comunicados corporativos y sus extracciones son parciales; no hay contraste independiente suficiente. |
| Fidelidad numérica | Parcial | Muestra comprobada: 215.938 y 130.387 millones FY2026 coinciden con la tabla conservada; los márgenes operativos 60,4 % y 62,4 % corresponden a las divisiones ejecutadas. No se certificó exhaustivamente cada cifra o inferencia. |
| Expediente | Fallo | No existe ninguna revisión publicada. La respuesta y el archivo de ejecución no sustituyen el expediente que A debería recuperar. |
| Continuidad | Fallo | El segundo proceso lista casos y carpetas vacías; reconoce que no puede recuperar una evaluación anterior. Investiga de nuevo sin fingir memoria. |
| Revisión ante evidencia nueva | N/O | No hay evaluación persistida contra la que contrastar cambios, ni evidencia contradictoria controlada. |
| Operación y coste | Parcial | Primera entrega fallida; segunda respuesta conservada. Hay llamadas y tiempos observables, pero no se ha calculado coste monetario. |

El segundo cierre distingue el FCF definido por NVIDIA (96.575 millones) del dato del
proveedor (96.676 millones). El extracto archivado identifica pagos de principal dentro
de la definición de la compañía: conservar la diferencia evita tratarlos como cifras
idénticas. La comprobación se limita al material extraído, no a una auditoría del estado
financiero completo. También reconoce que faltan el desglose de Data Center y partes
del pronóstico en las extracciones de esa intervención, en vez de completarlos de memoria.

La respuesta atribuye el mensaje de finalización sin herramientas a «tu instrucción».
Ese mensaje procede del harness al alcanzar el límite de llamadas, no de una nueva
orden humana. Es una imprecisión de explicación de la restricción, visible en transcript.

## Interpretación y siguiente hipótesis

**Observado:** hay investigación, fuentes y cálculos, pero no una acción de persistencia
antes del cierre en ninguno de los dos procesos. El segundo se comporta con honestidad
ante la ausencia de memoria, pero necesita reconstruir materiales. El primero añade
un fallo de entrega por límite de salida del proveedor.

**Interpretación:** disponer de herramienta y explicación semántica no ha bastado para
que este agente, con estos recursos y mensajes, convierta investigación en conocimiento
durable. La gestión de recursos y el momento del guardado deben estudiarse antes de
atribuir la pérdida a falta de `Claim`, `OpenIssue`, grafo o PostgreSQL.

**Próximo contraste propuesto, no ejecutado:** mantener herramientas, modelo y presupuestos,
e introducir una instrucción explícita de guardar una primera evaluación provisional
antes de ampliar la investigación, actualizándola cuando cambien sus fundamentos.
Comprobar primero si existe revisión y después qué recupera el proceso nuevo. Mantener
separado un estudio del truncamiento de salida; cambiar ambos factores simultáneamente
impediría saber cuál produjo una mejora. Nuevos intentos requieren protocolo y registro
propios, sin reemplazar estos fallos.

No se recomienda nueva ontología a partir de este intento. Las pruebas locales sostienen
el mecanismo de almacenamiento; la ejecución real aún no satisface conservación ni
continuidad. No se infieren calidad de decisión o rentabilidad.
