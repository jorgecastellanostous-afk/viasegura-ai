"""
app/pages/5_metodologia.py -- Metodologia completa ViaSegura AI
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Metodologia -- ViaSegura AI",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.styles import inject_global_css, SIDEBAR_BRAND

inject_global_css()

with st.sidebar:
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)
    st.page_link("main.py", label="Inicio")
    st.page_link("pages/1_mapa.py", label="Mapa Interactivo")
    st.page_link("pages/2_zonas_criticas.py", label="Zonas Criticas")
    st.page_link("pages/3_localidades.py", label="Por Localidad")
    st.page_link("pages/4_agente.py", label="Agente IA")
    st.page_link("pages/5_metodologia.py", label="Metodologia")
    st.markdown("---")
    st.caption("Fuente: SIMUR · sig.simur.gov.co")

# -- Hero --
st.markdown(
    """
<div class="vs-hero">
  <div class="vs-hero-eyebrow">Metodologia · IPI v1.0</div>
  <h1 class="vs-hero-title">
    Decisiones tecnicas,<br>limitaciones <em>honestas</em>
  </h1>
  <p class="vs-hero-sub">
    Como se construyo el IPI, que datos se usaron, que decisiones se tomaron y
    que limitaciones tiene el analisis.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

tab_ipi, tab_datos, tab_nb05, tab_limites, tab_decisiones, tab_arq = st.tabs([
    "IPI -- Formula",
    "Pipeline de datos",
    "NB05 -- Normalizacion",
    "Limitaciones",
    "Decisiones ADR",
    "Arquitectura MCP",
])

# ============================================================
# TAB 1 -- IPI Formula
# ============================================================
with tab_ipi:
    st.markdown('<div class="vs-label">Indice de Prioridad de Intervencion</div>', unsafe_allow_html=True)

    st.markdown(
        """
        El IPI es un **score compuesto [0-100]** construido sobre
        **260,831 siniestros viales** registrados en SIMUR entre 2016 y 2019.
        Prioriza zonas de la ciudad segun la combinacion de cinco dimensiones de siniestralidad.
        """
    )

    st.markdown(
        """
<div class="vs-callout">
  <strong>Unidad espacial:</strong> celdas de grilla regular a 0.001 grados (~111 m en latitud).
  Cada celda se identifica por (lat_grid, lon_grid) redondeados a 3 decimales.
  Universo base: <strong>17,130 zonas activas</strong> en el periodo 2016-2019.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="vs-label">5 Dimensiones</div>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">01</div>
  <div>
    <div class="vs-ipi-title">Volumen -- 20%</div>
    <div class="vs-ipi-desc">
      pct_rank(cantidad_siniestros) -- Cuantos eventos ocurrieron en la celda en 4 anos.
      Percentil 0-100 sobre todas las zonas activas.
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">02</div>
  <div>
    <div class="vs-ipi-title">Criticidad -- 20%</div>
    <div class="vs-ipi-desc">
      pct_rank(criticidad_total) donde criticidad = 1 x leves + 3 x graves + 5 x fatales.
      Pesos 1/3/5 calibrados para el contexto colombiano (ADR-11).
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">03</div>
  <div>
    <div class="vs-ipi-title">Severidad -- 20%</div>
    <div class="vs-ipi-desc">
      pct_rank(criticidad_total / cantidad_siniestros) -- Gravedad promedio por evento.
      Detecta zonas de alta letalidad aunque tengan bajo volumen.
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">04</div>
  <div>
    <div class="vs-ipi-title">Persistencia -- 20%</div>
    <div class="vs-ipi-desc">
      pct_rank(anios_activos) -- Numero de anos (1-4) en los que la zona registro
      al menos un siniestro. Distingue problemas estructurales de anomalias estadisticas.
    </div>
  </div>
</div>
<div class="vs-ipi-step">
  <div class="vs-ipi-idx">05</div>
  <div>
    <div class="vs-ipi-title">Fatalidad -- 20%</div>
    <div class="vs-ipi-desc">
      pct_rank(siniestros_con_muertos / cantidad_siniestros) -- Proporcion de eventos fatales.
      Prioriza donde el riesgo de muerte es estructuralmente alto.
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Formula final")
    st.code(
        "IPI = 0.20 * P_volumen + 0.20 * P_criticidad + 0.20 * P_severidad + 0.20 * P_persistencia + 0.20 * P_fatalidad",
        language="python",
    )

    st.markdown("#### Escala de prioridades")
    c1, c2, c3, c4 = st.columns(4)
    for col, color, label, rango, desc in [
        (c1, "#ff2233", "Prioridad 1", "IPI >= 75", "Intervencion inmediata"),
        (c2, "#f97316", "Prioridad 2", "IPI 50-74", "Seguimiento activo"),
        (c3, "#eab308", "Prioridad 3", "IPI 25-49", "Monitoreo"),
        (c4, "#3b82f6", "Prioridad 4", "IPI < 25",  "Baja prioridad"),
    ]:
        col.markdown(
            f"<div style='border-left:3px solid {color};padding:10px 14px;background:#111;border-radius:0 8px 8px 0'>"
            f"<strong style='color:{color};font-family:Archivo,sans-serif'>{label}</strong><br>"
            f"<span style='font-size:0.85rem;color:#f5f5f5'>{rango}</span><br>"
            f"<span style='font-size:0.72rem;color:#888'>{desc}</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        """
<div class="vs-callout-warn" style="margin-top:20px">
  <strong>Importante:</strong> El IPI mide prioridad exploratoria, no riesgo vial real.
  Sin datos de TPDA (trafico promedio diario), una zona con alto trafico aparece primero
  por exposicion vehicular, no por ser intrinsecamente peligrosa. NB05 corrige esto parcialmente.
  Lenguaje correcto: "zonas priorizadas", "concentracion de siniestros". Nunca "zonas mas peligrosas".
</div>
""",
        unsafe_allow_html=True,
    )

# ============================================================
# TAB 2 -- Pipeline de datos
# ============================================================
with tab_datos:
    st.markdown('<div class="vs-label">Fuente primaria</div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="vs-mcp-card">
  <h4>SIMUR ArcGIS FeatureServer</h4>
  <p>API publica de la Secretaria Distrital de Movilidad de Bogota.
  260,831 registros base · 72,903 validacion · 961,101 en Layer 6.</p>
  <div>
    <span class="vs-mcp-tool">Layer 2 -- Accidentes base (2016-2019)</span>
    <span class="vs-mcp-tool">Layer 3 -- Validacion (2020-2021)</span>
    <span class="vs-mcp-tool">Layer 6 -- VM_ACC_VIA (condiciones viales)</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="vs-label">Secuencia de notebooks</div>', unsafe_allow_html=True)

    notebooks = [
        ("NB01", "Exploracion y validacion", "Deteccion de duplicados, outliers de coordenadas, distribucion temporal. Descarga SIMUR via API REST en chunks de 1,000 registros."),
        ("NB02", "Construccion IPI base", "Grid 0.001 grados, 5 dimensiones percentil, formula final, Top 200. Genera zonas_criticas_IPI_completo_2016_2019.csv con 17,130 filas."),
        ("NB03", "Validacion de actualidad", "Layer 3 (2020-2021): solapamiento 18.5% Top 200. Anos 2022-2025 excluidos por cambio estructural SIMUR (ADR-10)."),
        ("NB03.5", "Sintesis metodologica", "Notebook ejecutable en CI. Verifica integridad del pipeline sin descarga de datos."),
        ("NB04", "Actores, vehiculos y causas", "Enriquecimiento: distribucion por tipo de vehiculo, causa_top1/top2, analisis EPDO (ADR-12)."),
        ("NB04.5", "Analisis geoespacial", "H3 resolucion 8 (~460m), localidades OSM (fix admin_level=9), KDE. 3 mapas Folium."),
        ("NB05", "Normalizacion por exposicion", "Red OSM 14,884 km · poblacion DANE 2018. Tipologia 4 categorias. causa_efectiva rescue OTRA -> top2."),
    ]

    for code, name, desc in notebooks:
        st.markdown(
            f"""
<div class="vs-ipi-step">
  <div class="vs-ipi-idx" style="min-width:52px;font-size:0.62rem">{code}</div>
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
        | Fuente | Uso | Resolucion |
        |---|---|---|
        | OSMnx / OpenStreetMap | Red vial (14,884 km · 174,311 segmentos) | Segmento |
        | DANE Censo 2018 | Poblacion por localidad | Localidad (20 unidades) |
        | H3 (Uber) | Indexacion hexagonal resolucion 8 (~460m) | Celda |
        | SIMUR Layer 6 VM_ACC_VIA | Condiciones viales (semaforo, iluminacion, superficie) | Accidente |
        """
    )

# ============================================================
# TAB 3 -- NB05 Normalizacion
# ============================================================
with tab_nb05:
    st.markdown('<div class="vs-label">NB05 -- Normalizacion por exposicion</div>', unsafe_allow_html=True)

    st.markdown(
        """
        **Hallazgo central:** solo el 10% del Top 200 volumetrico (20 zonas) tiene
        tambien alta tasa relativa de siniestros por km de red vial.
        El 90% restante refleja el efecto de alto trafico vehicular.
        """
    )

    st.markdown(
        """
<div style="display:grid;grid-template-columns:1fr 1fr;gap:3px;border-radius:12px;overflow:hidden;margin:12px 0 24px">
  <div class="vs-bento-main" style="min-height:160px">
    <div class="vs-num-xl" style="font-size:3.5rem">20</div>
    <div class="vs-bento-label">zonas hotspot absoluto + relativo</div>
    <div class="vs-bento-sub">Alta prioridad estructural. Aparecen en ambos rankings.</div>
  </div>
  <div class="vs-bento-sm">
    <div class="vs-num-sm">180</div>
    <div class="vs-bento-label">solo volumetricas</div>
    <div class="vs-bento-sub">Alto trafico explica la concentracion. No intrinsecamente peligrosas.</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("#### Las 4 tipologias")
    st.markdown(
        """
        | Tipologia | Zonas | Interpretacion |
        |---|---|---|
        | Hotspot absoluto + relativo | **20** | Alto IPI volumetrico Y alta tasa/km -- auditoria urgente |
        | Hotspot por volumen | 180 | Top 200 IPI pero baja tasa/km -- efecto de trafico |
        | Hotspot relativo oculto | 180 | Alta tasa/km pero fuera del Top 200 IPI |
        | Alta tasa poblacional | 138 | Alto riesgo para residentes -- equidad vial |
        """
    )

    st.markdown("#### causa_efectiva -- rescate de OTRA")
    st.code(
        """# Cuando causa_top1 = "OTRA" o "OTRAS", usar causa_top2
df["causa_efectiva"] = df["causa_top1"]
mask_otra = df["causa_top1"].isin(["OTRA", "OTRAS"])
df.loc[mask_otra, "causa_efectiva"] = df.loc[mask_otra, "causa_top2"]
df.loc[mask_otra, "causa_imputed"] = True
# Resultado: 90/200 zonas rescatadas (45%)""",
        language="python",
    )

# ============================================================
# TAB 4 -- Limitaciones
# ============================================================
with tab_limites:
    st.markdown('<div class="vs-label">Limitaciones honestas del analisis</div>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="vs-callout-warn">
  El IPI mide <strong>prioridad exploratoria</strong>, no riesgo vial real. Estas limitaciones
  deben citarse al presentar resultados. Lenguaje correcto: "zonas priorizadas",
  "concentracion de siniestros". Nunca "zonas mas peligrosas" ni "riesgo real".
</div>
""",
        unsafe_allow_html=True,
    )

    limitaciones = [
        ("L1", "Alta", "Sin datos TPDA", "El IPI no mide riesgo por vehiculo-km. Una via con 100,000 veh/dia y 10 accidentes aparece igual que una con 1,000 veh/dia y 10 accidentes.", "Integrar aforos IDU. NB05 usa red OSM como proxy."),
        ("L2", "Media", "Grilla 0.001 grados no es unidad estandar", "Una interseccion real puede caer en la frontera de 2-4 celdas, diluyendo su senal.", "Snap-to-network o DBSCAN. H3 implementado en NB04.5 como alternativa parcial."),
        ("L3", "Media", "Validacion 2020-2021 = anos pandemia", "Movilidad atipica (-30% a -60% en trafico). El solapamiento del 18.5% esta confundido por la pandemia.", "Usar 2022-2023 cuando SIMUR confirme el cambio estructural."),
        ("L4", "Alta", "Causa OTRA en 45% de zonas Top 200", "SIMUR tiene alta tasa de causa sin clasificar. NB05 implementa rescate con causa_top2.", "Solicitar datos desagregados al SDM/SIMUR."),
        ("L5", "Baja", "Score persistencia casi binario (n=2 periodos)", "Con solo 2 puntos temporales, el score es binario: persistente o no.", "4+ periodos independientes para regresion temporal."),
        ("L6", "Media", "Poblacion DANE a nivel localidad (no UPZ)", "Sobreestima densidad en zonas de baja densidad. 20 localidades vs 112 UPZs.", "Proyecciones DANE a nivel UPZ o WorldPop (100m)."),
        ("L7", "Baja", "Sensibilidad EPDO: 84.5% estabilidad", "15.5% de zonas Top 50 cambia con pesos EPDO (1:8:24) vs actuales (1:3:5).", "Selector de escala ya implementable -- pesos parametrizables (ADR-11)."),
        ("L8", "Alta", "Anos 2022-2025 excluidos -- cambio SIMUR sin confirmar", "Caida del 61-78% en registros. Puede ser subreporte o cambio metodologico.", "Contactar SDM/SIMUR para tabla de equivalencias."),
        ("L9", "Media", "Universo incompatible entre notebooks", "NB04.5 = 17,130 zonas (base). NB04/NB05 = 19,255 zonas (incluye validacion).", "Documentar explicitamente en cada notebook. Disclaimers en UI."),
    ]

    for lid, sev, titulo, desc, mejora in limitaciones:
        color = {"Alta": "#ff2233", "Media": "#f97316", "Baja": "#eab308"}.get(sev, "#3b82f6")
        st.markdown(
            f"""
<div style="border-left:3px solid {color};padding:12px 16px;margin-bottom:8px;
            background:#111;border-radius:0 8px 8px 0">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
    <span style="font-family:'DM Mono',monospace;font-size:0.65rem;color:{color};font-weight:600">{lid}</span>
    <span style="font-size:0.62rem;color:{color};border:1px solid {color};padding:1px 7px;border-radius:20px">{sev}</span>
    <strong style="font-family:'Archivo',sans-serif;font-size:0.85rem;color:#f5f5f5">{titulo}</strong>
  </div>
  <p style="font-family:'DM Sans',sans-serif;font-size:0.8rem;color:#888;margin:0 0 5px">{desc}</p>
  <p style="font-family:'DM Sans',sans-serif;font-size:0.75rem;color:#60a5fa;margin:0">
    <strong>Mejora:</strong> {mejora}
  </p>
</div>
""",
            unsafe_allow_html=True,
        )

# ============================================================
# TAB 5 -- Decisiones ADR
# ============================================================
with tab_decisiones:
    st.markdown('<div class="vs-label">Architecture Decision Records (ADR)</div>', unsafe_allow_html=True)

    decisiones = [
        ("ADR-01", "Grilla regular 0.001 grados", "Se eligio grilla regular sobre DBSCAN por reproducibilidad y comparabilidad con datos SIMUR nativos."),
        ("ADR-10", "Exclusion anos 2022-2025", "Caida del 61-78% en registros. Hasta confirmar si es subreporte o cambio metodologico, se excluyen para no contaminar el analisis."),
        ("ADR-11", "Pesos IPI 1/3/5", "Pesos 1 (leve) / 3 (grave) / 5 (fatal). Pesos EPDO internacionales (1/8/24) probados en ADR-12: 84.5% estabilidad."),
        ("ADR-12", "Analisis de sensibilidad EPDO", "Prueba 1/3/5 vs EPDO 1/8/24. 84.5% de las zonas Top 50 son estables. Pesos parametrizables en el codigo."),
        ("ADR-13", "Join Layer 6 por CODIGO_ACCIDENTE", "La clave de join correcta para VM_ACC_VIA (Layer 6) es CODIGO_ACCIDENTE, no FORMULARIO. Validado contra 961,101 registros."),
        ("ADR-14", "causa_efectiva rescue", "Cuando causa_top1 es OTRA/OTRAS (45% zonas Top 200), se usa causa_top2. Implementado en NB05."),
    ]

    for code, titulo, desc in decisiones:
        st.markdown(
            f"""
<div class="vs-ipi-step">
  <div class="vs-ipi-idx" style="min-width:58px;font-size:0.62rem">{code}</div>
  <div>
    <div class="vs-ipi-title">{titulo}</div>
    <div class="vs-ipi-desc">{desc}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

# ============================================================
# TAB 6 -- Arquitectura MCP
# ============================================================
with tab_arq:
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<div class="vs-label">Stack tecnico</div>', unsafe_allow_html=True)
        capas = [
            ("Datos", ["SIMUR ArcGIS REST", "GeoPandas", "OSMnx", "DANE"]),
            ("Analisis espacial", ["H3 (Uber)", "Folium", "PyDeck", "Shapely"]),
            ("IA / Agentes", ["Claude API", "MCP Server", "Anthropic SDK"]),
            ("Infraestructura", ["Streamlit", "GitHub Actions CI", "uv · pytest · ruff"]),
        ]
        for capa, badges in capas:
            st.markdown(
                f'<p style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;color:#444;margin:12px 0 6px">{capa}</p>',
                unsafe_allow_html=True,
            )
            pills = " ".join(
                f'<span class="vs-stack-badge{"  red" if "Claude" in b or "MCP" in b or "SIMUR" in b else ""}">{b}</span>'
                for b in badges
            )
            st.markdown(f'<div class="vs-stack-row" style="margin:0 0 4px">{pills}</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="vs-label">MCP Server -- 6 herramientas</div>', unsafe_allow_html=True)
        st.markdown(
            """
<div class="vs-mcp-card">
  <h4>mcp_simur.server</h4>
  <p>Expone SIMUR/IPI a Claude y cualquier cliente MCP compatible.</p>
  <div style="display:flex;flex-direction:column;gap:6px">
    <div><span class="vs-mcp-tool">get_top_zonas_ipi</span>
         <small style="color:#888;font-size:0.72rem"> Top N zonas con mayor IPI</small></div>
    <div><span class="vs-mcp-tool">get_zona_detail</span>
         <small style="color:#888;font-size:0.72rem"> Detalle completo (32 columnas NB05)</small></div>
    <div><span class="vs-mcp-tool">query_simur_layer</span>
         <small style="color:#888;font-size:0.72rem"> Query directo al FeatureServer</small></div>
    <div><span class="vs-mcp-tool">get_localidad_stats</span>
         <small style="color:#888;font-size:0.72rem"> IPI P75 por localidad</small></div>
    <div><span class="vs-mcp-tool">get_tipologia_nb05</span>
         <small style="color:#888;font-size:0.72rem"> Tipologia 4 categorias</small></div>
    <div><span class="vs-mcp-tool">list_recursos_ipi</span>
         <small style="color:#888;font-size:0.72rem"> CSVs y GeoJSONs del proyecto</small></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="vs-label" style="margin-top:24px">CI/CD -- GitHub Actions</div>', unsafe_allow_html=True)
    st.markdown(
        """
        | Job | Herramienta | Que valida |
        |---|---|---|
        | Lint | ruff | Estilo PEP 8 + imports |
        | Tests unitarios | pytest (no-network) | Formula IPI, config de paths, 25 tests |
        | NB03.5 | nbconvert | Ejecucion del notebook de sintesis |
        | Integridad notebooks | nbformat | Que todos los .ipynb tienen outputs |
        """
    )

    st.markdown(
        """
<div class="vs-callout" style="margin-top:20px">
  <strong>Sub-agentes Claude Code:</strong> el proyecto tiene 6 agentes especializados en
  <code>.claude/agents/</code> -- analista-nb, geoespacial-nb, backend-py, tests-ci,
  docs-writer, agente-ipi. Cada uno con instrucciones de rol y permisos diferenciados.
</div>
""",
        unsafe_allow_html=True,
    )
