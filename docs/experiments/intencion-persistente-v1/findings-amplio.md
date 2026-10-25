# Intención persistente — ejecución con presupuesto ampliado

Fecha: 2026-10-24. Estado: ambas condiciones completadas; revisión semántica preliminar,
sin puntuación ni aceptación financiera. El usuario autorizó ampliar recursos y ejecutar
después de la entrega de implementación. El [protocolo](protocol.md) conserva la condición
inicial sin ejecutar y la ampliación aprobada antes del lanzamiento.

## Condición efectiva y evidencia

Se ejecutaron dos campañas en paralelo, con procesos y estados independientes. Seis
activaciones mensuales, enero–junio de 2023, 50 empresas, 100.000 USD ficticios y hasta
diez posiciones. Ambas usaron OpenAI `gpt-6-luna`, razonamiento `medium`, salida máxima
16000, 60 llamadas, 90 herramientas, 1200 segundos, reserva temporal de 90 segundos
y 1048576 bytes de contexto por activación. No hubo cambios de código, prompts,
configuración o límites durante las ejecuciones. El piloto de 18 llamadas no se ejecutó.

Se comprobaron iguales hashes de escenario congelado, runtime y dataset del simulador:

- Escenario: `ea5d1f58d3ef2489165b1504dccd91a311d26ade1f192413962648cb4761dd2f`.
- Runtime: `29240fe616446df46ba53c1d99c526e7d89438ea5845bf0b3d8f371a4d7c21bf`.
- Dataset serializado del simulador: `4d93cafb0f0816a9ed3af6c047cb3a75d3cf790b204cf5d91eb86c64aecd34b6`.

El archivo fuente revisado mantuvo el SHA-256 documentado `2b65121feae3ae0f2784584f53af6649856d988997eda6eb402f0a71f2b58745`;
su representación guardada por el simulador tiene otro hash por serialización.
Se usó `--data`, sin nueva exportación de Findata. La web fue viva, no un corpus idéntico.

Las capturas completas están en `artifacts/intencion-amplia-baseline-v1/` y
`artifacts/intencion-amplia-deliberative-v1/`. Son locales, ignoradas y no portables por
estar enlazadas aquí. Para trasladar evidencia se necesitan ambas carpetas completas
y `artifacts/intencion-amplia-comparacion-v1/`, previa revisión de datos privados.

## Resultado operativo

| Medida | Baseline | Deliberativa |
|---|---:|---:|
| Activaciones completadas / intentos | 6 / 6 | 6 / 6 |
| Llamadas al modelo | 182 | 172 |
| Herramientas | 176 | 166 |
| Duración entre primer y último evento | 973,4 s | 802,9 s |
| Cierres `answered` | 6 | 6 |
| Empresas distintas con lecturas financieras | 9 | 9 |
| Búsquedas web | 55 | 30 |
| Lecturas explícitas `read_file` | 17 | 22 |
| Escrituras `write_markdown` | 17 | 21 |
| Errores de herramienta | 0 | 1 |
| Errores de captura | 0 | 0 |

Ambos controladores retornaron 0, `progress.finished=true`, con capturas íntegras y sin
reintentos. El error deliberativo fue leer `indice.md` todavía inexistente al comenzar;
el modelo continuó. No fue pérdida de captura ni interrupción.

| Fecha simulada | Llamadas baseline | Llamadas deliberativa |
|---|---:|---:|
| 2023-01-01 | 56 | 42 |
| 2023-02-01 | 22 | 24 |
| 2023-03-01 | 18 | 34 |
| 2023-04-01 | 36 | 21 |
| 2023-05-01 | 24 | 26 |
| 2023-06-01 | 26 | 25 |

No hubo transiciones a consolidación forzada ni timeouts de fase. Todas las sesiones
terminaron por respuesta propia antes de los límites ampliados. La sesión inicial del
baseline duró 304,2 segundos: este presupuesto sí permitió superar cinco minutos.
No se prueba qué habría hecho esa misma trayectoria con el presupuesto original.

Uso informado por el proveedor, sumado desde todos los payloads:

| Tokens | Baseline | Deliberativa |
|---|---:|---:|
| Entrada, incluidos los de caché | 9.888.664 | 6.937.151 |
| Entrada de caché | 9.442.451 | 6.549.438 |
| Salida, incluido razonamiento | 61.416 | 48.742 |

Se comprobó un payload por llamada contabilizada. Los tokens de entrada incluyen
contexto reenviado, no información única investigada. No se calculó coste monetario.
Las duraciones corresponden a ejecución simultánea y no acreditan una diferencia
estable de rendimiento. Menos llamadas o búsquedas no demuestran mayor eficiencia semántica.

## Continuidad y lectura preliminar

En la primera entrada real al proveedor de cada una de las seis activaciones deliberativas
se verificó presencia del mandato y de la agenda registrados en el manifiesto. En las cinco continuaciones,
la agenda coincide exactamente con la guardada al final de la activación anterior.
El mandato contiene solo mensajes auténticos disponibles hasta la fecha, sin mensajes
futuros. La agenda no cambió entre los cortes de marzo y abril; no se impuso una escritura.
La captura demuestra disponibilidad de contexto, no utilización correcta de cada afirmación.

Ambas condiciones leyeron fundamentales de nueve empresas durante la primera activación.
Las lecturas posteriores se limitaron a subconjuntos de esas empresas: no ampliaron
el conjunto financiero después del arranque. Hubo seguimiento, búsquedas y cálculos,
pero la amplitud adicional no se mantuvo como exploración de nuevas empresas.

Las respuestas finales y la agenda deliberativa mantienen pendientes precios comparables,
documentación primaria y valoración. La deliberativa conserva intenciones explícitas,
pero eso no demuestra resolverlas. Ambas abrieron posiciones ficticias inicialmente
y después no añadieron operaciones: cuatro compras baseline y cinco deliberativas;
ninguna usó `notify_user`. No se exige rotación y ese recuento no puntúa iniciativa.

Interpretación provisional: el margen ampliado fue utilizado, sobre todo al comenzar,
y permite observar cierres autónomos sin presión inmediata del presupuesto. En esta
pareja no hay evidencia suficiente para recomendar otra ampliación como solución al
progreso limitado. Conviene revisar las preguntas pendientes, acciones disponibles,
fuentes y criterios de cierre antes de atribuir el comportamiento a falta de recursos.
No se ha realizado una revisión semántica exhaustiva ni una réplica independiente.

## Referencias y reproducción del resumen

- [Observaciones por sesión](../../../artifacts/intencion-amplia-comparacion-v1/observaciones.json):
  consumos, errores, símbolos, escrituras, hashes y rutas a cada run nativo.
- [Comprobaciones de continuidad](../../../artifacts/intencion-amplia-comparacion-v1/continuidad.json):
  contexto en entradas del proveedor y enlace entre agendas guardadas y recibidas.
- [Respuesta final baseline](../../../artifacts/intencion-amplia-baseline-v1/agente/ejecuciones/2026-10-24-activation-0006-attempt-0006/respuesta.md).
- [Respuesta final deliberativa](../../../artifacts/intencion-amplia-deliberative-v1/agente/ejecuciones/2026-10-24-activation-0006-attempt-0006/respuesta.md)
  y [agenda final](../../../artifacts/intencion-amplia-deliberative-v1/agente/estado/agenda.md).

El resumen numérico se regenera sin proveedores desde la raíz con:

```powershell
.\.venv\Scripts\python.exe -X utf8 artifacts/intencion-amplia-comparacion-v1/resumir.py
```

El script y sus resultados son evidencia local derivada; las capturas nativas siguen
siendo la fuente. Las comprobaciones de continuidad compararon manifiestos, snapshots
y `provider_input.input` de `modelo-0001.json.gz`, incluyendo el JSON de contexto.
No se modificó memoria, cartera, materiales ni capturas originales al analizarlos.

Persisten los límites históricos: fechas de disponibilidad estimadas, posibles
revisiones, conocimiento del modelo, universo seleccionado y web viva cuyo contenido
no queda temporalmente validado por published_at. No se ha auditado de nuevo toda la
web recibida. No se evalúa alfa, rentabilidad relativa ni calidad financiera.
