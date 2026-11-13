# Revisión del piloto Adobe con DCF Lab

Fecha: 2026-11-11. El usuario solicitó detener y revisar; el proceso ya había cerrado
voluntariamente a las 17:37 Europe/Madrid. No fue necesario cancelarlo. No se lanzó
otra campaña ni se editaron el workspace del agente, código o configuración.
Se conservaron los cambios ajenos presentes en el checkout.

Se registran los [hallazgos](../experiments/dcf-lab-v1/adbe-findings.md) del
[protocolo](../experiments/dcf-lab-v1/adbe-longitudinal.md): único brazo experimental,
dos intentos fallidos conservados y una continuación completada, 114 ReAct,
cinco revisiones generales y dos llamadas internas de DCF. Incluye cronología,
evaluación general y específica, seguimiento de incertidumbres, fallos y propuestas.
No hay comparación causal ni auditoría financiera externa.

Verificación de esta revisión: reconstrucción desde resultados/eventos nativos,
119 payloads del transporte principal presentes, inputs/outputs especializados y
bundle auditado, `capture_errors=[]` en los tres resultados, copia DCF editable
coincidente con auditoría y recálculo determinista idéntico mediante el paquete
instalado, cuya huella coincide con el manifiesto. Sin nuevas llamadas LLM, web,
bases remotas o escrituras financieras. Los tokens de dos intentos fallidos y el
coste total real siguen desconocidos. Comprobados enlaces locales de los documentos
afectados y `git diff --check`; no se repitieron suites de software por una revisión
documental. Sin commit ni push.
