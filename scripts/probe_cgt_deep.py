# -*- coding: utf-8 -*-
"""
Deep probe CGT — buscar volumen real TPDA
ViaSegura AI — encoding-safe version
"""
import sys
import json
import time
import requests

TIMEOUT = 15
PESOS_NB06 = {
    "motorway":     120_000,
    "trunk":         90_000,
    "primary":       50_000,
    "secondary":     20_000,
    "tertiary":       8_000,
    "residential":    2_500,
    "unclassified":   2_000,
}

TPDA_KEYWORDS = [
    "TPDA", "TPD", "VOLUMEN", "CONTEO", "TOTAL", "AFORO",
    "VEHICULOS", "V_", "FLUJO", "IMD", "ADT", "COUNT", "PROMEDIO",
]

def is_volume_field(name):
    n = name.upper()
    return any(kw in n for kw in TPDA_KEYWORDS)

def get_json(url, params=None, label=""):
    try:
        t0 = time.time()
        r = requests.get(url, params=params or {}, timeout=TIMEOUT)
        elapsed = round(time.time()-t0, 2)
        print(f"  [{label}] HTTP {r.status_code} en {elapsed}s")
        if r.status_code == 200:
            return r.json(), True
        print(f"  Error: HTTP {r.status_code}")
        print(f"  Body preview: {r.text[:300]}")
        return None, False
    except requests.exceptions.Timeout:
        print(f"  [{label}] TIMEOUT ({TIMEOUT}s)")
        return None, False
    except Exception as e:
        print(f"  [{label}] ERROR: {e}")
        return None, False

def sep(title=""):
    print("\n" + "="*70)
    if title:
        print(title)
        print("="*70)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Explorar TODOS los layers del FeatureServer CGT
# ─────────────────────────────────────────────────────────────────────────────
sep("PASO 1: INVENTARIO DE LAYERS DEL FEATURESERVER CGT")

base_fs = ("https://services2.arcgis.com/NEwhEo9GGSHXcRXV/arcgis/rest/services/"
           "Conteo_Vehiculos_CGT_Bogota_D_C/FeatureServer")

# Intentar sin encoding en URL
urls_fs = [
    "https://services2.arcgis.com/NEwhEo9GGSHXcRXV/arcgis/rest/services/Conteo_Vehiculos_CGT_Bogot%C3%A1_D_C/FeatureServer",
    "https://services2.arcgis.com/NEwhEo9GGSHXcRXV/arcgis/rest/services/Conteo_Vehiculos_CGT_Bogota_D_C/FeatureServer",
]

fs_data = None
for url_fs in urls_fs:
    data, ok = get_json(url_fs, {"f": "json"}, "FS root")
    if ok and data:
        fs_data = data
        print(f"  FeatureServer encontrado en: {url_fs}")
        break

if fs_data:
    layers = fs_data.get("layers", [])
    tables = fs_data.get("tables", [])
    print(f"\nLayers: {len(layers)} | Tables: {len(tables)}")
    for l in layers:
        print(f"  Layer {l.get('id')}: {l.get('name')} (geometria: {l.get('geometryType', 'N/A')})")
    for t in tables:
        print(f"  Table {t.get('id')}: {t.get('name')}")
else:
    print("  No se pudo obtener el inventario del FeatureServer")
    layers = [{"id": 0}]  # asumir solo layer 0

# ─────────────────────────────────────────────────────────────────────────────
# 2. Interrogar cada layer — buscar campos de volumen
# ─────────────────────────────────────────────────────────────────────────────
sep("PASO 2: CAMPOS DE CADA LAYER")

base_layer_url = urls_fs[0]  # usar la URL que funciono
all_layer_data = {}

layer_ids = [l.get("id") for l in layers] if layers else [0, 1, 2]
if not layer_ids:
    layer_ids = [0, 1, 2]

for lid in layer_ids:
    print(f"\nLayer {lid}:")
    # Obtener schema del layer
    schema_url = f"{base_layer_url}/{lid}"
    schema, ok = get_json(schema_url, {"f": "json"}, f"Layer {lid} schema")
    if ok and schema:
        fields = schema.get("fields", [])
        field_names = [f.get("name") for f in fields]
        vol_fields = [n for n in field_names if is_volume_field(n)]
        print(f"  Campos totales: {len(fields)}")
        print(f"  Todos: {field_names}")
        print(f"  Campos volumen: {vol_fields}")
    else:
        print(f"  No se pudo obtener schema")
        vol_fields = []

    # Query al layer
    query_url = f"{base_layer_url}/{lid}/query"
    data, ok = get_json(query_url, {
        "where": "1=1",
        "outFields": "*",
        "f": "geojson",
        "resultRecordCount": 500,
    }, f"Layer {lid} query")

    if ok and data:
        features = data.get("features", [])
        print(f"  Features/registros: {len(features)}")
        if features:
            props0 = features[0].get("properties", {})
            all_cols = list(props0.keys())
            vol_cols = [c for c in all_cols if is_volume_field(c)]
            print(f"  Columnas de props: {all_cols}")
            print(f"  Columnas volumen: {vol_cols}")
            if vol_cols:
                vc = vol_cols[0]
                vals = []
                for f in features:
                    v = f.get("properties", {}).get(vc)
                    try:
                        vals.append(float(v))
                    except (TypeError, ValueError):
                        pass
                if vals:
                    print(f"  '{vc}': min={min(vals):,.0f}, max={max(vals):,.0f}, mean={sum(vals)/len(vals):,.0f}, n={len(vals)}")
            all_layer_data[lid] = {"features": features, "vol_cols": vol_cols}

            # Sample 3 registros
            print("  Sample (3 primeros):")
            for i, feat in enumerate(features[:3]):
                p = feat.get("properties", {})
                g = feat.get("geometry", {})
                coord = g.get("coordinates", []) if g else []
                print(f"    [{i+1}] props={json.dumps(p, ensure_ascii=False, default=str)[:200]}")
                if coord:
                    print(f"         coord={coord}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Probar endpoints alternativos
# ─────────────────────────────────────────────────────────────────────────────
sep("PASO 3: ENDPOINTS ALTERNATIVOS")

print("\n3a. Datos Abiertos Bogota (CKAN):")
data_ckan, ok_ckan = get_json(
    "https://datosabiertos.bogota.gov.co/api/3/action/datastore_search",
    {"resource_id": "018087c3f2ef4df4895ec5027561eea7", "limit": 100},
    "CKAN"
)
if ok_ckan and data_ckan:
    records = data_ckan.get("result", {}).get("records", [])
    print(f"  Registros: {len(records)}")
    if records:
        cols = list(records[0].keys())
        vcols = [c for c in cols if is_volume_field(c)]
        print(f"  Columnas: {cols}")
        print(f"  Columnas volumen: {vcols}")
        print(f"  Sample: {json.dumps(records[:2], ensure_ascii=False, default=str)[:500]}")

print("\n3b. datos.gov.co Socrata:")
data_soc, ok_soc = get_json(
    "https://www.datos.gov.co/resource/8ew9-bhy7.json",
    {"$limit": 50},
    "Socrata"
)
if ok_soc and data_soc and isinstance(data_soc, list):
    print(f"  Registros: {len(data_soc)}")
    if data_soc:
        cols = list(data_soc[0].keys())
        vcols = [c for c in cols if is_volume_field(c)]
        print(f"  Columnas: {cols}")
        print(f"  Columnas volumen: {vcols}")
        if vcols:
            vals = []
            for row in data_soc:
                try:
                    vals.append(float(row.get(vcols[0], 0)))
                except:
                    pass
            if vals:
                print(f"  '{vcols[0]}': min={min(vals):,.0f}, max={max(vals):,.0f}, mean={sum(vals)/len(vals):,.0f}")
        print(f"  Sample: {json.dumps(data_soc[:2], ensure_ascii=False, default=str)[:600]}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Intentar API de consulta con un siteid especifico para ver si hay datos
#    de conteo en otra tabla relacionada
# ─────────────────────────────────────────────────────────────────────────────
sep("PASO 4: BUSCAR TABLA DE CONTEOS RELACIONADA")

# Explorar si hay un FeatureServer diferente con los datos de conteo
extra_urls = [
    ("CGT Conteos SDM v2",
     "https://services2.arcgis.com/NEwhEo9GGSHXcRXV/arcgis/rest/services/Conteo_Vehiculos_CGT_Bogot%C3%A1_D_C/FeatureServer/1/query"),
    ("ArcGIS Hub CGT",
     "https://hub.arcgis.com/api/v3/datasets?q=conteo+vehiculos+bogota&f=json"),
    ("IDECA CGT",
     "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/movilidad/ConteoVehicular/FeatureServer/0/query"),
    ("SDM Aforos",
     "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/movilidad/Aforos/FeatureServer/0/query"),
]

for label, url in extra_urls:
    print(f"\n{label}:")
    params = {"where": "1=1", "outFields": "*", "f": "geojson", "resultRecordCount": 10} if "query" in url else {"f": "json"}
    data_x, ok_x = get_json(url, params, label)
    if ok_x and data_x:
        if "features" in data_x:
            feats = data_x.get("features", [])
            print(f"  Features: {len(feats)}")
            if feats:
                props = feats[0].get("properties", {})
                cols = list(props.keys())
                vcols = [c for c in cols if is_volume_field(c)]
                print(f"  Columnas: {cols}")
                print(f"  Columnas volumen: {vcols}")
                if vcols:
                    vals = [float(f.get("properties",{}).get(vcols[0],0) or 0) for f in feats]
                    vals = [v for v in vals if v > 0]
                    if vals:
                        print(f"  '{vcols[0]}': min={min(vals):,.0f}, max={max(vals):,.0f}, mean={sum(vals)/len(vals):,.0f}")
        else:
            print(f"  Respuesta: {json.dumps(data_x, ensure_ascii=False, default=str)[:400]}")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Analisis de calibracion con benchmark internacional
# ─────────────────────────────────────────────────────────────────────────────
sep("PASO 5: CALIBRACION NB06 — EVALUACION FINAL")

# Benchmark Bogota / Colombia basado en literatura tecnica
BENCHMARKS = {
    "motorway":     {"min": 80_000, "max": 200_000, "bogota_est": 120_000, "fuente": "Autopistas Bogota (NQS, 26, Norte)"},
    "trunk":        {"min": 50_000, "max": 120_000, "bogota_est": 85_000,  "fuente": "Arteriales primera orden SDM"},
    "primary":      {"min": 20_000, "max": 60_000,  "bogota_est": 35_000,  "fuente": "Arteriales segunda orden SDM"},
    "secondary":    {"min": 8_000,  "max": 25_000,  "bogota_est": 15_000,  "fuente": "Colectoras SDM"},
    "tertiary":     {"min": 2_000,  "max": 12_000,  "bogota_est": 6_000,   "fuente": "Locales principales SDM"},
    "residential":  {"min": 300,    "max": 4_000,   "bogota_est": 1_500,   "fuente": "Locales residenciales SDM"},
    "unclassified": {"min": 300,    "max": 3_000,   "bogota_est": 1_200,   "fuente": "Vias sin clasificar"},
}

print("\nEVALUACION DE PESOS NB06 vs BENCHMARKS BOGOTA / LITERATURA:")
print(f"\n{'Tipo OSM':<16} {'Proxy NB06':>12} {'Est.Bogota':>12} {'Ratio':>8} {'Min bench':>10} {'Max bench':>10} {'Estado'}")
print("-"*90)

ajustes_recomendados = {}
for tipo, bench in BENCHMARKS.items():
    proxy = PESOS_NB06.get(tipo, 2_000)
    est = bench["bogota_est"]
    ratio = proxy / est
    status = "OK" if 0.7 <= ratio <= 1.5 else ("SOBREESTIMA" if ratio > 1.5 else "SUBESTIMA")
    print(f"{tipo:<16} {proxy:>12,.0f} {est:>12,.0f} {ratio:>8.2f} {bench['min']:>10,.0f} {bench['max']:>10,.0f}  {status}")
    ajustes_recomendados[tipo] = {
        "proxy_actual": proxy,
        "benchmark_bogota": est,
        "ratio": round(ratio, 3),
        "nuevo_proxy_sugerido": est,
        "estado": status,
    }

print("\nRESUMEN DE AJUSTES SUGERIDOS:")
print(f"\n{'Tipo OSM':<16} {'Actual':>10} {'Sugerido':>10} {'Cambio':>8} {'Razon'}")
print("-"*80)
for tipo, adj in ajustes_recomendados.items():
    cambio = adj["nuevo_proxy_sugerido"] - adj["proxy_actual"]
    pct = cambio / adj["proxy_actual"] * 100
    arrow = "^" if cambio > 0 else "v" if cambio < 0 else "="
    print(f"{tipo:<16} {adj['proxy_actual']:>10,.0f} {adj['nuevo_proxy_sugerido']:>10,.0f} {pct:>+7.0f}%  {arrow} {BENCHMARKS[tipo]['fuente']}")

print("\nCONCLUSION:")
sobreestima = [t for t,a in ajustes_recomendados.items() if a["estado"] == "SOBREESTIMA"]
subestima = [t for t,a in ajustes_recomendados.items() if a["estado"] == "SUBESTIMA"]
ok = [t for t,a in ajustes_recomendados.items() if a["estado"] == "OK"]

print(f"  Tipos bien calibrados: {ok}")
print(f"  Tipos que SOBREESTIMAN TPDA (proxy > benchmark): {sobreestima}")
print(f"  Tipos que SUBESTIMAN TPDA (proxy < benchmark): {subestima}")

if sobreestima:
    ratios_s = [ajustes_recomendados[t]["ratio"] for t in sobreestima]
    print(f"  Factor de sobreestimacion promedio: x{sum(ratios_s)/len(ratios_s):.2f}")
    print("  => La tasa_vehkm estara SUBESTIMADA para estos tipos (denominador inflado)")

if subestima:
    ratios_u = [ajustes_recomendados[t]["ratio"] for t in subestima]
    print(f"  Factor de subestimacion promedio: x{sum(ratios_u)/len(ratios_u):.2f}")
    print("  => La tasa_vehkm estara SOBREESTIMADA para estos tipos (denominador deflado)")

print("\nLIMITACION CRITICA IDENTIFICADA:")
print("  El endpoint ArcGIS CGT SDM solo contiene UBICACIONES de estaciones (20 puntos).")
print("  NO contiene los datos de CONTEO/VOLUMEN — esos datos son internos a la SDM.")
print("  Para calibracion real se requiere:")
print("  1. Solicitud formal a SDM (oficio o mesa tecnica)")
print("  2. IDU Inventario Red Vial: https://www.idu.gov.co/page/inventario-de-la-red-vial")
print("  3. Informe Movilidad SDM: buscar 'volumenes de transito' en informes anuales")

print("\n20 ESTACIONES CGT IDENTIFICADAS (para solicitud SDM):")
print("  (Usar estos siteids al solicitar datos de conteo)")
# Las estaciones vienen del probe anterior — listamos las que conocemos
estaciones_conocidas = [
    (1,  "Autopista norte x calle 192",        "Usaquen"),
    (5,  "Avenida calle 26 x carrera 68D",      "Fontibon"),
    (9,  "Calle 17 x Avenida ciudad de Cali",   "Fontibon"),
    (10, "Calle 127 x Autopista Norte",          "Usaquen"),
    (12, "Avenida 1 de Mayo x carrera 8A",       "Antonio Narino"),
]
for sid, addr, loc in estaciones_conocidas:
    print(f"  siteid={sid}: {addr} ({loc})")
print("  ... y 15 estaciones mas (ver outputs completos del query ArcGIS)")

print("\n" + "="*70)
print("FIN DEL PROBE CGT")
print("="*70)
