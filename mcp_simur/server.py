"""
mcp_simur/server.py — MCP Server para SIMUR ArcGIS FeatureServer
=================================================================
Expone los datos de accidentalidad vial de Bogotá (SIMUR) como herramientas
MCP que Claude puede invocar directamente desde Claude Code o cualquier
cliente MCP compatible.

Instalación y uso:
    # Instalar dependencia
    pip install mcp

    # Correr el servidor (stdio transport — compatible con Claude Code)
    python -m mcp_simur.server

    # O bien registrar en claude_desktop_config.json / claude_code_config:
    {
      "mcpServers": {
        "simur": {
          "command": "python",
          "args": ["-m", "mcp_simur.server"],
          "cwd": "C:/Users/jorge/Documents/viasegura_ai"
        }
      }
    }

Herramientas expuestas:
    - simur_contar_registros      → COUNT por año (auditoría rápida)
    - simur_descargar_muestra     → Primeros N registros con filtros
    - simur_localidades_activas   → Lista localidades únicas de un año
    - simur_estadisticas_zona     → Stats de una zona lat/lon dada
    - ipi_top_zonas               → Top N zonas del CSV de IPI ya calculado
    - ipi_resumen_ejecutivo       → Resumen global del IPI para Claude
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import requests

# ── Agregar raíz al path para importar config ──────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import REPORTS  # noqa: E402

# ── Constantes SIMUR ───────────────────────────────────────────────────────
SIMUR_URL = (
    "https://sig.simur.gov.co/arcgis/rest/services/"
    "Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query"
)
TIMEOUT_S = 30
DEFAULT_CHUNK = 500

# ── Importar MCP ───────────────────────────────────────────────────────────
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    print(
        "ERROR: El paquete 'mcp' no está instalado.\n"
        "Instálalo con:  pip install mcp\n"
        f"Detalle: {exc}",
        file=sys.stderr,
    )
    sys.exit(1)

mcp = FastMCP(
    name="viasegura-simur",
    version="1.0.0",
    description=(
        "Herramientas para consultar los datos de accidentalidad vial de Bogotá "
        "del portal SIMUR (sig.simur.gov.co) y los índices IPI ya calculados."
    ),
)


# ═══════════════════════════════════════════════════════════════════════════
# Helpers internos
# ═══════════════════════════════════════════════════════════════════════════

def _simur_get(params: dict[str, Any]) -> dict:
    """GET al FeatureServer de SIMUR con manejo de errores."""
    defaults = {
        "f": "json",
        "outFields": "*",
        "returnGeometry": "false",
    }
    resp = requests.get(SIMUR_URL, params={**defaults, **params}, timeout=TIMEOUT_S)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"SIMUR API error: {data['error']}")
    return data


def _where_anio(anio: int) -> str:
    return f"ANIO_ACCIDENTE = {anio}"


def _load_ipi_csv() -> list[dict]:
    """Carga el CSV de IPI completo y lo retorna como lista de dicts."""
    ipi_path = REPORTS / "zonas_criticas_IPI_completo_2016_2019.csv"
    if not ipi_path.exists():
        raise FileNotFoundError(
            f"CSV de IPI no encontrado en {ipi_path}. "
            "Ejecuta NB02 para generarlo."
        )
    import csv
    with open(ipi_path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ═══════════════════════════════════════════════════════════════════════════
# Herramientas MCP
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def simur_contar_registros(anio: int) -> str:
    """
    Cuenta cuántos registros de accidentalidad hay en SIMUR para el año dado.
    Útil para auditoría rápida de integridad sin descargar datos.

    Args:
        anio: Año a consultar (ej. 2023).

    Returns:
        JSON con el conteo de registros.
    """
    data = _simur_get({
        "where": _where_anio(anio),
        "returnCountOnly": "true",
    })
    count = data.get("count", 0)
    return json.dumps({"anio": anio, "total_registros": count})


@mcp.tool()
def simur_descargar_muestra(
    anio: int,
    n: int = 100,
    where_extra: str = "1=1",
) -> str:
    """
    Descarga una muestra de registros de SIMUR para un año.
    No descarga el dataset completo (usa simur_contar_registros primero).

    Args:
        anio: Año de los accidentes (ej. 2023).
        n: Número de registros a retornar (máx 1000).
        where_extra: Cláusula WHERE adicional en SQL (ej. "CLASE_ACCIDENTE='CHOQUE'").

    Returns:
        JSON con lista de registros y campos disponibles.
    """
    n = min(n, 1000)
    where = f"({_where_anio(anio)}) AND ({where_extra})"
    data = _simur_get({
        "where": where,
        "resultRecordCount": n,
        "orderByFields": "OBJECTID DESC",
    })
    features = data.get("features", [])
    records = [f["attributes"] for f in features]
    fields = list(records[0].keys()) if records else []
    return json.dumps({
        "anio": anio,
        "n_retornados": len(records),
        "campos": fields,
        "registros": records,
    }, ensure_ascii=False, default=str)


@mcp.tool()
def simur_localidades_activas(anio: int) -> str:
    """
    Retorna las localidades de Bogotá con al menos 1 accidente registrado en SIMUR
    para el año dado, junto con el conteo por localidad.

    Args:
        anio: Año a consultar.

    Returns:
        JSON con lista de {localidad, cantidad_siniestros}.
    """
    data = _simur_get({
        "where": _where_anio(anio),
        "groupByFieldsForStatistics": "LOCALIDAD_ACCIDENTE",
        "outStatistics": json.dumps([{
            "statisticType": "count",
            "onStatisticField": "OBJECTID",
            "outStatisticFieldName": "cantidad_siniestros",
        }]),
        "orderByFields": "cantidad_siniestros DESC",
    })
    features = data.get("features", [])
    localidades = [f["attributes"] for f in features]
    return json.dumps({
        "anio": anio,
        "n_localidades": len(localidades),
        "localidades": localidades,
    }, ensure_ascii=False)


@mcp.tool()
def simur_estadisticas_zona(lat: float, lon: float, radio_grados: float = 0.003) -> str:
    """
    Retorna estadísticas de accidentalidad para una zona geográfica
    centrada en (lat, lon) con un radio aproximado en grados decimales.
    0.001 grado ≈ 111 metros. Default: 0.003 ≈ 330 metros.

    Args:
        lat: Latitud del centro (ej. 4.602 para Centro Bogotá).
        lon: Longitud del centro (ej. -74.081).
        radio_grados: Radio de la zona en grados decimales.

    Returns:
        JSON con conteo total, desglose por clase y gravedad.
    """
    lat_min = lat - radio_grados
    lat_max = lat + radio_grados
    lon_min = lon - radio_grados
    lon_max = lon + radio_grados

    where = (
        f"LATITUD_ACCIDENTE >= {lat_min} AND LATITUD_ACCIDENTE <= {lat_max} "
        f"AND LONGITUD_ACCIDENTE >= {lon_min} AND LONGITUD_ACCIDENTE <= {lon_max}"
    )

    # Conteo total
    total_data = _simur_get({"where": where, "returnCountOnly": "true"})
    total = total_data.get("count", 0)

    # Desglose por gravedad
    grav_data = _simur_get({
        "where": where,
        "groupByFieldsForStatistics": "GRAVEDAD_ACCIDENTE",
        "outStatistics": json.dumps([{
            "statisticType": "count",
            "onStatisticField": "OBJECTID",
            "outStatisticFieldName": "n",
        }]),
    })
    gravedad = [f["attributes"] for f in grav_data.get("features", [])]

    # Desglose por clase
    clase_data = _simur_get({
        "where": where,
        "groupByFieldsForStatistics": "CLASE_ACCIDENTE",
        "outStatistics": json.dumps([{
            "statisticType": "count",
            "onStatisticField": "OBJECTID",
            "outStatisticFieldName": "n",
        }]),
    })
    clase = [f["attributes"] for f in clase_data.get("features", [])]

    return json.dumps({
        "lat": lat, "lon": lon, "radio_grados": radio_grados,
        "total_accidentes_historico": total,
        "por_gravedad": gravedad,
        "por_clase": clase,
    }, ensure_ascii=False)


@mcp.tool()
def ipi_top_zonas(n: int = 20, prioridad: str = "") -> str:
    """
    Retorna las N zonas con mayor Índice de Prioridad de Intervención (IPI)
    del análisis histórico 2016-2019.

    Args:
        n: Número de zonas a retornar (máx 500, default 20).
        prioridad: Filtrar por prioridad: "Prioridad 1", "Prioridad 2",
                   "Prioridad 3" o "" para todas.

    Returns:
        JSON con lista de zonas ordenadas por IPI descendente.
    """
    n = min(n, 500)
    rows = _load_ipi_csv()

    # Filtrar por prioridad si se pide
    if prioridad:
        rows = [r for r in rows if prioridad.lower() in r.get("prioridad_IPI", "").lower()]

    # Ordenar por IPI descendente (ya viene ordenado, pero por si acaso)
    def _ipi_val(r: dict) -> float:
        try:
            return float(r.get("IPI", 0))
        except (ValueError, TypeError):
            return 0.0

    rows_sorted = sorted(rows, key=_ipi_val, reverse=True)[:n]

    # Seleccionar columnas clave
    campos = [
        "rank_IPI", "IPI", "prioridad_IPI", "LAT_ZONA", "LON_ZONA",
        "cantidad_siniestros", "criticidad_total", "localidad_predominante",
        "barrio_predominante", "via_predominante", "clase_predominante",
        "anios_activos", "tipo_hotspot", "score_volumen", "score_fatalidad",
    ]
    result = []
    for r in rows_sorted:
        result.append({k: r.get(k, "") for k in campos})

    return json.dumps({
        "n_zonas": len(result),
        "filtro_prioridad": prioridad or "todas",
        "zonas": result,
    }, ensure_ascii=False)


@mcp.tool()
def ipi_resumen_ejecutivo() -> str:
    """
    Genera un resumen ejecutivo del análisis IPI 2016-2019:
    total de zonas, distribución por prioridad, localidades más críticas,
    y estadísticas globales. Listo para usar como contexto en prompts.

    Returns:
        JSON con métricas ejecutivas del IPI.
    """
    rows = _load_ipi_csv()

    total_zonas = len(rows)

    # Distribución por prioridad
    from collections import Counter
    prioridades = Counter(r.get("prioridad_IPI", "Sin clasificar") for r in rows)

    # Localidades más críticas (top 5)
    localidad_count: dict[str, int] = {}
    for r in rows:
        loc = r.get("localidad_predominante", "")
        if loc:
            localidad_count[loc] = localidad_count.get(loc, 0) + 1
    top_localidades = sorted(localidad_count.items(), key=lambda x: x[1], reverse=True)[:5]

    # Estadísticas IPI
    ipi_vals = []
    for r in rows:
        try:
            ipi_vals.append(float(r["IPI"]))
        except (ValueError, TypeError, KeyError):
            pass

    import statistics
    stats_ipi = {
        "min": round(min(ipi_vals), 2) if ipi_vals else None,
        "max": round(max(ipi_vals), 2) if ipi_vals else None,
        "media": round(statistics.mean(ipi_vals), 2) if ipi_vals else None,
        "mediana": round(statistics.median(ipi_vals), 2) if ipi_vals else None,
    }

    # Top 3 zonas
    top3 = []
    for r in rows[:3]:
        top3.append({
            "rank": r.get("rank_IPI"),
            "IPI": r.get("IPI"),
            "localidad": r.get("localidad_predominante"),
            "barrio": r.get("barrio_predominante"),
            "via": r.get("via_predominante"),
            "siniestros": r.get("cantidad_siniestros"),
        })

    return json.dumps({
        "periodo_base": "2016-2019",
        "total_zonas_analizadas": total_zonas,
        "distribucion_prioridad": dict(prioridades),
        "top5_localidades_criticas": [
            {"localidad": loc, "n_zonas": n} for loc, n in top_localidades
        ],
        "estadisticas_IPI": stats_ipi,
        "top3_zonas": top3,
        "fuente_datos": "SIMUR - sig.simur.gov.co",
        "metodologia": (
            "IPI = combinación lineal normalizada de 5 scores: "
            "volumen (25%), criticidad_total (25%), severidad_promedio (20%), "
            "persistencia_temporal (15%), fatalidad (15%)"
        ),
    }, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# Recursos MCP (contexto estático que Claude puede leer)
# ═══════════════════════════════════════════════════════════════════════════

@mcp.resource("simur://metodologia")
def resource_metodologia() -> str:
    """Documentación de la metodología IPI para que Claude tenga contexto."""
    return """# Metodología IPI — VíaSegura AI

## Fuente de datos
- Portal SIMUR: sig.simur.gov.co
- Endpoint: FeatureServer/2 (Accidentalidad Análisis)
- Período base: 2016-2019 → 260,831 registros

## Índice de Prioridad de Intervención (IPI)
Combina 5 scores normalizados [0-1] por zona geográfica (~100m x 100m):

| Score               | Peso | Descripción                                   |
|---------------------|------|-----------------------------------------------|
| score_volumen        | 25%  | Cantidad total de siniestros en la zona        |
| score_criticidad     | 25%  | Suma de puntajes de gravedad (Daños=1, Heridos=3, Muertos=5) |
| score_severidad      | 20%  | Criticidad promedio por siniestro              |
| score_persistencia   | 15%  | Años activos de los 4 del período base        |
| score_fatalidad      | 15%  | Siniestros con muertos                        |

IPI ∈ [0, 100], mayor = mayor urgencia de intervención.

## Clasificación de prioridad
- Prioridad 1: Top 50 zonas por IPI → Intervención inmediata
- Prioridad 2: Top 51-200 → Auditoría de seguridad vial
- Prioridad 3: Top 201-500 → Monitoreo periódico

## Localidades más críticas (histórico 2016-2019)
Kennedy, Engativá, Suba, Usaquén, Fontibón
"""


@mcp.resource("simur://estructura-campos")
def resource_campos() -> str:
    """Campos disponibles en el FeatureServer de SIMUR."""
    return json.dumps({
        "campos_principales": [
            "OBJECTID", "ANIO_ACCIDENTE", "MES_ACCIDENTE",
            "DIA_ACCIDENTE", "HORA_ACCIDENTE",
            "CLASE_ACCIDENTE",        # CHOQUE, ATROPELLO, CAIDA, VOLCAMIENTO, etc.
            "GRAVEDAD_ACCIDENTE",     # CON HERIDOS, CON MUERTOS, SOLO DAÑOS
            "LOCALIDAD_ACCIDENTE",    # Nombre de localidad
            "BARRIO_ACCIDENTE",       # Nombre de barrio
            "VIA_ACCIDENTE",          # Nombre de vía
            "LATITUD_ACCIDENTE",      # Coordenada decimal
            "LONGITUD_ACCIDENTE",     # Coordenada decimal
        ],
        "valores_gravedad": ["CON HERIDOS", "CON MUERTOS", "SOLO DAÑOS"],
        "valores_clase": ["CHOQUE", "ATROPELLO", "CAIDA OCUPANTE", "VOLCAMIENTO",
                          "INCENDIO", "OTRO"],
        "nota": "Los campos exactos pueden variar. Usa simur_descargar_muestra para ver los campos reales.",
    }, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Stdio transport — compatible con Claude Code y Claude Desktop
    mcp.run(transport="stdio")
