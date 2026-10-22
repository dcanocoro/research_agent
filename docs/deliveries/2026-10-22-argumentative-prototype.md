# Benchmark v2 y prototipo argumentativo

Fecha: 2026-10-22. Base Git: `736bd8798f9c05edb5aac49c10dbde342324b154`.
Encargo: plan aceptado para benchmark y prototipo, sin campañas reales.
Se conservan los cambios previos de M2 y su documentación; no se modifica FinMate,
el wheel compartido, configuraciones privadas ni campañas anteriores.

## Cambio

Se incorpora [longitudinal v2](../experiments/longitudinal-v2/protocol.md): ASML,
NVIDIA y Ford mantienen seis sesiones con nuevas dependencias, evidencia rival y
correcciones retrospectivas. Rúbricas privadas por sesión, trayectoria y estado,
sin nota global ni premio por formalización. V1 permanece intacta.

El [prototipo optativo](../argumentative-prototype.md) añade SQLite por experimento,
cinco herramientas, revisiones inmutables, lotes atómicos, control de referencias y
ciclos de fundamentación y causas de revisión pendiente. Conserva el juicio del
agente al propagar impactos. M1 + M2 y guía financiera son comunes a A0/A1.

CLI y benchmark fijan modo, corpus cerrado, límites y perfil explícito; A1 puede
guardar durante consolidación y conserva capturas SQLite/JSON verificables en el
archivo compacto. El modo por defecto y los lectores históricos siguen disponibles.

Se corrigen referencias documentales a los archivos del piloto retirado, indicando
su recuperación desde Git. Dos pruebas que dependían de aquel catálogo ausente
usan ahora longitudinal v1, conservando validación offline y publicación progresiva.

## Verificación

Pruebas locales con transportes simulados, SQLite y archivos temporales: integridad,
historia, retirada, rollback, revisión localizada, debate, continuidad en procesos
nuevos, fases de cierre, cancelación, corpus/cuotas, archivo compacto trasladado y
corrupción. Resultado: 92 pruebas superadas en la suite completa. Mypy sin errores,
`pip check` sin dependencias rotas, ambas suites válidas (3 casos/18 sesiones cada
una), 32 documentos y 509 enlaces locales sin errores, y `git diff --check` limpio.
La integración A1 incluye dos sesiones CLI en procesos distintos, con modelo
simulado y captura compacta real. No hay verificación de transporte con proveedor real.

## Límites y siguiente paso

No se invocan modelos reales, Tavily, PostgreSQL, ingestas ni migraciones remotas.
La integridad estructural no demuestra inferencia económica correcta. Las marcas
son conservadoras y no acreditan revisión semántica; un localizador de fuente no
certifica un pasaje. No hay sincronización bidireccional con Markdown ni migración
de estados antiguos. El mecanismo sigue siendo una excepción experimental local.

Quedan pendientes discriminación del benchmark, ventaja semántica, coste real y
decisión arquitectónica. La siguiente campaña debe elegir y congelar perfil y
presupuesto monetario, calibrar A0 y comparar A1 con iguales entradas y condiciones.
