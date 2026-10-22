# Recuperación por ID y persistencia material de A1

Fecha: 2026-10-22. Base Git: `736bd8798f9c05edb5aac49c10dbde342324b154`, con
el prototipo y cambios locales previos conservados. Encargo: reparar y preparar;
las campañas nuevas las ejecuta manualmente el usuario.

Los [hallazgos de A0/A1 v2](../experiments/longitudinal-v2/findings.md) motivan una
reparación pequeña: búsqueda literal por ID o contenido, descripciones explícitas,
conflictos con indicación de lectura vigente y prompt que pide conservar avances
materiales en SQLite. El prompt orienta la recuperación y el reintento, sin hacerlo
automático ni bloquear la entrega. No cambian schema, tipos, presupuestos o wheel.

Se prepara [v2.1 y prueba corta](../experiments/longitudinal-v2-1/protocol.md).
La versión larga cambia solo el identificador y los importes explícitos de la ficha
ASML; v2, instrucciones copiadas de experimentos anteriores y capturas permanecen
intactos. El usuario debe crear campañas nuevas para recibir el prompt actualizado.

Verificación local: búsqueda por ID y contenido con filtros/paginación/retirada;
cuatro procesos que crean, recuperan, sufren un conflicto, verifican rollback,
leen la revisión vigente, reintentan y comparan historia. Incluye captura verificable
y regresión CLI simulada. Suite completa: 96 pruebas superadas; mypy sin errores,
pip check correcto, cuatro suites válidas, enlaces locales y git diff --check
correctos. Las definiciones congeladas de ambas campañas v2 conservan sus hashes;
sus copias del prompt A1 anterior permanecen intactas.

No se han llamado modelos reales, web o bases remotas. La prueba corta con modelo
y la comparación A0/A1 v2.1 siguen pendientes. Un recorrido determinista correcto
no demuestra adopción del prompt ni mejora semántica del agente.
