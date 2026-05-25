# Próximos pasos — VíaSegura AI

> **Para qué sirve este archivo:** saber qué hacer cuando se retoma el proyecto. Se actualiza al cerrar cada notebook o hito importante.

---

## Estado actual (actualizado 2026-05-24)

- [x] NB01 — Exploración y validación de datos SIMUR 2016–2019
- [x] NB02 — IPI, familias analíticas, Top 50, mapa final **(corregido: pesos iguales via fix_ipi_nb02.py)**
- [x] NB03 — Validación de actualidad + exploración de capas complementarias SIMUR
- [x] NB03.5 — Síntesis metodológica: variables, IPI, índices de criticidad, limitaciones
- [x] NB04 — Enriquecimiento con actores viales, vehículos, causas (integración FORMULARIO + capas hermanas SIMUR)
- [x] NB04.5 — Análisis geoespacial avanzado: H3, choropleth, heatmap, KDE de densidad, top vías/barrios
- [x] NB05 — Normalización por exposición (km red vial OSM + población DANE 2018); tipología hotspots relativos ocultos
- [x] App Streamlit — 4 páginas operativas (ver sección abajo)
- [x] CI — 4 jobs en producción (lint, tests-unit, notebook-035, notebook-integrity)
- [x] Snapshot MD5 generado: `data/raw/_snapshot_metadata.json`
- [x] ADR-11 documentado: puntos de intervención para parametrizar pesos del IPI

---

## App Streamlit — Estado y descripción de páginas

**Comando:** `.venv\Scripts\streamlit.exe run app/main.py`

### Página principal (`app/main.py`) — Dashboard de inicio
- KPIs globales: total siniestros (260,831), accidentes fatales (eventos SIMUR con ≥1 muerto), zonas analizadas (17,130), zonas Prioridad 1 (50), IPI máximo con localidad.
- Tabla metodológica del IPI: 5 dimensiones con pesos iguales (20% cada una).
- Gráfico Plotly de distribución de zonas por prioridad (P1/P2/P3).
- Sidebar con navegación entre las 4 páginas.

### Página 1 (`app/pages/1_mapa.py`) — Mapa Interactivo
- 3 capas seleccionables via radio button: hexágonos H3 (IPI por zona ~460m), choropleth por localidad, heatmap + clusters de Prioridad 1.
- Mapas folium pre-generados en `outputs/maps/` cargados como HTML embebido.
- Métricas contextuales (zonas P1, IPI máximo, accidentes fatales).
- **Pendiente de mejora:** los mapas son estáticos (pre-generados), sin filtros dinámicos ni tooltips enriquecidos con actor/vehículo/causa.

### Página 2 (`app/pages/2_zonas_criticas.py`) — Zonas Críticas
- Tabla filtrable con sidebar (filtros por prioridad, localidad, clase de accidente, años activos mínimos, top N).
- Descarga CSV del subset filtrado.
- 3 tabs: Tabla coloreada por prioridad | Gráficos (histograma IPI + scatter siniestros vs IPI + radar de scores) | Top vías y barrios (bar charts horizontales).
- Lookup OSM para sustituir `SIN_NMG` con nombre aproximado de vía (identificado por Nominatim/Overpass, mayo 2026).

### Página 3 (`app/pages/3_localidades.py`) — Análisis por Localidad
- Vista global: bar chart de IPI (P75) por localidad + scatter bubble (siniestros vs zonas P1) + tabla completa.
- Vista de localidad específica (selectbox): KPIs, top 10 barrios de la localidad, distribución anual de criticidad 2016-2019, mapa pydeck de puntos de la localidad.

### Página 4 (`app/pages/4_agente.py`) — Agente IA
- Chat con Claude Haiku 4.5 via API Anthropic.
- Prompt caching del contexto IPI (top 200 zonas + estadísticas globales + ranking localidades + top vías + top barrios + tipología NB05).
- API key configurable via sidebar o `.env`.
- 6 preguntas sugeridas en sidebar. Muestra tokens utilizados y estado de caché por turno.

---

## CI — Estado (4 jobs en producción)

| Job | Nombre | Disparo | Estado |
|---|---|---|---|
| 1 | lint (ruff) | push a main/develop, PR a main | Activo |
| 2 | tests-unit | tras lint | Activo (stub data 25k filas) |
| 3 | notebook-035 | solo push main o PR a main | Activo |
| 4 | notebook-integrity | tras lint | Activo (valida JSON de todos los .ipynb) |

**Lección CI clave:** tests de red SIMUR usan `pytest.skip` como primera línea del fixture + `collect_ignore` en `conftest.py` + `--ignore=tests/test_data_loader.py` en el YAML. SIMUR es geo-restringido desde GitHub Actions (fuera de Colombia devuelve count=0).

---

## NB04.5 — Análisis Geoespacial Avanzado (COMPLETO)

**Archivo:** `notebooks/04.5_analisis_geoespacial_avanzado.ipynb`

**Qué hace:**
1. Hexágonos H3 resolución 8 (~460m): 581 hexágonos cubriendo Bogotá, con IPI máximo por hexágono. 153 Crítico (IPI≥90), 270 Alto (IPI 75-90).
2. Polígonos de localidades vía OSM + join espacial con zonas IPI. Exporta `ipi_por_localidad.geojson` (5.8 MB).
3. Mapa choropleth de IPI por localidad con `folium.Choropleth` + marcadores circulares por localidad.
4. Mapa hexágonos H3 coloreados por categoría IPI, sobre fondo dark matter.
5. Mapa combinado: HeatMap de 5,000 accidentes + MarkerCluster de 50 zonas Prioridad 1.
6. Análisis de densidad espacial: KDE sobre top-500 zonas IPI (ponderado por IPI/100) + mapa de persistencia temporal.
7. Top 15 vías y barrios: por criticidad acumulada y por IPI máximo.

**Outputs generados:**

| Archivo | Tamaño |
|---|---|
| `outputs/maps/ipi_hexagonos_h3.geojson` | 426 KB |
| `outputs/maps/ipi_por_localidad.geojson` | 5.8 MB |
| `outputs/maps/mapa_choropleth_localidades_IPI.html` | 5.8 MB |
| `outputs/maps/mapa_hexagonos_H3_IPI.html` | 472 KB |
| `outputs/maps/mapa_heatmap_clusters_P1.html` | 229 KB |
| `outputs/reports/densidad_espacial_IPI.png` | 591 KB |
| `outputs/reports/top_vias_barrios_criticos.png` | 121 KB |
| `outputs/reports/top_vias_criticas_geoespacial.csv` | 0.9 KB |
| `outputs/reports/top_barrios_criticos_geoespacial.csv` | 0.8 KB |
| `outputs/reports/ipi_por_localidad_stats.csv` | 22 KB |

**Nota metodológica:** el spatial join localidades usa polígonos OSM, que incluyen entidades superpuestas (Colombia, Cundinamarca, UPZs, Bogotá D.C. Municipio). El fallback usa `localidad_predominante` del IPI cuando el sjoin no asigna localidad. El join es funcional para la app pero no está depurado para análisis de cobertura exacta.

---

## NB05 — Normalización por Exposición (COMPLETO)

**Outputs clave:** `outputs/reports/hotspots_normalizados_nb05.csv`

**Tipología de 4 clases:** hotspot absoluto y relativo | hotspot absoluto oculto relativo | hotspot relativo oculto | zona de baja prioridad.

**Exposición usada:** km de red vial OSM por zona + población DANE 2018 a nivel localidad (no UPZ — limitación L6).

---

## Próximos pasos reales (prioridad decreciente)

### PR-2 — Validación externa con datos ANSV/IDU (alta prioridad)
- Contrastar el ranking IPI con datos de siniestralidad publicados por la ANSV para el mismo periodo.
- Comparar con planes de seguridad vial del IDU para verificar si las zonas Prioridad 1 ya tienen intervención planificada o ejecutada.
- **Por qué es importante:** es la única validación externa del modelo. Sin esto, el IPI es autovalidado.

### PR-4 — Página de intervenciones (media prioridad)
- Nueva página Streamlit que cruce zonas Prioridad 1 con tipología NB05 + actor predominante + causa predominante.
- Propuesta: tabla de recomendaciones por zona (ingeniería, fiscalización, educación).
- Insumos ya disponibles: `hotspots_normalizados_nb05.csv`, top_vias, top_barrios.

### Mejora de página mapa (media prioridad)
- Problema: los 3 mapas son archivos HTML estáticos pre-generados; no se pueden filtrar dinámicamente.
- Opciones: integrar pydeck con GeoJSONs en Streamlit | regenerar HTMLs con parámetros desde la app | añadir tooltips enriquecidos con actor/vehículo/causa al HTML de hexágonos.
- **Esfuerzo estimado:** 1-2 días.

### NB06 — Síntesis final y portafolio (baja prioridad inmediata)
- Notebook narrativo de cierre: integra hallazgos de NB01–NB05, conclusiones metodológicas, limitaciones, y recomendaciones de política.

---

## Deuda técnica pendiente

| ID | Ítem | Estado |
|---|---|---|
| DT-01 | Mover funciones repetidas a `src/` | Parcialmente hecho |
| DT-02 | Parametrizar pesos IPI (actualmente fijos 1/3/5) | Pendiente |
| DT-03 | Análisis de sensibilidad EPDO vs 1/3/5 | Documentado en ADR-12; 84.5% estabilidad del top 50 |
| DT-04 | Comparar métodos de agregación: 3-decimal vs H3 vs DBSCAN | H3 implementado en NB04.5; comparación formal pendiente |
| DT-05 | Spatial join localidades: depurar polígonos OSM anidados | Pendiente — ver nota NB04.5 arriba |

---

## Hoja de ruta completa

| Notebook | Nombre | Estado |
|---|---|---|
| NB01 | Exploración y validación de datos SIMUR | Completado |
| NB02 | Índice de criticidad y hotspots (IPI) | Completado |
| NB03 | Validación de actualidad + exploración SIMUR | Completado |
| NB03.5 | Síntesis metodológica | Completado |
| NB04 | Enriquecimiento con actores, vehículos, causas | Completado |
| NB04.5 | Análisis geoespacial avanzado (H3, mapas folium) | Completado |
| NB05 | Normalización por exposición (red vial + población) | Completado |
| NB06 | Síntesis final y portafolio | Pendiente |
