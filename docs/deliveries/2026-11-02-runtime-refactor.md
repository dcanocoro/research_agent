# Motor ReAct compartido y organización experimental

Fecha: 2026-11-02. Base: `73794dfcc587b6a7521e422f4e90a010f1d5cac8`, rama
`experiment/fileAgent`. Sin commit ni campaña real.

La [auditoría previa](2026-11-02-runtime-audit.md) documenta la inspección antes de
modificar código. El usuario revisó el plan y encargó la unificación, registrada
en [ADR-0005](../decisions/0005-nucleo-react-extensiones.md).

## Cambio

- `AgentA` conserva su interfaz y delega en un único motor para A acotado, continuo
  y B. Las políticas producen pasos; no contienen otros bucles ReAct ni invocan
  directamente modelos/herramientas.
- Multiagente posee encargos, contexto preparado, reservas y cierre de B. Progreso
  posee objetivos, revisión, observaciones y criterios de evaluación. Regímenes
  conserva E2 y su estado operativo, con colaboradores aportados desde composición.
- La contabilidad y deadlines se comparten, sin transferir la reserva no utilizada
  de B a A. Las revisiones usan el transporte común y presupuestos del padre.
- Directorios pasan a `experiment_store`; los imports anteriores se mantienen.
  Límites y resultados neutrales se separan del adaptador público de solicitudes.
- La preparación offline usa el mismo ensamblaje de instrucciones y semilla que
  la ejecución. Los manifiestos añaden la composición efectiva sin retirar campos.
- Se conservan prompts, schemas, rutas, recibos, formatos y el hash de los bytes de
  `runtime.json` anteriores al refactor. La definición E2 se empaqueta como recurso;
  los fingerprints del código cambian y no se migran campañas silenciosamente.

El [mapa de arquitectura](../architecture.md#organización-del-código) indica
propietarios y compatibilidad. No hay nuevos flags, regímenes, evaluadores ni
escrituras financieras. No se modifica FinMate ni el wheel compartido.

## Verificación

La suite completa sigue detenida en recopilación por `tests/test_price_review.py`,
que importa `scripts/review_historical_prices.py` ausente en la base y en el checkout.
Se ejecuta separadamente el resto, excluyendo solo ese archivo identificado.

- Suite amplia: **416 pruebas aprobadas** en 391,33 s.
- Tras los últimos ajustes de composición y reloj: **156 pruebas relevantes
  aprobadas** en 98,02 s, incluyendo acotado/B mediante el motor común, E2,
  continuo, V7/V8, objetivos decisorios, CLI y piloto offline.
- Cierre de validación temprana: **6 pruebas de arquitectura aprobadas** en
  13,03 s; una combinación inválida de B se rechaza antes de recuperar transacciones.
- Mypy sin errores en **67 archivos**; `pip check` y `git diff --check` correctos.
- Wheel del laboratorio construido sin reinstalar dependencias. Verificados
  imports, prompts y recurso de identidad congelada desde el wheel fuera del
  checkout. No se modifica el wheel compartido de Findata/Infra.
- Comprobación documental global: 745 enlaces frente a 731 en la base, sin
  errores nuevos. Permanecen 241 referencias externas ausentes a FinMate y un
  ancla previa en `2026-11-01-knowledge-agent.md` hacia la guía de desarrollo.
  Se compararon enlaces y destinos con la base Git, sin excluir errores internos.
- Comprobación corta adicional: una interrupción `BaseException` se propaga
  conservando la captura de resultado `interrupted`, como antes del refactor.

Las pruebas nuevas cubren el motor común de las tres rutas, ejecución básica con
imports experimentales bloqueados, único punto de transporte/despacho, identidad
E2 congelada, cancelación con captura de intento y metadatos de composición.
La regresión existente cubre contextos, objetivos, B, transacciones, CLI y campañas
con clientes controlados. No se usan proveedores LLM ni bases remotas.

## Límites

Se mantienen los aliases usados y la representación E2 compartida. Retirarlos o
cambiar combinaciones requiere revisar consumidores; no se elimina código activo
por antigüedad. La incidencia huérfana de precios queda fuera de este refactor.
Los checks no acreditan continuidad semántica, calidad financiera o rentabilidad.
