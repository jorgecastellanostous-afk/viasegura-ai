"""
Página 1 — Mapa Interactivo
"""

import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data_loader import html_mapa, metricas_globales
from app.styles import inject_global_css, SIDEBAR_BRAND

st.set_page_config(page_title="Mapa · VíaSegura AI", page_icon="🗺️", layout="wide")
inject_global_css()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)
    st.page_link("main.py",                      label="Inicio")
    st.page_link("pages/1_mapa.py",              label="Mapa Interactivo")
    st.page_link("pages/2_zonas_criticas.py",    label="Zonas Críticas")
    st.page_link("pages/3_localidades.py",       label="Por Localidad")
    st.page_link("pages/4_agente.py",            label="Agente IA")
    st.page_link("pages/5_metodologia.py",       label="Metodología")
    st.markdown("---")
    st.caption("SDM · SIMUR · sig.simur.gov.co")

# ── Datos ─────────────────────────────────────────────────────────────────
m = metricas_globales()

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="vs-hero">
  <div class="vs-hero-eyebrow">Visualización espacial · 17,130 zonas</div>
  <h1 class="vs-hero-title">
    Mapa de<br><em>siniestralidad</em><br>Bogotá D.C.
  </h1>
  <p class="vs-hero-sub">
    Tres vistas complementarias: hexágonos H3 resolución 8 (~460 m) con IPI por zona,
    choropleth por localidad y heatmap de densidad con marcadores de zonas Prioridad 1.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# ── KPI strip ─────────────────────────────────────────────────────────────
st.markdown('<div class="vs-label">Contexto del análisis</div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="vs-kpi-strip">
  <div class="vs-kpi">
    <div class="vs-kpi-value">{m['zonas_p1']}</div>
    <div class="vs-kpi-label">zonas Prioridad 1<br>intervención inmediata</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">{m['ipi_max']}</div>
    <div class="vs-kpi-label">IPI máximo<br>sobre escala 0–100</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">{m['total_muertos']:,}</div>
    <div class="vs-kpi-label">accidentes fatales<br>2016–2019</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">{m['localidad_top']}</div>
    <div class="vs-kpi-label">localidad<br>con mayor IPI</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Selector de capa ───────────────────────────────────────────────────────
st.markdown('<div class="vs-label">Selecciona la capa</div>', unsafe_allow_html=True)

MAP_FILES = {
    "Hexágonos H3 — IPI por zona (~460 m)": "mapa_hexagonos_H3_IPI.html",
    "Choropleth — IPI por localidad":        "mapa_choropleth_localidades_IPI.html",
    "Heatmap + Zonas Prioridad 1":           "mapa_heatmap_clusters_P1.html",
}

DESCRIPCIONES = {
    "Hexágonos H3 — IPI por zona (~460 m)": (
        "Cada hexágono (~460 m de diámetro) muestra el **IPI máximo** de las zonas que contiene. "
        "Rojo intenso = IPI ≥ 90 (crítico). Pasa el cursor sobre un hexágono para ver el detalle."
    ),
    "Choropleth — IPI por localidad": (
        "IPI representativo (percentil 75) por **localidad administrativa**. "
        "Los marcadores circulares muestran el detalle de cada zona al hacer clic."
    ),
    "Heatmap + Zonas Prioridad 1": (
        "**Heatmap** de densidad con una muestra de 5,000 accidentes. "
        "Los marcadores agrupados son las **50 zonas Prioridad 1** — haz clic para ver el ranking."
    ),
}

capa = st.radio(
    "Capa:",
    options=list(MAP_FILES.keys()),
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown(
    f'<div class="vs-callout">{DESCRIPCIONES[capa]}</div>',
    unsafe_allow_html=True,
)

# ── Mapa ───────────────────────────────────────────────────────────────────
with st.spinner("Cargando mapa..."):
    html = html_mapa(MAP_FILES[capa])

components.html(html, height=620, scrolling=False)

st.caption(
    "Mapas generados en NB04 con datos SIMUR 2016-2019. "
    "Hexágonos H3 resolución 8 (~460 m). Zoom y pan habilitados."
)
