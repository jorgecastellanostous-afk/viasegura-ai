"""
Página 3 — Análisis por Localidad
"""

import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data_loader import cargar_ipi_por_localidad, cargar_ipi
from app.styles import inject_global_css, SIDEBAR_BRAND

st.set_page_config(page_title="Localidades · VíaSegura AI", page_icon="📍", layout="wide")
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
df_loc = cargar_ipi_por_localidad().sort_values("IPI_localidad", ascending=False)
df_ipi = cargar_ipi()

localidades = df_loc["localidad"].dropna().tolist()

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="vs-hero">
  <div class="vs-hero-eyebrow">Análisis territorial · 20 localidades</div>
  <h1 class="vs-hero-title">
    Siniestralidad<br>por <em>localidad</em>
  </h1>
  <p class="vs-hero-sub">
    Comparación de IPI, siniestros y zonas Prioridad 1 entre localidades de Bogotá.
    Selecciona una localidad para ver el detalle de barrios, distribución anual y mapa de zonas.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Selector ──────────────────────────────────────────────────────────────
st.markdown('<div class="vs-label">Seleccionar localidad</div>', unsafe_allow_html=True)
loc_sel = st.selectbox(
    "Localidad:",
    options=["— Ver todas —"] + localidades,
    label_visibility="collapsed",
)

st.markdown("---")

# ── Vista global ──────────────────────────────────────────────────────────
if loc_sel == "— Ver todas —":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="vs-label">IPI por localidad (percentil 75)</div>',
            unsafe_allow_html=True,
        )
        fig_bar = px.bar(
            df_loc.head(20),
            x="IPI_localidad",
            y="localidad",
            orientation="h",
            color="IPI_localidad",
            color_continuous_scale="Reds",
            hover_data=["n_zonas", "siniestros_total", "siniestros_muertos", "zonas_p1"],
            template="plotly_dark",
            labels={
                "IPI_localidad": "IPI (P75)",
                "localidad": "",
                "siniestros_muertos": "Acc. fatales (eventos SIMUR)",
            },
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=520,
            margin=dict(t=10, b=10),
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown(
            '<div class="vs-label">Zonas Prioridad 1 vs siniestros por localidad</div>',
            unsafe_allow_html=True,
        )
        fig_bub = px.scatter(
            df_loc,
            x="siniestros_total",
            y="zonas_p1",
            size="IPI_localidad",
            color="IPI_localidad",
            color_continuous_scale="Reds",
            hover_name="localidad",
            hover_data={"siniestros_muertos": True, "n_zonas": True},
            template="plotly_dark",
            labels={
                "siniestros_total": "Total siniestros",
                "zonas_p1": "Zonas Prioridad 1",
                "IPI_localidad": "IPI (P75)",
                "siniestros_muertos": "Acc. fatales (eventos SIMUR)",
            },
        )
        fig_bub.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=520,
            margin=dict(t=10, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_bub, use_container_width=True)

    st.markdown('<div class="vs-label">Tabla completa</div>', unsafe_allow_html=True)
    df_loc_tabla = df_loc.copy()
    for col in ["IPI_localidad", "ipi_medio", "ipi_max"]:
        if col in df_loc_tabla.columns:
            df_loc_tabla[col] = df_loc_tabla[col].round(1)
    st.dataframe(df_loc_tabla, use_container_width=True, height=350)

# ── Vista de localidad específica ─────────────────────────────────────────
else:
    row = df_loc[df_loc["localidad"] == loc_sel].iloc[0]
    df_loc_zonas = df_ipi[df_ipi["localidad_predominante"].str.upper() == loc_sel.upper()].copy()

    st.markdown(
        f"""
<div class="vs-kpi-strip">
  <div class="vs-kpi">
    <div class="vs-kpi-value">{row['IPI_localidad']:.1f}</div>
    <div class="vs-kpi-label">IPI (P75)<br>localidad</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">{int(row['siniestros_total']):,}</div>
    <div class="vs-kpi-label">siniestros<br>2016–2019</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">{int(row['siniestros_muertos']):,}</div>
    <div class="vs-kpi-label">accidentes<br>fatales</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">{int(row['zonas_p1'])}</div>
    <div class="vs-kpi-label">zonas<br>Prioridad 1</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(
            f'<div class="vs-label">Top 10 barrios — {loc_sel}</div>',
            unsafe_allow_html=True,
        )
        top_barrios_loc = (
            df_loc_zonas.groupby("barrio_predominante")
            .agg(
                ipi_max=("IPI", "max"),
                siniestros=("cantidad_siniestros", "sum"),
                muertos=("siniestros_con_muertos", "sum"),
            )
            .sort_values("ipi_max", ascending=False)
            .head(10)
            .reset_index()
        )
        fig_b = px.bar(
            top_barrios_loc.sort_values("ipi_max"),
            x="ipi_max",
            y="barrio_predominante",
            orientation="h",
            color="muertos",
            color_continuous_scale="OrRd",
            hover_data=["siniestros"],
            template="plotly_dark",
            labels={"ipi_max": "IPI máximo", "barrio_predominante": ""},
        )
        fig_b.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320,
            margin=dict(t=10, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_b, use_container_width=True)

    with col_r:
        st.markdown(
            f'<div class="vs-label">Distribución anual — {loc_sel}</div>',
            unsafe_allow_html=True,
        )
        cols_anio = ["criticidad_2016", "criticidad_2017", "criticidad_2018", "criticidad_2019"]
        cols_ok = [c for c in cols_anio if c in df_loc_zonas.columns]
        if cols_ok:
            por_anio = df_loc_zonas[cols_ok].sum().reset_index()
            por_anio.columns = ["Año", "Criticidad total"]
            por_anio["Año"] = por_anio["Año"].str.replace("criticidad_", "")
            fig_lin = px.line(
                por_anio,
                x="Año",
                y="Criticidad total",
                markers=True,
                template="plotly_dark",
                color_discrete_sequence=["#ff2233"],
            )
            fig_lin.update_traces(
                marker=dict(size=8, color="#ff2233"),
                line=dict(width=2),
            )
            fig_lin.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                margin=dict(t=10, b=10),
            )
            st.plotly_chart(fig_lin, use_container_width=True)

    st.markdown(
        f'<div class="vs-label">Mapa de zonas — {loc_sel} (top 200 por IPI)</div>',
        unsafe_allow_html=True,
    )
    df_mapa = df_loc_zonas.nlargest(200, "IPI")
    if not df_mapa.empty and "LAT_ZONA" in df_mapa.columns:
        import pydeck as pdk

        def _color_prioridad(p):
            if "Prioridad 1" in str(p):
                return [255, 34, 51, 210]
            elif "Prioridad 2" in str(p):
                return [249, 115, 22, 200]
            return [234, 179, 8, 180]

        df_mapa = df_mapa.copy()
        df_mapa["color"] = df_mapa["prioridad_IPI"].apply(_color_prioridad)
        df_mapa["IPI_fmt"] = df_mapa["IPI"].round(1).astype(str)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_mapa,
            get_position=["LON_ZONA", "LAT_ZONA"],
            get_radius=120,
            get_fill_color="color",
            pickable=True,
        )
        view = pdk.ViewState(
            latitude=df_mapa["LAT_ZONA"].mean(),
            longitude=df_mapa["LON_ZONA"].mean(),
            zoom=13,
            pitch=0,
        )
        tooltip = {
            "html": "<b>Rank #{rank_IPI}</b> — IPI {IPI_fmt}<br>{barrio_predominante}<br>Siniestros: {cantidad_siniestros}",
            "style": {"backgroundColor": "#111111", "color": "#f5f5f5", "fontFamily": "DM Sans, sans-serif"},
        }
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            tooltip=tooltip,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        )
        st.pydeck_chart(deck)
