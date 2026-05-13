# Decisiones técnicas — VíaSegura AI

> Registro formal de Architecture Decision Records (ADR) para el proyecto. Cada entrada documenta el contexto, la decisión, la razón y las consecuencias. Las decisiones no se borran ni se sobreescriben: si una decisión cambia, se agrega una nueva entrada que la supersede.

---

## ADR-01 — Fuente de datos: API ArcGIS SIMUR vs archivos estáticos

**Fecha:** Inicio del proyecto.
**Estado:** Activa.

**Contexto:** Los datos de siniestralidad de Bogotá están disponibles tanto en `datos.gov.co` (archivos planos descargables) como en la API ArcGIS del SIMUR de la Secretaría Distrital de Movilidad.

**Decisión:** Usar la API ArcGIS `AccidentalidadAnalisis/FeatureServer/2`.

**Razón:** La API ArcGIS es la fuente que la SDM actualiza directamente. Es más actualizada que los datasets en `datos.gov.co`, permite consultas filtradas por campo (año, localidad, etc.) y es reproducible mediante código.

**Consecuencias:**
- Dependencia de la disponibilidad del servidor SIMUR.
- Necesidad de descarga por bloques con manejo de errores y reanudación.
- Pendiente: crear snapshot con hash MD5 para blindar reproducibilidad.

---

## ADR-02 — Periodo base: 2016–2019

**Fecha:** Después de la auditoría por año en NB01.
**Estado:** Activa.

**Contexto:** La base completa de SIMUR cubre 2007–2026 (904,424 registros). Los años 2025–2026 están incompletos (año en curso). Los años 2023–2024 tienen ~14,000 registros vs ~65,000 del periodo estable, sin explicación clara. Los años 2020–2021 están afectados por la pandemia COVID-19.

**Decisión:** Trabajar con el periodo **2016–2019** como base de análisis.

**Razón:**
- Periodo cerrado, completo y consistente (~65,000 registros/año).
- Pre-pandemia, sin distorsiones en los patrones de movilidad.
- Cuatro años consecutivos permiten calcular persistencia temporal.
- Los años anteriores a 2016 tienen volúmenes más bajos (~55,000–58,000/año) que podrían reflejar menor cobertura de registro.

**Consecuencias:**
- Los resultados son válidos para el Bogotá pre-2020. No son un diagnóstico del Bogotá de 2026.
- La validación de actualidad con datos recientes es el objetivo del NB03.
- Todo lenguaje de presentación debe enmarcarlo explícitamente como "periodo base".

---

## ADR-03 — Puntaje de gravedad: escala 1/3/5

**Fecha:** Durante la limpieza de datos en NB01.
**Estado:** Activa para MVP. Pendiente de análisis de sensibilidad.

**Contexto:** Se necesita un puntaje numérico para ponderar la gravedad de los siniestros. Las tres categorías de GRAVEDAD son SOLO DAÑOS, CON HERIDOS, CON MUERTOS.

**Decisión:** Escala ordinal simple: SOLO DAÑOS = 1, CON HERIDOS = 3, CON MUERTOS = 5.

**Razón:** Sencilla, defendible para un MVP, fácil de comunicar. No requiere calibración con datos externos.

**Alternativas conocidas y sus implicaciones:**

| Escala | SOLO DAÑOS | CON HERIDOS | CON MUERTOS | Fuente |
|---|---|---|---|---|
| VíaSegura AI (actual) | 1 | 3 | 5 | Escala MVP |
| EPDO (NHTSA) | 1 | ~8 | ~24 | Equivalent Property Damage Only |
| Costos económicos (FHWA) | 1 | ~5 | ~542 | Valor estadístico de vida |

Con la escala 1/3/5, un accidente fatal equivale a 5 accidentes materiales. Con la escala EPDO equivale a 24. Esto significa que el IPI actual puede sub-rankear zonas con muchos muertos relativos al volumen total.

**Acción futura:** análisis de sensibilidad comparando el ranking del IPI con pesos 1/3/5 vs 1/8/24 vs 1/5/25.

---

## ADR-04 — Agregación espacial por grilla de 0.001° (~111 m × 111 m)

**Fecha:** Durante el mapa de calor en NB01 y el IPI en NB02.
**Estado:** Activa para las fases 1 y 2. Pendiente de evaluación comparativa.

**Contexto:** Para agregar 260,831 siniestros en zonas comparables se necesita una unidad espacial. Las opciones son: grilla regular, hexágonos H3, clustering DBSCAN, o segmentos de la red vial.

**Decisión:** Redondear coordenadas a 3 decimales (0.001°). Cada celda mide aproximadamente 111 m × 111 m en Bogotá.

**Razón:** Simple, rápido, reproducible sin dependencias externas, geográficamente interpretable. Permite comparar resultados entre NB01 (mapa de calor) y NB02 (IPI) sobre la misma grilla.

**Limitaciones conocidas:**
- La grilla no respeta la red vial ni las intersecciones reales.
- Una intersección puede quedar en la frontera entre 2 o 4 celdas y dividirse.
- No garantiza que cada celda sea un "punto negro" real de la red vial.

**Acción futura:** comparación con H3 (Uber), snap-to-network y DBSCAN para evaluar sensibilidad del Top 50 a la elección de grilla.

---

## ADR-05 — Normalización del IPI por percentil de rango

**Fecha:** NB02.
**Estado:** Activa.

**Contexto:** Los 5 componentes del IPI están en escalas distintas (número de siniestros, suma de criticidad, ratio de persistencia). Hay que normalizarlos antes de promediarlos.

**Decisión:** Normalización por rango percentil (`rank(x) / n`) para cuatro de los cinco scores. `score_persistencia` usa ratio directo `anios_activos / 4`.

**Razón:** La normalización min-max es sensible a outliers. La normalización por rango produce distribuciones uniformes y es robusta ante casos extremos. Para `score_persistencia`, el ratio directo es preferible porque la variable solo toma 4 valores discretos (1, 2, 3, 4 años) y un percentil de rango artificialmente distorsionaría esa escala.

**Consecuencias:** El IPI refleja la posición relativa de una zona dentro del conjunto completo, no su valor absoluto. Una zona con IPI 90 no significa que "90% de algo" — significa que supera en promedio al ~90% de las zonas en las 5 dimensiones.

---

## ADR-06 — IPI como promedio simple de 5 scores (pesos iguales)

**Fecha:** NB02.
**Estado:** Activa para MVP. Pendiente de evaluación.

**Contexto:** Una vez normalizados los 5 scores, hay que combinarlos. Las opciones son promedio simple (pesos iguales) o promedio ponderado (pesos definidos por experto o datos).

**Decisión:** `IPI = mean(score_volumen, score_criticidad_total, score_severidad_promedio, score_persistencia, score_fatalidad) × 100`

**Razón:** El promedio simple es transparente, reproducible y no requiere calibración. En ausencia de evidencia empírica que justifique una ponderación distinta, la igualdad de pesos es el supuesto más conservador y más fácil de defender.

**Acción futura:** análisis de sensibilidad con ponderaciones alternativas (ej: más peso a fatalidad o a persistencia).

---

## ADR-07 — Top 50 como output operativo principal

**Fecha:** NB02.
**Estado:** Activa.

**Contexto:** Se generaron Top 50, Top 200 y la tabla completa (~17,130 zonas).

**Decisión:** El Top 50 es el output operativo presentable. El Top 200 es la lista analítica extendida.

**Razón:** 50 zonas es manejable en una reunión técnica o un informe ejecutivo. Más allá de 50, la mayoría de las audiencias pierde el hilo del análisis. El Top 200 está disponible en CSV para análisis más profundos.

---

## ADR-08 — Clasificación en 5 familias analíticas

**Fecha:** NB02.
**Estado:** Activa.

**Contexto:** El IPI produce un ranking continuo pero no comunica por qué una zona es crítica. Dos zonas con IPI similar pueden tener perfiles completamente distintos.

**Decisión:** Clasificar zonas en 5 familias cualitativas según su perfil de scores:

| Familia | Perfil |
|---|---|
| Hotspot robusto integral | Alto en volumen, criticidad Y fatalidad. Problema multidimensional. |
| Hotspot de severidad/fatalidad | Score de severidad o fatalidad muy alto frente al volumen. Pocos siniestros pero muy graves. |
| Hotspot de carga acumulada | Alto volumen, baja severidad promedio. Problema de cantidad. |
| Hotspot preventivo prioritario | Señales de deterioro sin alcanzar aún los umbrales más altos. Intervención antes que escale. |
| Seguimiento | Resto de zonas con actividad de siniestralidad no prioritaria. |

**Razón:** Las familias permiten comunicar el tipo de intervención más adecuado. Una zona "de severidad/fatalidad" requiere ingeniería de seguridad vial; una "de carga acumulada" puede necesitar gestión de tráfico; una "preventiva" puede requerir solo señalización y educación vial.

---

## ADR-09 — Lenguaje técnico permitido y prohibido

**Fecha:** Definición del marco de comunicación del proyecto.
**Estado:** Permanente.

**Decisión:** Aplicar las siguientes convenciones de lenguaje en toda comunicación del proyecto.

**Permitido:**
- "zonas priorizadas", "zonas críticas"
- "concentración de siniestros", "criticidad"
- "prioridad exploratoria de intervención"
- "hotspot persistente", "hotspot emergente", "hotspot de severidad/fatalidad"

**Prohibido o a evitar:**
- "zonas más peligrosas" — implica riesgo relativo que no se ha medido
- "riesgo real" sin normalización por exposición
- afirmaciones causales sin datos adicionales ("esta intersección es peligrosa porque...")
- presentar resultados 2016–2019 como diagnóstico actual de Bogotá

**Razón:** la honestidad metodológica es un activo del proyecto. Afirmaciones que excedan lo que los datos permiten concluir dañan la credibilidad técnica.

---

## ADR-10 — Periodo de validación post-base: 2020–2021

**Fecha:** NB03, después de la auditoría de integridad de datos recientes.
**Estado:** Activa.

**Contexto:** La auditoría de la Sección 3 del NB03 evaluó los años 2020–2025 contra cuatro criterios de integridad: volumen de registros, cobertura mensual, ratio de gravedad (CON HERIDOS / SOLO DAÑOS), y cobertura de localidades.

**Resultados de la auditoría:**

| Año | Registros | % del base | Ratio gravedad | Desviación | Criterios cumplidos |
|---|---|---|---|---|---|
| 2020 | 44,049 | 67.6 % | 0.619 | 25.1 % | 4/4 ✅ |
| 2021 | 28,854 | 44.2 % | 0.633 | 27.9 % | 4/4 ✅ |
| 2022 | 25,446 | 39.0 % | 0.984 | 98.8 % | 3/4 ⚠️ |
| 2023 | 14,115 | 21.6 % | 11.17 | 2157 % | 2/4 ❌ |
| 2024 | 14,018 | 21.5 % | 11.87 | 2299 % | 2/4 ❌ |
| 2025 | 12,377 | 19.0 % | 13.73 | 2674 % | 2/4 ❌ |

**Decisión:** Usar **2020–2021** como periodo de validación post-base para la comparación del IPI.

**Razón:**
- 2020 y 2021 son los únicos años que pasan los 4 criterios de integridad.
- 2022–2025 presentan una estructura de gravedad radicalmente diferente al periodo base (ratio CON HERIDOS / SOLO DAÑOS > 10× en 2023–2025). Esto sugiere un cambio de metodología de registro en SIMUR, no una caída real en la accidentalidad.
- El periodo 2020–2021 no se usa como diagnóstico actual de Bogotá: incluye los años de pandemia COVID-19, con movilidad reducida.

**Marco de comunicación:**
- Los años 2020–2021 se denominan "periodo de validación post-base".
- No se presentan como diagnóstico del Bogotá de 2026.
- La comparación de IPI entre periodos es de rankings y presencia en cortes, no de magnitudes absolutas.

**Consecuencias:**
- `score_persistencia` del periodo reciente usa divisor `N_ANIOS_RECIENTES = 2`.
- Los outputs recientes se nombran con sufijo `_reciente_notebook_03` para distinguirlos de los del periodo base.
- Los años 2022–2025 quedan documentados como "no comparables para IPI" por posible cambio de estructura de reporte de gravedad en SIMUR.

---

## ADR-11 — Parametrización futura de pesos del IPI y puntaje de gravedad

**Fecha:** 2026-05-08.
**Estado:** Documentado. Pendiente de implementación.

**Contexto:** Los pesos del IPI (5 scores con `mean()`) y los pesos del puntaje de gravedad (1/3/5) son valores de MVP elegidos por simplicidad y transparencia. Análisis de sensibilidad futuros requerirán modificarlos.

**Decisión:** No refactorizar el código ahora. Documentar los puntos de intervención exactos para cuando se implemente la parametrización.

**Puntos de intervención en el código:**

| Constante | Archivo | Dónde está | Valor actual |
|---|---|---|---|
| `PESOS_GRAVEDAD` | `notebooks/02_indice_criticidad_y_hotspots.ipynb` | Celda de configuración inicial (Sección 1) | `{"SOLO DAÑOS": 1, "CON HERIDOS": 3, "CON MUERTOS": 5}` |
| `PESOS_IPI` | `notebooks/02_indice_criticidad_y_hotspots.ipynb` | Celda de cálculo del IPI (Sección 7) | `[1, 1, 1, 1, 1]` (iguales, vía `mean()`) |
| `N_ANIOS_BASE` | `notebooks/02_indice_criticidad_y_hotspots.ipynb` | Divisor de `score_persistencia` | `4` |
| `N_ANIOS_RECIENTES` | `notebooks/03_validacion_actualidad_y_enriquecimiento_simur.ipynb` | Divisor de `score_persistencia` reciente | `2` |

**Escalas alternativas documentadas para referencia:**

| Fuente | Solo daños | Con heridos | Con muertos |
|---|---|---|---|
| VíaSegura AI MVP | 1 | 3 | 5 |
| NHTSA EPDO | 1 | ~8 | ~24 |
| FHWA (costos económicos) | 1 | ~5 | ~542 |
| OMS / ETSC (QALY) | 1 | 10–15 | 70–150 |

**Acción futura:** cuando se ejecute el análisis de sensibilidad, crear una celda de configuración al inicio del NB02 con estas constantes exportables, y regenerar todos los outputs con sufijo `_v2`.

---

## ADR-12 — Sensibilidad del Top 200 a los pesos de gravedad (EPDO vs. 1/3/5)

**Fecha:** 2026-05-12.
**Estado:** Documentado. Pendiente de decisión sobre ADR-11.

**Contexto:** En la Sección 13.2 de NB04 se realizó un análisis de sensibilidad comparando el ranking de zonas bajo dos esquemas de pesos:
- **Actual (VíaSegura AI MVP):** SOLO DAÑOS=1, CON HERIDOS=3, CON MUERTOS=5
- **EPDO estándar (FHWA/HSM):** SOLO DAÑOS=1, CON HERIDOS=8, CON MUERTOS=24

**Resultados del análisis (periodo reciente 2020–2021):**
- Top 200 estable: **169/200 zonas coinciden** (84.5% de solapamiento)
- 31 zonas cambiarían al usar pesos EPDO
- Correlación Spearman entre rankings: **ρ = 0.81** (p < 0.001)
- Top 50 estable: 40/50 (80% de solapamiento)

**Decisión:** Los pesos 1/3/5 producen un Top 200 razonablemente estable (84.5%), pero con variación material. Se documenta como **limitación L-9**.

**Razón:** La correlación de 0.81 indica que el orden relativo entre zonas se preserva en gran medida, pero el 15.5% de variación en el Top 200 es suficiente para que las recomendaciones de intervención difieran según el esquema de pesos. EPDO amplifica el peso de los muertos (×4.8 vs muertos en 1/3/5), lo que eleva las zonas con accidentes fatales aunque sean menos frecuentes.

**Consecuencias:**
- Los outputs de NB04 y NB05 se generan con pesos 1/3/5 (MVP). 
- El análisis de sensibilidad completo (regenerar IPI con EPDO) queda pendiente para una versión posterior.
- En comunicaciones del proyecto, presentar las 31 zonas de diferencia como banda de incertidumbre metodológica.
- Considerar presentar dos listas paralelas ("IPI volumétrico" con 1/3/5 y "IPI fatalidad" con pesos EPDO) en el dashboard NB06.

---

## ADR-13 — CONDICION vs. CLASE: distinción rol/vehículo en VM_ACC_ACTOR_VIAL

**Fecha:** 2026-05-12.
**Estado:** Activa. Corrección aplicada en NB04 v2.

**Contexto:** En la primera versión de NB04 se interpretó erróneamente que el campo `CONDICION` de la capa VM_ACC_ACTOR_VIAL registraba el tipo de vehículo del actor. En realidad, `CONDICION` registra el **rol** del actor en el siniestro.

**Distinción crítica:**
- `CONDICION` (Layer 3 — VM_ACC_ACTOR_VIAL): rol del actor → CONDUCTOR, PASAJERO, PEATON, CICLISTA, MOTOCICLISTA
- `CLASE` (Layer 5 — VM_ACC_VEHICULO): tipo de vehículo → AUTOMOVIL, MOTOCICLETA, BUS, CAMIONETA, BICICLETA

**Por qué CONDUCTOR domina (97% de zonas en v1):** Todo conductor —de automóvil, moto o bus— aparece como "CONDUCTOR" en CONDICION. La dominancia de CONDUCTOR no indica que "solo hay carros"; indica que la mayoría de actores son conductores (no peatones ni pasajeros).

**Distribución real de vehículos (CLASE, Top 200 reciente):**

| Clase | % promedio por zona |
|---|---|
| AUTOMOVIL | 31.5% |
| MOTOCICLETA | 24.9% |
| BUS | 10.6% |
| CAMIONETA | 10.3% |
| BICICLETA | 8.8% |

**Decisión:** Renombrar `actor_predominante` → `condicion_predominante` y reemplazar columnas de moda por distribuciones completas por zona. Aplicado en NB04 v2 (Sección 10).

**Consecuencias:**
- El CSV de outputs (`hotspots_enriquecidos_nb04.csv`) ahora tiene columnas `pct_conductor`, `pct_motociclista`, `pct_automovil`, `pct_motocicleta`, `pct_bus`, `pct_camioneta`, `pct_bicicleta`, `pct_ciclista`, `pct_peaton`, `pct_pasajero` más HHI por dimensión.
- El mapa interactivo muestra distribuciones en el popup, no solo la moda.
- Lección: verificar siempre el diccionario de campos SIMUR antes de interpretar columnas.
