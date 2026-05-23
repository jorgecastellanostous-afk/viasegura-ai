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
from app.styles import inject_global_css

st.set_page_config(page_title="Localidades · VíaSegura AI", page_icon="📍", layout="wide")
inject_global_css()

st.markdown('<p class="vs-page-title">Análisis por Localidad</p>', unsafe_allow_html=True)

df_loc = cargar_ipi_por_localidad().sort_values("IPI_localidad", ascending=False)
df_ipi = cargar_ipi()

# ── Selector de localidad ────────────────────────────────────────────────
localidades = df_loc["localidad"].dropna().tolist()
loc_sel = st.selectbox(
    "Selecciona una localidad para ver el detalle:",
    options=["— Ver todas —"] + localidades,
)

st.markdown("---")

# ── Vista global ─────────────────────────────────────────────────────────
if loc_sel == "— Ver todas —":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**IPI por localidad (percentil 75)**")
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
        st.markdown("**Zonas Prioridad 1 vs Siniestros por localidad**")
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

    st.markdown("**Tabla completa**")
    df_loc_tabla = df_loc.copy()
    for col in ["IPI_localidad", "ipi_medio", "ipi_max"]:
        if col in df_loc_tabla.columns:
            df_loc_tabla[col] = df_loc_tabla[col].round(1)
    st.dataframe(df_loc_tabla, use_container_width=True, height=350)

# ── Vista de localidad específica ─────────────────────────────────────────
else:
    row = df_loc[df_loc["localidad"] == loc_sel].iloc[0]
    df_loc_zonas = df_ipi[df_ipi["localidad_predominante"].str.upper() == loc_sel.upper()].copy()

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("IPI (P75)", f"{row['IPI_localidad']:.1f}")
    c2.metric("Siniestros", f"{int(row['siniestros_total']):,}")
    c3.metric(
        "Acc. fatales",
        f"{int(row['siniestros_muertos']):,}",
        help=(
            "Eventos SIMUR clasificados como CON MUERTOS. "
            "No equivale al número de víctimas individuales "
            "(ratio ~2 eventos por víctima según SDM)."
        ),
    )
    c4.metric("Zonas Prioridad 1", int(row["zonas_p1"]))

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(f"**Top 10 barrios en {loc_sel}**")
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
        st.markdown(f"**Distribución anual en {loc_sel}**")
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
                color_discrete_sequence=["#d73027"],
            )
            fig_lin.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                margin=dict(t=10, b=10),
            )
            st.plotly_chart(fig_lin, use_container_width=True)

    # Mapa de puntos de la localidad
    st.markdown(f"**Mapa de zonas — {loc_sel}** (top 200 por IPI)")
    df_mapa = df_loc_zonas.nlargest(200, "IPI")
    if not df_mapa.empty and "LAT_ZONA" in df_mapa.columns:
        import pydeck as pdk

        def _color_prioridad(p):
            if "Prioridad 1" in str(p):
                return [215, 48, 39, 200]
            elif "Prioridad 2" in str(p):
                return [252, 141, 89, 200]
            return [254, 224, 139, 200]

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
            "style": {"backgroundColor": "#1a1d27", "color": "white"},
        }
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            tooltip=tooltip,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        )
        st.pydeck_chart(deck)
