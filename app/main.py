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
    st.page_link("pages/5_metodologia.py", label="Metodología")

    st.markdown("---")
    st.caption("Fuente: SIMUR · sig.simur.gov.co")
    st.caption("Metodología IPI v1.0 · Bogotá 2016–2019")

# ── Hero ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="vs-hero">
  <div class="vs-brand">
    <div class="vs-brand-dot"></div>
    <span class="vs-brand-name">VíaSegura AI</span>
    <span class="vs-brand-badge">2016–2019</span>
  </div>
  <p class="vs-subtitle">
    Análisis espacial de siniestralidad vial en Bogotá D.C.<br>
    <span style="font-size:0.9rem;opacity:0.7">
      Índice de Prioridad de Intervención reproducible · fuente oficial SIMUR
    </span>
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# ── KPIs ─────────────────────────────────────────────────────────────────
st.markdown('<p class="vs-section-label">Escala del análisis</p>', unsafe_allow_html=True)

with st.spinner("Cargando datos..."):
    m = metricas_globales()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Siniestros analizados", f"{m['total_siniestros']:,}", "2016–2019")
with col2:
    st.metric(
        "Accidentes fatales",
        f"{m['total_muertos']:,}",
        "eventos con fallecido",
        help=(
            "Siniestros clasificados como CON MUERTOS en SIMUR. "
            "Cada registro es un accidente con ≥1 fallecido, no el conteo de víctimas individuales."
        ),
    )
with col3:
    st.metric("Zonas analizadas", f"{m['total_zonas']:,}", "celdas ~100 m")
with col4:
    st.metric("Zonas Prioridad 1", f"{m['zonas_p1']}", "intervención urgente")
with col5:
    st.metric("Red vial cubierta", "14,884 km", "OSM · 174 K segmentos")

st.markdown("---")

# ── Hallazgos clave (pitch SDM) ───────────────────────────────────────────
st.markdown('<p class="vs-section-label">Hallazgos que justifican la intervención</p>', unsafe_allow_html=True)

st.markdown(
    """
<div class="vs-finding-grid">

  <div class="vs-finding-card" style="animation-delay:0s">
    <div class="vs-finding-number">0.29%</div>
    <div class="vs-finding-label">de las zonas concentra el 6.39% de todas las muertes del periodo</div>
    <div class="vs-finding-sub">
      El Top 50 sobre 17,130 zonas activas. Concentración extrema —
      intervenir esas 50 zonas tiene impacto desproporcionado.
    </div>
  </div>

  <div class="vs-finding-card" style="animation-delay:0.1s">
    <div class="vs-finding-number">35</div>
    <div class="vs-finding-label">zonas persisten como críticas en el periodo de validación 2020–2021</div>
    <div class="vs-finding-sub">
      Solapamiento Top 200 base ↔ Top 200 reciente: 18.5%.
      Las 35 zonas persistentes son estructurales, no ruido estadístico.
    </div>
  </div>

  <div class="vs-finding-card" style="animation-delay:0.2s">
    <div class="vs-finding-number">10%</div>
    <div class="vs-finding-label">del Top 200 volumétrico tiene también alta tasa relativa de siniestros</div>
    <div class="vs-finding-sub">
      Solo 20 zonas son hotspot absoluto + relativo. El 90% restante refleja
      alto tráfico, no vías intrínsecamente peligrosas.
    </div>
  </div>

</div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Distribución + detalles ───────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<p class="vs-section-label">IPI — Índice de Prioridad de Intervención</p>', unsafe_allow_html=True)
    st.markdown(
        """
        Score compuesto **[0–100]** construido sobre 260,831 registros SIMUR.
        Combina 5 dimensiones con igual peso para capturar distintos tipos de criticidad:
        """
    )

    st.markdown(
        """
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">1</div>
  <div>
    <div class="vs-ipi-title">Volumen · 20%</div>
    <div class="vs-ipi-desc">Cantidad de siniestros en la celda durante 2016–2019</div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">2</div>
  <div>
    <div class="vs-ipi-title">Criticidad · 20%</div>
    <div class="vs-ipi-desc">Gravedad ponderada (1×leve + 3×grave + 5×fatal)</div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">3</div>
  <div>
    <div class="vs-ipi-title">Severidad · 20%</div>
    <div class="vs-ipi-desc">Criticidad promedio por evento — detecta zonas de alta letalidad con bajo volumen</div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">4</div>
  <div>
    <div class="vs-ipi-title">Persistencia · 20%</div>
    <div class="vs-ipi-desc">Años consecutivos activos (1–4) — distingue problemas estructurales de anomalías</div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">5</div>
  <div>
    <div class="vs-ipi-title">Fatalidad · 20%</div>
    <div class="vs-ipi-desc">Proporción de siniestros con fallecido — prioriza donde el riesgo es letal</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="vs-callout">
  <strong>Mayor IPI = mayor urgencia de intervención.</strong><br>
  Cada dimensión se normaliza por percentil [0–100] antes de promediar, eliminando el efecto de escala entre variables de diferente magnitud.
</div>
""",
        unsafe_allow_html=True,
    )

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
  <p class="vs-kv">Red normalización &nbsp;<b>14,884 km OSM</b></p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── MCP Server showcase ───────────────────────────────────────────────────
st.markdown('<p class="vs-section-label">Infraestructura técnica</p>', unsafe_allow_html=True)

col_mcp, col_stack = st.columns([3, 2])

with col_mcp:
    st.markdown(
        """
<div class="vs-mcp-card">
  <h4>MCP Server — SIMUR como herramienta de IA</h4>
  <p style="font-size:0.85rem;margin-bottom:12px;color:var(--vs-text-muted)">
    El proyecto expone los datos SIMUR/IPI como <strong>Model Context Protocol server</strong>,
    permitiendo que Claude (y cualquier cliente MCP) consulte zonas críticas en lenguaje natural.
  </p>
  <div style="display:flex;flex-wrap:wrap;gap:6px">
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
    st.markdown('<p class="vs-section-label">Stack técnico</p>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="vs-stack-row">
  <span class="vs-stack-badge vs-stack-accent">SIMUR ArcGIS REST</span>
  <span class="vs-stack-badge">GeoPandas · OSMnx</span>
  <span class="vs-stack-badge">H3 · Folium · PyDeck</span>
  <span class="vs-stack-badge vs-stack-accent">Claude API · MCP</span>
  <span class="vs-stack-badge">Streamlit · Plotly</span>
  <span class="vs-stack-badge">GitHub Actions CI</span>
  <span class="vs-stack-badge">uv · pytest</span>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Navegación cards ──────────────────────────────────────────────────────
st.markdown('<p class="vs-section-label">Explorar el análisis</p>', unsafe_allow_html=True)

st.markdown(
    """
<div class="vs-nav-grid">

  <div class="vs-nav-card">
    <div class="vs-nav-icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/>
        <line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/>
      </svg>
    </div>
    <div class="vs-nav-title">Mapa Interactivo</div>
    <div class="vs-nav-desc">Choropleth por localidad, hexágonos H3 y heatmap de clusters P1</div>
  </div>

  <div class="vs-nav-card">
    <div class="vs-nav-icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/>
        <line x1="8" y1="18" x2="21" y2="18"/>
        <line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/>
        <line x1="3" y1="18" x2="3.01" y2="18"/>
      </svg>
    </div>
    <div class="vs-nav-title">Zonas Críticas</div>
    <div class="vs-nav-desc">Ranking IPI filtrable por localidad, prioridad y tipo de siniestro</div>
  </div>

  <div class="vs-nav-card">
    <div class="vs-nav-icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
        <circle cx="12" cy="10" r="3"/>
      </svg>
    </div>
    <div class="vs-nav-title">Por Localidad</div>
    <div class="vs-nav-desc">Análisis comparativo por las 20 localidades distritales + mapa PyDeck</div>
  </div>

  <div class="vs-nav-card">
    <div class="vs-nav-icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    </div>
    <div class="vs-nav-title">Agente IA</div>
    <div class="vs-nav-desc">Chat con Claude Haiku 4.5 con prompt caching sobre el dataset IPI</div>
  </div>

  <div class="vs-nav-card">
    <div class="vs-nav-icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
      </svg>
    </div>
    <div class="vs-nav-title">Metodología</div>
    <div class="vs-nav-desc">IPI paso a paso, decisiones de datos, limitaciones honestas y arquitectura MCP</div>
  </div>

</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='font-size:0.75rem;color:var(--vs-text-muted);text-align:center;margin-top:24px'>"
    "Proyecto de portafolio — Ingeniería Civil énfasis Transporte · Universidad de los Andes · Coterminal"
    "</p>",
    unsafe_allow_html=True,
)
