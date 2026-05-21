"""
app/main.py — VíaSegura AI Dashboard
=====================================
Punto de entrada del dashboard Streamlit.

Cómo correr:
    cd C:\\Users\\jorge\\Documents\\viasegura_ai
    .venv\\Scripts\\streamlit.exe run app/main.py
"""
import sys
from pathlib import Path

import streamlit as st

# ── Path setup ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Configuración de página ─────────────────────────────────────────────
st.set_page_config(
    page_title="VíaSegura AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar */
[data-testid="stSidebar"] { background-color: #12151f; }

/* Métricas */
[data-testid="stMetric"] {
    background: #1a1d27;
    border-radius: 10px;
    padding: 16px 20px;
    border-left: 4px solid #d73027;
}
[data-testid="stMetricLabel"] { font-size: 0.78rem; color: #9e9e9e; }
[data-testid="stMetricValue"] { font-size: 1.7rem; font-weight: 700; }

/* Tablas */
.dataframe thead th { background-color: #d73027 !important; color: white !important; }

/* Título principal */
.viasegura-title {
    font-size: 2rem; font-weight: 800; color: #d73027;
    letter-spacing: -1px; margin-bottom: 0;
}
.viasegura-sub {
    font-size: 1rem; color: #9e9e9e; margin-top: 0;
}
</style>
""", unsafe_allow_html=True)

# ── Importar datos ──────────────────────────────────────────────────────
from app.data_loader import metricas_globales, cargar_ipi

# ── Sidebar ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0 20px'>
        <span style='font-size:2.5rem'>🚦</span>
        <p style='font-size:1.1rem;font-weight:700;color:#d73027;margin:4px 0'>VíaSegura AI</p>
        <p style='font-size:0.75rem;color:#9e9e9e;margin:0'>Bogotá · 2016-2019</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Navegación**")
    st.page_link("main.py",                    label="🏠 Inicio")
    st.page_link("pages/1_mapa.py",            label="🗺️ Mapa Interactivo")
    st.page_link("pages/2_zonas_criticas.py",  label="🔴 Zonas Críticas")
    st.page_link("pages/3_localidades.py",     label="📍 Por Localidad")
    st.page_link("pages/4_agente.py",          label="🤖 Agente IA")

    st.markdown("---")
    st.caption("Fuente: SIMUR · sig.simur.gov.co")
    st.caption("Metodología IPI v1.0")

# ── Contenido principal ─────────────────────────────────────────────────
st.markdown(
    "<p class='viasegura-title'>🚦 VíaSegura AI</p>"
    "<p class='viasegura-sub'>Sistema de Priorización de Intervención Vial · Bogotá D.C.</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── KPIs globales ───────────────────────────────────────────────────────
with st.spinner("Cargando datos..."):
    m = metricas_globales()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Siniestros", f"{m['total_siniestros']:,}", "2016-2019")
with col2:
    st.metric("Fallecidos", f"{m['total_muertos']:,}", "periodo base")
with col3:
    st.metric("Zonas analizadas", f"{m['total_zonas']:,}", "~100m resolución")
with col4:
    st.metric("Zonas Prioridad 1", f"{m['zonas_p1']}", "intervención inmediata")
with col5:
    st.metric("IPI Máximo", f"{m['ipi_max']}", m["localidad_top"])

st.markdown("---")

# ── Dos columnas: descripción + estadísticas rápidas ────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("¿Qué es VíaSegura AI?")
    st.markdown("""
    VíaSegura AI analiza **260,831 registros** de accidentalidad vial de Bogotá
    (fuente SIMUR, período 2016-2019) para identificar las zonas que requieren
    intervención prioritaria en infraestructura y seguridad vial.

    **Índice de Prioridad de Intervención (IPI)**
    Combina 5 dimensiones normalizadas en un score [0-100]:

    | Dimensión | Peso |
    |---|---|
    | Volumen de siniestros | 25% |
    | Criticidad total (gravedad × cantidad) | 25% |
    | Severidad promedio por siniestro | 20% |
    | Persistencia temporal (4 años) | 15% |
    | Índice de fatalidad | 15% |

    **Mayor IPI = mayor urgencia de intervención.**
    """)

with col_right:
    st.subheader("Resumen del análisis")

    df = cargar_ipi()
    prioridades = df["prioridad_IPI"].value_counts()

    import plotly.graph_objects as go

    labels = [p.split(" - ")[0] for p in prioridades.index]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=prioridades.values,
        hole=0.55,
        marker_colors=["#d73027", "#fc8d59", "#fee08b", "#91bfdb"],
        textinfo="label+percent",
        textfont_size=12,
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e8eaf6",
        annotations=[dict(
            text=f"<b>{m['total_zonas']:,}</b><br>zonas",
            x=0.5, y=0.5, font_size=14, showarrow=False,
            font_color="#e8eaf6",
        )],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    - 🔴 **{m['zonas_p1']} zonas** de intervención inmediata
    - ⏳ **{m['persistentes_4a']:,} zonas** activas los 4 años del período
    - 📍 Zona más crítica: **{m['via_top']}** ({m['localidad_top']})
    - IPI promedio: **{m['ipi_medio']}** / 100
    """)

st.markdown("---")
st.caption("Navega por las páginas del menú lateral para explorar mapas, zonas y el agente IA.")
