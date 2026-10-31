# Revisión de precios y acciones corporativas — 2023–2024

Fecha de captura: 2026-10-24. Estado: aprobada para el laboratorio exploratorio con las excepciones descritas. No es un registro jurídico exhaustivo de acciones corporativas ni una validación de alfa.

## Resultado y procedencia

Se conserva el universo de 50 empresas. El dataset revisado contiene 25.400 cierres diarios y los fundamentales reales previamente exportados de Findata en solo lectura. No se ha escrito en Findata ni modificado su wheel. El escenario original con revisión pendiente permanece intacto; el escenario revisado (`campaigns/colaboracion-historica-v1/reviewed-scenario.yaml`; referencia local histórica) requiere este dataset ajustado mediante `--data`.

Las respuestas completas, hashes, parámetros y cálculo se conservan localmente en `artifacts/price-review-adjusted-v3/`: `responses/`, `sources.json`, `findata-original.json`, `issuer-actions.json`, `data.json`, `review.json`, `reconciliation.json` y `preflight-approved.json`. El preflight resulta `ready=true` para las 50 empresas.

El intento inicial de Alpha Vantage utilizó la clave demo configurada y no devolvió la serie ajustada. Los intentos Yahoo incompletos permanecen en `artifacts/price-review-adjusted-v1/` y `-v2/`; no se redujo el universo para ocultar el fallo de AVB.

## Convención económica

Para 49 empresas se usa Yahoo Finance Chart, cierre ajustado diario USD, validando símbolo, moneda, granularidad diaria y valores positivos. Su [metodología](https://in.help.yahoo.com/kb/adjusted-close-sln28256.html) incorpora splits y dividendos. El simulador opera participaciones normalizadas, no cantidades reales de acciones:

```text
precio_unidad(t) = 100 × cierre_ajustado(t) / cierre_ajustado(2022-12-30)
```

El ancla es la última sesión anterior o igual al inicio del escenario, 2023-01-01. Es común al baseline y a la prueba corta. Los factores posteriores comunes se cancelan en el cociente; no se muestran niveles absolutos retrospectivamente ajustados como si fueran precios negociados entonces. Las revisiones del proveedor y sus reglas de ajuste siguen limitando el aislamiento temporal.

Los dividendos/distribuciones que el proveedor incorpora en el ajuste quedan embebidos en el precio de la participación. No se abona efectivo adicional ni se multiplica otra vez la cantidad por los splits: eso duplicaría el efecto. Las órdenes siguen ejecutándose al siguiente cierre observado, estrictamente posterior a la activación. No se simulan dividendos con fiscalidad, entrega de nuevos valores ni derechos de suscripción separados.

## Splits confirmados

| Símbolo | Primer día ajustado | Ratio | Evidencia primaria |
|---|---|---|---|
| ANET | 2024-12-04 | 4:1 | [Emisor / SEC](https://investors.arista.com/Communications/Press-Releases-and-Events/Press-Release-Detail/2024/Arista-Networks-Completes-Four-for-One-Stock-Split-2024-UzV4VbnUJu/default.aspx) |
| APH | 2024-06-12 | 2:1 | [Emisor / SEC](https://www.sec.gov/Archives/edgar/data/820313/000110465924070695/tm2416925d1_8k.htm) |
| AVGO | 2024-07-15 | 10:1 | [Emisor / SEC](https://investors.broadcom.com/static-files/e90fe911-25c9-47eb-afbe-8e763b71eb64) |

La fuente financiera registra exactamente esos tres splits dentro del intervalo. En los cierres sin ajustar de Findata se observan los saltos correspondientes. Para 49 empresas se compararon los factores de cambio diarios de Findata, corregidos por esos splits, con los cierres Yahoo ajustados por split: 508 sesiones comunes por empresa, sin diferencias absolutas superiores a 0,001 en el factor de cambio diario. Esto comprueba coherencia de series; no certifica todos los eventos societarios posibles.

## Excepción AvalonBay (AVB)

Yahoo rechazó las fechas históricas y otras consultas devolvieron granularidad intradiaria y metadatos incompatibles con el intervalo. Se descartaron esas respuestas como fuente de precios de 2023–2024. No se sustituyó AVB por otra empresa.

Se mantienen sus cierres reales sin ajustar de Findata. Se documentan ocho dividendos ordinarios en declaraciones del emisor (`campaigns/colaboracion-historica-v1/issuer-actions.json`; referencia local histórica): cuatro de 1,65 USD para 2023 y cuatro de 1,70 USD para 2024. Las páginas del emisor se capturaron en `artifacts/price-review-2023-2024-v1/AVB-declaration-*.html`, comprobando importe y record date.

Las fechas ex-dividendo se **derivan**, no se presentan como suministradas por el emisor: sesión observada anterior al record date para el régimen T+2; mismo record date desde 2024-05-29. La [regla y transición](https://www.nasdaqtrader.com/TraderNews.aspx?id=ETA2024-29) se guardan como procedencia. Las ocho fechas resultantes son 2023-03-30, 2023-06-29, 2023-09-28, 2023-12-28, 2024-03-27, 2024-06-28, 2024-09-30 y 2024-12-31.

Para cada dividendo ordinario se aplica a los precios anteriores el multiplicador `1 - dividendo / cierre_previo`, documentado en la metodología Yahoo, y después se normaliza al mismo ancla. No se identificó un split de AVB en esta revisión. Esta reconstrucción tiene una excepción de procedencia y una inferencia de fecha explícitas; no tiene la misma comprobación independiente de precios que las otras 49 series.

## Otras acciones y movimientos grandes

El feed revisado recoge 296 dividendos y tres splits. No identifica otras distribuciones de capital en los datos descargados. Una ausencia en ese feed no prueba ausencia jurídica de fusiones, escisiones, cambios de domicilio o ticker. El alcance consiste en la continuidad de las series revisadas, no en reconstruir todo el registro societario.

Las recompras, emisiones y adquisiciones del emisor que no alteran obligatoriamente la cantidad del accionista se dejan reflejar en los precios; no se añade una corrección mecánica. Si aparece una conversión de valores o entrega de una escisión no representada adecuadamente por el proveedor, debe detenerse esa continuación y revisar el dato/convenio; el simulador no dispone de contabilidad de nuevos títulos.

Se revisaron los cinco cambios diarios ajustados superiores al 20%. No se corrigieron como si fueran splits: coinciden temporalmente con noticias/resultados y se mantienen como observaciones de mercado. Esa coincidencia contextual no prueba una causa única de la variación.

| Símbolo | Fecha | Cambio ajustado observado | Contexto y evidencia primaria |
|---|---|---|---|
| ADM | 2024-01-22 | −24,20 % | Investigación contable anunciada el 21 de enero; [informe del emisor](https://s1.q4cdn.com/365366812/files/doc_downloads/2024/11/ADM-2023-12-31-10K_A.pdf). |
| ALGN | 2023-02-02 | +27,38 % | [Resultados publicados el 1 de febrero](https://investor.aligntech.com/news-releases/news-release-details/align-technology-announces-fourth-quarter-and-fiscal-2022/). |
| ALGN | 2023-10-26 | −24,88 % | [Resultados publicados el 25 de octubre](https://aligntech.gcs-web.com/news-releases/news-release-details/align-technology-announces-third-quarter-2023-financial-results). |
| AVGO | 2024-12-13 | +24,43 % | [Resultados publicados el 12 de diciembre](https://www.sec.gov/Archives/edgar/data/1730168/000173016824000125/avgo-11032024x8kxex99.htm). |
| AXON | 2024-11-08 | +28,68 % | [Resultados publicados el 7 de noviembre](https://www.sec.gov/Archives/edgar/data/1069183/000106918324000055/axon-20241107.htm). |

## Cobertura por empresa

Cada fila cubre las 508 sesiones capturadas. «Yahoo» implica cierre ajustado y conciliación diaria con Findata. «Emisor» identifica la excepción AVB. Los contadores de dividendos son registros de fecha ex-dividendo; no importes comparables entre compañías.

| Empresa | Sesiones | Splits | Dividendos | Procedencia |
|---|---:|---:|---:|---|
| A | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AAPL | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ABBV | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ABNB | 508 | 0 | 0 | Yahoo + conciliación Findata |
| ABT | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ACGL | 508 | 0 | 1 | Yahoo + conciliación Findata |
| ACN | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ADBE | 508 | 0 | 0 | Yahoo + conciliación Findata |
| ADI | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ADM | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ADP | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ADSK | 508 | 0 | 0 | Yahoo + conciliación Findata |
| AEE | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AEP | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AES | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AFL | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AIG | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AIZ | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AJG | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AKAM | 508 | 0 | 0 | Yahoo + conciliación Findata |
| ALB | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ALGN | 508 | 0 | 0 | Yahoo + conciliación Findata |
| ALL | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ALLE | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AMAT | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AMCR | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AMD | 508 | 0 | 0 | Yahoo + conciliación Findata |
| AME | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AMGN | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AMP | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AMT | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AMZN | 508 | 0 | 0 | Yahoo + conciliación Findata |
| ANET | 508 | 1 | 0 | Yahoo + conciliación Findata |
| AON | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AOS | 508 | 0 | 8 | Yahoo + conciliación Findata |
| APA | 508 | 0 | 8 | Yahoo + conciliación Findata |
| APD | 508 | 0 | 7 | Yahoo + conciliación Findata |
| APH | 508 | 1 | 8 | Yahoo + conciliación Findata |
| APO | 508 | 0 | 8 | Yahoo + conciliación Findata |
| APTV | 508 | 0 | 0 | Yahoo + conciliación Findata |
| ARE | 508 | 0 | 8 | Yahoo + conciliación Findata |
| ATO | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AVB | 508 | 0 | 8 | Emisor + Findata |
| AVGO | 508 | 1 | 8 | Yahoo + conciliación Findata |
| AVY | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AWK | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AXON | 508 | 0 | 0 | Yahoo + conciliación Findata |
| AXP | 508 | 0 | 8 | Yahoo + conciliación Findata |
| AZO | 508 | 0 | 0 | Yahoo + conciliación Findata |
| BA | 508 | 0 | 0 | Yahoo + conciliación Findata |

## Reproducción y alcance de aceptación

```powershell
.\.venv\Scripts\python.exe scripts/review_historical_prices.py --output artifacts/review-NOMBRE-NUEVO --facts artifacts/longitudinal-preflight-v1/data.json --cached-responses artifacts/price-review-adjusted-v1/responses --issuer-actions benchmarks/colaboracion-historica-v1/issuer-actions.json
.\.venv\Scripts\python.exe -m research_benchmarks longitudinal run benchmarks/colaboracion-historica-v1/reviewed-scenario.yaml --data artifacts/price-review-adjusted-v3/data.json --output artifacts/campana-NOMBRE-NUEVO
```

La reproducción del cálculo reutiliza respuestas congeladas; una descarga nueva puede cambiar precios ajustados. La aprobación no es automática: `review.json` generado inicialmente queda en `awaiting_review`. La revisión documentada aprobó el dataset con SHA-256 `2b65121feae3ae0f2784584f53af6649856d988997eda6eb402f0a71f2b58745`. Conservar la campaña **y** el directorio de revisión para trasladar la procedencia completa. Los datos y capturas son locales e ignorados; los scripts, escenarios y explicación están en el repositorio.

Este trabajo habilita el baseline con esa convención y sus límites. No se ha ejecutado aquí la campaña de dos años. La [prueba corta real](historical-smoke.md) tiene su propia definición y evidencia.
