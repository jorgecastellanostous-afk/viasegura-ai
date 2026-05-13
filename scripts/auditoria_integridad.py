import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import os

results = []
errors = []

def log(msg):
    results.append(msg)
    print(msg)

def logerr(msg):
    errors.append(msg)
    print(f"[ERROR] {msg}")

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE = r"C:\Users\jorge\Documents\viasegura_ai"
PROC = os.path.join(BASE, "data", "processed")
RPT  = os.path.join(BASE, "outputs", "reports")

f_base       = os.path.join(PROC, "accidentes_bogota_2016_2019_limpio.csv")
f_reciente   = os.path.join(PROC, "accidentes_bogota_reciente_limpio.csv")
f_ipi        = os.path.join(RPT,  "zonas_criticas_IPI_completo_2016_2019.csv")
f_hotspots   = os.path.join(RPT,  "clasificacion_hotspots_persistencia_notebook_03.csv")
f_top200r    = os.path.join(RPT,  "top200_IPI_reciente_notebook_03.csv")
f_esquema    = os.path.join(RPT,  "esquema_integracion_nb04_notebook_03.csv")

log("=" * 70)
log("AUDITORÍA DE INTEGRIDAD — VíaSegura AI — 2026-05-08")
log("=" * 70)

# ─── 1. CONTEOS GENERALES ────────────────────────────────────────────────────
log("\n[1] CONTEOS GENERALES")

# 1a. Dataset base 2016-2019
try:
    df_base = pd.read_csv(f_base, low_memory=False)
    n_base, nc_base = df_base.shape
    log(f"  accidentes_bogota_2016_2019_limpio.csv : {n_base:,} filas | {nc_base} columnas  → OK")
    log(f"     Columnas: {list(df_base.columns)}")
except Exception as e:
    logerr(f"No se pudo leer {f_base}: {e}")
    df_base = None

# 1b. Dataset reciente
try:
    df_rec = pd.read_csv(f_reciente, low_memory=False)
    n_rec, nc_rec = df_rec.shape
    log(f"  accidentes_bogota_reciente_limpio.csv  : {n_rec:,} filas | {nc_rec} columnas  → OK")
    log(f"     Columnas: {list(df_rec.columns)}")
except Exception as e:
    logerr(f"No se pudo leer {f_reciente}: {e}")
    df_rec = None

# 1c. IPI completo 2016-2019
IPI_REQUIRED_COLS = ["IPI", "rank_IPI", "familia_analitica", "prioridad_IPI",
                     "score_volumen", "score_fatalidad"]
try:
    df_ipi = pd.read_csv(f_ipi, low_memory=False)
    n_ipi, nc_ipi = df_ipi.shape
    log(f"\n  zonas_criticas_IPI_completo_2016_2019.csv : {n_ipi:,} zonas | {nc_ipi} columnas  → OK")
    missing_ipi_cols = [c for c in IPI_REQUIRED_COLS if c not in df_ipi.columns]
    if missing_ipi_cols:
        logerr(f"  Columnas faltantes en IPI: {missing_ipi_cols}")
    else:
        log(f"  Columnas requeridas IPI presentes: {IPI_REQUIRED_COLS}  → OK")
    log(f"  Todas las columnas: {list(df_ipi.columns)}")
except Exception as e:
    logerr(f"No se pudo leer {f_ipi}: {e}")
    df_ipi = None

# 1d. Hotspots persistencia NB03
try:
    df_hot = pd.read_csv(f_hotspots, low_memory=False)
    n_hot, nc_hot = df_hot.shape
    log(f"\n  clasificacion_hotspots_persistencia_notebook_03.csv : {n_hot:,} filas | {nc_hot} columnas  → OK")
    log(f"  Columnas: {list(df_hot.columns)}")
except Exception as e:
    logerr(f"No se pudo leer {f_hotspots}: {e}")
    df_hot = None

# 1e. Top 200 reciente NB03
if os.path.exists(f_top200r):
    try:
        df_top200r = pd.read_csv(f_top200r, low_memory=False)
        n_t200r = len(df_top200r)
        log(f"\n  top200_IPI_reciente_notebook_03.csv : {n_t200r:,} filas  → OK")
        log(f"  Columnas: {list(df_top200r.columns)}")
    except Exception as e:
        logerr(f"No se pudo leer {f_top200r}: {e}")
        df_top200r = None
else:
    logerr(f"ARCHIVO NO EXISTE: {f_top200r}")
    df_top200r = None

# 1f. Esquema integración NB04
if os.path.exists(f_esquema):
    try:
        df_esq = pd.read_csv(f_esquema, low_memory=False)
        n_esq = len(df_esq)
        log(f"\n  esquema_integracion_nb04_notebook_03.csv : {n_esq:,} filas  → OK")
        log(f"  Columnas: {list(df_esq.columns)}")
        log(f"  Contenido:\n{df_esq.to_string()}")
    except Exception as e:
        logerr(f"No se pudo leer {f_esquema}: {e}")
        df_esq = None
else:
    logerr(f"ARCHIVO NO EXISTE: {f_esquema}")
    df_esq = None

# ─── 2. COLUMNAS CRÍTICAS PARA NB04 ─────────────────────────────────────────
log("\n" + "=" * 70)
log("[2] COLUMNAS CRÍTICAS PARA NB04")

if df_rec is not None:
    if "FORMULARIO" in df_rec.columns:
        n_null_form = df_rec["FORMULARIO"].isna().sum()
        n_uniq_form = df_rec["FORMULARIO"].nunique()
        log(f"  FORMULARIO presente en reciente_limpio  → OK")
        log(f"  Nulos en FORMULARIO: {n_null_form:,} ({100*n_null_form/len(df_rec):.2f}%)")
        log(f"  FORMULARIOs únicos: {n_uniq_form:,}")
        # Show a few sample values
        sample = df_rec["FORMULARIO"].dropna().head(5).tolist()
        log(f"  Muestra valores FORMULARIO: {sample}")
    else:
        logerr("FORMULARIO NO está en accidentes_bogota_reciente_limpio.csv")
        log(f"  Columnas disponibles: {list(df_rec.columns)}")

if df_ipi is not None:
    for coord_col in ["LAT_ZONA", "LON_ZONA"]:
        if coord_col in df_ipi.columns:
            n_null_c = df_ipi[coord_col].isna().sum()
            log(f"\n  {coord_col} presente en IPI completo  → OK")
            log(f"  Nulos en {coord_col}: {n_null_c:,}")
        else:
            logerr(f"{coord_col} NO está en zonas_criticas_IPI_completo_2016_2019.csv")

# ─── 3. VERIFICACIÓN IPI CORREGIDO ───────────────────────────────────────────
log("\n" + "=" * 70)
log("[3] VERIFICACIÓN IPI CORREGIDO (primeras 5 filas)")

if df_ipi is not None:
    # Identify score columns
    score_cols = [c for c in df_ipi.columns if c.startswith("score_")]
    log(f"  Columnas score encontradas: {score_cols}")

    head5 = df_ipi.head(5).copy()

    # Try known score column names
    known_scores = ["score_volumen", "score_fatalidad", "score_recurrencia",
                    "score_expansion", "score_gravedad"]
    present_scores = [c for c in known_scores if c in df_ipi.columns]
    log(f"  Score cols known/present: {present_scores}")

    discrepancias = []
    for idx, row in head5.iterrows():
        if present_scores:
            expected = np.mean([row[c] for c in present_scores]) * 100
        else:
            expected = np.mean([row[c] for c in score_cols]) * 100
        ipi_real = row["IPI"]
        delta = abs(ipi_real - expected)
        status = "OK" if delta <= 0.01 else f"DISCREPANCIA delta={delta:.5f}"
        log(f"  Fila {idx}: IPI={ipi_real:.5f} | expected={expected:.5f} | {status}")
        if delta > 0.01:
            discrepancias.append({
                "fila": idx,
                "IPI_real": ipi_real,
                "IPI_esperado": expected,
                "delta": delta,
                "scores_usados": {c: row[c] for c in (present_scores or score_cols)}
            })

    if discrepancias:
        logerr(f"IPI NO coincide con media de scores en {len(discrepancias)} filas de las primeras 5")
        for d in discrepancias:
            log(f"    {d}")
    else:
        log("  IPI = mean(scores) × 100 verificado en primeras 5 filas  → OK")

# ─── 4. SOLAPAMIENTO NB02 TOP-200 vs NB03 TOP-200 ────────────────────────────
log("\n" + "=" * 70)
log("[4] SOLAPAMIENTO Top-200 NB02 vs Top-200 NB03")

if df_ipi is not None and df_top200r is not None:
    # Get top200 from IPI base (NB02)
    if "rank_IPI" in df_ipi.columns:
        top200_base = df_ipi[df_ipi["rank_IPI"] <= 200].copy()
    else:
        top200_base = df_ipi.head(200).copy()
    log(f"  Top-200 base (NB02): {len(top200_base)} zonas")
    log(f"  Top-200 reciente (NB03): {len(df_top200r)} zonas")

    # Check coordinate columns in both
    lat_base = "LAT_ZONA" if "LAT_ZONA" in top200_base.columns else None
    lon_base = "LON_ZONA" if "LON_ZONA" in top200_base.columns else None
    lat_rec  = "LAT_ZONA" if "LAT_ZONA" in df_top200r.columns else None
    lon_rec  = "LON_ZONA" if "LON_ZONA" in df_top200r.columns else None

    log(f"  Coord cols base: lat={lat_base}, lon={lon_base}")
    log(f"  Coord cols rec:  lat={lat_rec}, lon={lon_rec}")

    if lat_base and lon_base and lat_rec and lon_rec:
        # Round to 3 decimals
        top200_base["_key"] = (
            top200_base[lat_base].round(3).astype(str) + "_" +
            top200_base[lon_base].round(3).astype(str)
        )
        df_top200r["_key"] = (
            df_top200r[lat_rec].round(3).astype(str) + "_" +
            df_top200r[lon_rec].round(3).astype(str)
        )
        overlap = set(top200_base["_key"]) & set(df_top200r["_key"])
        n_overlap = len(overlap)
        pct = 100 * n_overlap / 200
        log(f"  Solapamiento (join LAT_ZONA/LON_ZONA @3dec): {n_overlap} / 200  ({pct:.1f}%)")
        if n_overlap == 0:
            logerr("Solapamiento = 0. Verificar nombres de columnas o escala de coordenadas.")
    else:
        logerr("No se puede calcular solapamiento: columnas de coordenadas no encontradas")
        log(f"  Columnas base top200: {list(top200_base.columns[:20])}")
        log(f"  Columnas reciente top200: {list(df_top200r.columns[:20])}")
else:
    log("  OMITIDO: alguno de los datasets no cargó correctamente.")

# ─── 5. RESUMEN FINAL ────────────────────────────────────────────────────────
log("\n" + "=" * 70)
log("[5] RESUMEN DE ERRORES/ALERTAS")
if errors:
    for e in errors:
        log(f"  ALERTA: {e}")
else:
    log("  Sin errores críticos detectados.")

log("\nAuditoría completada.")

# Write results to file
out_file = r"C:\Users\jorge\Documents\viasegura_ai\outputs\reports\auditoria_resultado.txt"
with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print(f"\nResultados escritos en: {out_file}")
