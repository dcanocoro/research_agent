# Criterios de evaluación aplicados a V0

**Versión de la rúbrica aportada:** 1.0.  
**Aplicación documentada:** 2026-11-08.  
**Ámbito:** evaluación retrospectiva de V0, una pareja de ejecuciones de 150 llamadas.

Se conserva la rúbrica D1–D5 de 0 a 4 y los indicadores T1/T2 del texto aportado
por el usuario. Se adapta exclusivamente el diseño del informe a la campaña realizada.
El texto de ejemplo no se interpreta como configuración ejecutada ni como encargo.
La rúbrica se aplica después de la campaña; no fue un criterio registrado antes de
lanzarla. Sus puntuaciones son juicios del evaluador, no mediciones automáticas.

## Aplicación y reglas de evidencia

- V0 es la campaña; V0-SN (sin nota) y V0-CN (con nota) son dos condiciones, con una
  ejecución por condición. No son repeticiones equivalentes ni agentes colaborando.
- La evaluación es externa al ciclo y posterior al cierre. El mismo asistente participó
  en preparación/correcciones y revisión; sin segundo evaluador ni condiciones ocultas.
- Se utilizan estado inicial/final, snapshots, eventos, materiales, Progress, notas y
  payloads disponibles. La calificación interna de Progress no sustituye el juicio externo.
- Referencia 120 mediante snapshots consistentes más cercanos: 118 SN y 124 CN,
  desfases −2/+4; se añade el cierre real 150. No se inventan estados superiores al techo.
- Cada valoración contiene soporte y límites. No se atribuye al snapshot integración
  posterior; material calculado sin integrar se identifica separadamente.
- N/O no equivale a cero. La falta de oportunidad controlada de revisar contradicciones
  externas limita D4; no demuestra incapacidad ni justifica penalización automática.
- Se distingue observación, interpretación y causa probable. Se evalúa el mandato real,
  sin añadir obligación de DCF, gestión de cartera o dataset congelado.
- Los intervalos son 0–corte y corte–150, usando las categorías T2 de la rúbrica.
- No se modifica arquitectura ni estados al evaluar. Recomendaciones son hipótesis,
  no autorización de implementación o ejecución.
- Las capturas completas son locales e ignoradas por Git. El relato y sus referencias
  no sustituyen los originales. No se copian credenciales ni payloads privados.

## 4. Rúbrica de evaluación

La evaluación será **externa al funcionamiento del agente**. Codex analizará las trazas, checkpoints, resultados de herramientas y estado persistente, sin introducir feedback durante la campaña.

Las cinco capacidades serán las dimensiones principales. Añadiremos eficiencia y progreso incremental como medidas transversales.

### 4.1. Dimensiones

| Dimensión | Qué evaluamos | Evidencias observables |
|---|---|---|
| **D1. Investigación** | Capacidad para obtener y utilizar conocimiento relevante, fiable y suficiente | Fuentes, cobertura de cuestiones materiales, datos contrastados, trazabilidad |
| **D2. Razonamiento** | Capacidad para transformar información en hipótesis, modelos, valoraciones y juicios defendibles | Argumentos, cálculos, hipótesis alternativas, incertidumbres, conclusiones |
| **D3. Integración** | Capacidad para conectar conocimientos y conservar coherencia entre expedientes | Relaciones económicas, dependencias, modelos compartidos, consistencia |
| **D4. Aprendizaje** | Capacidad para aprovechar descubrimientos, corregir errores y actualizar conocimientos | Revisiones, contradicciones resueltas, cambios justificados, reutilización |
| **D5. Autodirección** | Capacidad para seleccionar y ejecutar acciones de investigación útiles | Prioridades, compromisos, cambios de dirección, decisiones de profundizar o cerrar |
| **T1. Eficiencia** | Recursos consumidos en relación con el progreso | Llamadas, consultas redundantes, coste, trabajo improductivo |
| **T2. Progreso incremental** | Mejora o deterioro del conocimiento y de los juicios entre checkpoints | Cambios de calidad, incertidumbres resueltas, regresiones |

### 4.2. Escala común

Cada dimensión D1–D5 recibirá una puntuación de 0 a 4.

| Puntuación | Criterio |
|---|---|
| **0 — Ausente** | No se observa la capacidad, o existe evidencia clara de fallo grave |
| **1 — Incipiente** | Comportamiento parcial, superficial o predominantemente incorrecto |
| **2 — Funcional** | Comportamiento útil, pero con carencias materiales de calidad, consistencia o autonomía |
| **3 — Sólido** | Comportamiento fundamentado, coherente y útil, con deficiencias menores |
| **4 — Avanzado** | Comportamiento robusto, crítico, adaptable y económicamente relevante |

**N/O — No observable:** las trazas o el escenario no permiten evaluar la dimensión. No equivale a 0.

### 4.3. Criterios específicos por dimensión

**D1. Investigación**

- Identifica cuestiones económicamente relevantes.
- Recupera datos verificables con fechas, periodos y unidades.
- Distingue hechos, inferencias e incertidumbres.
- Contrasta información cuando existe conflicto.
- No confunde volumen documental con conocimiento útil.

**D2. Razonamiento**

- Formula hipótesis económicas y financieras explícitas.
- Conecta fundamentos empresariales con proyecciones y valoración.
- Considera explicaciones alternativas y evidencia adversa.
- Utiliza cálculos y supuestos consistentes.
- Produce juicios de inversión, con incertidumbre y condiciones que podrían modificarlos.

**D3. Integración**

- Reutiliza conocimientos de otros expedientes.
- Identifica relaciones económicas justificadas entre empresas.
- Conecta hipótesis con modelos, valoraciones y evaluaciones.
- Mantiene coherencia entre conclusiones relacionadas.
- Diferencia dependencias documentadas de relaciones hipotéticas.

**D4. Aprendizaje**

- Aprovecha descubrimientos y decisiones anteriores.
- Detecta contradicciones o errores.
- Revisa hipótesis, modelos o conclusiones cuando procede.
- Conserva el conocimiento válido y evita reabrir innecesariamente cuestiones resueltas.
- Propaga las revisiones a los elementos dependientes.

Importante: no se penalizará al agente por no revisar conclusiones cuando no existan motivos para ello. La ausencia de oportunidades observables de revisión deberá reflejarse como limitación de la evaluación.

**D5. Autodirección**

- Identifica las principales incertidumbres pendientes.
- Prioriza asuntos con posible impacto económico.
- Selecciona acciones proporcionales a su valor esperado.
- Reconoce cuándo profundizar, contrastar, cambiar de enfoque o finalizar.
- Evita ciclos improductivos y trabajo repetitivo sin justificación.

### 4.4. Indicadores transversales

**T1. Eficiencia**

Registrar:

- Llamadas totales y por componente.
- Coste y duración, cuando estén disponibles.
- Llamadas destinadas a investigación, integración, revisión, evaluación interna y operaciones.
- Repeticiones evitables.
- Trabajo sin contribución identificable.

No convertir automáticamente estos datos en una puntuación de calidad. Un análisis difícil puede necesitar muchas llamadas.

**T2. Progreso incremental**

En cada intervalo evaluar:

- Conocimiento material incorporado.
- Incertidumbres relevantes reducidas o resueltas.
- Nuevas conclusiones defendibles.
- Conclusiones anteriores fortalecidas o corregidas.
- Contradicciones y errores introducidos.
- Trabajo repetido y estancamientos.

Clasificar cada intervalo como:

**Regresión material / Estancamiento / Progreso limitado / Progreso material / Progreso sustancial.**

La clasificación debe acompañarse de evidencias. El progreso sustancial exige cambios importantes en la calidad o utilidad de los juicios, no simplemente más producción.

### 4.5. Criterios de valoración general

La evaluación debe considerar expresamente:

1. **Calidad final:** qué conocimiento y juicios útiles existen al finalizar.
2. **Evolución:** cómo ha cambiado su calidad durante la campaña.
3. **Autonomía:** qué decisiones relevantes ha tomado el agente sin intervención externa.
4. **Fiabilidad:** qué errores o contradicciones materiales permanecen.
5. **Coste:** qué esfuerzo ha necesitado para conseguir el resultado.

Para V0 no se utilizará una media ponderada única como resultado principal. Se presentará el perfil de las cinco dimensiones, los indicadores transversales y una conclusión cualitativa fundamentada.
