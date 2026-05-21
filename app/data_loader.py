"""
app/data_loader.py — Carga y caché de datos para el dashboard VíaSegura AI
===========================================================================
Todos los datasets se cargan una sola vez con @st.cache_data.
Importa este módulo en cada página para compartir el mismo caché.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Resolver raíz del proyecto ───────────────────────────────────────────
_here = Path(__file__).resolve().parent          # app/
ROOT  = _here.parent                              # viasegura_ai/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import REPORTS, MAPS  # noqa: E402


# ════════════════════════════════════════════════════════════════════════
# Datos IPI
# ════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def cargar_ipi() -> pd.DataFrame:
    """DataFrame completo de zonas IPI (17 130 filas)."""
    return pd.read_csv(REPORTS / "zonas_criticas_IPI_completo_2016_2019.csv")


@st.cache_data(show_spinner=False)
def cargar_ipi_por_localidad() -> pd.DataFrame:
    """Stats IPI agregados por localidad."""
    return pd.read_csv(REPORTS / "ipi_por_localidad_stats.csv")


@st.cache_data(show_spinner=False)
def cargar_top_vias() -> pd.DataFrame:
    return pd.read_csv(REPORTS / "top_vias_criticas_geoespacial.csv")


@st.cache_data(show_spinner=False)
def cargar_top_barrios() -> pd.DataFrame:
    return pd.read_csv(REPORTS / "top_barrios_criticos_geoespacial.csv")


# ════════════════════════════════════════════════════════════════════════
# GeoJSONs
# ════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def cargar_gdf_hexagonos():
    """GeoDataFrame de hexágonos H3 con IPI."""
    import geopandas as gpd
    return gpd.read_file(MAPS / "ipi_hexagonos_h3.geojson")


@st.cache_data(show_spinner=False)
def cargar_gdf_localidades():
    """GeoDataFrame de localidades con IPI."""
    import geopandas as gpd
    return gpd.read_file(MAPS / "ipi_por_localidad.geojson")


# ════════════════════════════════════════════════════════════════════════
# Métricas globales (calculadas una vez)
# ════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def metricas_globales() -> dict:
    df = cargar_ipi()
    p1 = df[df["prioridad_IPI"].str.contains("Prioridad 1", na=False)]
    return {
        "total_zonas":        len(df),
        "total_siniestros":   int(df["cantidad_siniestros"].sum()),
        "total_muertos":      int(df["siniestros_con_muertos"].sum()),
        "zonas_p1":           len(p1),
        "ipi_max":            round(df["IPI"].max(), 1),
        "ipi_medio":          round(df["IPI"].mean(), 1),
        "localidad_top":      df.loc[df["IPI"].idxmax(), "localidad_predominante"],
        "via_top":            df.loc[df["IPI"].idxmax(), "via_predominante"],
        "persistentes_4a":    int((df["anios_activos"] == 4).sum()),
    }


# ════════════════════════════════════════════════════════════════════════
# HTML de mapas pre-generados
# ════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def html_mapa(nombre: str) -> str:
    """Carga el HTML de un mapa folium pre-generado."""
    p = MAPS / nombre
    if not p.exists():
        return "<p style='color:red'>Mapa no encontrado. Ejecuta NB04.</p>"
    return p.read_text(encoding="utf-8")
