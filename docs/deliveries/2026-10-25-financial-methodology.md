# Entrega — metodología financiera longitudinal

Fecha: 2026-10-25. Base Git: `9014327890194589c33c1681bfef586dbdfb16b0`.
Encargo: implementar el plan aprobado, sin proveedores, campañas ni pruebas con LLM real.
Diseño y límites: [protocolo](../experiments/analisis-financiero-v1/protocol.md).

## Cambios

Instrucciones nuevas por defecto: metodología de inversión, conservación flexible por
empresa, referencias con ruta e ID y agenda vinculada a preguntas y dependencias. Se
conservan recuperación selectiva, mandato protegido, materiales, ciclo y reservas.
Se permiten estimaciones sustentadas en aritmética ejecutada, sin añadir DCF ni herramientas.

Control anterior congelado como texto efectivo UTF-8/LF verificado contra seis manifiestos.
Las diferencias de hashes de plantillas y copias inicialmente observadas eran finales de
línea, no diferencias de contenido efectivo. No se alteraron las campañas históricas.
`run --instructions-dir` y el parámetro de preparación seleccionan un conjunto completo
al crear la campaña; las continuaciones conservan sus copias congeladas.

Escenario comparativo y casos sintéticos/rúbrica preparados sin ejecutar. No hay nuevo
runner semántico, schema persistente, grafo, cambios en FinMate, wheel ni simulador.

## Verificaciones

- Tests específicos iniciales de persistencia e integración: 93 passed.
- Selección de instrucciones y CLI real con proveedor controlado: 5 passed.
- Mypy: sin errores en 26 archivos fuente. `pip check`: sin dependencias rotas.
- Validación offline del escenario: 50 empresas y seis activaciones. Comparación local
  del YAML: idéntico al escenario ampliado anterior salvo ID.
- `git diff --check`: sin errores; archivos nuevos comprobados como UTF-8 sin espacios finales.
- Enlaces documentales: 41 Markdown y 561 enlaces; tres errores preexistentes, todos al
  informe local ausente `artifacts/campana-historica-completa-v1/informe-ejecucion.md`.
  Se verificó su presencia en HEAD en estrategia, índice experimental y protocolo histórico;
  no se reconstruyó ni sustituyó esa evidencia. Sin errores en enlaces nuevos.
- Suite completa: **148 passed en 149,31 segundos**, con transportes controlados, sin
  proveedores ni bases remotas. No se ejecutó campaña real ni prueba con LLM real.

## Límites y siguiente paso

La integración con clientes programados prueba operaciones y continuidad mecánica; no
selección autónoma ni calidad económica. Falta aceptación semántica con casos controlados
y comparación posterior autorizada de ambos brazos nuevos. Web viva, precios ajustados y
disponibilidad estimada siguen limitando la interpretación histórica. No hay hallazgos
semánticos, rentabilidad demostrada, commits ni publicación en esta entrega.

## Revisión coordinada de instrucciones solicitada por el usuario

Los cambios posteriores del usuario en `agent_a.md` y `deliberation.md` se tomaron como
base de esta revisión, conservando sus criterios de autonomía, intención, adaptación y
cierre. Los tres prompts están ahora en español y con responsabilidades separadas:
persistencia y rigor general, dirección del trabajo y agenda, metodología y conocimiento
financiero. El general pasa de 1110 a 676 palabras, una reducción aproximada del 39 %.
Se retiran los ciclos genéricos duplicados del financiero, conservando sus cinco dimensiones.

La ubicación por empresa pasa a ser obligatoria para evaluaciones con continuidad prevista,
sin exigir documentos vacíos. Al modificar una hipótesis identificada debe consultarse su
impacto en dependientes antes de considerar terminada la actualización; quedan previstos
revisión, confirmación justificada o pendiente explícito. Se distingue comparación de
alternativas (`oportunidades.md`) de interpretación de asignación (`cartera.md`, opcional).

La prueba de integración se amplía para calcular V1 de 20 a 10 USD tras cambiar H1 en
un proceso nuevo y actualizar la evaluación dependiente; la rama de fallo conserva ambas
como pendientes antes de interrumpirse. Sigue siendo una prueba con acciones programadas,
no demuestra que un LLM decida revisar correctamente. Los casos semánticos quedan pendientes.

No se modifican copias de instrucciones ni estados de campañas existentes, el control
histórico, el escenario, el runtime ni las herramientas. Una campaña ya creada conserva
sus instrucciones anteriores; las nuevas campañas copian los prompts revisados.

Verificaciones de esta revisión: 55 pruebas de metodología y persistencia y 20 del
ciclo general pasadas, sin proveedores ni bases remotas. `git diff --check` sin errores.
El checker documental conserva los mismos tres enlaces históricos a un informe local
ausente (41 Markdown, 561 enlaces); no introduce errores nuevos. No se repite ni se
atribuye a esta revisión la suite completa histórica de 148 pruebas.
