"""
query_layer6_condiciones_viales.py
===================================
Descarga Layer 6 (VM_ACC_VIA) de SIMUR para los accidentes del Top 200 IPI
y agrega condiciones de vía por zona.

Join key: CODIGO_ACCIDENTE (Layer 6) == CODIGO_ACCIDENTE (accidentes_limpio.csv)
Campos: SEMAFORO, ILUMINACION_ARTIFICIAL, SUPERFICIE_RODADURA, CARRILES, ESTADO

Output: outputs/reports/condiciones_viales_top200.csv
"""

import sys
import time
import requests
import numpy as np
import pandas as pd
from pathlib import Path

# ── Rutas ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
REPORTS = BASE / "outputs" / "reports"
DATA_PROC = BASE / "data" / "processed"

URL_LAYER6 = (
    "https://sig.simur.gov.co/arcgis/rest/services"
    "/Accidentalidad/AccidentalidadAnalisis/FeatureServer/6/query"
)

CAMPOS_VIALES = [
    "CODIGO_ACCIDENTE",
    "SUPERFICIE_RODADURA",
    "SEMAFORO",
    "ILUMINACION_ARTIFICIAL",
    "CARRILES",
    "ESTADO",
    "AGENTE",
]

BATCH_SIZE = 500   # ArcGIS REST permite ~500-1000 IDs por query
SLEEP_SEC  = 0.5   # pausa entre batches para no saturar el servidor


def redondear_zona(lat: float, lon: float, decimales: int = 3) -> tuple:
    """Replica la lógica de grilla usada en NB02/NB04."""
    return round(lat, decimales), round(lon, decimales)


def query_batch(codigos: list[int]) -> list[dict]:
    """Consulta Layer 6 para un batch de CODIGO_ACCIDENTE."""
    where = f"CODIGO_ACCIDENTE IN ({','.join(str(int(c)) for c in codigos)})"
    params = {
        "where": where,
        "outFields": ",".join(CAMPOS_VIALES),
        "resultRecordCount": len(codigos) + 10,
        "f": "json",
    }
    try:
        resp = requests.get(URL_LAYER6, params=params, timeout=30)
        data = resp.json()
        if "features" in data:
            return [f["attributes"] for f in data["features"]]
        if "error" in data:
            print(f"  Error API: {data['error']}", file=sys.stderr)
    except Exception as exc:
        print(f"  Timeout/Error: {exc}", file=sys.stderr)
    return []


def main() -> None:
    # ── 1. Cargar accidentes 2016-2019 ────────────────────────────────────────
    print("Cargando accidentes_bogota_2016_2019_limpio.csv ...")
    df_acc = pd.read_csv(
        DATA_PROC / "accidentes_bogota_2016_2019_limpio.csv",
        usecols=["CODIGO_ACCIDENTE", "LATITUD", "LONGITUD"],
    )
    df_acc = df_acc.dropna(subset=["LATITUD", "LONGITUD", "CODIGO_ACCIDENTE"])
    df_acc["lat_grid"] = df_acc["LATITUD"].round(3)
    df_acc["lon_grid"] = df_acc["LONGITUD"].round(3)
    print(f"  {len(df_acc):,} accidentes con coordenadas")

    # ── 2. Cargar Top 200 zonas ───────────────────────────────────────────────
    print("Cargando Top 200 zonas ...")
    df_hot = pd.read_csv(REPORTS / "hotspots_normalizados_nb05.csv")
    top200 = df_hot[df_hot["en_top200_rec"] == True][["lat_grid", "lon_grid"]].copy()
    print(f"  {len(top200)} zonas en Top 200")

    # ── 3. Filtrar accidentes que caen en zonas Top 200 ───────────────────────
    df_merged = df_acc.merge(top200, on=["lat_grid", "lon_grid"], how="inner")
    codigos_top200 = df_merged["CODIGO_ACCIDENTE"].dropna().astype(int).unique().tolist()
    print(f"  {len(codigos_top200):,} accidentes únicos en Top 200")

    # ── 4. Descargar Layer 6 en batches ──────────────────────────────────────
    print(f"Consultando Layer 6 en batches de {BATCH_SIZE} ...")
    registros = []
    n_batches = (len(codigos_top200) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(n_batches):
        batch = codigos_top200[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        result = query_batch(batch)
        registros.extend(result)
        pct = (i + 1) / n_batches * 100
        print(f"  Batch {i+1}/{n_batches} ({pct:.0f}%) — {len(result)} registros")
        time.sleep(SLEEP_SEC)

    if not registros:
        print("ERROR: Layer 6 no retornó registros. Verificar conectividad.")
        sys.exit(1)

    df_l6 = pd.DataFrame(registros)
    df_l6["CODIGO_ACCIDENTE"] = pd.to_numeric(df_l6["CODIGO_ACCIDENTE"], errors="coerce")
    df_l6 = df_l6.dropna(subset=["CODIGO_ACCIDENTE"])
    df_l6["CODIGO_ACCIDENTE"] = df_l6["CODIGO_ACCIDENTE"].astype(int)
    print(f"  Total registros Layer 6 obtenidos: {len(df_l6):,}")

    # ── 5. Join con zonas ─────────────────────────────────────────────────────
    df_join = df_merged.merge(df_l6, on="CODIGO_ACCIDENTE", how="inner")
    print(f"  Accidentes con condición vial asignada: {len(df_join):,}")

    # ── 6. Agregar condiciones por zona ───────────────────────────────────────
    def pct_val(series, valor):
        if len(series) == 0:
            return np.nan
        return (series == valor).sum() / len(series) * 100

    agg = df_join.groupby(["lat_grid", "lon_grid"]).agg(
        n_acc_viales=("CODIGO_ACCIDENTE", "count"),
        pct_semaforo=(    "SEMAFORO",             lambda s: pct_val(s, "SI")),
        pct_asfalto=(     "SUPERFICIE_RODADURA",   lambda s: pct_val(s, "ASFALTO")),
        pct_iluminacion=( "ILUMINACION_ARTIFICIAL", lambda s: pct_val(s, "CON")),
        semaforo_modal=(  "SEMAFORO",              lambda s: s.mode().iloc[0] if len(s) else ""),
        superficie_modal=("SUPERFICIE_RODADURA",   lambda s: s.mode().iloc[0] if len(s) else ""),
        iluminacion_modal=("ILUMINACION_ARTIFICIAL",lambda s: s.mode().iloc[0] if len(s) else ""),
        carriles_mediana=("CARRILES",              lambda s: pd.to_numeric(s, errors="coerce").median()),
        estado_modal=(    "ESTADO",                lambda s: s.mode().iloc[0] if len(s) else ""),
    ).reset_index()

    # ── 7. Guardar ───────────────────────────────────────────────────────────
    out_path = REPORTS / "condiciones_viales_top200.csv"
    agg.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nOutput guardado: {out_path}")
    print(f"  Zonas con datos de condición vial: {len(agg)} / 200")
    print(f"\nDistribución semaforo_modal:")
    print(agg["semaforo_modal"].value_counts().to_string())
    print(f"\nDistribución superficie_modal:")
    print(agg["superficie_modal"].value_counts().to_string())
    print(f"\nDistribución iluminacion_modal:")
    print(agg["iluminacion_modal"].value_counts().to_string())


if __name__ == "__main__":
    main()
