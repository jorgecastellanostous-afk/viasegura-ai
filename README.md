# VíaSegura AI

Análisis espacial de siniestralidad vial en Bogotá usando datos oficiales de la Secretaría Distrital de Movilidad (SIMUR). El proyecto construye un **Índice de Prioridad de Intervención (IPI)** reproducible y metodológicamente defendible para identificar zonas críticas de intervención vial, con normalización por exposición y tipología de concordancia entre rankings absolutos y relativos.

> Proyecto de portafolio — Ingeniería Civil con énfasis en Transporte, Universidad de los Andes (Coterminal).

---

## Estado del proyecto

| Notebook | Nombre | Estado |
|---|---|---|
| NB01 | Exploración y validación de datos SIMUR | ✅ Completado |
| NB02 | Índice de Prioridad de Intervención (IPI) | ✅ Completado |
| NB03 | Validación de actualidad + exploración de capas SIMUR | ✅ Completado |
| NB03.5 | Síntesis metodológica | ✅ Completado |
| NB04 | Enriquecimiento con actores viales, vehículos y causas | ✅ Completado |
| NB04.5 | Análisis geoespacial avanzado (H3 + OSM localidades + KDE) | ✅ Completado |
| NB05 | Normalización por exposición (red vial OSM + población DANE) | ✅ Completado |
| NB06 | Dashboard Streamlit + síntesis final | ✅ Completado |

### Infraestructura complementaria

| Componente | Descripción | Estado |
|---|---|---|
| `app/` | Dashboard Streamlit multip-página (4 vistas + agente IA) | ✅ Activo |
| `mcp_simur/` | MCP Server que expone SIMUR/IPI como herramientas Claude | ✅ Implementado |
| `agents/insights_agent.py` | Agente Claude API con prompt caching sobre CSV IPI | ✅ Implementado |
| `tests/` | Suite pytest: 34 tests (fórmula IPI, config, API de red) | ✅ Pasando |
| `.github/workflows/validate.yml` | CI/CD: lint + tests unitarios + ejecución NB03.5 | ✅ Activo |

---

## Resultados principales

### NB02 — Priorización base (2016–2019)
El IPI construido sobre **260,831 siniestros** identificó 17,130 zonas activas. El **Top 50 (0.29% de zonas) concentra el 6.39% de todas las muertes** del periodo. El IPI combina 5 dimensiones normalizadas por percentil: volumen, criticidad, severidad, fatalidad y persistencia espacial.

### NB03 — Validación de actualidad (2020–2021)
Solapamiento entre Top 200 base y Top 200 reciente: **18.5% (37 zonas persistentes)**. 163 zonas emergentes y 35 disminuidas. El periodo 2022–2025 fue excluido por cambio estructural en el registro de gravedad (ADR-10).

### NB04 — Perfil de actores y causas por zona
Distribución por zona en el Top 200: **Automóvil 31.5% · Moto 24.9% · Bus 10.6% · Camioneta 10.3% · Bicicleta 8.8%**. Causa principal identificada en 55% de zonas: "No mantener distancia / Adelantar cerrando" (53 zonas). Análisis de sensibilidad EPDO: 84.5% de estabilidad frente al IPI 1/3/5 (ADR-12).

### NB04.5 — Análisis geoespacial avanzado
Integración espacial del IPI con celdas H3 (resolución 8, ~460 m de diámetro) y límites de localidades vía OSM. Análisis KDE sobre las 17,130 zonas activas. Genera 3 mapas interactivos Folium con leyendas en español: mapa hexagonal H3, coropleta por localidad y mapa de calor + clusters. Outputs: `ipi_hexagonos_h3.geojson` (426 KB), `ipi_por_localidad.geojson` (6.1 MB), 3 HTML, 2 PNG.

### NB05 — Normalización por exposición ⭐
**Hallazgo central:** solo el **10% del Top 200 volumétrico (20 zonas)** tiene también alta tasa relativa de siniestros por km de red vial. El 90% restante refleja el efecto de alto tráfico, no vías intrínsecamente peligrosas.

| Tipología NB05 | Zonas | Interpretación |
|---|---|---|
| Hotspot absoluto + relativo | **20** | Alta prioridad estructural — auditoría urgente |
| Hotspot por volumen | 180 | Alto tráfico explica la concentración |
| Hotspot relativo oculto | 180 | Sub-representados por IPI volumétrico |
| Alta tasa poblacional | 138 | Riesgo para residentes — equidad vial |

Red vial descargada desde OSM: **14,884.9 km · 174,311 segmentos**. Denominadores: km de red vial (proxy exposición vehicular) y 100,000 hab DANE 2018 (exposición poblacional).

---

## Limitaciones honestas

El IPI mide **prioridad exploratoria**, no riesgo vial real. Sin normalización por TPDA (tráfico promedio diario), una zona de alto tráfico aparece primero simplemente por exposición, no por ser más peligrosa. NB05 introduce la primera corrección parcial mediante proxies de exposición.

Ver `memory/limitations.md` para el detalle completo (L1–L14).

---

## Estructura del repositorio

```
viasegura_ai/
├── notebooks/               # Análisis en Jupyter (NB01–NB05 + NB03.5 + NB04.5 ejecutados)
├── agents/
│   └── insights_agent.py    # Agente Claude API con prompt caching sobre CSV IPI
├── mcp_simur/
│   ├── __init__.py
│   ├── server.py            # MCP Server — 6 herramientas + 2 recursos SIMUR/IPI
│   └── README.md
├── app/                     # Dashboard Streamlit (NB06)
│   ├── main.py              # Página de inicio + KPIs globales
│   ├── data_loader.py       # Carga centralizada con @st.cache_data
│   └── pages/
│       ├── 1_mapa.py        # Mapa interactivo (3 vistas Folium)
│       ├── 2_zonas_criticas.py  # Ranking IPI filtrable + descarga CSV
│       ├── 3_localidades.py     # Análisis por localidad + Pydeck
│       └── 4_agente.py          # Chat con Claude Opus 4.7 (prompt caching)
├── tests/
│   ├── conftest.py          # Marks: network, slow
│   ├── test_config.py       # 18 tests de paths y archivos
│   ├── test_ipi_formula.py  # 13 tests de fórmula IPI
│   └── test_simur_api.py    # 7 tests de red (marcados @network)
├── .github/
│   └── workflows/
│       └── validate.yml     # CI: lint + tests + NB03.5 + integridad notebooks
├── .streamlit/
│   └── config.toml          # Tema oscuro rojo (#d73027)
├── .claude/agents/          # 6 sub-agentes Claude Code especializados
├── scripts/                 # Scripts auxiliares y utilidades
├── memory/                  # Documentación operativa del proyecto
├── outputs/
│   ├── maps/                # Mapas interactivos Folium (.html) — no versionados
│   └── reports/             # CSVs de resultados y figuras (.png)
├── data/
│   ├── raw/                 # Datos originales SIMUR (no versionados — >150MB)
│   └── processed/           # Datos limpios (no versionados — >50MB)
├── README.md
├── PLAN.md                  # Hoja de ruta por notebook
├── CHANGELOG.md             # Historial de cambios
├── DECISIONS.md             # Decisiones técnicas en formato ADR (ADR-01 a ADR-14)
├── DATA_SOURCES.md          # Documentación formal de fuentes
├── COMUNICACION.md          # Resumen ejecutivo para audiencia distrital (SDM/ANSV)
├── pyproject.toml           # Dependencias (uv)
└── uv.lock
```

---

## Reproducibilidad

Los datos crudos no se versionan por su tamaño (>150MB), pero son descargables directamente desde la API pública de SIMUR:

```
https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query
```

Los notebooks están diseñados para correr de inicio a fin con los datos descargados. Ver `PLAN.md` para el orden de ejecución.

---

## Entorno de desarrollo

```bash
# Requiere uv (https://docs.astral.sh/uv/)
uv sync
# Activar entorno y abrir VS Code
code .
```

Dependencias principales: `pandas · geopandas · osmnx · folium · matplotlib · shapely · scipy · nbconvert · streamlit · plotly · pydeck · h3 · anthropic · mcp`

Para correr el dashboard:

```bash
.venv\Scripts\streamlit.exe run app/main.py
# → http://localhost:8501
```

Para correr los tests:

```bash
.venv\Scripts\pytest.exe tests/ -m "not network" -v
```

Para correr el MCP server:

```bash
.venv\Scripts\python.exe -m mcp_simur.server
```

---

## Fuente de datos

- **Organismo:** Secretaría Distrital de Movilidad de Bogotá (SDM / SIMUR)
- **Servicio:** ArcGIS FeatureServer — `AccidentalidadAnalisis/FeatureServer`
- **Periodo base:** 2016–2019 · **Periodo validación:** 2020–2021
- **Registros:** 260,831 base + 72,903 validación

Ver `DATA_SOURCES.md` para documentación completa.

---

## Documentación

| Archivo | Contenido |
|---|---|
| `PLAN.md` | Hoja de ruta por notebook |
| `CHANGELOG.md` | Historial de cambios |
| `DECISIONS.md` | Decisiones técnicas ADR-01 a ADR-14 |
| `DATA_SOURCES.md` | Fuentes de datos |
| `COMUNICACION.md` | Resumen ejecutivo para SDM/ANSV (no técnico) |
| `memory/limitations.md` | Limitaciones L1–L14 |
| `memory/decisions_log.md` | Bitácora narrativa |
