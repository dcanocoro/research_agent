# Consolidación documental antes del archivo externo

Fecha: 2026-10-31. Base Git: `3c1d481`, árbol limpio al inicio. Encargo: actualizar,
consolidar y organizar documentación, conservando aprendizajes antes de sacar capturas
de `artifacts/`. Se eligió conservación narrativa y consolidación intensa.

## Cambio

El mapa documental y la estrategia separan funcionamiento vigente, preguntas abiertas
y registros fechados. Arquitectura se ordena por capacidades y conserva los límites
de perfiles, persistencia, revisión y evaluación. Desarrollo y campañas documentan
la CLI actual y marcan las definiciones y utilidades retiradas; no se restauran.
AGENTS identifica `research_campaigns` como propietario de campañas.

El registro experimental distingue preparación, ejecución y resultado. Los hallazgos
V1–V4 incorporan V3 y la síntesis del informe local V4, incluidos error aritmético en
prosa, referencia inexistente, confusión de fase y respuesta textual desactualizada.
Se conserva por separado la observación V4 con Python. V5 reúne primer intento y
repetición corregida; V6, V7, V8 y Microsoft mantienen sus preguntas diferenciadas.
Los registros incluyen procedencia y disponibilidad, sin inventar destino externo.

Documentos retirados después de trasladar contenido y actualizar consumidores:

| Documento anterior | Destino |
|---|---|
| Entrega de piloto en bytes del 26 de octubre | [Entrega continua consolidada](2026-10-26-continuous-context.md) |
| Entrega de corrección de resultados del 26 de octubre | Misma entrega continua, sección posterior |
| Entrega de errores de consolidación del 28 de octubre | [Entrega V5](2026-10-28-state-tools-v5.md) |
| Diseño previo de herramientas V5 | [Protocolo V5, anexo histórico](../experiments/herramientas-estado-v5/protocol.md#diseño-original-del-2026-10-28) |
| Hallazgos de repetición V5 | [Hallazgos V5 de ambos intentos](../experiments/herramientas-estado-v5/findings.md) |

Las entregas conservan verificaciones y límites por corte, sin convertir las pruebas
antiguas en resultados actuales. El diseño V5 conserva sus propuestas como históricas.
La arqueología conceptual y su anexo físico siguen separados por responsabilidad;
las referencias a FinMate son externas y requieren el checkout correspondiente.

## Evidencia consultada y comprobaciones

Se contrastaron manifiestos, resultados, eventos y snapshots finales disponibles de
los pilotos V1/V2, V3, V4 sin/con Python, ambos V5, V6, las tres tentativas V7, V8 y
Microsoft. Se leyeron los informes locales V4/V8/Microsoft y documentos finales
seleccionados; no se repitieron sus replays ni auditorías financieras exhaustivas.
Las cifras nuevas de actividad V3/V4 se contrastaron con eventos y resultados.
Los desgloses de consumo del informe V4 quedan atribuidos a ese informe.

La comprobación `artifacts/setup/smoke-model-2026-10-23` conserva un run completado,
una llamada LLM y cero herramientas: verifica esa comunicación, no autonomía ni
análisis. Los logs `artifacts/v6-local-validation` conservan verificación histórica
(315 tests en el log final y enlaces ausentes); no son otra campaña ni se ejecutaron
de nuevo. Ambos quedan registrados aquí sin crear informes experimentales adicionales.

- Comparación de contenido de los cinco documentos fusionados contra sus destinos:
  contenido sustantivo conservado; enlaces y niveles de encabezado adaptados.
- Recuperación Git de los cuatro documentos E001/E002 en `20afee9`: comprobada.
- Comprobador de enlaces/anclas de `d2600fb:scripts/check_docs.py` ejecutado en memoria
  sobre la raíz actual, sin restaurar el script retirado. Cero errores internos;
  las referencias externas ausentes a FinMate se informan por separado.
- Enlaces navegables a `artifacts/`: sustituidos por procedencia textual. Las guías
  vigentes no dependen de ejemplos de campañas retirados.
- `git diff --check`: aprobado. La pregunta congelada de Microsoft conserva sus bytes.

## Límites y archivo posterior

No se movieron ni borraron artefactos, no se cambiaron runtime, prompts, contratos,
dependencias o decisiones aceptadas, y no se llamó a proveedores ni bases remotas.
No hubo commit ni push. La edición es documental y no requiere suite del runtime.

La narrativa permite entender condiciones y resultados sin capturas; una auditoría
completa necesita recuperar originales. Para antecedentes ausentes solo se conserva
lo documentado previamente y se declara esa limitación. El archivo externo debe
preservar tentativas e instrucciones efectivas junto a los datos, registros y diarios;
su creación y ubicación no forman parte de esta entrega. La [guía](../campaigns.md#conservar-aprendizajes-antes-de-archivar-capturas)
explica qué conservar antes de hacerlo.
