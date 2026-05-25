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

st.set_page_config(
    page_title="VíaSegura AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.styles import inject_global_css, SIDEBAR_BRAND

inject_global_css()

from app.data_loader import metricas_globales, cargar_ipi

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)
    st.page_link("main.py", label="Inicio")
    st.page_link("pages/1_mapa.py", label="Mapa Interactivo")
    st.page_link("pages/2_zonas_criticas.py", label="Zonas Críticas")
    st.page_link("pages/3_localidades.py", label="Por Localidad")
    st.page_link("pages/4_agente.py", label="Agente IA")
    st.page_link("pages/5_metodologia.py", label="Metodología")
    st.markdown("---")
    st.caption("SDM · SIMUR · sig.simur.gov.co")

# ── Datos ────────────────────────────────────────────────────────────────
with st.spinner(""):
    m = metricas_globales()

# ── Hero ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="vs-hero">
  <div class="vs-hero-eyebrow">Proyecto de portafolio · Ingeniería Civil</div>
  <h1 class="vs-hero-title">
    Priorización de<br><em>intervención vial</em><br>en Bogotá D.C.
  </h1>
  <p class="vs-hero-sub">
    Análisis espacial de 260,831 siniestros viales (SIMUR 2016–2019).
    Índice reproducible y metodológicamente defendible para identificar
    zonas críticas de intervención en infraestructura vial.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# ── KPI strip (puro HTML) ─────────────────────────────────────────────────
st.markdown('<div class="vs-label">Escala del análisis</div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="vs-kpi-strip">
  <div class="vs-kpi">
    <div class="vs-kpi-value">{m['total_siniestros']:,}</div>
    <div class="vs-kpi-label">siniestros registrados<br>2016–2019</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">{m['total_zonas']:,}</div>
    <div class="vs-kpi-label">zonas activas<br>~100 m resolución</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">{m['total_muertos']:,}</div>
    <div class="vs-kpi-label">accidentes fatales<br>periodo base</div>
  </div>
  <div class="vs-kpi">
    <div class="vs-kpi-value">14,884 km</div>
    <div class="vs-kpi-label">red vial OSM<br>174 K segmentos</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Bento de hallazgos ────────────────────────────────────────────────────
st.markdown('<div class="vs-label">Hallazgos que justifican la intervención</div>', unsafe_allow_html=True)
st.markdown(
    """
<div class="vs-bento">

  <!-- Card principal — 0.29% -->
  <div class="vs-bento-main">
    <div style="flex:1"></div>
    <div class="vs-num-xl">0.29%</div>
    <div class="vs-bento-label">
      del total de zonas concentra el <strong>6.39%</strong> de todas las muertes del periodo
    </div>
    <div class="vs-bento-sub">
      Top 50 sobre 17,130 zonas activas. Intervenir estas 50 zonas tiene
      impacto desproporcionado sobre la mortalidad vial.
    </div>
  </div>

  <!-- Card 2 — 35 zonas -->
  <div class="vs-bento-sm">
    <div style="flex:1"></div>
    <div class="vs-num-sm">35</div>
    <div class="vs-bento-label">zonas persistentes</div>
    <div class="vs-bento-sub">
      Permanecen críticas en validación 2020–2021 (18.5% solapamiento Top 200).
      Son estructurales — no ruido estadístico.
    </div>
  </div>

  <!-- Card 3 — 10% -->
  <div class="vs-bento-sm">
    <div style="flex:1"></div>
    <div class="vs-num-sm vs-num-sm-red">10%</div>
    <div class="vs-bento-label">hotspot real</div>
    <div class="vs-bento-sub">
      Solo 20 zonas del Top 200 tienen alta tasa relativa de siniestros/km de red.
      El 90% restante es efecto de tráfico.
    </div>
  </div>

</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── IPI — 5 dimensiones ───────────────────────────────────────────────────
st.markdown('<div class="vs-label">Índice de Prioridad de Intervención</div>', unsafe_allow_html=True)

col_ipi_left, col_ipi_right = st.columns([5, 4], gap="large")

with col_ipi_left:
    st.markdown(
        """
<p style="font-family:'DM Sans',sans-serif;font-size:1rem;color:#888;line-height:1.7;margin-bottom:20px">
  Score compuesto <strong style="color:#f5f5f5">[0–100]</strong> construido sobre 5 dimensiones
  normalizadas por percentil. Cada dimensión captura un tipo distinto de criticidad.
  Mayor IPI = mayor urgencia de intervención.
</p>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="vs-dim-grid">
  <div class="vs-dim-card">
    <div class="vs-dim-num">01</div>
    <div class="vs-dim-title">Volumen</div>
    <div class="vs-dim-weight">20%</div>
    <div class="vs-dim-desc">Cantidad de siniestros en la celda durante 4 años</div>
  </div>
  <div class="vs-dim-card">
    <div class="vs-dim-num">02</div>
    <div class="vs-dim-title">Criticidad</div>
    <div class="vs-dim-weight">20%</div>
    <div class="vs-dim-desc">Gravedad ponderada 1×leve + 3×grave + 5×fatal</div>
  </div>
  <div class="vs-dim-card">
    <div class="vs-dim-num">03</div>
    <div class="vs-dim-title">Severidad</div>
    <div class="vs-dim-weight">20%</div>
    <div class="vs-dim-desc">Gravedad promedio por evento — detecta alta letalidad con bajo volumen</div>
  </div>
  <div class="vs-dim-card">
    <div class="vs-dim-num">04</div>
    <div class="vs-dim-title">Persistencia</div>
    <div class="vs-dim-weight">20%</div>
    <div class="vs-dim-desc">Años consecutivos activos (1–4) — distingue problemas estructurales</div>
  </div>
  <div class="vs-dim-card">
    <div class="vs-dim-num">05</div>
    <div class="vs-dim-title">Fatalidad</div>
    <div class="vs-dim-weight">20%</div>
    <div class="vs-dim-desc">Proporción de siniestros con fallecido</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="vs-callout">
  <strong>Importante:</strong> el IPI mide prioridad exploratoria, no riesgo vial real.
  Sin datos de TPDA (tráfico promedio diario), una zona de alto tráfico aparece primero
  por exposición, no por ser intrínsecamente peligrosa. NB05 introduce corrección parcial.
</div>
""",
        unsafe_allow_html=True,
    )

with col_ipi_right:
    st.markdown(
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:0.65rem;letter-spacing:0.1em;'
        'text-transform:uppercase;color:#444;margin-bottom:12px">Distribución por prioridad</p>',
        unsafe_allow_html=True,
    )
    df = cargar_ipi()
    prioridades = df["prioridad_IPI"].value_counts()
    labels = [p.split(" - ")[0] for p in prioridades.index]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=prioridades.values,
            hole=0.62,
            marker_colors=["#ff2233", "#f97316", "#eab308", "#3b82f6"],
            textinfo="label+percent",
            textfont_size=10.5,
            textfont_color="#f5f5f5",
        )
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=240,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f5f5f5",
        annotations=[
            dict(
                text=f"<b>{m['total_zonas']:,}</b><br><span style='font-size:10px;color:#888'>zonas</span>",
                x=0.5,
                y=0.5,
                font=dict(size=18, color="#f5f5f5", family="Archivo"),
                showarrow=False,
            )
        ],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
<div style="margin-top:8px">
  <p class="vs-kv">Prioridad 1 (urgente) &nbsp;<b>{m['zonas_p1']} zonas</b></p>
  <p class="vs-kv">Activas los 4 años &nbsp;<b>{m['persistentes_4a']:,} zonas</b></p>
  <p class="vs-kv">Zona top &nbsp;<b>{m['via_top']}</b></p>
  <p class="vs-kv">IPI máximo &nbsp;<b>{m['ipi_max']} / 100</b></p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Infraestructura técnica ───────────────────────────────────────────────
col_mcp, col_stack = st.columns([3, 2], gap="large")

with col_mcp:
    st.markdown('<div class="vs-label">MCP Server</div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="vs-mcp-card">
  <h4>SIMUR como herramienta de IA</h4>
  <p>
    El proyecto expone los datos SIMUR/IPI como un
    <strong>Model Context Protocol server</strong>, permitiendo que Claude
    consulte zonas críticas de Bogotá en lenguaje natural.
  </p>
  <div>
    <span class="vs-mcp-tool">get_top_zonas_ipi</span>
    <span class="vs-mcp-tool">get_zona_detail</span>
    <span class="vs-mcp-tool">query_simur_layer</span>
    <span class="vs-mcp-tool">get_localidad_stats</span>
    <span class="vs-mcp-tool">get_tipologia_nb05</span>
    <span class="vs-mcp-tool">list_recursos_ipi</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

with col_stack:
    st.markdown('<div class="vs-label">Stack técnico</div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="vs-stack-row">
  <span class="vs-stack-badge red">SIMUR ArcGIS REST</span>
  <span class="vs-stack-badge red">Claude API · MCP</span>
  <span class="vs-stack-badge">GeoPandas · OSMnx</span>
  <span class="vs-stack-badge">H3 · Folium · PyDeck</span>
  <span class="vs-stack-badge">Streamlit · Plotly</span>
  <span class="vs-stack-badge">GitHub Actions CI</span>
  <span class="vs-stack-badge">uv · pytest · ruff</span>
  <span class="vs-stack-badge">DANE · OSM</span>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Navegación — botones reales con st.page_link ──────────────────────────
st.markdown('<div class="vs-label">Explorar el análisis</div>', unsafe_allow_html=True)

st.markdown('<div class="vs-nav-links">', unsafe_allow_html=True)
nav_cols = st.columns(5, gap="small")
with nav_cols[0]:
    st.page_link("pages/1_mapa.py",         label="Mapa Interactivo")
with nav_cols[1]:
    st.page_link("pages/2_zonas_criticas.py", label="Zonas Críticas")
with nav_cols[2]:
    st.page_link("pages/3_localidades.py",  label="Por Localidad")
with nav_cols[3]:
    st.page_link("pages/4_agente.py",       label="Agente IA")
with nav_cols[4]:
    st.page_link("pages/5_metodologia.py",  label="Metodología")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    "<p style='font-family:var(--font-b);font-size:0.72rem;color:#444;margin-top:4px'>"
    "Proyecto de portafolio — Ingeniería Civil énfasis Transporte · Universidad de los Andes · Coterminal"
    "</p>",
    unsafe_allow_html=True,
)
