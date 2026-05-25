# -*- coding: utf-8 -*-
"""
Obtener lista completa de 20 estaciones CGT e inferir tipo OSM por nombre de via
"""
import requests
import json

URL = ("https://services2.arcgis.com/NEwhEo9GGSHXcRXV/arcgis/rest/services/"
       "Conteo_Vehiculos_CGT_Bogot%C3%A1_D_C/FeatureServer/0/query")
PARAMS = {"where": "1=1", "outFields": "*", "f": "geojson", "resultRecordCount": 100, "orderByFields": "siteid"}

r = requests.get(URL, params=PARAMS, timeout=15)
data = r.json()
features = data.get("features", [])

print(f"Total estaciones CGT: {len(features)}\n")

# Reglas de clasificacion OSM por nombre de via bogotana
def classify_via(address, name):
    s = (address + " " + name).upper()
    if any(k in s for k in ["AUTOPISTA", "CIRCUNVALAR", "BOSA", "BOYACA NORTE"]):
        return "motorway"
    if any(k in s for k in ["NQS", "CARACAS", "BOYACA", "SUR", "CALI", "68", "AMERICAS",
                              "1 DE MAYO", "VILLAVICENCIO", "LONGITUDINAL", "FERROCARRIL"]):
        return "trunk"
    if any(k in s for k in ["CARRERA 7", "CARRERA 11", "CARRERA 15", "CARRERA 30",
                              "CALLE 26", "CALLE 80", "CALLE 127", "CALLE 100",
                              "CALLE 116", "CALLE 170", "AVENIDA"]):
        return "primary"
    if any(k in s for k in ["CARRERA", "CALLE", "DIAGONAL", "TRANSVERSAL"]):
        return "secondary"
    return "secondary"  # default para vias bogotanas con conteos

PESOS = {
    "motorway": 120_000, "trunk": 90_000, "primary": 50_000,
    "secondary": 20_000, "tertiary": 8_000,
    "residential": 2_500, "unclassified": 2_000,
}

BENCHMARK = {
    "motorway": 120_000, "trunk": 85_000, "primary": 35_000,
    "secondary": 15_000, "tertiary": 6_000,
    "residential": 1_500, "unclassified": 1_200,
}

print(f"{'siteid':>7} {'Tipo OSM infer.':>16} {'Proxy NB06':>12} {'Benchmark':>11} {'Direccion'}")
print("-"*90)

from collections import defaultdict
tipo_counts = defaultdict(int)

for f in features:
    p = f.get("properties", {})
    g = f.get("geometry", {})
    sid = p.get("siteid")
    addr = p.get("address", "")
    loc = p.get("location", "")
    nm = p.get("name", "")
    coords = g.get("coordinates", []) if g else []
    tipo = classify_via(addr, nm)
    tipo_counts[tipo] += 1
    proxy = PESOS.get(tipo, 2_000)
    bench = BENCHMARK.get(tipo, 1_200)
    print(f"{sid:>7} {tipo:>16} {proxy:>12,.0f} {bench:>11,.0f}  {addr} ({loc})")

print("\nDISTRIBUCION INFERIDA DE TIPOS OSM:")
for tipo, cnt in sorted(tipo_counts.items(), key=lambda x: -x[1]):
    proxy = PESOS[tipo]
    bench = BENCHMARK.get(tipo)
    pct = cnt / len(features) * 100
    print(f"  {tipo:<16}: {cnt:>3} estaciones ({pct:.0f}%) | proxy={proxy:,.0f} | benchmark={bench:,.0f}")

# Guardar JSON para uso futuro en NB06
out = []
for f in features:
    p = f.get("properties", {})
    g = f.get("geometry", {})
    coords = g.get("coordinates", []) if g else [None, None]
    tipo = classify_via(p.get("address",""), p.get("name",""))
    out.append({
        "siteid": p.get("siteid"),
        "address": p.get("address"),
        "location": p.get("location"),
        "name": p.get("name"),
        "lon": coords[0] if len(coords) > 1 else None,
        "lat": coords[1] if len(coords) > 1 else None,
        "tipo_osm_inferred": tipo,
        "proxy_nb06": PESOS.get(tipo),
        "benchmark_bogota": BENCHMARK.get(tipo),
    })

import os
out_path = r"C:\Users\jorge\Documents\viasegura_ai\data\raw\cgt_stations_metadata.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print(f"\nEstaciones guardadas en: {out_path}")
