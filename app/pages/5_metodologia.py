"""
app/pages/5_metodologia.py — Metodología completa VíaSegura AI
================================================================
Explica el IPI, la pipeline de datos, las limitaciones honestas,
las decisiones técnicas (ADR) y la infraestructura MCP.
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Metodología — VíaSegura AI",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.styles import inject_global_css, SIDEBAR_BRAND

inject_global_css()

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

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="vs-hero">
  <div class="vs-brand">
    <div class="vs-brand-dot"></div>
    <span class="vs-brand-name">Metodología</span>
    <span class="vs-brand-badge">IPI v1.0</span>
  </div>
  <p class="vs-subtitle">
    Decisiones técnicas, limitaciones honestas y arquitectura del sistema
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────
tab_ipi, tab_datos, tab_nb05, tab_limites, tab_decisiones, tab_arq = st.tabs([
    "IPI — Fórmula",
    "Pipeline de datos",
    "NB05 — Normalización",
    "Limitaciones",
    "Decisiones ADR",
    "Arquitectura MCP",
])

# ════════════════════════════════════════════════════════════════════════
# TAB 1 — IPI Fórmula
# ════════════════════════════════════════════════════════════════════════
with tab_ipi:
    st.markdown('<p class="vs-section-label">Índice de Prioridad de Intervención</p>', unsafe_allow_html=True)

    st.markdown(
        """
        El IPI es un **score compuesto [0–100]** que prioriza zonas de la ciudad según
        la combinación de cinco dimensiones de siniestralidad. Está construido sobre
        **260,831 siniestros viales** registrados en SIMUR entre 2016 y 2019.
        """
    )

    st.markdown(
        """
<div class="vs-callout">
  <strong>Unidad espacial:</strong> celdas de grilla regular a 0.001° (~111 m en latitud, ~88 m en longitud a la latitud de Bogotá).
  Cada celda se identifica por (lat_grid, lon_grid) redondeados a 3 decimales.
  El universo final tiene <strong>17,130 zonas activas</strong> en el periodo base.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Dimensiones del IPI")

    st.markdown(
        """
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">1</div>
  <div>
    <div class="vs-ipi-title">Volumen — 20%</div>
    <div class="vs-ipi-desc">
      <code>pct_rank(cantidad_siniestros)</code> — Cuántos eventos ocurrieron en la celda en 4 años.
      Percentil 0–100 sobre todas las zonas activas.
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">2</div>
  <div>
    <div class="vs-ipi-title">Criticidad — 20%</div>
    <div class="vs-ipi-desc">
      <code>pct_rank(criticidad_total)</code> donde <code>criticidad = 1×leves + 3×graves + 5×fatales</code>.
      Pesos 1/3/5 calibrados para el contexto colombiano (ADR-11).
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">3</div>
  <div>
    <div class="vs-ipi-title">Severidad — 20%</div>
    <div class="vs-ipi-desc">
      <code>pct_rank(criticidad_total / cantidad_siniestros)</code> — Gravedad promedio por evento.
      Detecta zonas de alta letalidad aunque tengan bajo volumen.
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">4</div>
  <div>
    <div class="vs-ipi-title">Persistencia — 20%</div>
    <div class="vs-ipi-desc">
      <code>pct_rank(anios_activos)</code> — Número de años (1–4) en los que la zona registró
      al menos un siniestro. Distingue problemas estructurales de anomalías estadísticas.
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">5</div>
  <div>
    <div class="vs-ipi-title">Fatalidad — 20%</div>
    <div class="vs-ipi-desc">
      <code>pct_rank(siniestros_con_muertos / cantidad_siniestros)</code> — Proporción de eventos fatales.
      Prioriza donde el riesgo de muerte es estructuralmente alto.
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Fórmula final")
    st.code(
        "IPI = 0.20 × P_volumen + 0.20 × P_criticidad + 0.20 × P_severidad + 0.20 × P_persistencia + 0.20 × P_fatalidad",
        language="python",
    )

    st.markdown("#### Escala de prioridades")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            "<div style='border-left:3px solid #e63946;padding:8px 12px'>"
            "<strong style='color:#e63946'>Prioridad 1</strong><br>IPI ≥ 75<br>"
            "<small>Intervención inmediata</small></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            "<div style='border-left:3px solid #fc8d59;padding:8px 12px'>"
            "<strong style='color:#fc8d59'>Prioridad 2</strong><br>IPI 50–74<br>"
            "<small>Seguimiento activo</small></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            "<div style='border-left:3px solid #fee08b;padding:8px 12px'>"
            "<strong style='color:#fee08b'>Prioridad 3</strong><br>IPI 25–49<br>"
            "<small>Monitoreo</small></div>",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            "<div style='border-left:3px solid #91bfdb;padding:8px 12px'>"
            "<strong style='color:#91bfdb'>Prioridad 4</strong><br>IPI &lt; 25<br>"
            "<small>Baja prioridad</small></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div class="vs-callout-warn" style="margin-top:16px">
  <strong>Importante:</strong> El IPI mide <em>prioridad exploratoria</em>, no riesgo vial real.
  Sin datos de TPDA (tráfico promedio diario), una zona con alto tráfico aparece primero
  por exposición vehicular, no por ser intrínsecamente peligrosa. NB05 corrige esto parcialmente.
  Usar "zonas priorizadas" o "concentración de siniestros" — nunca "zonas más peligrosas".
</div>
""",
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════════════
# TAB 2 — Pipeline de datos
# ════════════════════════════════════════════════════════════════════════
with tab_datos:
    st.markdown('<p class="vs-section-label">Pipeline de datos</p>', unsafe_allow_html=True)

    st.markdown(
        """
        Los datos provienen de la **API pública de SIMUR** (Secretaría Distrital de Movilidad).
        El endpoint es un FeatureServer de ArcGIS con múltiples capas de accidentalidad.
        """
    )

    st.markdown("#### Fuente primaria")
    st.markdown(
        """
<div class="vs-mcp-card">
  <h4>SIMUR ArcGIS FeatureServer</h4>
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">
    <span class="vs-mcp-tool">Layer 2 — Accidentes base (2016–2019)</span>
    <span class="vs-mcp-tool">Layer 3 — Validación (2020–2021)</span>
    <span class="vs-mcp-tool">Layer 6 — VM_ACC_VIA (condiciones viales)</span>
  </div>
  <p style="font-size:0.8rem;margin-top:10px;color:var(--vs-text-muted)">
    260,831 registros base · 72,903 validación · 961,101 en Layer 6 (clave: CODIGO_ACCIDENTE)
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Secuencia de notebooks")

    notebooks = [
        ("NB01", "Exploración y validación", "Detección de duplicados, outliers de coordenadas, distribución temporal. Descarga SIMUR via API REST en chunks de 1,000 registros."),
        ("NB02", "Construcción IPI base", "Grid 0.001°, 5 dimensiones percentil, fórmula final, Top 200. Genera zonas_criticas_IPI_completo_2016_2019.csv con 17,130 filas."),
        ("NB03", "Validación de actualidad", "Layer 3 (2020-2021): solapamiento 18.5% Top 200. Años 2022-2025 excluidos por cambio estructural SIMUR (ADR-10)."),
        ("NB03.5", "Síntesis metodológica", "Notebook ejecutable en CI. Verifica integridad del pipeline sin descarga de datos."),
        ("NB04", "Actores, vehículos y causas", "Enriquecimiento: distribución por tipo de vehículo, causa_top1/top2, análisis EPDO (ADR-12)."),
        ("NB04.5", "Análisis geoespacial", "H3 (resolución 8 · ~460m), localidades OSM (fix admin_level=9 → filtro 'Localidad '), KDE. 3 mapas Folium."),
        ("NB05", "Normalización por exposición", "Red OSM 14,884 km · población DANE 2018. Tipología 4 categorías. causa_efectiva rescue de OTRA→top2."),
    ]

    for code, name, desc in notebooks:
        st.markdown(
            f"""
<div class="vs-ipi-step" style="margin-bottom:8px">
  <div class="vs-ipi-idx" style="min-width:52px;font-size:0.7rem">{code}</div>
  <div>
    <div class="vs-ipi-title">{name}</div>
    <div class="vs-ipi-desc">{desc}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("#### Fuentes complementarias")
    st.markdown(
        """
        | Fuente | Uso | Resolución |
        |---|---|---|
        | OSMnx / OpenStreetMap | Red vial completa (14,884 km · 174,311 segmentos) | Segmento individual |
        | DANE Censo 2018 | Población por localidad (denominador tasa) | Localidad (20 unidades) |
        | H3 (Uber) | Indexación hexagonal resolución 8 (~460m) | Celda |
        | SIMUR Layer 6 VM_ACC_VIA | Condiciones viales (semáforo, iluminación, superficie) | Accidente |
        """
    )

# ════════════════════════════════════════════════════════════════════════
# TAB 3 — NB05 Normalización
# ════════════════════════════════════════════════════════════════════════
with tab_nb05:
    st.markdown('<p class="vs-section-label">NB05 — Normalización por exposición</p>', unsafe_allow_html=True)

    st.markdown(
        """
        **Hallazgo central:** solo el 10% del Top 200 volumétrico (20 zonas) tiene también alta
        tasa relativa de siniestros por km de red vial. El 90% restante refleja el efecto de
        alto tráfico vehicular, no vías intrínsecamente peligrosas.
        """
    )

    st.markdown(
        """
<div class="vs-finding-grid" style="grid-template-columns:repeat(2,1fr)">
  <div class="vs-finding-card">
    <div class="vs-finding-number">20</div>
    <div class="vs-finding-label">zonas hotspot absoluto + relativo</div>
    <div class="vs-finding-sub">Alta prioridad estructural — auditoría urgente. Aparecen en ambos rankings.</div>
  </div>
  <div class="vs-finding-card">
    <div class="vs-finding-number">180</div>
    <div class="vs-finding-label">zonas solo volumétricas</div>
    <div class="vs-finding-sub">Alto tráfico explica la concentración. No son intrínsecamente peligrosas.</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Las 4 tipologías")
    st.markdown(
        """
        | Tipología | Zonas | Interpretación |
        |---|---|---|
        | Hotspot absoluto + relativo | **20** | Alto IPI volumétrico Y alta tasa/km — auditoría urgente |
        | Hotspot por volumen | 180 | Top 200 IPI pero baja tasa/km — efecto de tráfico |
        | Hotspot relativo oculto | 180 | Alta tasa/km pero fuera del Top 200 IPI — sub-representados |
        | Alta tasa poblacional | 138 | Alto riesgo para residentes — perspectiva de equidad vial |
        """
    )

    st.markdown("#### Denominadores de normalización")
    st.markdown(
        """
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">km</div>
  <div>
    <div class="vs-ipi-title">Red vial OSM (proxy exposición vehicular)</div>
    <div class="vs-ipi-desc">
      14,884.9 km · 174,311 segmentos. Buffer 100m alrededor de cada zona para asignar km de red.
      Limitación: no refleja TPDA real — una avenida y una calle local pesan igual por km.
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">hab</div>
  <div>
    <div class="vs-ipi-title">Población DANE 2018 (exposición peatonal/residente)</div>
    <div class="vs-ipi-desc">
      A nivel localidad (20 unidades). Tasa = siniestros / 100,000 hab.
      Limitación: resolución localidad sobreestima densidad en zonas de alta densidad intra-localidad.
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### causa_efectiva — rescate de OTRA")
    st.markdown(
        """
        El campo de causa SIMUR tiene alta tasa de respuesta "OTRA" (sin clasificar).
        En NB05 se implementó el rescate:
        """
    )
    st.code(
        """# Cuando causa_top1 = "OTRA" o "OTRAS", usar causa_top2 (siempre accionable)
df["causa_efectiva"] = df["causa_top1"]
mask_otra = df["causa_top1"].isin(["OTRA", "OTRAS"])
df.loc[mask_otra, "causa_efectiva"] = df.loc[mask_otra, "causa_top2"]
df.loc[mask_otra, "causa_imputed"] = True
# Resultado: 90/200 zonas rescatadas (45%)""",
        language="python",
    )

# ════════════════════════════════════════════════════════════════════════
# TAB 4 — Limitaciones
# ════════════════════════════════════════════════════════════════════════
with tab_limites:
    st.markdown('<p class="vs-section-label">Limitaciones honestas del análisis</p>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="vs-callout-warn">
  El IPI mide <strong>prioridad exploratoria</strong>, no riesgo vial real. Estas limitaciones
  deben citarse al presentar resultados. El lenguaje correcto es "zonas priorizadas" o
  "concentración de siniestros", nunca "zonas más peligrosas" ni "riesgo real".
</div>
""",
        unsafe_allow_html=True,
    )

    limitaciones = [
        ("L1", "Alta", "Sin datos TPDA (tráfico diario)", "El IPI no mide riesgo por vehículo-km. Una vía con 100,000 veh/día y 10 accidentes aparece igual que una con 1,000 veh/día y 10 accidentes.", "Integrar aforos IDU o modelos de demanda SDM como denominador. NB05 usa red OSM como proxy."),
        ("L2", "Media", "Grilla 0.001° no es unidad estándar de transporte", "Una intersección real puede caer en la frontera de 2-4 celdas, diluyendo su señal. H3 implementado en NB04.5 como alternativa parcial.", "Snap-to-network o DBSCAN sin grilla predefinida."),
        ("L3", "Media", "Validación 2020-2021 = años pandemia", "Movilidad atípica (-30% a -60% en tráfico). El solapamiento del 18.5% está confundido por la pandemia.", "Usar 2022-2023 cuando SIMUR confirme el cambio estructural (ver L8)."),
        ("L4", "Alta", "Causa OTRA en 45% de zonas Top 200", "SIMUR tiene alta tasa de causa sin clasificar. El campo causa_top1 no es accionable para 45% de las zonas. NB05 implementa rescate con causa_top2.", "Solicitar datos desagregados al SDM o cruzar con informes Policía de Tránsito."),
        ("L5", "Baja", "Score de persistencia casi binario (n=2 periodos)", "Con solo 2 puntos temporales, el score es binario: persistente o no. No captura tendencias.", "4+ periodos independientes para regresión temporal de tendencia."),
        ("L6", "Media", "Población DANE a nivel localidad (no UPZ)", "Sobreestima densidad en zonas de baja densidad. 20 localidades vs 112 UPZs disponibles.", "Proyecciones DANE a nivel UPZ o WorldPop (100m resolución)."),
        ("L7", "Baja", "Análisis sensibilidad EPDO: 84.5% estabilidad", "15.5% de zonas Top 50 cambia con pesos EPDO (1:8:24) vs actuales (1:3:5). ~8 de 50 zonas P1 pueden desplazarse.", "Selector de escala ya implementable — pesos parametrizables en el código (ADR-11)."),
        ("L8", "Alta", "Años 2022-2025 excluidos — cambio SIMUR sin confirmar", "Caída del 61-78% en registros 2022-2025 vs base. Puede ser subreporte, cambio de plataforma o metodológico. Sin confirmación oficial.", "Contactar SDM/SIMUR para tabla de equivalencias. Documentar conclusión en ADR-10."),
        ("L9", "Media", "Universo incompatible entre notebooks", "NB04.5 = 17,130 zonas (base 2016-2019). NB04/NB05 = 19,255 zonas (incluye validación). Comparaciones cruzadas usan denominadores distintos.", "Documentar explícitamente en cada notebook. Disclaimers en UI."),
    ]

    for lid, severidad, titulo, desc, mejora in limitaciones:
        color = {"Alta": "#e63946", "Media": "#fc8d59", "Baja": "#fee08b"}.get(severidad, "#91bfdb")
        st.markdown(
            f"""
<div style="border-left:3px solid {color};padding:10px 14px;margin-bottom:10px;
            background:rgba(255,255,255,0.03);border-radius:0 6px 6px 0">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
    <span style="font-family:var(--font-mono);font-size:0.75rem;color:{color};font-weight:600">{lid}</span>
    <span style="font-size:0.7rem;color:{color};border:1px solid {color};padding:1px 6px;border-radius:4px">{severidad}</span>
    <strong style="font-size:0.85rem">{titulo}</strong>
  </div>
  <p style="font-size:0.82rem;color:var(--vs-text-muted);margin:0 0 4px 0">{desc}</p>
  <p style="font-size:0.78rem;color:#60a5fa;margin:0"><strong>Mejora:</strong> {mejora}</p>
</div>
""",
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════════════════
# TAB 5 — Decisiones ADR
# ════════════════════════════════════════════════════════════════════════
with tab_decisiones:
    st.markdown('<p class="vs-section-label">Architecture Decision Records (ADR)</p>', unsafe_allow_html=True)

    st.markdown(
        """
        Las decisiones técnicas clave están documentadas en `DECISIONS.md` en formato ADR.
        Las más relevantes para entender el análisis:
        """
    )

    decisiones = [
        ("ADR-01", "Grilla regular 0.001°", "Se eligió grilla regular sobre DBSCAN por reproducibilidad y comparabilidad con datos SIMUR nativos. La resolución 0.001° (~100m) es el mínimo que evita dispersión excesiva."),
        ("ADR-10", "Exclusión años 2022-2025", "Los datos 2022-2025 muestran caída del 61-78% en registros vs el periodo base. Hasta confirmar si es subreporte o cambio metodológico en SIMUR, se excluyen para no contaminar el análisis con datos de calidad desconocida."),
        ("ADR-11", "Pesos IPI 1/3/5", "Se adoptaron pesos 1 (leve) / 3 (grave) / 5 (fatal) como aproximación al contexto colombiano. Los pesos EPDO internacionales (1/8/24) se probaron en análisis de sensibilidad (ADR-12): 84.5% de estabilidad."),
        ("ADR-12", "Análisis de sensibilidad EPDO", "Prueba 1/3/5 vs EPDO 1/8/24. Resultado: 84.5% de las zonas Top 50 son estables. Los pesos son parametrizables en el código para facilitar comparación."),
        ("ADR-13", "Join Layer 6 por CODIGO_ACCIDENTE", "La clave de join correcta para VM_ACC_VIA (Layer 6) es CODIGO_ACCIDENTE, no FORMULARIO. Validado contra 961,101 registros de Layer 6."),
        ("ADR-14", "causa_efectiva rescue", "Cuando causa_top1 es OTRA/OTRAS (45% de zonas Top 200), se usa causa_top2 como causa_efectiva. Siempre es accionable. Implementado en NB05 como columna adicional."),
    ]

    for code, titulo, desc in decisiones:
        st.markdown(
            f"""
<div class="vs-ipi-step" style="margin-bottom:10px">
  <div class="vs-ipi-idx" style="min-width:56px;font-size:0.65rem">{code}</div>
  <div>
    <div class="vs-ipi-title">{titulo}</div>
    <div class="vs-ipi-desc">{desc}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════════════════
# TAB 6 — Arquitectura MCP
# ════════════════════════════════════════════════════════════════════════
with tab_arq:
    st.markdown('<p class="vs-section-label">Arquitectura del sistema</p>', unsafe_allow_html=True)

    col_diag, col_detail = st.columns([1, 1])

    with col_diag:
        st.markdown("#### Stack técnico")
        st.markdown(
            """
<div class="vs-stack-row" style="flex-direction:column;align-items:flex-start;gap:8px">
  <div>
    <span style="font-size:0.75rem;color:var(--vs-text-muted);display:block;margin-bottom:4px">Datos</span>
    <span class="vs-stack-badge vs-stack-accent">SIMUR ArcGIS REST</span>
    <span class="vs-stack-badge">GeoPandas</span>
    <span class="vs-stack-badge">OSMnx</span>
    <span class="vs-stack-badge">DANE</span>
  </div>
  <div>
    <span style="font-size:0.75rem;color:var(--vs-text-muted);display:block;margin-bottom:4px">Análisis espacial</span>
    <span class="vs-stack-badge">H3 (Uber)</span>
    <span class="vs-stack-badge">Folium</span>
    <span class="vs-stack-badge">PyDeck</span>
    <span class="vs-stack-badge">Shapely</span>
  </div>
  <div>
    <span style="font-size:0.75rem;color:var(--vs-text-muted);display:block;margin-bottom:4px">IA / Agentes</span>
    <span class="vs-stack-badge vs-stack-accent">Claude API</span>
    <span class="vs-stack-badge vs-stack-accent">MCP Server</span>
    <span class="vs-stack-badge">Anthropic SDK</span>
  </div>
  <div>
    <span style="font-size:0.75rem;color:var(--vs-text-muted);display:block;margin-bottom:4px">Infraestructura</span>
    <span class="vs-stack-badge">Streamlit</span>
    <span class="vs-stack-badge">GitHub Actions CI</span>
    <span class="vs-stack-badge">uv · pytest</span>
    <span class="vs-stack-badge">ruff</span>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col_detail:
        st.markdown("#### MCP Server — 6 herramientas")
        st.markdown(
            """
<div class="vs-mcp-card">
  <h4>mcp_simur.server</h4>
  <p style="font-size:0.82rem;color:var(--vs-text-muted);margin-bottom:12px">
    Model Context Protocol server que expone SIMUR/IPI a Claude y cualquier cliente MCP compatible.
    Permite consultas en lenguaje natural sobre las zonas más críticas de Bogotá.
  </p>
  <div style="display:flex;flex-direction:column;gap:6px">
    <div><span class="vs-mcp-tool">get_top_zonas_ipi</span> &nbsp;<small style="color:var(--vs-text-muted)">Top N zonas con mayor IPI, filtrables por localidad</small></div>
    <div><span class="vs-mcp-tool">get_zona_detail</span> &nbsp;<small style="color:var(--vs-text-muted)">Detalle completo de una zona (32 columnas NB05)</small></div>
    <div><span class="vs-mcp-tool">query_simur_layer</span> &nbsp;<small style="color:var(--vs-text-muted)">Query directo al FeatureServer de SIMUR</small></div>
    <div><span class="vs-mcp-tool">get_localidad_stats</span> &nbsp;<small style="color:var(--vs-text-muted)">IPI P75 y distribución por localidad</small></div>
    <div><span class="vs-mcp-tool">get_tipologia_nb05</span> &nbsp;<small style="color:var(--vs-text-muted)">Tipología de concordancia (4 categorías)</small></div>
    <div><span class="vs-mcp-tool">list_recursos_ipi</span> &nbsp;<small style="color:var(--vs-text-muted)">Recursos estáticos: CSVs, GeoJSONs del proyecto</small></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("#### CI/CD — GitHub Actions")
    st.markdown(
        """
        El pipeline de validación corre en cada push y pull request:

        | Job | Herramienta | Qué valida |
        |---|---|---|
        | Lint | ruff | Estilo PEP 8 + errores de imports |
        | Tests unitarios | pytest (no-network) | Fórmula IPI, config de paths, 25 tests |
        | NB03.5 | nbconvert | Ejecución del notebook de síntesis |
        | Integridad notebooks | nbformat | Que todos los .ipynb tienen outputs y no están corruptos |
        """
    )

    st.markdown(
        """
<div class="vs-callout">
  <strong>Sub-agentes Claude Code:</strong> el proyecto tiene 6 agentes especializados en
  <code>.claude/agents/</code> con roles y permisos diferenciados:
  analista-nb, geoespacial-nb, backend-py, tests-ci, docs-writer, agente-ipi.
  Cada uno tiene instrucciones de rol en su YAML y acceso limitado a las herramientas necesarias.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='font-size:0.75rem;color:var(--vs-text-muted);margin-top:24px'>"
        "Proyecto de portafolio — Ingeniería Civil énfasis Transporte · Universidad de los Andes · Coterminal"
        "</p>",
        unsafe_allow_html=True,
    )
