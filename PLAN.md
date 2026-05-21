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

## Fase 4 — Enriquecimiento (Completada)

### NB04 — Actores viales, vehículos y causas

**Objetivo:** integrar capas hermanas SIMUR para enriquecer el IPI y distinguir perfiles de intervención por tipo de actor, vehículo y causa en cada zona priorizada.

**Salidas:**
- `outputs/reports/hotspots_enriquecidos_nb04.csv`
- `outputs/maps/mapa_hotspots_enriquecidos_nb04.html`
- `outputs/reports/resumen_ejecutivo_notebook_04.md`

**Estado:** Completado.

---

### NB04.5 — Análisis geoespacial avanzado (H3 + OSM + KDE)

**Objetivo:** superponer el IPI sobre hexágonos H3 y límites oficiales de localidades para habilitar visualización espacialmente coherente en el dashboard.

**Entradas:**
- `outputs/reports/zonas_criticas_IPI_completo_2016_2019.csv`

**Metodología:**
1. Mapeo de zonas IPI a celdas H3 resolución 8 (~460 m de diámetro) con `h3.latlng_to_cell()`
2. Descarga de límites de localidades Bogotá vía OSM (`osmnx.geocode_to_gdf`), con fallback convex hull
3. Spatial join zonas → localidades con GeoPandas
4. Agregación de IPI, siniestros, fallecidos por localidad y por hexágono H3
5. KDE con `scipy.stats.gaussian_kde` sobre coordenadas de las 17,130 zonas
6. 3 mapas Folium con leyendas en español: hexagonal H3, coropleta por localidad, calor + clusters
7. Export GeoJSON para consumo del dashboard

**Salidas:**
- `outputs/reports/ipi_hexagonos_h3.csv`
- `outputs/reports/ipi_por_localidad.csv`
- `outputs/reports/ipi_densidad_kde.csv`
- `outputs/reports/ipi_hexagonos_h3.geojson` (426 KB)
- `outputs/reports/ipi_por_localidad.geojson` (6.1 MB)
- `outputs/maps/mapa_ipi_hexagonos_h3.html`
- `outputs/maps/mapa_ipi_por_localidad.html`
- `outputs/maps/mapa_ipi_calor_clusters.html`
- `outputs/reports/figura_ipi_kde_superficie.png`
- `outputs/reports/figura_ipi_treemap_localidades.png`

**Estado:** Completado (2026-05-21).

---

## Fase 5 — Normalización (Completada)

### NB05 — Normalización por exposición

**Objetivo:** estimar tasas de accidentalidad por unidad de exposición. Distinguir entre zonas con muchos siniestros porque tienen mucho tráfico vs. zonas con alta tasa relativa de accidentalidad.

**Resultado clave:** solo el 10% del Top 200 volumétrico (20 zonas) tiene también alta tasa relativa. El 90% restante refleja el efecto de alto tráfico, no vías intrínsecamente peligrosas.

**Estado:** Completado.

---

## Fase 6 — Producto final (Completada)

### NB06 — Dashboard Streamlit

**Objetivo:** consolidar los resultados en un dashboard interactivo presentable y reproducible.

**Implementación:** `app/` — aplicación Streamlit multi-página.

**Páginas:**
| Página | Archivo | Descripción |
|---|---|---|
| 🏠 Inicio | `app/main.py` | KPIs globales + donut IPI + metodología |
| 🗺️ Mapa Interactivo | `pages/1_mapa.py` | 3 vistas Folium (H3 hex, coropleta, calor) |
| 🔴 Zonas Críticas | `pages/2_zonas_criticas.py` | Tabla filtrable + gráficos + radar + descarga CSV |
| 📍 Por Localidad | `pages/3_localidades.py` | Global view + detalle con Pydeck |
| 🤖 Agente IA | `pages/4_agente.py` | Chat Claude Opus 4.7 con prompt caching |

**Cómo correr:**
```bash
.venv\Scripts\streamlit.exe run app/main.py
```

**Estado:** Completado (2026-05-21). Dashboard funcional en localhost:8501.

---

## Infraestructura complementaria (Completada — 2026-05-21)

### MCP Server SIMUR (`mcp_simur/server.py`)
Expone datos SIMUR e IPI como herramientas Claude via protocolo MCP. 6 herramientas: `simur_contar_registros`, `simur_descargar_muestra`, `simur_localidades_activas`, `simur_estadisticas_zona`, `ipi_top_zonas`, `ipi_resumen_ejecutivo`. 2 recursos: `simur://metodologia`, `simur://estructura-campos`.

### Agente de insights (`agents/insights_agent.py`)
Script autónomo que usa Claude Opus 4.7 con prompt caching sobre el CSV IPI completo. Ejecuta preguntas predefinidas y muestra ahorro de tokens por caché.

### Suite de tests (`tests/`)
34 tests pytest: 18 de configuración, 13 de fórmula IPI (con validación de coordenadas y localidades), 7 de red (marcados `@network`).

### CI/CD (`.github/workflows/validate.yml`)
4 jobs: lint (ruff), tests unitarios (con stub data), ejecución NB03.5, integridad de notebooks.

---

## Criterios de avance entre fases

Antes de iniciar un nuevo notebook:
- El notebook anterior está ejecutado, sin celdas con errores.
- Los outputs están guardados y verificados.
- `memory/methodology.md`, `memory/decisions_log.md` y este `PLAN.md` están actualizados.
- `CHANGELOG.md` tiene la entrada correspondiente.
