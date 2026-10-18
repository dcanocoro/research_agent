# 2026-10-18 — Estado por experimento y archivo por ejecución

Base Git: `d6a866c3ffd2ee5fde488b302cefe9c009822968`. Árbol inicial limpio.
Encargo: implementar el plan aprobado por el usuario; [decisión](../decisions/0001-estado-por-experimento.md).

## Cambio

Estado único Markdown/JSON/TXT/CSV, materiales originales automáticos, instrucciones
copiadas y runs con nombres humanos. CLI crea experimentos aislados o continúa su
estado en otro proceso. La [arquitectura](../architecture.md) fija responsabilidades;
[desarrollo](../development.md) contiene comandos y Git manual.

Se retiran `CaseStore`, herramientas de expedientes y publicación obligatoria.
Se mantienen dos oportunidades de consolidación sin cierre forzado tras escribir.
Respuesta, snapshots y payloads se archivan separados del conocimiento editable.
El resumen de archivos/materiales/errores sustituye a la confirmación de revisiones.
Audit conserva su interfaz básica y captura propia, con el wheel instalado intacto.

## Verificación local

- 44 pruebas pytest con modelos y herramientas controlados: formatos, aislamiento,
  continuación en subprocess, traslado de archivos, paginación, bloqueo entre procesos,
  consolidación, cancelación, timeout, errores parciales y captura local del proveedor.
- Integración de Archive, consulta, informes y viewer de Audit con modelo simulado;
  subprocess con imports de `finmate`, `engine` y `api` bloqueados.
- Git en repositorios temporales: ausente, sin primer commit, limpio y con cambios;
  lectura sin modificar índice. Los commits de fixtures se limitan a esos temporales.
- Mypy sin incidencias, dependencias instaladas coherentes y `git diff --check`.
- Enlaces locales afectados comprobados. La exploración completa detectó 285 enlaces
  rotos preexistentes en la arqueología copiada de FinMate; no se corrige ese informe
  como parte de esta entrega ni se presenta el conjunto documental como libre de errores.

Pytest descubre solo `tests/`, evitando recoger copias congeladas dentro de `artifacts/`.
No se han alterado E001/E002, sus protocolos, resultados ni capturas. No se modifica
FinMate ni el wheel compartido. Sin commit o push del proyecto.

## Límites y siguiente contraste

Son comprobaciones técnicas; no se ha ejecutado una campaña con LLM, Tavily o PostgreSQL
remotos ni establecido aceptación semántica del mecanismo nuevo. Los proveedores del
test de captura son simulados. El siguiente encargo experimental deberá medir qué
conocimiento queda consolidado y recuperado, además de qué materiales existen.

Git es manual y no garantiza una revisión por run. Los snapshots conservan los extremos,
no todas las ediciones. Las escrituras son atómicas por archivo, sin transacción
multiarchivo ni protección frente a editores externos. Los almacenes históricos no
se migran; las referencias portables nuevas son relativas a `estado/materiales/`.
