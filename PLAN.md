# Plan del proyecto — VíaSegura AI

> Este archivo describe la hoja de ruta completa por notebook. Se actualiza al completar cada fase.

---

## Fase 1 — Datos base y exploración (Completada)

### NB01 — Exploración y validación de datos SIMUR

**Objetivo:** conectar a la fuente oficial, auditar la disponibilidad de datos, descargar el periodo base y construir una base limpia validada.

**Entradas:** API ArcGIS SIMUR — FeatureServer/2 (capa ACCIDENTE)

**Salidas:**
- `data/raw/accidentes_bogota_2016_2019_raw.csv` — 260,831 registros
- `data/raw/chunks_accidentes_2016_2019/` — 262 chunks de descarga
- `data/processed/accidentes_bogota_2016_2019_limpio.csv` — 260,831 registros, 19 columnas
- `outputs/reports/auditoria_conteo_siniestros_por_anio.csv`
- `outputs/maps/mapa_calor_criticidad_siniestros_2016_2019.html`

**Estado:** Completado.

---

## Fase 2 — Priorización espacial con IPI (Completada)

### NB02 — Índice de Prioridad de Intervención (IPI)

**Objetivo:** construir un índice multidimensional para priorizar zonas de intervención. Pasar del mapa descriptivo de siniestros a una lista rankeada y defendible.

**Entradas:** `data/processed/accidentes_bogota_2016_2019_limpio.csv`

**Metodología central:**
1. Agregación espacial en grilla de 0.001° (~111 m × 111 m)
2. Puntaje de gravedad: SOLO DAÑOS=1, CON HERIDOS=3, CON MUERTOS=5
3. 5 scores normalizados: volumen, criticidad total, severidad promedio, persistencia temporal, fatalidad
4. IPI = promedio de los 5 scores × 100
5. Clasificación en 5 familias analíticas

**Salidas:**
- `outputs/reports/top50_IPI_final_2016_2019.csv` — Top 50 operativo
- `outputs/reports/zonas_criticas_IPI_completo_2016_2019.csv` — Todas las zonas
- `outputs/reports/resumen_familia_analitica_2016_2019.csv`
- `outputs/reports/resumen_concentracion_IPI_2016_2019_final.csv`
- `outputs/maps/mapa_top50_IPI_final_2016_2019.html`
- `outputs/reports/resumen_ejecutivo_notebook_02.md`

**Estado:** Completado.

**Correcciones aplicadas (2026-05-08):**
- Bug ADR-06: celda `4e635223` usaba pesos desiguales (0.25/0.15) en vez de `mean()`. Corregido via `fix_ipi_nb02.py`.
- Todos los outputs IPI regenerados con pesos iguales. Distribución familias: Robusto=45, Severidad/fatalidad=68, Carga acumulada=155, Preventivo=346.
- Nota: NB03 se ejecutó con el IPI anterior. Los cambios de ranking son menores (~0.03 pts en top zonas). Se recomienda reejecutar NB03 antes de NB05.

---

## Fase 3 — Validación de actualidad (Completada)

### NB03 — Validación de actualidad + exploración de capas SIMUR

**Objetivo:** validar si las zonas priorizadas en 2016–2019 siguen siendo relevantes con datos recientes. Explorar capas complementarias de SIMUR para enriquecer el análisis.

**Estado: Completado (2026-05-07)**

**Resultados clave:**
- Periodo post-base seleccionado: **2020–2021** (ADR-10 — 2022–2025 excluidos por ratio gravedad anómalo)
- 72,903 siniestros descargados (44,049 en 2020 + 28,854 en 2021)
- Solapamiento Top 200 base vs reciente: **37 zonas (18.5%)**
- Clasificación: 37 Persistentes / 163 Emergentes / 35 Disminuidos / 0 Históricos / 2,211 Sensibles fatalidad
- 7 capas hermanas SIMUR auditadas; 4 para NB04 (ACTOR_VIAL, CAUSA, VEHICULO, VIA)
- 19 outputs generados y verificados

**Correcciones aplicadas:**
- Bug merge Sección 9 corregido: celdas `5829fb7d` y `ce83497a` usan `zonas_base_m` con rename `LAT_ZONA→lat_grid`
- Resumen ejecutivo: `outputs/reports/resumen_ejecutivo_notebook_03.md`

**Salidas:**
- `data/processed/accidentes_bogota_reciente_limpio.csv`
- `outputs/reports/clasificacion_hotspots_persistencia_notebook_03.csv`
- `outputs/reports/comparacion_IPI_base_vs_reciente_notebook_03.csv`
- `outputs/maps/mapa_clasificacion_persistencia_notebook_03.html`
- `outputs/maps/mapa_comparacion_persistencia_notebook_03.html`
- `outputs/reports/esquema_integracion_nb04_notebook_03.csv`
- `outputs/reports/manifiesto_outputs_notebook_03_completo.csv`

---

## Fase 4 — Enriquecimiento (Próxima)

### NB04 — Actores viales, vehículos y causas

**Objetivo:** integrar capas hermanas SIMUR para enriquecer el IPI y distinguir perfiles de intervención por tipo de actor, vehículo y causa en cada zona priorizada.

**Entradas:**
- `outputs/reports/clasificacion_hotspots_persistencia_notebook_03.csv`
- `outputs/reports/top200_IPI_reciente_notebook_03.csv`
- `data/processed/accidentes_bogota_reciente_limpio.csv`
- `outputs/reports/esquema_integracion_nb04_notebook_03.csv`

**Tareas:**
1. Para cada zona del Top 200 reciente: obtener FORMULARIOs de siniestros en esa celda
2. JOIN a VM_ACC_ACTOR_VIAL (layer 3) → moda de campo `CONDICION`
3. JOIN a VM_ACC_VEHICULO (layer 5) → moda de campo `CLASE`
4. JOIN a VM_ACC_CAUSA (layer 4) → moda de campo `NOMBRE`
5. Verificar cobertura de VM_ACC_VIA antes de incluirla (devolvió 0 en muestra)
6. Añadir columnas de contexto al DataFrame de clasificación
7. Generar mapa enriquecido con popup de actor/vehículo/causa por zona

**Salidas esperadas:**
- `outputs/reports/hotspots_enriquecidos_nb04.csv`
- `outputs/maps/mapa_hotspots_enriquecidos_nb04.html`
- `outputs/reports/resumen_ejecutivo_notebook_04.md`

**Estado:** Próximo. Insumos listos desde NB03.

---

## Fase 5 — Normalización (Pendiente)

### NB05 — Normalización por exposición

**Objetivo:** estimar tasas de accidentalidad por unidad de exposición. Distinguir entre zonas con muchos siniestros porque tienen mucho tráfico vs. zonas con alta tasa relativa de accidentalidad.

**Entradas:** base de accidentalidad + datos de población (DANE) + red vial (OSM o IGAC)

**Tareas (preliminares):**
1. Obtener población por UPZ o localidad (DANE)
2. Calcular longitud de red vial por zona (OSM o capa oficial)
3. Calcular tasa de siniestros por 10,000 habitantes
4. Calcular tasa de siniestros por km de red vial
5. Comparar ranking del IPI vs ranking de tasas normalizadas

**Estado:** Pendiente. Requiere fuentes externas adicionales (DANE, red vial).

---

## Fase 6 — Producto final (Pendiente)

### NB06 — Dashboard y síntesis

**Objetivo:** consolidar los resultados en un producto presentable y reproducible.

**Tareas (preliminares):**
1. Dashboard Streamlit en `app/`
2. Informe técnico PDF
3. README final con instrucciones de reproducción completa
4. Snapshot y hash de todas las fuentes usadas

**Estado:** Pendiente. Depende de NB04 y NB05.

---

## Criterios de avance entre fases

Antes de iniciar un nuevo notebook:
- El notebook anterior está ejecutado, sin celdas con errores.
- Los outputs están guardados y verificados.
- `memory/methodology.md`, `memory/decisions_log.md` y este `PLAN.md` están actualizados.
- `CHANGELOG.md` tiene la entrada correspondiente.
