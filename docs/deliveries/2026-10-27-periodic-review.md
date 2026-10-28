# Revisión deliberativa permanente — 2026-10-27

Base Git: `ec331a8`. Implementación local del plan aceptado por el usuario;
sin commit, proveedor, base remota ni campaña v4.

## Cambio

El ciclo continuo incorpora una llamada sin herramientas cada diez llamadas de
investigación. Conserva la cadencia entre reconstrucciones y da prioridad a la
consolidación. Las revisiones usan presupuesto adicional de llamadas, comparten
tiempo y contexto y no sustituyen la respuesta ordinaria ni escriben archivos.
El ciclo acotado conserva su comportamiento. No se modifica el wheel compartido.

El resultado añade desglose por fase, manteniendo el total real; manifiesto,
presupuesto técnico, captura del proveedor e informe de campañas hacen explícita
la política y permiten atribuir consumo. Se conserva lectura de resultados antiguos.
La [decisión](../decisions/0004-revision-periodica.md), la
[arquitectura](../architecture.md#revisión-periódica-permanente--2026-10-27) y el
[protocolo](../experiments/contexto-continuo-v1/protocol.md#v4--revisión-periódica-permanente)
poseen el diseño y sus límites.

## Verificación local

- Regresión afectada: **148 passed, 12 deselected**, ejecutando `test_continuous`,
  `test_continuous_pilot`, `test_campaigns`, `test_agent` y `test_persistent_execution`,
  excluyendo los casos que dependen de definiciones históricas ausentes.
- Suite completa: **201 passed, 4 failed, 10 errors**. Los cuatro fallos requieren
  `campaigns/longitudinal-v1` o `campaigns/intencion-persistente-v1`; los diez errores
  de preparación requieren `campaigns/contexto-continuo-v1`. Esas definiciones ya
  faltan en la base Git; no se restauran ni sustituyen en este cambio.
- Los 13 casos de revisión se repitieron tras añadir la comprobación de bytes para
  cada petición: **13 passed, 28 deselected**. Cubren 60 ordinarias + 5 revisiones,
  contexto y continuidad tras consolidar, límites, fallo, timeout, cancelación,
  respuesta vacía, herramienta inesperada y captura de intentos por fase.
- `mypy src/research_agent src/research_campaigns --follow-imports=silent`:
  sin errores en 31 archivos. `git diff --check`: sin errores.
- Comprobador de enlaces: **20 errores**, todos referencias a campañas históricas
  ausentes. Comparación de los enlaces con los documentos de `HEAD`: **20 antes,
  20 después, cero errores introducidos**. Enlaces y anclas nuevos válidos.

La regresión incluye clientes controlados, frontera de imports y capturas locales;
no establece calidad intelectual ni financiera. Las definiciones y capturas de v3
se conservan intactas. Observar una futura v4 y revisar acciones, conocimiento y
coste corresponde a otro encargo.
