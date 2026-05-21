"""
Página 4 — Agente IA
Chat con Claude (Opus 4.7) sobre los datos IPI de Bogotá.
Usa prompt caching para no re-enviar el CSV en cada mensaje.
La API key se puede ingresar directamente en la barra lateral.
"""
import sys, os
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

from app.styles import inject_global_css
inject_global_css()

# ── API Key (sidebar primero) ────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 Configuración")
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
    st.markdown("### 💡 Preguntas sugeridas")
    sugeridas = [
        "¿Cuáles son las 3 zonas más urgentes y por qué?",
        "¿Qué localidades tienen más fallecidos?",
        "Dame recomendaciones para Kennedy",
        "¿Qué tipo de accidentes predomina en Prioridad 1?",
        "¿Cuáles vías necesitan intervención de ingeniería?",
        "Resume los hallazgos en 5 puntos para una presentación",
    ]
    for q in sugeridas:
        if st.button(q, use_container_width=True, key=f"sug_{q[:20]}"):
            st.session_state.pregunta_rapida = q

    st.markdown("---")
    if st.button("🗑️ Limpiar chat", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

# ── Header ───────────────────────────────────────────────────────────────
st.markdown('<p class="vs-page-title">Agente Intérprete de Seguridad Vial</p>', unsafe_allow_html=True)
st.markdown(
    "Pregúntale a **Claude Haiku 4.5** sobre el análisis IPI de Bogotá 2016-2019. "
    "El agente tiene acceso completo a las 17,130 zonas analizadas."
)

if not api_key:
    st.warning(
        "**Ingresa tu Anthropic API Key** en la barra lateral para activar el agente.\n\n"
        "Puedes obtenerla en [console.anthropic.com](https://console.anthropic.com) "
        "— o agrega `ANTHROPIC_API_KEY=sk-ant-...` al archivo `.env` del proyecto."
    )
    st.stop()

# ── Cargar resumen IPI (cacheado) ─────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _cargar_ipi_resumen() -> str:
    import csv
    from config import REPORTS
    ipi_path = REPORTS / "zonas_criticas_IPI_completo_2016_2019.csv"
    with open(ipi_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    top = rows[:100]
    encabezado = (
        "## Dataset: Zonas Críticas IPI Bogotá 2016-2019\n"
        f"Total zonas analizadas: {len(rows):,}\n"
        "Top 100 por IPI (formato compacto pipe-separado):\n\n"
        "rank|IPI|prioridad|lat|lon|siniestros|criticidad|localidad|barrio|via|clase|anios|score_vol|score_fat\n"
    )
    lineas = [encabezado]
    for r in top:
        lineas.append(
            f"{r.get('rank_IPI','?')}|{float(r.get('IPI',0)):.1f}"
            f"|{r.get('prioridad_IPI','?').split(' - ')[0]}"
            f"|{r.get('LAT_ZONA','?')}|{r.get('LON_ZONA','?')}"
            f"|{r.get('cantidad_siniestros','?')}|{r.get('criticidad_total','?')}"
            f"|{r.get('localidad_predominante','?')}|{r.get('barrio_predominante','?')}"
            f"|{r.get('via_predominante','?')}|{r.get('clase_predominante','?')}"
            f"|{r.get('anios_activos','?')}"
            f"|{float(r.get('score_volumen',0)):.3f}|{float(r.get('score_fatalidad',0)):.3f}"
        )

    from collections import Counter
    import statistics
    ipi_vals = [float(r["IPI"]) for r in rows if r.get("IPI")]
    prioridades = Counter(r.get("prioridad_IPI","?").split(" - ")[0] for r in rows)
    localidades = Counter(r.get("localidad_predominante","?") for r in rows)

    lineas += [
        "\n## Estadísticas globales",
        f"IPI: min={min(ipi_vals):.1f} max={max(ipi_vals):.1f} media={statistics.mean(ipi_vals):.1f}",
        f"Prioridades: {dict(prioridades)}",
        f"Top 5 localidades por n° de zonas: {dict(localidades.most_common(5))}",
        f"Zonas activas 4 años: {sum(1 for r in rows if r.get('anios_activos')=='4'):,}",
        f"Total fallecidos (suma): {sum(int(r.get('siniestros_con_muertos',0) or 0) for r in rows):,}",
        f"Total siniestros (suma): {sum(int(r.get('cantidad_siniestros',0) or 0) for r in rows):,}",
    ]
    return "\n".join(lineas)


with st.spinner("Preparando datos para el agente..."):
    ipi_texto = _cargar_ipi_resumen()

st.success(f"✅ Agente listo — {len(ipi_texto):,} caracteres de contexto cargados")
st.markdown("---")

# ── Historial ─────────────────────────────────────────────────────────────
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "pregunta_rapida" not in st.session_state:
    st.session_state.pregunta_rapida = ""

# Mostrar historial
for msg in st.session_state.mensajes:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Capturar pregunta (input normal o botón lateral) ─────────────────────
pregunta_digita = st.chat_input("Escribe tu pregunta sobre seguridad vial en Bogotá...")

pregunta = pregunta_digita or st.session_state.pop("pregunta_rapida", "") or ""

if pregunta:
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(pregunta)

    # ── Llamar a Claude ───────────────────────────────────────────────────
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
                ),
            },
            {
                "type": "text",
                "text": ipi_texto,
                "cache_control": {"type": "ephemeral"},
            },
        ]

        messages_api = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.mensajes
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

            # Info de tokens
            final_msg = stream.get_final_message()
            usage = final_msg.usage
            cache_read    = getattr(usage, "cache_read_input_tokens", 0) or 0
            cache_created = getattr(usage, "cache_creation_input_tokens", 0) or 0
            ahorro = f" · 🟢 caché activa ({cache_read:,} tokens reutilizados)" if cache_read else \
                     f" · ⏳ caché creada ({cache_created:,} tokens)" if cache_created else ""
            st.caption(f"Tokens: {usage.input_tokens:,} entrada · {usage.output_tokens:,} salida{ahorro}")

        st.session_state.mensajes.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"**Error al llamar a Claude:** {e}\n\nVerifica que tu API key sea válida.")
