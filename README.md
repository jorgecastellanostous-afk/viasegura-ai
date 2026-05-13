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
| NB05 | Normalización por exposición (red vial OSM + población DANE) | ✅ Completado |
| NB06 | Dashboard Streamlit + síntesis final | 🔄 En desarrollo |

---

## Resultados principales

### NB02 — Priorización base (2016–2019)
El IPI construido sobre **260,831 siniestros** identificó 17,130 zonas activas. El **Top 50 (0.29% de zonas) concentra el 6.39% de todas las muertes** del periodo. El IPI combina 5 dimensiones normalizadas por percentil: volumen, criticidad, severidad, fatalidad y persistencia espacial.

### NB03 — Validación de actualidad (2020–2021)
Solapamiento entre Top 200 base y Top 200 reciente: **18.5% (37 zonas persistentes)**. 163 zonas emergentes y 35 disminuidas. El periodo 2022–2025 fue excluido por cambio estructural en el registro de gravedad (ADR-10).

### NB04 — Perfil de actores y causas por zona
Distribución por zona en el Top 200: **Automóvil 31.5% · Moto 24.9% · Bus 10.6% · Camioneta 10.3% · Bicicleta 8.8%**. Causa principal identificada en 55% de zonas: "No mantener distancia / Adelantar cerrando" (53 zonas). Análisis de sensibilidad EPDO: 84.5% de estabilidad frente al IPI 1/3/5 (ADR-12).

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
├── notebooks/               # Análisis en Jupyter (NB01–NB05 ejecutados)
├── agents/                  # Agentes Python de orquestación
├── scripts/                 # Scripts auxiliares y utilidades
├── memory/                  # Documentación operativa del proyecto
├── .claude/agents/          # 6 sub-agentes Claude Code especializados
├── app/                     # Dashboard futuro (NB06 — Streamlit)
├── outputs/
│   ├── maps/                # Mapas interactivos Folium (.html)
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

Dependencias principales: `pandas · geopandas · osmnx · folium · matplotlib · shapely · scipy · nbconvert`

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
