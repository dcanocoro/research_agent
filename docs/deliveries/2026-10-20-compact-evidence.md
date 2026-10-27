# Evidencia compacta para revisión del agente

Fecha: 2026-10-20. Base: `eb673ef` más benchmark piloto y diff local, sin commit/push.

El benchmark consolida al terminar sus capturas sin cambiar el razonamiento, prompts
o herramientas de A. Una sesión conserva metadatos, trayectoria comprimida, respuesta
y estados inicial/final. Las herramientas mantienen argumentos, resultado original y
resultado entregado. Los materiales e instrucciones se referencian por hash; las
citas antiguas de resultados siguen funcionando. Capturas incompletas se retienen.

La [operación](../development.md#campañas) documenta lectura y exportación a
una carpeta separada. El [protocolo](../experiments/benchmark-pilot-v1/protocol.md)
define revisión por Codex/humano con evidencia y sin puntuación automática.

Verificación de fidelidad sobre una copia de la campaña local
`20261020T152426Z-28b005da`: 79 payloads del modelo, 71 llamadas/resultados de herramientas,
16 snapshots y ocho respuestas coinciden con los originales. El origen conserva todos
sus archivos y hashes. La copia pasa de 419 a 133 archivos y de aproximadamente
4,95 MB a 2,14 MB. Rutas locales bajo `artifacts/`, ignoradas; no evidencia portable.
Esta verificación no reejecutó proveedores ni evalúa corrección financiera.

Verificación final: `pytest -q tests` da 70 passed (26 del benchmark), incluyendo
procesos nuevos con servicios simulados en formatos nativo y compacto, conversión con
resultados completos/limitados, Unicode, refs históricas, aislamiento del workspace,
detección de corrupción y conservación de capturas incompletas. Mypy: 19 fuentes sin
errores. Enlaces: 26 Markdown y 474 enlaces locales sin errores. `git diff --check`
sin errores de whitespace. No se ejecutaron proveedores ni bases remotas.
