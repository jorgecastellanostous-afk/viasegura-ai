# Changelog — VíaSegura AI

> Registro cronológico de cambios significativos por fase de trabajo. Las fechas son aproximadas al mes de trabajo.

---

## [DT-01 / DT-02 / DT-03 — Infraestructura de ingeniería] — 2026-05-21

### DT-01 — Módulo `src/` reutilizable

- `src/__init__.py` — re-exporta todos los símbolos públicos.
- `src/data_utils.py` — limpieza y validación de siniestros (NB01): `limpiar_siniestros`, `validar_coordenadas`, `calcular_puntaje_gravedad`. Constantes `PUNTAJE_GRAVEDAD` y `PUNTAJE_EPDO`.
- `src/ipi_utils.py` — cálculo del IPI (NB02): `calcular_ipi`, `asignar_prioridad_ipi`, `clasificar_familia_analitica`, `clasificar_hotspot`. Constante `SCORES_COLS`.
- `src/geo_utils.py` — utilidades H3/GeoPandas con lazy import: `asignar_h3`, `h3_to_polygon`, `agregar_por_hexagono`, `clasificar_hex`. Guard `_GEO_AVAILABLE` para entornos sin geopandas.
- `src/simur_client.py` — cliente SIMUR con descarga paginada + retry: `descargar_accidentes_por_anio_seguro`, `descargar_por_formularios`, `agregar_por_zona` (con HHI).
- `CLAUDE.md` y `AGENTS.md` — instrucciones de proyecto para Claude Code.

### DT-02 — Suite de tests unitarios (133 tests, 93% cobertura)

- `tests/test_data_utils.py` — 21 tests: bbox, puntajes gravedad/EPDO, parseo fechas, inmutabilidad.
- `tests/test_ipi_utils.py` — 29 tests: rango IPI [0,100], scores [0,1], límites P1/P2/P3, fórmula exacta.
- `tests/test_geo_utils.py` — 27 tests: H3 bounds en Bogotá, CRS EPSG:4326, `_require_geo` error path.
- `tests/test_simur_client.py` — 27 tests: HTTP mocked, HHI monopoly/uniforme, cache resume desde CSV.
- `pyproject.toml` — añadido `pytest-cov`, markers `network`/`slow`, `per-file-ignores` para E402.

### DT-03 — CI/CD + CRLF

- `.github/workflows/validate.yml` — añadido `--cov=src --cov-fail-under=80` al job de tests; `h3` a pip install; `src/ app/ agents/ mcp_simur/` a targets de ruff.
- `.gitattributes` — `* text=auto eol=lf` para normalizar a LF en commit (previene fallas de `ruff format --check` en Ubuntu CI desde Windows).
- Corregidos 17 errores ruff en `agents/` y `mcp_simur/` (imports no usados, f-string sin placeholder, import múltiple).
- Normalización CRLF→LF en 28 archivos.

---

## [Fix IPI NB02] — 2026-05-08

### Corregido
- Bug ADR-06: celda `4e635223` en NB02 usaba pesos desiguales (`score_criticidad_total × 0.25`, `score_fatalidad × 0.15`) en lugar de `mean()` de 5 scores igualmente ponderados.
- Aplicado via `fix_ipi_nb02.py` (script standalone — workaround encoding Windows/conda).

### Outputs regenerados con pesos iguales
- `outputs/reports/zonas_criticas_IPI_completo_2016_2019.csv`
- `outputs/reports/top50_IPI_final_2016_2019.csv`
- `outputs/reports/top200_prioridad_intervencion_IPI_2016_2019.csv`
- `outputs/reports/zonas_criticas_IPI_familia_analitica_2016_2019.csv`
- `outputs/reports/resumen_familia_analitica_2016_2019.csv`
- `outputs/reports/resumen_concentracion_IPI_2016_2019_final.csv`
- `outputs/reports/zonas_sensibles_fatalidad_2016_2019.csv`
- `outputs/maps/mapa_top50_IPI_final_2016_2019.html`

### Nueva distribución de familias analíticas (post-fix)

| Familia | Zonas |
|---|---|
| Hotspot robusto integral | 45 |
| Hotspot de severidad/fatalidad | 68 |
| Hotspot de carga acumulada | 155 |
| Hotspot preventivo prioritario | 346 |
| Seguimiento | 16,516 |

### Impacto en NB03
NB03 fue ejecutado con el IPI anterior. El delta en valores IPI es ~0.03 pts en las zonas top. Los rankings y clasificaciones de persistencia no cambian de forma material. Se recomienda reejecutar NB03 antes de comenzar NB05.

---

## [NB02 completo] — 2025 Q1–Q2

### Añadido
- `notebooks/02_indice_criticidad_y_hotspots.ipynb` — Notebook completo del IPI.
- `outputs/reports/top50_IPI_final_2016_2019.csv` — Top 50 zonas por IPI (output operativo).
- `outputs/reports/top200_prioridad_intervencion_IPI_2016_2019.csv` — Top 200 extendido.
- `outputs/reports/zonas_criticas_IPI_completo_2016_2019.csv` — Todas las ~17,130 zonas con IPI completo.
- `outputs/reports/resumen_familia_analitica_2016_2019.csv` — Distribución de zonas por familia analítica.
- `outputs/reports/resumen_concentracion_IPI_2016_2019_final.csv` — Concentración de siniestros/muertes por corte Top N.
- `outputs/reports/zonas_sensibles_fatalidad_2016_2019.csv` — Zonas con presencia de siniestros con muertos.
- `outputs/reports/zonas_criticas_IPI_familia_analitica_2016_2019.csv` — Zonas clasificadas con familia.
- `outputs/maps/mapa_top50_IPI_final_2016_2019.html` — Mapa interactivo final del Top 50.
- `outputs/reports/resumen_ejecutivo_notebook_02.md` — Resumen ejecutivo del NB02.
- `outputs/reports/manifiesto_outputs_notebook_02.csv` — Lista de outputs con flag de existencia.

### Metodología incorporada
- Índice de Prioridad de Intervención (IPI): 5 scores normalizados promediados.
- Clasificación en 5 familias analíticas: robusto integral, severidad/fatalidad, carga acumulada, preventivo prioritario, seguimiento.
- Top 50 como output operativo de priorización.

### Resultado clave
El Top 50 IPI (0.29% de zonas) concentra el 6.39% de muertes del periodo. El Top 1000 (5.84% de zonas) concentra el 63.33% de muertes.

---

## [NB01 completo] — 2025 Q1

### Añadido
- `notebooks/01_exploracion_datos_siniestralidad.ipynb` — Notebook de exploración y descarga.
- `data/raw/accidentes_bogota_muestra_10000.csv` — Muestra exploratoria inicial.
- `data/raw/accidentes_bogota_2016_2019_raw.csv` — Base completa 2016–2019 descargada.
- `data/raw/chunks_accidentes_2016_2019/` — 262 chunks de descarga segura por año y bloque.
- `data/processed/accidentes_bogota_2016_2019_limpio.csv` — Base limpia con puntaje de gravedad.
- `outputs/reports/auditoria_conteo_siniestros_por_anio.csv` — Conteo oficial 2007–2026.
- `outputs/reports/resumen_calidad_datos_2016_2019.csv` — Métricas de calidad de la base.
- `outputs/reports/tabla_localidad_2016_2019.csv` — Siniestros y criticidad por localidad.
- `outputs/reports/tabla_gravedad_2016_2019.csv` — Distribución por gravedad.
- `outputs/reports/tabla_clase_accidente_2016_2019.csv` — Distribución por clase de accidente.
- `outputs/reports/tabla_anio_2016_2019.csv` — Distribución por año.
- `outputs/maps/mapa_calor_criticidad_siniestros_2016_2019.html` — Mapa de calor exploratorio.

### Validaciones realizadas
- Total descargado (260,831) coincide con conteo oficial del FeatureServer: diferencia = 0.
- Sin duplicados en OBJECTID, CODIGO_ACCIDENTE ni FORMULARIO.
- Sin nulos en coordenadas. Sin registros fuera del bounding box de Bogotá.
- Sin nulos en `puntaje_gravedad`.

---

## [Inicialización] — 2025 Q1

### Añadido
- Estructura de carpetas: `notebooks/`, `data/raw/`, `data/processed/`, `outputs/maps/`, `outputs/reports/`, `memory/`, `app/`, `sql/`.
- Archivos de memoria operativa: `memory/project_context.md`, `memory/methodology.md`, `memory/decisions_log.md`, `memory/code_log.md`, `memory/data_sources.md`.

---

## [NB03 Fase 2 completa] — 2026 Q2

### Añadido
- Secciones 5–10 de `notebooks/03_validacion_actualidad_y_enriquecimiento_simur.ipynb`
- `data/raw/chunks_accidentes_2020_2021/` — chunks de descarga del periodo reciente
- `data/raw/accidentes_bogota_reciente_raw.csv` — 72,903 registros crudos (2020–2021)
- `data/processed/accidentes_bogota_reciente_limpio.csv` — base procesada con puntaje de gravedad
- `outputs/reports/validacion_descarga_reciente_notebook_03.csv` — validación de integridad
- `outputs/reports/calidad_datos_reciente_notebook_03.csv` — métricas de calidad
- `outputs/reports/top50_IPI_reciente_notebook_03.csv` — Top 50 zonas priorizadas 2020–2021
- `outputs/reports/top200_IPI_reciente_notebook_03.csv` — Top 200 extendido reciente
- `outputs/reports/zonas_criticas_IPI_reciente_completo_notebook_03.csv` — todas las zonas con IPI reciente
- `outputs/reports/comparacion_IPI_base_vs_reciente_notebook_03.csv` — merge base vs reciente
- `outputs/reports/clasificacion_hotspots_persistencia_notebook_03.csv` — clasificación de 19,255 zonas
- `outputs/maps/mapa_comparacion_persistencia_notebook_03.html` — mapa Top 200 base (rojo) vs reciente (azul)
- `outputs/maps/mapa_clasificacion_persistencia_notebook_03.html` — mapa de clasificación por categoría
- `DECISIONS.md` ADR-10 — periodo de validación post-base 2020–2021 y exclusión de 2022–2025
- `run_sec9_10.py` — script standalone para Secciones 9–10 (workaround encoding Windows/conda)

### Decisión metodológica clave (ADR-10)
Los años 2022–2025 fueron excluidos del análisis IPI por presentar un ratio CON HERIDOS/SOLO DAÑOS de 11–14x respecto al periodo base, indicando un posible cambio de metodología de registro en SIMUR. Solo 2020–2021 superan los 4 criterios de integridad y se usan como "periodo de validación post-base".

### Resultados de la comparación (Secciones 9–10)

| Categoría | Zonas | Descripción |
|---|---|---|
| **Persistente** | **37** | En Top 200 de ambos periodos |
| **Emergente** | **163** | Top 200 reciente, fuera de Top 500 base |
| **Disminuido** | **35** | Top 50 base, fuera de Top 500 reciente |
| **Histórico** | **0** | Top 50 base sin actividad reciente |
| Sensibles a fatalidad | 2,211 | CON MUERTOS en cualquier periodo |

- Solapamiento Top 200 base vs reciente: **37 zonas (18.5%)**
- Del Top 50 base: **12 zonas (24%)** permanecen en Top 200 reciente
- Zonas persistentes más robustas: SANTA FE (4.611, -74.075), CHAPINERO (4.647, -74.065)
- Kennedy concentra 7 de las 10 zonas emergentes más altas

### Limitación crítica documentada
El bajo solapamiento (18.5%) y los 35 Disminuidos se explican parcialmente por la **pandemia COVID-19** en 2020–2021. Menos tráfico implica menos siniestros en todas las zonas. No se puede atribuir la disminución a intervenciones exitosas sin datos de exposición.

---

## [NB03 Fase 1 completa] — 2026 Q2

### Añadido
- Secciones 1–4 y Sección 11 de `notebooks/03_validacion_actualidad_y_enriquecimiento_simur.ipynb`
- `outputs/reports/auditoria_conteo_actualizada_notebook_03.csv`
- `outputs/reports/auditoria_cobertura_mensual_reciente_notebook_03.csv`
- `outputs/reports/auditoria_ratios_gravedad_notebook_03.csv`
- `outputs/reports/auditoria_cobertura_localidades_reciente_notebook_03.csv`
- `outputs/reports/diagnostico_integridad_datos_recientes_notebook_03.csv`
- `outputs/reports/auditoria_capas_hermanas_simur_notebook_03.csv`
- `outputs/reports/detalle_campos_capas_simur_notebook_03.csv`
- `outputs/reports/manifiesto_outputs_notebook_03_fase1.csv`

### Capas hermanas SIMUR auditadas
7 capas encontradas: MUERTO (15.6K), LESIONADO (475K), ACCIDENTE (900K), VM_ACC_ACTOR_VIAL (3.3M), VM_ACC_CAUSA (1.9M), VM_ACC_VEHICULO (2.8M), VM_ACC_VIA (961K). Clave de join: `FORMULARIO`.

---

## [NB03 completo] — 2026 Q2

### Añadido
- Secciones 12–13 de `notebooks/03_validacion_actualidad_y_enriquecimiento_simur.ipynb`
- `outputs/reports/esquema_integracion_nb04_notebook_03.csv` — contrato de integración para NB04 (4 capas VM_ACC_*)
- `outputs/reports/manifiesto_outputs_notebook_03_completo.csv` — manifiesto completo de 18 outputs del NB03
- `add_sections12_13.py` — script de inserción de celdas (workaround encoding Windows/conda)

### Sección 12 — Esquema de integración NB04
Documenta las 4 capas hermanas SIMUR para el siguiente notebook:

| Capa | ID | Registros | Prioridad NB04 |
|---|---|---|---|
| VM_ACC_ACTOR_VIAL | 3 | 3,267,086 | Alta |
| VM_ACC_CAUSA | 4 | 1,865,722 | Alta |
| VM_ACC_VEHICULO | 5 | 2,803,601 | Alta |
| VM_ACC_VIA | 6 | 961,101 | Media |

Estrategia NB04: para cada zona del Top 200 reciente, JOIN de FORMULARIOs → moda de tipo_actor, tipo_vehiculo, causa_accidente.

### Sección 13 — Manifiesto final
18 outputs documentados (reports + maps). Verifica existencia y tamaño de cada archivo.

### Corrección crítica aplicada
- Celdas `5829fb7d` y `ce83497a` (Sección 9): añadido bloque `zonas_base_m = zonas_base.copy()` con rename `LAT_ZONA→lat_grid`, `LON_ZONA→lon_grid`, `localidad_predominante→localidad_modal`. El merge fallaba silenciosamente porque NB02 usa nomenclatura distinta.
- `outputs/reports/resumen_ejecutivo_notebook_03.md` — resumen ejecutivo de 167 líneas

### Estado final del NB03
Todas las secciones 1–13 construidas y corregidas. 19 outputs generados.

---

## [Revisión pre-NB04 + NB03.5] — 2026-05-08

### Añadido
- `notebooks/03.5_sintesis_metodologica_y_documentacion.ipynb` — Notebook de referencia con síntesis metodológica completa de NB01–NB03. Explica cada variable derivada, los 5 scores del IPI, la comparación de índices de criticidad y sus límites. No genera outputs nuevos — solo documentación ejecutable.
- `scripts/generar_snapshot_metadata.py` — Script para calcular hash MD5 de archivos raw y guardarlos en `data/raw/_snapshot_metadata.json`.
- `data/raw/_snapshot_metadata.json` — Snapshot generado: 2016-2019 raw (260,831 filas, 69.0 MB, md5=88b1aa5e...), reciente raw (72,903 filas, 11.8 MB, md5=f39e9986...), muestra (10,000 filas, 2.6 MB).

### Modificado
- `DECISIONS.md` — Añadido ADR-11: parametrización futura de pesos del IPI. Documenta puntos de intervención exactos en el código (`PESOS_GRAVEDAD`, `PESOS_IPI`, `N_ANIOS_BASE`, `N_ANIOS_RECIENTES`) y escala comparativa de estándares internacionales.
- `memory/project_context.md` — Estado actualizado al cierre de NB03.5. Próximo paso corregido: NB04 (antes decía NB03).

### NB03.5 — Secciones incluidas

| Sección | Contenido |
|---|---|
| 0 | Propósito y navegación del notebook |
| 1 | Contexto de VíaSegura AI (qué es, qué no es, audiencia) |
| 2 | Fuente de datos: SIMUR ArcGIS FeatureServer (capas 0–6) |
| 3 | NB01: variables originales, descarga segura, limpieza, `puntaje_gravedad` |
| 4 | NB02: grilla 0.001°, variables por zona, 5 scores del IPI, clasificaciones |
| 5 | NB03: auditoría de años recientes, ADR-10, IPI reciente, persistencia, capas SIMUR |
| 6 | Comparación de índices de criticidad + estándares internacionales (EPDO, FHWA, OMS) |
| 7 | Limitaciones globales L1–L10 con severidad y estado |
| 8 | Hoja de ruta NB04–NB06 con insumos y secciones propuestas |

---

---

## [NB04.5 + NB06 Dashboard + Infraestructura] — 2026-05-21

### Añadido — NB04.5 Análisis geoespacial avanzado

- `notebooks/04.5_analisis_geoespacial_avanzado.ipynb` — Notebook completo ejecutado (~17 s).
- Hexágonos H3 resolución 8 (`h3==4.4.2`): mapeo de todas las 17,130 zonas IPI.
- Límites de localidades Bogotá descargados vía OSM (`osmnx`), con fallback convex hull.
- Spatial join zonas → localidades con GeoPandas.
- KDE con `scipy.stats.gaussian_kde` sobre coordenadas.
- 3 mapas Folium con leyendas flotantes en español y tooltips con alias legibles:
  - `outputs/maps/mapa_ipi_hexagonos_h3.html` — Mapa hexagonal H3 (CARTO Dark)
  - `outputs/maps/mapa_ipi_por_localidad.html` — Coropleta por localidad (CARTO Light + CircleMarker popup)
  - `outputs/maps/mapa_ipi_calor_clusters.html` — Mapa de calor + clusters (gradiente azul→rojo)
- Exports geoespaciales:
  - `outputs/reports/ipi_hexagonos_h3.geojson` (426 KB)
  - `outputs/reports/ipi_por_localidad.geojson` (6.1 MB)
  - `outputs/reports/ipi_hexagonos_h3.csv`, `ipi_por_localidad.csv`, `ipi_densidad_kde.csv`
- Figuras:
  - `outputs/reports/figura_ipi_kde_superficie.png`
  - `outputs/reports/figura_ipi_treemap_localidades.png`

### Añadido — NB06 Dashboard Streamlit (`app/`)

- `app/main.py` — Página de inicio con 5 KPIs globales, donut chart IPI por prioridad, tabla de metodología.
- `app/data_loader.py` — Módulo centralizado con `@st.cache_data` para 8 loaders (IPI, localidades, hexágonos, vías, barrios, GeoJSON, HTML mapas, métricas globales).
- `app/pages/1_mapa.py` — Mapa interactivo: radio selector entre los 3 mapas Folium de NB04.5.
- `app/pages/2_zonas_criticas.py` — Tabla filtrable por prioridad/localidad/clase/años, con gráficos Plotly (histograma, scatter, radar) y descarga CSV.
- `app/pages/3_localidades.py` — Vista global (bar chart + bubble chart) y vista detalle por localidad (barrios, tendencia anual, Pydeck ScatterplotLayer).
- `app/pages/4_agente.py` — Chat con Claude Opus 4.7: API key en sidebar, 6 preguntas rápidas, streaming con `client.messages.stream()`, prompt caching sobre CSV IPI, caption de tokens + ahorro de caché.
- `.streamlit/config.toml` — Tema oscuro: `primaryColor=#d73027`, `backgroundColor=#0f1117`.

### Añadido — MCP Server SIMUR (`mcp_simur/`)

- `mcp_simur/__init__.py` — Paquete Python.
- `mcp_simur/server.py` — FastMCP server con 6 herramientas y 2 recursos. Transporte stdio.
  - `simur_contar_registros(anio)`, `simur_descargar_muestra(anio, n, where_extra)`
  - `simur_localidades_activas(anio)`, `simur_estadisticas_zona(lat, lon, radio_grados)`
  - `ipi_top_zonas(n, prioridad)`, `ipi_resumen_ejecutivo()`
  - Recursos: `simur://metodologia`, `simur://estructura-campos`
- `mcp_simur/README.md` — Documentación de herramientas e instrucciones de registro en Claude Code.

### Añadido — Agente de insights (`agents/insights_agent.py`)

- Claude Opus 4.7 con `thinking: {type: "adaptive"}` y streaming.
- Prompt caching (`cache_control: ephemeral`) sobre el bloque de texto CSV IPI.
- 5 preguntas predefinidas ejecutadas en secuencia; muestra ahorro de tokens por caché.

### Añadido — Suite de tests (`tests/`)

- `tests/conftest.py` — Registro de marks `network` y `slow`.
- `tests/test_config.py` — 18 tests: rutas absolutas, archivos de datos y notebooks existen.
- `tests/test_ipi_formula.py` — 13 tests de fórmula IPI: rango [0,100], scores [0,1], rank1 es IPI máximo, sin nulos, coords en bbox Bogotá (lat 4.0–4.90, lon -74.35 a -73.95), localidades conocidas (con `unicodedata.normalize("NFD")`), top10 IPI>80, ranking ordenado.
- `tests/test_simur_api.py` — 7 tests de red (`@pytest.mark.network`): endpoint responde, conteo 2016>50k, campos requeridos presentes, muertos<heridos, ≥15 localidades, tendencia 2016-2019.

### Añadido — CI/CD (`.github/workflows/validate.yml`)

- Job `lint`: `ruff check` + `ruff format --check`.
- Job `tests-unit`: genera CSVs stub, ejecuta `pytest -m "not network"`.
- Job `notebook-035`: ejecuta NB03.5 con datos stub via `nbconvert --execute`.
- Job `notebook-integrity`: valida todos los notebooks como JSON nbformat válido.

### Modificado

- `pyproject.toml` — Añadidas dependencias: `mcp>=1.0`, `streamlit>=1.35`, `streamlit-folium>=0.25`, `plotly>=5.20`, `pydeck>=0.9`, `h3>=4.0`.
- `.gitignore` — Añadidos outputs NB04.5 (mapas HTML, GeoJSONs, PNGs geoespaciales) para no versionar archivos grandes.

### Bugs corregidos

- `app/main.py`: `st.page_link()` usaba paths `"app/pages/..."` — corregido a relativos al entrypoint: `"pages/..."`.
- `app/pages/2_zonas_criticas.py`: `df_tabla.style.applymap(...)` → `df_tabla.style.map(...)` (pandas ≥ 2.1 renombró el método).
- `.streamlit/config.toml`: `enableCORS = false` → `true` (conflicto con protección XSRF).
- `tests/test_ipi_formula.py`: bbox LAT_MIN corregido de 4.45 a 4.0 para incluir Sumapaz; normalización NFD para manejar tilde en "ANTONIO NARIÑO".
- `notebooks/04.5_analisis_geoespacial_avanzado.ipynb`: choropleth — helper `_safe_int()` para manejar NaN en `int()`; hexágonos — usar `__geo_interface__` como FeatureCollection en lugar de geometría individual.
