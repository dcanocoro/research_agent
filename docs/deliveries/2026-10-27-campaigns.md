# Campañas: organización, captura nativa y revisión

Encargo aceptado por el usuario el 2026-10-27. Base de comparación: `5809d01`.
La [guía de campañas](../campaigns.md) posee los comandos y el formato vigente.

## Cambio

Se renombraron el paquete a `research_campaigns` y las definiciones a `campaigns/`.
La CLI reúne `validate`, `run`, `resume` y `report`; cada ejecución crea el destino
exacto indicado. La preparación y lanzamiento continuo forman parte del mismo flujo.

`campaign.json` concentra configuración, identidad, hashes, comprobaciones, sesiones,
intentos y progreso. Se escribe atómicamente; `README.md` ofrece la entrada humana
con peticiones, cierre, recursos observables, respuestas, snapshots y diagnósticos.
El informe se regenera sin reescribir la evidencia. Las suites mantienen sus casos
aislados; históricas y continuas usan directamente la raíz como experimento.

Se comparte lanzamiento, inspección de capturas y generación del informe. Se retiraron
la conversión compacta, sus lectores, la extracción de pasos y los pequeños archivos
de control duplicados. El núcleo solo recibe el registro que contiene sus límites;
no importa el controlador de campañas. Las definiciones congelan los archivos usados,
sin copiar conjuntos alternativos de instrucciones ni escenarios no ejecutados.

Los checkpoints históricos, estados fallidos y resultados nativos siguen disponibles.
La recuperación conserva los intentos y evita repetir efectos ya aceptados. Las suites
y pilotos continuos no ofrecen `resume`. No hay compatibilidad con las interfaces
antiguas; los artefactos anteriores permanecen intactos. Los comandos originales de
protocolos y entregas se conservan como antecedentes fechados.

## Reducción medida

Se contaron líneas físicas de Python, incluidos comentarios y líneas vacías, en el
paquete anterior/nuevo y los archivos del núcleo afectados (`archive.py`, `cli.py`
y `recording.py`; el primero se retiró): **1809 → 1420**, reducción de **389 líneas
(21,5 %)**. Esta cifra corresponde a ese perímetro de producción, no a todo el repositorio.

Se ejecutaron los coordinadores anterior y nuevo en directorios temporales separados,
con las mismas entradas sintéticas y `fake_cli` de `tests/support.py`. La histórica
usó dos empresas y tres activaciones de las fixtures de `tests/test_longitudinal.py`;
el piloto continuo comparó la preparación local con la misma configuración y dataset.
La única adaptación de la suite anterior fue su identificador de esquema retirado.

| Modalidad / estado | Archivos antes | Archivos después |
|---|---:|---:|
| Suite, dos casos y dos sesiones, captura nativa | 79 | 67 |
| Histórica, tres activaciones completadas | 72 | 46 |
| Continua, preparación local sin lanzamiento | 15 | 14 |

Se contaron todos los archivos, incluidos logs no vacíos de la fixture, instrucciones,
definiciones, snapshots y checkpoints. Como referencia adicional, la suite anterior
**compactada** tenía 50 archivos frente a los 67 actuales: conservar captura nativa
incrementa archivos respecto a esa representación comprimida. El objetivo aceptado
prioriza retirar el conversor y las representaciones redundantes, no minimizar el
número de archivos de la evidencia nativa. El control y revisión comunes quedan en
`campaign.json` y `README.md`.

Las mediciones se realizaron en almacenamiento temporal local; no son una campaña
financiera ni evidencia de mejoras de razonamiento o inversión.

## Verificación

Pruebas locales con clientes controlados: publicación e aislamiento, procesos nuevos,
recuperación tras interrupciones, ausencia de duplicación de órdenes, instrucciones
y datos congelados, presupuestos continuos, perfiles, snapshots y lectura paginada
de resultados originales. Casos adicionales comprueban escritura atómica, regeneración
del informe sin alterar capturas, rechazo de opciones incompatibles y retirada de
comandos antiguos. Sin llamadas reales a proveedores ni bases remotas.

También se comprobaron tipos, enlaces locales, `git diff --check`, dependencias e
instalación editable sin acceso a índices. La suite completa finalizó con **200 pruebas correctas**. Los checks de tipos,
enlaces locales (604 enlaces), dependencias y diff también finalizaron correctamente.

No se modificaron prompts, reglas financieras ni el simulador. No hubo commit ni push.
