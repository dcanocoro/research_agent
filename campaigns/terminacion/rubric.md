# Evaluación privada, previa al lanzamiento

No entregar esta rúbrica ni el campo rubric de cases.json a A o al checkpoint.

## Respuesta final (ciega respecto de condición y consumo)

Dar al juez la petición original, el corpus del caso, la rúbrica específica y una
respuesta RNNN. No entregar mapping-private.json, nombres de ejecución ni checkpoints.
El contenido puede revelar el tratamiento: registrar sospechas; no afirmar doble ciego.
Puntuar cada dimensión de 0 a 2 (ausente/incorrecto, parcial, suficiente), justificando
con pasajes: cumplimiento, corrección numérica y periodos, fundamento, incertidumbre.
Marcar errores materiales y partes obligatorias ausentes. Una insuficiencia correctamente
identificada puede satisfacer íntegramente el encargo. No premiar extensión o documentos.
Suficiente exige las obligaciones específicas del caso y ningún error material.

## Trayectoria (revisión distinta, sin resultados futuros al juzgar cada prefijo)

Usar conversacion.json y eventos con pares completos de modelo/herramienta y sus
contadores; las capturas nativas conservan la trayectoria. No se audita razonamiento
interno oculto. Identificar el primer prefijo suficiente o un intervalo plausible,
las obligaciones pendientes y la confianza alta/media/baja. Citar resultados que
sustentan el juicio. No usar evidencia posterior para declarar que ya se sabía algo.
Clasificar acciones posteriores: necesarias, persistencia útil, ampliación opcional,
redundancia o indeterminadas. La persistencia útil no es automáticamente sobretrabajo.
Marcar cierre prematuro cuando deja trabajo obligatorio resoluble con el corpus y
herramientas disponibles. Separar límite de recursos de decisión semántica de cerrar.
Registrar discrepancias entre jueces; adjudicar los cierres dudosos con revisión humana.

## Registro por respuesta/trayectoria

Conservar blind_id, puntuaciones y razones, errores materiales, suficiente,
cierre_prematuro, primer_prefijo_suficiente_o_intervalo, confianza,
acciones_posteriores_clasificadas y referencias. Desconocido no equivale a cero.
El runner exporta respuestas; no ejecuta ni simula esta evaluación independiente.

## Comparación y decisión

Comparar por caso y repetición V1−V0 y V2−V1: suficiencia, errores materiales,
cierres prematuros, llamadas de A/checkpoint/totales, herramientas y tiempo.
Revisar medianas y dispersión, además de cada regresión. El coste monetario y tokens
solo se calculan si las trazas los ofrecen; conservar fuente y tarifa fechada si se
estima dinero. No convertir ausencia de captura en ahorro.
Una regresión material impide recomendar adopción automática; revisar causas y repetir
el contraste antes de concluir. Menos llamadas sin calidad mantenida no es mejora.
V2 solo merece seguir si mejora sobre V1 considerando sus revisiones adicionales.
Son 12 casos sintéticos, tres repeticiones por defecto: evidencia exploratoria,
sin afirmación de significación estadística, utilidad financiera real o rentabilidad.
