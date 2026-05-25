"""
Página 1 — Mapa Interactivo
Muestra los mapas folium pre-generados con controles de capa.
"""

import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data_loader import html_mapa, metricas_globales
from app.styles import inject_global_css

st.set_page_config(page_title="Mapa · VíaSegura AI", page_icon="🗺️", layout="wide")
inject_global_css()

st.markdown(
    '<p class="vs-page-title">Mapa Interactivo de Siniestralidad</p>', unsafe_allow_html=True
)
st.markdown(
    '<p class="vs-section-label">Selecciona la capa que quieres explorar</p>',
    unsafe_allow_html=True,
)

m = metricas_globales()

# ── Selector de capa ────────────────────────────────────────────────────
capa = st.radio(
    "Capa:",
    options=[
        "Hexágonos H3 (IPI por zona ~460m)",
        "Choropleth por Localidad",
        "Heatmap + Zonas Prioridad 1",
    ],
    horizontal=True,
)

MAP_FILES = {
    "Hexágonos H3 (IPI por zona ~460m)": "mapa_hexagonos_H3_IPI.html",
    "Choropleth por Localidad": "mapa_choropleth_localidades_IPI.html",
    "Heatmap + Zonas Prioridad 1": "mapa_heatmap_clusters_P1.html",
}

DESCRIPCIONES = {
    "Hexágonos H3 (IPI por zona ~460m)": (
        "Cada hexágono (~460m de diámetro) muestra el **IPI máximo** de las zonas "
        "que contiene. 🔴 Rojo = IPI≥90 (crítico). "
        "Pasa el cursor sobre un hexágono para ver detalles."
    ),
    "Choropleth por Localidad": (
        "IPI representativo (percentil 75) por **localidad**. "
        "Los marcadores circulares muestran el detalle al hacer clic."
    ),
    "Heatmap + Zonas Prioridad 1": (
        "**Heatmap** de densidad de todos los accidentes (muestra 5k puntos). "
        "Los marcadores rojos agrupados son las **50 zonas Prioridad 1** — haz clic para ver el ranking."
    ),
}

st.info(DESCRIPCIONES[capa])

# ── Métricas contextuales ────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Zonas Prioridad 1", m["zonas_p1"], "intervención inmediata")
c2.metric("IPI máximo", m["ipi_max"], m["localidad_top"])
c3.metric("Acc. fatales (2016-19)", f"{m['total_muertos']:,}", "periodo base")

st.markdown("---")

# ── Renderizar mapa ──────────────────────────────────────────────────────
with st.spinner("Cargando mapa..."):
    html = html_mapa(MAP_FILES[capa])

components.html(html, height=620, scrolling=False)

st.caption(
    "📌 Mapas generados en NB04 con datos SIMUR 2016-2019. "
    "Hexágonos H3 resolución 8 (~460m). Zoom y pan habilitados."
)
