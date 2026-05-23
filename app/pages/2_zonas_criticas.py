"""
Página 2 — Zonas Críticas
Tabla filtrable de las zonas IPI con descarga CSV.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data_loader import cargar_ipi, cargar_top_vias, cargar_top_barrios
from app.styles import inject_global_css

st.set_page_config(page_title="Zonas Críticas · VíaSegura AI", page_icon="🔴", layout="wide")
inject_global_css()

st.markdown('<p class="vs-page-title">Zonas Críticas — Ranking IPI</p>', unsafe_allow_html=True)

# ── Disclaimer metodológico ──────────────────────────────────────────────
st.info(
    "**Nota metodológica:** El umbral Prioridad 1 (top 50 zonas) es una decisión operativa, "
    "no un corte estadístico natural. Las zonas en los puestos 48-55 tienen IPIs muy similares "
    "(diferencia < 0.5 puntos). Las zonas **SIN_NMG** en el top 50 no tienen nombre de vía en "
    "SIMUR; se incluye la calle identificada vía OpenStreetMap como referencia aproximada (±100 m).",
    icon="ℹ️",
)

# ── Lookup OSM para zonas sin nombre de vía en SIMUR ────────────────────
# Identificadas por reverse-geocoding Nominatim + Overpass (mayo 2026)
_OSM_VIA = {
    # (localidad, barrio): nombre OSM
    ("BOSA", "EL CORZO I"): "Cra. 100 [OSM]",
    ("PUENTE ARANDA", "SAN EUSEBIO"): "Cra. 52 / Av. Cll. 26 Sur [OSM]",
    ("ANTONIO NARI\xd1O", "CIUDAD JARDIN SUR"): "Cra. 10B [OSM]",
    ("SUBA", "RINCON ALTAMAR"): "Av. Cll. 127 [OSM]",
    ("FONTIBON", "VILLEMAR"): "Av. Cll. 17 [OSM]",
    ("BOSA", "ESCOCIA"): "Cra. 88C [OSM]",
    ("KENNEDY", "CHUCUA DE LA VACA II"): "Cra. 80F [OSM]",
}


def _patch_via(row):
    """Reemplaza SIN_NMG con nombre OSM si está disponible."""
    if str(row.get("via_predominante", "")).startswith("SIN_NMG"):
        key = (
            str(row.get("localidad_predominante", "")).upper(),
            str(row.get("barrio_predominante", "")).upper(),
        )
        return _OSM_VIA.get(key, row["via_predominante"])
    return row["via_predominante"]


df = cargar_ipi()

# ── Sidebar de filtros ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filtros")

    prioridades = st.multiselect(
        "Prioridad IPI",
        options=["Prioridad 1", "Prioridad 2", "Prioridad 3"],
        default=["Prioridad 1"],
    )

    localidades_disponibles = sorted(df["localidad_predominante"].dropna().unique())
    localidades_sel = st.multiselect(
        "Localidad",
        options=localidades_disponibles,
        default=[],
        placeholder="Todas las localidades",
    )

    clases_disponibles = sorted(df["clase_predominante"].dropna().unique())
    clases_sel = st.multiselect(
        "Clase de accidente",
        options=clases_disponibles,
        default=[],
        placeholder="Todas las clases",
    )

    anios_min = st.slider("Años activos mínimo", 1, 4, 1)
    top_n = st.slider("Top N zonas", 10, 500, 50)

# ── Filtrar datos ────────────────────────────────────────────────────────
mask = pd.Series(True, index=df.index)

if prioridades:
    mask_p = df["prioridad_IPI"].str.contains("|".join(prioridades), na=False)
    mask = mask & mask_p

if localidades_sel:
    mask = mask & df["localidad_predominante"].isin(localidades_sel)

if clases_sel:
    mask = mask & df["clase_predominante"].isin(clases_sel)

mask = mask & (df["anios_activos"] >= anios_min)

df_filtrado = df[mask].nlargest(top_n, "IPI").copy()

# ── KPIs del filtro ──────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Zonas mostradas", len(df_filtrado))
c2.metric("Total siniestros", f"{df_filtrado['cantidad_siniestros'].sum():,}")
c3.metric(
    "Acc. fatales",
    f"{df_filtrado['siniestros_con_muertos'].sum():,}",
    help="Eventos SIMUR clasificados CON MUERTOS (≠ víctimas individuales).",
)
c4.metric("IPI promedio", f"{df_filtrado['IPI'].mean():.1f}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📋 Tabla", "📊 Gráficos", "🔥 Top Vías y Barrios"])

# ── TAB 1: Tabla ─────────────────────────────────────────────────────────
with tab1:
    COLS = [
        "rank_IPI",
        "IPI",
        "prioridad_IPI",
        "localidad_predominante",
        "barrio_predominante",
        "via_predominante",
        "cantidad_siniestros",
        "siniestros_con_muertos",
        "siniestros_con_heridos",
        "anios_activos",
        "clase_predominante",
        "LAT_ZONA",
        "LON_ZONA",
    ]
    cols_mostrar = [c for c in COLS if c in df_filtrado.columns]
    df_tabla = df_filtrado[cols_mostrar].copy()
    df_tabla["IPI"] = df_tabla["IPI"].round(1)
    # Parchar SIN_NMG con nombre OSM donde esté disponible
    if "via_predominante" in df_tabla.columns:
        df_tabla["via_predominante"] = df_tabla.apply(_patch_via, axis=1)

    # Colorear por prioridad
    def color_prioridad(val):
        if "Prioridad 1" in str(val):
            return "background-color: #7f1010; color: white"
        elif "Prioridad 2" in str(val):
            return "background-color: #7f4010; color: white"
        elif "Prioridad 3" in str(val):
            return "background-color: #7f6510; color: white"
        return ""

    styled = df_tabla.style.map(color_prioridad, subset=["prioridad_IPI"])
    st.dataframe(styled, use_container_width=True, height=450)

    # Descarga
    csv_bytes = df_tabla.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar CSV",
        data=csv_bytes,
        file_name=f"viasegura_zonas_criticas_top{top_n}.csv",
        mime="text/csv",
    )

# ── TAB 2: Gráficos ──────────────────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Distribución IPI**")
        fig_hist = px.histogram(
            df_filtrado,
            x="IPI",
            nbins=30,
            color="prioridad_IPI",
            color_discrete_map={
                "Prioridad 1 - Intervención prioritaria": "#d73027",
                "Prioridad 2 - Auditoría de seguridad vial": "#fc8d59",
                "Prioridad 3 - Monitoreo periódico": "#fee08b",
            },
            template="plotly_dark",
            labels={"IPI": "IPI", "count": "Zonas"},
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title="",
            height=300,
            margin=dict(t=10, b=40),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        st.markdown("**Siniestros vs IPI (top 200)**")
        df_scatter = df_filtrado.head(200)
        fig_scat = px.scatter(
            df_scatter,
            x="cantidad_siniestros",
            y="IPI",
            color="prioridad_IPI",
            size="siniestros_con_muertos",
            size_max=25,
            hover_data=["localidad_predominante", "barrio_predominante", "via_predominante"],
            template="plotly_dark",
            color_discrete_map={
                "Prioridad 1 - Intervención prioritaria": "#d73027",
                "Prioridad 2 - Auditoría de seguridad vial": "#fc8d59",
                "Prioridad 3 - Monitoreo periódico": "#fee08b",
            },
            labels={"cantidad_siniestros": "Siniestros", "IPI": "IPI"},
        )
        fig_scat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title="",
            height=300,
            margin=dict(t=10, b=40),
        )
        st.plotly_chart(fig_scat, use_container_width=True)

    # Scores radar del top 1
    st.markdown("**Perfil de scores — zona #1 del filtro**")
    if len(df_filtrado) > 0:
        top_zona = df_filtrado.iloc[0]
        score_cols = [
            "score_volumen",
            "score_criticidad_total",
            "score_severidad_promedio",
            "score_persistencia",
            "score_fatalidad",
        ]
        score_labels = ["Volumen", "Criticidad", "Severidad", "Persistencia", "Fatalidad"]
        score_vals = [float(top_zona.get(c, 0)) for c in score_cols]

        fig_radar = go.Figure(
            go.Scatterpolar(
                r=score_vals + [score_vals[0]],
                theta=score_labels + [score_labels[0]],
                fill="toself",
                fillcolor="rgba(215,48,39,0.3)",
                line_color="#d73027",
                name=f"Zona rank #{int(top_zona['rank_IPI'])}",
            )
        )
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1], color="#9e9e9e")),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            height=320,
            margin=dict(t=30, b=30),
            showlegend=True,
        )
        info_col, radar_col = st.columns([1, 2])
        with info_col:
            st.markdown(f"""
            **Rank #{int(top_zona["rank_IPI"])}**
            - IPI: **{top_zona["IPI"]:.1f}**
            - Localidad: {top_zona["localidad_predominante"]}
            - Barrio: {top_zona["barrio_predominante"]}
            - Vía: {top_zona["via_predominante"]}
            - Siniestros: {int(top_zona["cantidad_siniestros"])}
            - Acc. fatales: {int(top_zona["siniestros_con_muertos"])}
            - Años activos: {int(top_zona["anios_activos"])}/4
            """)
        with radar_col:
            st.plotly_chart(fig_radar, use_container_width=True)

# ── TAB 3: Top Vías y Barrios ────────────────────────────────────────────
with tab3:
    tv = cargar_top_vias()
    tb = cargar_top_barrios()

    col_v, col_b = st.columns(2)

    with col_v:
        st.markdown("**Top 10 vías — criticidad acumulada**")
        fig_vias = px.bar(
            tv.head(10).sort_values("criticidad"),
            x="criticidad",
            y="via_predominante",
            orientation="h",
            color="ipi_max",
            color_continuous_scale="Reds",
            hover_data=["n_zonas", "siniestros", "muertos"],
            template="plotly_dark",
            labels={"criticidad": "Criticidad total", "via_predominante": ""},
        )
        fig_vias.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            margin=dict(t=10, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_vias, use_container_width=True)

    with col_b:
        st.markdown("**Top 10 barrios — IPI máximo**")
        tb["label"] = tb["barrio_predominante"] + " (" + tb["localidad_predominante"] + ")"
        fig_barrios = px.bar(
            tb.head(10).sort_values("ipi_max"),
            x="ipi_max",
            y="label",
            orientation="h",
            color="muertos",
            color_continuous_scale="OrRd",
            hover_data=["n_zonas", "siniestros"],
            template="plotly_dark",
            labels={"ipi_max": "IPI máximo", "label": ""},
        )
        fig_barrios.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            margin=dict(t=10, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_barrios, use_container_width=True)
