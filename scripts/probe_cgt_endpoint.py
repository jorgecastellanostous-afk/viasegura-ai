"""
Probe CGT (Conteo Vehicular) endpoints — VíaSegura AI
Tarea: verificar disponibilidad de datos TPDA reales para calibración NB06
"""

import sys
import json
import time
import requests
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────

ENDPOINTS = [
    {
        "name": "ArcGIS CGT SDM",
        "url": (
            "https://services2.arcgis.com/NEwhEo9GGSHXcRXV/arcgis/rest/services/"
            "Conteo_Vehiculos_CGT_Bogot%C3%A1_D_C/FeatureServer/0/query"
        ),
        "params": {
            "where": "1=1",
            "outFields": "*",
            "f": "geojson",
            "resultRecordCount": 2000,   # cap por si hay miles
        },
    },
    {
        "name": "Datos Abiertos Bogotá (CKAN datastore)",
        "url": "https://datosabiertos.bogota.gov.co/api/3/action/datastore_search",
        "params": {
            "resource_id": "018087c3f2ef4df4895ec5027561eea7",
            "limit": 100,
        },
    },
    {
        "name": "datos.gov.co Socrata",
        "url": "https://www.datos.gov.co/resource/8ew9-bhy7.json",
        "params": {"$limit": 100},
    },
]

TPDA_KEYWORDS = [
    "TPDA", "TPD", "VOLUMEN", "CONTEO", "TOTAL", "AFORO",
    "VEHICULOS", "V_", "FLUJO", "IMD", "ADT", "COUNT",
]

PESOS_NB06 = {
    "motorway":     120_000,
    "trunk":         90_000,
    "primary":       50_000,
    "secondary":     20_000,
    "tertiary":       8_000,
    "residential":    2_500,
    "unclassified":   2_000,
}

TIMEOUT = 15


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def is_volume_field(name: str) -> bool:
    n = name.upper()
    return any(kw in n for kw in TPDA_KEYWORDS)


def probe_endpoint(ep: dict) -> dict:
    result = {"name": ep["name"], "url": ep["url"], "ok": False}
    try:
        t0 = time.time()
        resp = requests.get(ep["url"], params=ep.get("params", {}), timeout=TIMEOUT)
        elapsed = round(time.time() - t0, 2)
        result["http_status"] = resp.status_code
        result["elapsed_s"] = elapsed

        if resp.status_code != 200:
            result["error"] = f"HTTP {resp.status_code}"
            return result

        try:
            data = resp.json()
        except Exception as e:
            result["error"] = f"JSON parse error: {e}"
            result["raw_preview"] = resp.text[:500]
            return result

        result["ok"] = True
        result["raw"] = data
        return result

    except requests.exceptions.Timeout:
        result["error"] = f"Timeout after {TIMEOUT}s"
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"ConnectionError: {e}"
    except Exception as e:
        result["error"] = f"Unexpected: {e}"
    return result


def parse_arcgis_geojson(data: dict) -> dict:
    """Parse ArcGIS GeoJSON FeatureServer response."""
    out = {}
    features = data.get("features", [])
    out["n_features"] = len(features)

    if not features:
        out["columns"] = []
        return out

    # Columnas
    props0 = features[0].get("properties", {})
    out["columns"] = list(props0.keys())
    out["volume_columns"] = [c for c in out["columns"] if is_volume_field(c)]

    # Geometry type
    geom0 = features[0].get("geometry")
    if geom0:
        out["geometry_type"] = geom0.get("type")
        coords = geom0.get("coordinates", [])
        if geom0["type"] == "Point" and len(coords) >= 2:
            out["sample_coord"] = coords
    else:
        out["geometry_type"] = None

    # Sample records (3–5)
    sample = []
    for f in features[:5]:
        p = f.get("properties", {})
        row = {c: p.get(c) for c in (out["volume_columns"] + out["columns"][:8])}
        # add coord
        g = f.get("geometry")
        if g and g.get("type") == "Point":
            row["_lon"] = g["coordinates"][0]
            row["_lat"] = g["coordinates"][1]
        sample.append(row)
    out["sample"] = sample

    # Rango de volumen
    if out["volume_columns"]:
        vc = out["volume_columns"][0]
        vals = []
        for f in features:
            v = f.get("properties", {}).get(vc)
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                pass
        if vals:
            out["volume_stats"] = {
                "column": vc,
                "min": min(vals),
                "max": max(vals),
                "mean": round(sum(vals) / len(vals), 1),
                "n_valid": len(vals),
            }

    return out


def parse_ckan(data: dict) -> dict:
    out = {}
    records = data.get("result", {}).get("records", [])
    out["n_records"] = len(records)
    if not records:
        out["columns"] = []
        return out
    out["columns"] = list(records[0].keys())
    out["volume_columns"] = [c for c in out["columns"] if is_volume_field(c)]
    out["sample"] = records[:5]
    return out


def parse_socrata(data) -> dict:
    out = {}
    if isinstance(data, list):
        out["n_records"] = len(data)
        if data:
            out["columns"] = list(data[0].keys())
            out["volume_columns"] = [c for c in out["columns"] if is_volume_field(c)]
            out["sample"] = data[:5]
        else:
            out["columns"] = []
    else:
        out["error"] = "Unexpected format"
    return out


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("PROBE CGT ENDPOINTS — VíaSegura AI")
    print("=" * 70)

    results = []
    parsed = None
    source_name = None

    for i, ep in enumerate(ENDPOINTS):
        print(f"\n[{i+1}/{len(ENDPOINTS)}] Probando: {ep['name']}")
        print(f"    URL: {ep['url']}")
        r = probe_endpoint(ep)
        results.append(r)

        if r["ok"]:
            print(f"    OK — HTTP {r.get('http_status')} en {r.get('elapsed_s')}s")
            # Parse según fuente
            if i == 0:
                parsed = parse_arcgis_geojson(r["raw"])
            elif i == 1:
                parsed = parse_ckan(r["raw"])
            else:
                parsed = parse_socrata(r["raw"])
            source_name = ep["name"]
            print(f"    Registros/features: {parsed.get('n_features', parsed.get('n_records', '?'))}")
            break
        else:
            print(f"    FALLO — {r.get('error')}")

    print("\n" + "=" * 70)
    print("RESULTADO DEL PROBE")
    print("=" * 70)

    if parsed is None:
        print("\nTODOS LOS ENDPOINTS FALLARON")
        for r in results:
            print(f"  {r['name']}: {r.get('error')}")
        print("\nIMPLICACIONES PARA NB06:")
        print("  No es posible calibrar con datos CGT reales.")
        print("  Se recomienda usar los pesos proxy NB06 actuales con disclaimer.")
        sys.exit(0)

    print(f"\nFUENTE EXITOSA: {source_name}")
    n = parsed.get("n_features", parsed.get("n_records", 0))
    print(f"Registros/features: {n}")
    print(f"Tipo de geometría:  {parsed.get('geometry_type', 'N/A')}")
    if "sample_coord" in parsed:
        print(f"Coord muestra:      {parsed['sample_coord']}")

    print(f"\nTOTAL COLUMNAS: {len(parsed.get('columns', []))}")
    print("Todas las columnas:")
    for c in parsed.get("columns", []):
        marker = " <-- VOLUMEN/TPDA" if is_volume_field(c) else ""
        print(f"  {c}{marker}")

    vcols = parsed.get("volume_columns", [])
    print(f"\nCOLUMNAS DE VOLUMEN IDENTIFICADAS ({len(vcols)}): {vcols}")

    if "volume_stats" in parsed:
        vs = parsed["volume_stats"]
        print(f"\nESTADÍSTICAS COLUMNA '{vs['column']}':")
        print(f"  Min:    {vs['min']:,.0f} veh/día")
        print(f"  Max:    {vs['max']:,.0f} veh/día")
        print(f"  Media:  {vs['mean']:,.0f} veh/día")
        print(f"  N válidos: {vs['n_valid']}")

    print("\nSAMPLE DE REGISTROS (primeros 5):")
    for j, row in enumerate(parsed.get("sample", [])[:5]):
        print(f"  [{j+1}] {json.dumps(row, ensure_ascii=False, default=str)}")

    # ─────────────────────────────────────────────────────────────────────────
    # ANÁLISIS OSM + CALIBRACIÓN
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ANÁLISIS DE CALIBRACIÓN NB06")
    print("=" * 70)

    features_raw = None
    for r in results:
        if r["ok"] and r.get("name") == "ArcGIS CGT SDM":
            features_raw = r["raw"].get("features", [])
            break

    if features_raw and parsed.get("volume_columns"):
        try:
            analyze_calibration(features_raw, parsed["volume_columns"][0])
        except Exception as e:
            print(f"  Error en análisis de calibración: {e}")
            import traceback
            traceback.print_exc()
    else:
        analyze_calibration_no_data(parsed)


def analyze_calibration(features: list, vol_col: str):
    """Intenta cruzar puntos CGT con tipos OSM via osmnx."""
    try:
        import osmnx as ox
        import networkx as nx
        import numpy as np
        OSMNX_OK = True
        print(f"\nosmnx disponible: v{ox.__version__}")
    except ImportError:
        OSMNX_OK = False
        print("\nosmnx NO disponible en este entorno — análisis estadístico directo")

    # Extraer coordenadas y volúmenes
    stations = []
    for f in features:
        g = f.get("geometry", {})
        p = f.get("properties", {})
        if g and g.get("type") == "Point":
            lon, lat = g["coordinates"][0], g["coordinates"][1]
            vol = p.get(vol_col)
            try:
                vol = float(vol)
            except (TypeError, ValueError):
                vol = None
            if vol is not None and vol > 0:
                # Intentar identificar tipo de vía desde los atributos
                tipo = infer_road_type_from_props(p)
                stations.append({"lon": lon, "lat": lat, "vol": vol, "tipo_inferred": tipo, "props": p})

    print(f"\nEstaciones con coordenadas y volumen válido: {len(stations)}")

    if not stations:
        print("Sin estaciones válidas para calibración.")
        return

    # Mostrar distribución de tipos inferidos
    from collections import Counter
    tipos = Counter(s["tipo_inferred"] for s in stations)
    print("\nTipos de vía inferidos de atributos CGT:")
    for t, c in tipos.most_common():
        print(f"  {t}: {c} estaciones")

    if OSMNX_OK:
        run_osmnx_calibration(stations, vol_col)
    else:
        run_stat_calibration(stations)


def infer_road_type_from_props(props: dict) -> str:
    """Intenta inferir tipo OSM desde campos descriptivos CGT."""
    # Campos comunes en datos SDM/CGT
    for field in ["TIPO_VIA", "TIPO VIA", "CLASE_VIA", "CLASE VIA", "JERARQUIA",
                  "CATEGORIA", "NOMBRE_VIA", "VIA", "TIPO", "CLASE"]:
        val = props.get(field, props.get(field.replace(" ", "_"), ""))
        if not val:
            continue
        val_upper = str(val).upper()
        # Mapeo heurístico
        if any(k in val_upper for k in ["AUTOPISTA", "BORDE", "CIRCUNVALAR"]):
            return "motorway"
        if any(k in val_upper for k in ["ARTERIAL", "PRINCIPAL", "PRIMARIA"]):
            return "primary"
        if any(k in val_upper for k in ["COLECTORA", "SECUNDARIA"]):
            return "secondary"
        if any(k in val_upper for k in ["LOCAL", "RESIDENCIAL"]):
            return "residential"
        if any(k in val_upper for k in ["TRONCAL", "NACIONAL", "EXPRES"]):
            return "trunk"
    return "unknown"


def run_osmnx_calibration(stations: list, vol_col: str):
    """Usa osmnx para encontrar tipo OSM más cercano a cada estación CGT."""
    import osmnx as ox
    import numpy as np

    lats = [s["lat"] for s in stations]
    lons = [s["lon"] for s in stations]
    bbox_lat = (min(lats) - 0.01, max(lats) + 0.01)
    bbox_lon = (min(lons) - 0.01, max(lons) + 0.01)

    print(f"\nDescargando red OSM para bbox: lat={bbox_lat}, lon={bbox_lon}")
    print("(Esto puede tardar 30-60s...)")

    try:
        G = ox.graph_from_bbox(
            bbox=(bbox_lon[0], bbox_lat[0], bbox_lon[1], bbox_lat[1]),
            network_type="drive",
        )
        nodes, edges = ox.graph_to_gdfs(G)
        print(f"Red descargada: {len(edges)} segmentos")

        from shapely.geometry import Point
        import geopandas as gpd

        # Para cada estación, encontrar segmento OSM más cercano
        matched = []
        for s in stations:
            pt = Point(s["lon"], s["lat"])
            # Proyectar a metros para distancia real
            # Usar nearest_edges de osmnx
            ne = ox.nearest_edges(G, s["lon"], s["lat"])
            edge_data = G.edges[ne[0], ne[1], ne[2]]
            hw = edge_data.get("highway", "unclassified")
            if isinstance(hw, list):
                hw = hw[0]
            # Normalizar
            hw_norm = normalize_highway(hw)
            proxy = PESOS_NB06.get(hw_norm, PESOS_NB06["unclassified"])
            ratio = s["vol"] / proxy if proxy > 0 else None
            matched.append({
                "vol_real": s["vol"],
                "highway_osm": hw,
                "highway_norm": hw_norm,
                "proxy_nb06": proxy,
                "ratio": ratio,
            })

        print_calibration_results(matched)

    except Exception as e:
        print(f"  Error osmnx: {e}")
        print("  Fallback a análisis estadístico sin red OSM")
        run_stat_calibration(stations)


def normalize_highway(hw: str) -> str:
    hw = hw.lower()
    if "motorway" in hw or "freeway" in hw:
        return "motorway"
    if "trunk" in hw:
        return "trunk"
    if "primary" in hw:
        return "primary"
    if "secondary" in hw:
        return "secondary"
    if "tertiary" in hw:
        return "tertiary"
    if "residential" in hw or "living" in hw:
        return "residential"
    return "unclassified"


def print_calibration_results(matched: list):
    """Imprime factores de calibración por tipo OSM."""
    from collections import defaultdict
    import statistics

    by_type = defaultdict(list)
    for m in matched:
        if m["ratio"] is not None:
            by_type[m["highway_norm"]].append(m)

    print("\n" + "─" * 70)
    print("FACTORES DE CALIBRACIÓN POR TIPO OSM")
    print("─" * 70)
    print(f"{'Tipo OSM':<16} {'Proxy NB06':>12} {'Vol Real (μ)':>14} {'Ratio μ':>10} {'N':>5} {'Ajuste':>12}")
    print("─" * 70)

    global_ratios = []
    recomendaciones = {}

    for hw_type in ["motorway", "trunk", "primary", "secondary", "tertiary", "residential", "unclassified"]:
        items = by_type.get(hw_type, [])
        if not items:
            proxy = PESOS_NB06.get(hw_type, PESOS_NB06["unclassified"])
            print(f"{hw_type:<16} {proxy:>12,.0f} {'—':>14} {'—':>10} {'0':>5} {'sin datos':>12}")
            continue
        proxy = PESOS_NB06.get(hw_type, PESOS_NB06["unclassified"])
        ratios = [m["ratio"] for m in items]
        vols = [m["vol_real"] for m in items]
        mu_ratio = sum(ratios) / len(ratios)
        mu_vol = sum(vols) / len(vols)
        global_ratios.extend(ratios)
        nuevo_proxy = round(mu_vol / 1000) * 1000  # redondear a miles

        if mu_ratio > 1.3:
            ajuste = f"SUBESTIMA x{mu_ratio:.2f}"
        elif mu_ratio < 0.7:
            ajuste = f"SOBREESTIMA x{1/mu_ratio:.2f}"
        else:
            ajuste = "OK (±30%)"

        recomendaciones[hw_type] = {
            "proxy_actual": proxy,
            "vol_real_mu": round(mu_vol),
            "ratio": round(mu_ratio, 3),
            "nuevo_proxy": nuevo_proxy,
            "ajuste": ajuste,
            "n": len(items),
        }
        print(f"{hw_type:<16} {proxy:>12,.0f} {mu_vol:>14,.0f} {mu_ratio:>10.3f} {len(items):>5} {ajuste:>12}")

    print("─" * 70)
    if global_ratios:
        print(f"Factor global medio: {sum(global_ratios)/len(global_ratios):.3f}")

    print("\nPROXIES CALIBRADOS RECOMENDADOS:")
    for hw_type, rec in recomendaciones.items():
        print(f"  {hw_type:<16}: {rec['proxy_actual']:>8,.0f} → {rec['nuevo_proxy']:>8,.0f}  (ratio={rec['ratio']:.3f}, n={rec['n']})")


def run_stat_calibration(stations: list):
    """Análisis estadístico sin osmnx — usa tipo inferido de atributos CGT."""
    from collections import defaultdict

    print("\n" + "─" * 70)
    print("ANÁLISIS ESTADÍSTICO (tipo vía inferido de atributos CGT)")
    print("─" * 70)

    by_type = defaultdict(list)
    for s in stations:
        by_type[s["tipo_inferred"]].append(s["vol"])

    print(f"\n{'Tipo inferido':<16} {'Min':>10} {'Max':>10} {'Media':>10} {'N':>5}")
    print("─" * 55)
    for tipo, vols in sorted(by_type.items(), key=lambda x: -len(x[1])):
        print(f"{tipo:<16} {min(vols):>10,.0f} {max(vols):>10,.0f} {sum(vols)/len(vols):>10,.0f} {len(vols):>5}")

    # Comparar "unknown" contra promedio general (si no hay tipos identificados)
    all_vols = [s["vol"] for s in stations]
    mu_global = sum(all_vols) / len(all_vols)
    med_global = sorted(all_vols)[len(all_vols)//2]

    print(f"\nEstadísticas globales CGT:")
    print(f"  N estaciones:  {len(stations)}")
    print(f"  Min volumen:   {min(all_vols):,.0f} veh/día")
    print(f"  Max volumen:   {max(all_vols):,.0f} veh/día")
    print(f"  Media:         {mu_global:,.0f} veh/día")
    print(f"  Mediana:       {med_global:,.0f} veh/día")

    print("\n" + "─" * 70)
    print("EVALUACIÓN DE PESOS NB06 vs DATOS CGT")
    print("─" * 70)
    print("\nRango de datos CGT observados:")
    print(f"  [{min(all_vols):,.0f} — {max(all_vols):,.0f}] veh/día")
    print(f"  Media: {mu_global:,.0f} | Mediana: {med_global:,.0f}")

    print("\nPesos proxy NB06 (referencia):")
    for tipo, peso in PESOS_NB06.items():
        in_range = "dentro del rango CGT" if min(all_vols) <= peso <= max(all_vols) else (
            "SUPERIOR al max CGT" if peso > max(all_vols) else "inferior al min CGT"
        )
        print(f"  {tipo:<16}: {peso:>8,.0f}  → {in_range}")

    print("\n--- INFERENCIA SIN MATCH OSM ---")
    print(f"La media de volumen CGT ({mu_global:,.0f} veh/día) corresponde")
    for tipo, peso in sorted(PESOS_NB06.items(), key=lambda x: abs(x[1]-mu_global)):
        diff = abs(peso - mu_global)
        print(f"  más cerca a '{tipo}' (proxy={peso:,.0f}, diff={diff:,.0f})")
        break

    # Ratio proxy/mediana para cada tipo
    print(f"\nRatios proxy_NB06 / mediana_CGT ({med_global:,.0f}):")
    for tipo, peso in PESOS_NB06.items():
        r = peso / med_global
        flag = " ← MATCH aprox." if 0.5 <= r <= 2.0 else ""
        print(f"  {tipo:<16}: {r:.2f}{flag}")


def analyze_calibration_no_data(parsed: dict):
    """Sin datos CGT disponibles — análisis teórico."""
    print("\nSin datos CGT disponibles. Evaluación teórica de pesos NB06:")
    print("\nFuentes de referencia para calibración manual:")
    print("  1. IDU - Inventario de la Red Vial (TPDA por tramo)")
    print("     https://www.idu.gov.co/page/inventario-de-la-red-vial")
    print("  2. INVIAS - Volúmenes de tránsito (carreteras nacionales)")
    print("     https://www.invias.gov.co/index.php/red-vial/volumen-de-transito")
    print("  3. SDM - Informes de movilidad anuales")
    print("     https://www.sdm.gov.co/movilidad-en-cifras")
    print("\nPesos NB06 actuales vs. benchmarks internacionales:")
    benchmarks = {
        "motorway": (80_000, 200_000),
        "trunk":    (50_000, 120_000),
        "primary":  (20_000,  60_000),
        "secondary":(10_000,  30_000),
        "tertiary": (3_000,   15_000),
        "residential":(500,    5_000),
    }
    for tipo, peso in PESOS_NB06.items():
        bench = benchmarks.get(tipo)
        if bench:
            lo, hi = bench
            if peso < lo:
                status = f"bajo (bench {lo:,}-{hi:,})"
            elif peso > hi:
                status = f"alto (bench {lo:,}-{hi:,})"
            else:
                status = f"dentro benchmark ({lo:,}-{hi:,})"
            print(f"  {tipo:<16}: {peso:>8,.0f}  -> {status}")


if __name__ == "__main__":
    main()
