"""
app/main.py — VíaSegura AI Dashboard
=====================================
Cómo correr:
    cd C:\\Users\\jorge\\Documents\\viasegura_ai
    .venv\\Scripts\\streamlit.exe run app/main.py
"""

import sys
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VíaSegura AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.styles import inject_global_css, SIDEBAR_BRAND

inject_global_css()

# ── Datos ────────────────────────────────────────────────────────────────
from app.data_loader import metricas_globales, cargar_ipi

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)

    st.page_link("main.py", label="Inicio")
    st.page_link("pages/1_mapa.py", label="Mapa Interactivo")
    st.page_link("pages/2_zonas_criticas.py", label="Zonas Críticas")
    st.page_link("pages/3_localidades.py", label="Por Localidad")
    st.page_link("pages/4_agente.py", label="Agente IA")

    st.markdown("---")
    st.caption("Fuente: SIMUR · sig.simur.gov.co")
    st.caption("Metodología IPI v1.0")

# ── Hero ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="vs-hero">
  <div class="vs-brand">
    <div class="vs-brand-dot"></div>
    <span class="vs-brand-name">VíaSegura AI</span>
    <span class="vs-brand-badge">2016–2019</span>
  </div>
  <p class="vs-subtitle">Sistema de Priorización de Intervención Vial · Bogotá D.C.</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── KPIs ─────────────────────────────────────────────────────────────────
st.markdown('<p class="vs-section-label">Indicadores globales</p>', unsafe_allow_html=True)

with st.spinner("Cargando datos..."):
    m = metricas_globales()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Siniestros", f"{m['total_siniestros']:,}", "2016–2019")
with col2:
    st.metric("Fallecidos", f"{m['total_muertos']:,}", "periodo base")
with col3:
    st.metric("Zonas analizadas", f"{m['total_zonas']:,}", "~100 m resolución")
with col4:
    st.metric("Zonas Prioridad 1", f"{m['zonas_p1']}", "intervención inmediata")
with col5:
    st.metric("IPI Máximo", f"{m['ipi_max']}", m["localidad_top"])

st.markdown("---")

# ── Descripción + gráfico ────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<p class="vs-section-label">Metodología</p>', unsafe_allow_html=True)
    st.markdown("""
    VíaSegura AI analiza **260,831 registros** de accidentalidad vial de Bogotá
    (fuente SIMUR, período 2016-2019) para identificar las zonas que requieren
    intervención prioritaria en infraestructura y seguridad vial.

    **Índice de Prioridad de Intervención (IPI)**
    Combina 5 dimensiones normalizadas en un score [0–100]:

    | Dimensión | Peso |
    |---|---|
    | Volumen de siniestros | 20% |
    | Criticidad total (gravedad × cantidad) | 20% |
    | Severidad promedio por siniestro | 20% |
    | Persistencia temporal (4 años) | 20% |
    | Índice de fatalidad | 20% |

    **Mayor IPI = mayor urgencia de intervención.**
    """)

with col_right:
    st.markdown(
        '<p class="vs-section-label">Distribución por prioridad</p>', unsafe_allow_html=True
    )

    df = cargar_ipi()
    prioridades = df["prioridad_IPI"].value_counts()
    labels = [p.split(" - ")[0] for p in prioridades.index]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=prioridades.values,
            hole=0.58,
            marker_colors=["#e63946", "#fc8d59", "#fee08b", "#91bfdb"],
            textinfo="label+percent",
            textfont_size=11,
            textfont_color="#edf2f7",
        )
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#edf2f7",
        annotations=[
            dict(
                text=f"<b>{m['total_zonas']:,}</b><br><span style='font-size:11px'>zonas</span>",
                x=0.5,
                y=0.5,
                font=dict(size=16, color="#edf2f7"),
                showarrow=False,
            )
        ],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
    <div style="padding-left:4px">
      <p class="vs-kv">Intervención inmediata &nbsp;<b>{m["zonas_p1"]} zonas</b></p>
      <p class="vs-kv">Activas los 4 años &nbsp;<b>{m["persistentes_4a"]:,} zonas</b></p>
      <p class="vs-kv">Zona más crítica &nbsp;<b>{m["via_top"]}</b></p>
      <p class="vs-kv">IPI promedio &nbsp;<b>{m["ipi_medio"]} / 100</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption("Navega por el menú lateral para explorar mapas, zonas y el agente IA.")
