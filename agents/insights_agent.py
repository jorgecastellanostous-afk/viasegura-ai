"""
agents/insights_agent.py — Agente Intérprete de Resultados IPI
==============================================================
Usa la API de Claude (claude-opus-4-7, streaming + prompt caching) para generar
interpretaciones ejecutivas de los resultados del análisis IPI de VíaSegura AI.

Características:
    - Prompt caching: el CSV de IPI (~50K tokens) se cachea en el primer request.
      Llamadas subsecuentes cuestan ~10x menos en tokens de entrada.
    - Streaming: la respuesta se imprime en tiempo real.
    - Adaptive thinking: Claude razona antes de responder.

Uso:
    # Interpretación estándar (resumen ejecutivo)
    python -m agents.insights_agent

    # Pregunta específica sobre los datos
    python -m agents.insights_agent "¿Cuáles son las vías más peligrosas en Kennedy?"

    # Modo batch (varias preguntas desde un archivo .txt, una por línea)
    python -m agents.insights_agent --batch preguntas.txt

Requiere:
    ANTHROPIC_API_KEY en .env o en el entorno
"""
from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

# ── Path setup ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import REPORTS  # noqa: E402

# ── .env loader ─────────────────────────────────────────────────────────
_env = ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY no está configurada.", file=sys.stderr)
    print("Agrega ANTHROPIC_API_KEY=sk-ant-... al archivo .env del proyecto.", file=sys.stderr)
    sys.exit(1)

from anthropic import Anthropic  # noqa: E402

client = Anthropic()

# ── Modelo y configuración ───────────────────────────────────────────────
MODEL = "claude-opus-4-7"

# ── Cargar datos IPI ────────────────────────────────────────────────────

def _load_ipi_summary() -> str:
    """
    Carga el CSV de IPI y lo convierte en un bloque de texto compacto.
    Este bloque se cachea en el system prompt para todas las consultas.
    """
    ipi_path = REPORTS / "zonas_criticas_IPI_completo_2016_2019.csv"
    if not ipi_path.exists():
        raise FileNotFoundError(
            f"No se encontró {ipi_path}. Ejecuta NB02 para generarlo."
        )

    with open(ipi_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    # Top 100 por IPI (suficiente para análisis ejecutivo)
    top_rows = rows[:100]

    lines = [
        "## Dataset: Zonas Críticas IPI 2016-2019 (Top 100 de "
        + str(len(rows))
        + " zonas totales)\n",
        "Columnas: rank_IPI, IPI, prioridad_IPI, LAT_ZONA, LON_ZONA, "
        "cantidad_siniestros, criticidad_total, localidad_predominante, "
        "barrio_predominante, via_predominante, clase_predominante, "
        "anios_activos, score_volumen, score_fatalidad\n\n",
        "rank_IPI|IPI|prioridad_IPI|LAT|LON|siniestros|criticidad|localidad|"
        "barrio|via|clase|anios|score_vol|score_fat",
    ]
    for r in top_rows:
        lines.append(
            f"{r.get('rank_IPI','?')}|{float(r.get('IPI', 0)):.1f}|"
            f"{r.get('prioridad_IPI','?')}|{r.get('LAT_ZONA','?')}|"
            f"{r.get('LON_ZONA','?')}|{r.get('cantidad_siniestros','?')}|"
            f"{r.get('criticidad_total','?')}|{r.get('localidad_predominante','?')}|"
            f"{r.get('barrio_predominante','?')}|{r.get('via_predominante','?')}|"
            f"{r.get('clase_predominante','?')}|{r.get('anios_activos','?')}|"
            f"{float(r.get('score_volumen', 0)):.3f}|"
            f"{float(r.get('score_fatalidad', 0)):.3f}"
        )

    # Estadísticas globales
    def _stats(vals: list[float]) -> str:
        if not vals:
            return "N/A"
        return f"min={min(vals):.1f} max={max(vals):.1f} media={sum(vals)/len(vals):.1f}"

    all_ipi = []
    for r in rows:
        try:
            all_ipi.append(float(r["IPI"]))
        except (ValueError, KeyError):
            pass

    from collections import Counter
    prioridades = Counter(r.get("prioridad_IPI", "?") for r in rows)
    localidades = Counter(r.get("localidad_predominante", "?") for r in rows)

    summary = [
        "\n\n## Estadísticas Globales (todas las zonas)",
        f"Total zonas: {len(rows)}",
        f"IPI stats: {_stats(all_ipi)}",
        f"Distribución prioridad: {dict(prioridades)}",
        f"Top 5 localidades: {dict(localidades.most_common(5))}",
    ]
    return "\n".join(lines + summary)


# ── System prompt con caching ────────────────────────────────────────────

def _build_system_prompt(ipi_data: str) -> list[dict]:
    """
    System prompt con prompt caching habilitado en el bloque de datos IPI.
    El bloque grande (ipi_data) se marca con cache_control para que
    Anthropic lo cachee y reduzca costos en consultas subsecuentes.
    """
    return [
        {
            "type": "text",
            "text": (
                "Eres el Analista de Seguridad Vial de VíaSegura AI, un sistema de "
                "priorización espacial de accidentalidad en Bogotá, Colombia.\n\n"
                "Tu rol: interpretar los resultados del Índice de Priorización de "
                "Intervención (IPI), identificar patrones, y generar recomendaciones "
                "ejecutivas claras para tomadores de decisiones en política pública vial.\n\n"
                "Metodología IPI:\n"
                "- Combina 5 scores normalizados [0-1]: volumen (25%), criticidad_total (25%), "
                "severidad_promedio (20%), persistencia_temporal (15%), fatalidad (15%)\n"
                "- IPI ∈ [0, 100], mayor = mayor urgencia\n"
                "- Fuente: SIMUR (sig.simur.gov.co), período base 2016-2019, 260,831 registros\n\n"
                "Responde en español. Sé preciso, usa números del dataset. "
                "Para recomendaciones, distingue entre intervención física (ingeniería vial), "
                "fiscalización (control de tránsito) y educación vial.\n"
            ),
        },
        {
            "type": "text",
            "text": ipi_data,
            # Prompt cache — este bloque se almacena ~5 min en Anthropic
            "cache_control": {"type": "ephemeral"},
        },
    ]


# ── Consulta con streaming ───────────────────────────────────────────────

def consultar(
    pregunta: str,
    ipi_data: str | None = None,
    *,
    verbose: bool = True,
) -> str:
    """
    Envía una pregunta al agente con streaming.
    Retorna el texto completo de la respuesta.

    Args:
        pregunta: Pregunta en lenguaje natural sobre los datos IPI.
        ipi_data: Datos IPI pre-cargados (se carga automáticamente si es None).
        verbose: Si True, imprime la respuesta en tiempo real.

    Returns:
        Texto completo de la respuesta de Claude.
    """
    if ipi_data is None:
        ipi_data = _load_ipi_summary()

    system = _build_system_prompt(ipi_data)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Pregunta: {pregunta}")
        print(f"{'='*60}")
        print("Respuesta:\n")

    full_text = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": pregunta}],
    ) as stream:
        for text in stream.text_stream:
            if verbose:
                print(text, end="", flush=True)
            full_text += text

    if verbose:
        print("\n")

        # Mostrar info de uso (caching)
        msg = stream.get_final_message()
        usage = msg.usage
        print(f"[Tokens] input={usage.input_tokens} output={usage.output_tokens}", end="")
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        cache_created = getattr(usage, "cache_creation_input_tokens", 0) or 0
        if cache_read or cache_created:
            print(
                f" | cache_read={cache_read} cache_created={cache_created}",
                end="",
            )
        print()

    return full_text


# ── Consultas predefinidas (resumen ejecutivo) ───────────────────────────

PREGUNTAS_EJECUTIVAS = [
    (
        "resumen_ejecutivo",
        (
            "Genera un resumen ejecutivo (máx 300 palabras) de los hallazgos clave del "
            "análisis IPI 2016-2019: localidades más críticas, tipo de accidentes dominante, "
            "y las 3 zonas de intervención más urgente con su justificación."
        ),
    ),
    (
        "recomendaciones",
        (
            "Basándote en las zonas Prioridad 1 (top 50), proporciona 5 recomendaciones "
            "concretas para el equipo de Secretaría de Movilidad de Bogotá: "
            "distingue entre medidas de ingeniería vial, fiscalización y educación."
        ),
    ),
    (
        "patrones_temporales",
        (
            "Identifica si hay patrones de persistencia temporal en las zonas críticas: "
            "¿qué porcentaje de las zonas Prioridad 1 estuvo activo los 4 años del período base? "
            "¿Qué sugiere esto sobre la naturaleza del riesgo?"
        ),
    ),
]


def run_executive_report(output_path: Path | None = None) -> None:
    """
    Ejecuta las 3 consultas ejecutivas predefinidas y opcionalmente guarda el reporte.
    Aprovecha el prompt caching: datos IPI se cargan 1 sola vez.
    """
    print("Cargando datos IPI...", flush=True)
    ipi_data = _load_ipi_summary()
    print(f"Datos cargados: {len(ipi_data):,} caracteres\n")

    results: dict[str, str] = {}
    for nombre, pregunta in PREGUNTAS_EJECUTIVAS:
        results[nombre] = consultar(pregunta, ipi_data, verbose=True)
        time.sleep(0.5)  # pequeña pausa entre requests

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Reporte Ejecutivo IPI — VíaSegura AI\n\n")
            for nombre, texto in results.items():
                f.write(f"## {nombre.replace('_', ' ').title()}\n\n")
                f.write(texto)
                f.write("\n\n---\n\n")
        print(f"\nReporte guardado en: {output_path}")


# ── CLI ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Agente intérprete de resultados IPI — VíaSegura AI"
    )
    parser.add_argument(
        "pregunta",
        nargs="?",
        default="",
        help="Pregunta sobre los datos IPI (opcional; sin argumento → reporte ejecutivo)",
    )
    parser.add_argument(
        "--batch",
        metavar="ARCHIVO",
        help="Archivo .txt con una pregunta por línea",
    )
    parser.add_argument(
        "--output",
        metavar="ARCHIVO",
        help="Guardar reporte en este archivo .md",
    )
    args = parser.parse_args()

    if args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"ERROR: No existe {batch_path}", file=sys.stderr)
            sys.exit(1)
        preguntas = [
            line.strip()
            for line in batch_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        ipi_data = _load_ipi_summary()
        for pregunta in preguntas:
            consultar(pregunta, ipi_data, verbose=True)
            time.sleep(0.5)

    elif args.pregunta:
        consultar(args.pregunta, verbose=True)

    else:
        # Modo reporte ejecutivo completo
        output = Path(args.output) if args.output else REPORTS / "reporte_ejecutivo_IPI.md"
        run_executive_report(output_path=output)
