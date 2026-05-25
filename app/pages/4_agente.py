"""
Página 4 — Agente IA
Chat con Claude Haiku 4.5 sobre los datos IPI de Bogotá.
Usa prompt caching para no re-enviar el CSV en cada mensaje.
La API key se puede ingresar directamente en la barra lateral.
"""

import os
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Cargar .env si existe
_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

st.set_page_config(page_title="Agente IA · VíaSegura AI", page_icon="🤖", layout="wide")

from app.styles import inject_global_css, SIDEBAR_BRAND

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

    st.markdown('<div class="vs-label">Configuración</div>', unsafe_allow_html=True)
    api_key_env = os.environ.get("ANTHROPIC_API_KEY", "")
    api_key_input = st.text_input(
        "Anthropic API Key",
        value=api_key_env,
        type="password",
        placeholder="sk-ant-...",
        help="Obtén tu clave en console.anthropic.com",
    )
    api_key = api_key_input.strip() or api_key_env

    st.markdown("---")
    st.markdown('<div class="vs-label">Preguntas sugeridas</div>', unsafe_allow_html=True)
    sugeridas = [
        "¿Cuáles son las 3 zonas más urgentes y por qué?",
        "¿Qué localidades tienen más accidentes fatales?",
        "Dame recomendaciones para Kennedy",
        "¿Qué tipo de accidentes predomina en Prioridad 1?",
        "¿Cuáles vías necesitan intervención de ingeniería?",
        "Resume los hallazgos en 5 puntos para una presentación",
    ]
    for q in sugeridas:
        if st.button(q, use_container_width=True, key=f"sug_{q[:20]}"):
            st.session_state.pregunta_rapida = q

    st.markdown("---")
    if st.button("Limpiar historial", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

    st.caption("SDM · SIMUR · sig.simur.gov.co")

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="vs-hero">
  <div class="vs-hero-eyebrow">Claude Haiku 4.5 · Contexto: 17,130 zonas</div>
  <h1 class="vs-hero-title">
    Agente<br><em>intérprete</em><br>de seguridad vial
  </h1>
  <p class="vs-hero-sub">
    Pregúntale a Claude sobre el análisis IPI de Bogotá 2016–2019.
    El agente tiene acceso completo a las zonas analizadas, rankings de localidades,
    vías críticas y tipología de hotspots NB05.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

if not api_key:
    st.markdown(
        """
<div class="vs-callout-warn">
  <b>API Key requerida.</b> Ingresa tu Anthropic API Key en la barra lateral para activar el agente.
  Obtén la tuya en <a href="https://console.anthropic.com" target="_blank" style="color:var(--amber)">console.anthropic.com</a>
  o agrega <code>ANTHROPIC_API_KEY=sk-ant-...</code> al archivo <code>.env</code> del proyecto.
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()


# ── Cargar contexto del agente (cacheado) ─────────────────────────────────
@st.cache_data(show_spinner=False)
def _cargar_ipi_resumen() -> str:
    import csv
    import statistics
    from collections import Counter

    import pandas as pd

    from config import REPORTS

    ipi_path = REPORTS / "zonas_criticas_IPI_completo_2016_2019.csv"
    with open(ipi_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    top200 = rows[:200]
    lineas = [
        "## Dataset: Zonas Críticas IPI Bogotá 2016-2019",
        f"Total zonas analizadas: {len(rows):,}",
        "Top 200 por IPI (pipe-separado):",
        "rank|IPI|prioridad|lat|lon|siniestros|muertos|criticidad|localidad|barrio|via|clase|anios|score_vol|score_fat",
    ]
    for r in top200:
        lineas.append(
            f"{r.get('rank_IPI', '?')}|{float(r.get('IPI', 0)):.1f}"
            f"|{r.get('prioridad_IPI', '?').split(' - ')[0]}"
            f"|{r.get('LAT_ZONA', '?')}|{r.get('LON_ZONA', '?')}"
            f"|{r.get('cantidad_siniestros', '?')}|{r.get('siniestros_con_muertos', '?')}"
            f"|{r.get('criticidad_total', '?')}"
            f"|{r.get('localidad_predominante', '?')}|{r.get('barrio_predominante', '?')}"
            f"|{r.get('via_predominante', '?')}|{r.get('clase_predominante', '?')}"
            f"|{r.get('anios_activos', '?')}"
            f"|{float(r.get('score_volumen', 0)):.3f}|{float(r.get('score_fatalidad', 0)):.3f}"
        )

    ipi_vals = [float(r["IPI"]) for r in rows if r.get("IPI")]
    prioridades = Counter(r.get("prioridad_IPI", "?").split(" - ")[0] for r in rows)
    lineas += [
        "\n## Estadísticas globales",
        f"IPI: min={min(ipi_vals):.1f} max={max(ipi_vals):.1f} media={statistics.mean(ipi_vals):.1f}",
        f"Prioridades: {dict(prioridades)}",
        f"Zonas activas 4 años: {sum(1 for r in rows if r.get('anios_activos') == '4'):,}",
        f"Total accidentes fatales (eventos SIMUR): {sum(int(r.get('siniestros_con_muertos', 0) or 0) for r in rows):,}",
        f"Total siniestros: {sum(int(r.get('cantidad_siniestros', 0) or 0) for r in rows):,}",
    ]

    loc_path = REPORTS / "ipi_por_localidad_stats.csv"
    if loc_path.exists():
        df_loc = pd.read_csv(loc_path)
        lineas += [
            "\n## Ranking de localidades (rank_localidad|localidad|n_zonas|ipi_max|ipi_medio|siniestros|muertos|zonas_p1|zonas_p2)"
        ]
        for _, row in df_loc.sort_values("rank_localidad").iterrows():
            lineas.append(
                f"{int(row['rank_localidad'])}|{row['localidad']}"
                f"|{int(row['n_zonas'])}|{row['ipi_max']:.1f}|{row['ipi_medio']:.1f}"
                f"|{int(row['siniestros_total'])}|{int(row['siniestros_muertos'])}"
                f"|{int(row['zonas_p1'])}|{int(row['zonas_p2'])}"
            )

    vias_path = REPORTS / "top_vias_criticas_geoespacial.csv"
    if vias_path.exists():
        df_vias = pd.read_csv(vias_path)
        df_vias = df_vias[df_vias["via_predominante"] != "SIN_NMG"].head(20)
        lineas += ["\n## Top 20 vías críticas (via|n_zonas|ipi_max|siniestros|muertos|criticidad)"]
        for _, row in df_vias.iterrows():
            lineas.append(
                f"{row['via_predominante']}|{int(row['n_zonas'])}|{row['ipi_max']:.1f}"
                f"|{int(row['siniestros'])}|{int(row['muertos'])}|{int(row['criticidad'])}"
            )

    barrios_path = REPORTS / "top_barrios_criticos_geoespacial.csv"
    if barrios_path.exists():
        df_bar = pd.read_csv(barrios_path).head(20)
        lineas += [
            "\n## Top 20 barrios críticos (localidad|barrio|n_zonas|ipi_max|siniestros|muertos)"
        ]
        for _, row in df_bar.iterrows():
            lineas.append(
                f"{row['localidad_predominante']}|{row['barrio_predominante']}"
                f"|{int(row['n_zonas'])}|{row['ipi_max']:.1f}"
                f"|{int(row['siniestros'])}|{int(row['muertos'])}"
            )

    nb05_path = REPORTS / "hotspots_normalizados_nb05.csv"
    if nb05_path.exists():
        df_nb05 = pd.read_csv(nb05_path)
        tip_counts = df_nb05["tipologia_nb05"].value_counts().to_dict()
        top_ocultos = df_nb05[df_nb05["tipologia_nb05"] == "Hotspot relativo oculto"].nsmallest(
            10, "rank_tasa_red"
        )[["localidad_modal_rec", "rank_vol", "rank_tasa_red", "tasa_red"]]
        lineas += [
            "\n## Tipología NB05 (normalización por exposición OSM + población)",
            "Zonas que aparecen como hotspot solo al normalizar por km de red vial:",
            f"Distribución tipologías: {tip_counts}",
            "Top 10 hotspots relativos ocultos (localidad|rank_vol|rank_tasa_red|tasa_red_x_km):",
        ]
        for _, row in top_ocultos.iterrows():
            lineas.append(
                f"{row['localidad_modal_rec']}|{int(row['rank_vol'])}|{int(row['rank_tasa_red'])}|{row['tasa_red']:.2f}"
            )

    return "\n".join(lineas)


with st.spinner("Preparando datos para el agente..."):
    ipi_texto = _cargar_ipi_resumen()

st.markdown(
    f'<div class="vs-callout">Agente listo — <b>{len(ipi_texto):,} caracteres</b> de contexto cargados con prompt caching activo.</div>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Historial ──────────────────────────────────────────────────────────────
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "pregunta_rapida" not in st.session_state:
    st.session_state.pregunta_rapida = ""

for msg in st.session_state.mensajes:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Input ──────────────────────────────────────────────────────────────────
pregunta_digita = st.chat_input("Escribe tu pregunta sobre seguridad vial en Bogotá...")
pregunta = pregunta_digita or st.session_state.pop("pregunta_rapida", "") or ""

if pregunta:
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(pregunta)

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        system_prompt = [
            {
                "type": "text",
                "text": (
                    "Eres el Analista Experto de Seguridad Vial de VíaSegura AI, "
                    "un sistema de priorización espacial de accidentalidad en Bogotá, Colombia.\n\n"
                    "REGLAS:\n"
                    "- Responde siempre en español, con lenguaje claro para tomadores de decisión.\n"
                    "- Usa los datos del dataset — cita números concretos.\n"
                    "- Para recomendaciones, clasifica: Ingeniería vial (infraestructura física), "
                    "Fiscalización (control de tránsito, semaforización), Educación vial.\n"
                    "- El IPI varía de 0 a 100; mayor = más urgente.\n"
                    "- Prioridad 1 = top 50 zonas (intervención inmediata).\n"
                    "- Gravedad: Muertos=5pts, Heridos=3pts, Solo Daños=1pt.\n"
                    "- Período base: 2016-2019 · Fuente: SIMUR Bogotá.\n"
                    "- IMPORTANTE sobre fatalidades: 'siniestros_con_muertos' cuenta EVENTOS de accidente "
                    "clasificados como CON MUERTOS en SIMUR (4,197 eventos 2016-2019), NO víctimas individuales. "
                    "SDM/ANSV reporta ~2,142 víctimas fatales confirmadas en ese período "
                    "(ratio ~2 eventos SIMUR por víctima). Al responder sobre fallecidos o víctimas fatales, "
                    "usa el término 'accidentes fatales' y aclara esta distinción si es relevante.\n"
                ),
            },
            {
                "type": "text",
                "text": ipi_texto,
                "cache_control": {"type": "ephemeral"},
            },
        ]

        messages_api = [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.mensajes
        ]

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            full_response = ""

            with client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=1500,
                system=system_prompt,
                messages=messages_api,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

            final_msg = stream.get_final_message()
            usage = final_msg.usage
            cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
            cache_created = getattr(usage, "cache_creation_input_tokens", 0) or 0
            if cache_read:
                cache_info = f" · cache activa ({cache_read:,} tokens reutilizados)"
            elif cache_created:
                cache_info = f" · cache creada ({cache_created:,} tokens)"
            else:
                cache_info = ""
            st.caption(
                f"Tokens: {usage.input_tokens:,} entrada · {usage.output_tokens:,} salida{cache_info}"
            )

        st.session_state.mensajes.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"**Error al llamar a Claude:** {e}\n\nVerifica que tu API key sea válida.")
