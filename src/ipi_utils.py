"""IPI (Índice de Prioridad de Intervención) calculations (from NB02)."""

from __future__ import annotations

import pandas as pd

# Columns used for the IPI composite score
SCORES_COLS = [
    "score_volumen",
    "score_criticidad_total",
    "score_severidad_promedio",
    "score_persistencia",
    "score_fatalidad",
]

# Number of years in the study period (2016-2019)
_N_ANIOS = 4

# B3.1 — severity weight schemes for IPI sensitivity analysis
PESOS_1_3_5: dict[str, float] = {"solo_danos": 1, "con_heridos": 3, "con_muertos": 5}
PESOS_EPDO: dict[str, float] = {"solo_danos": 1, "con_heridos": 8, "con_muertos": 24}


def calcular_ipi(zonas: pd.DataFrame) -> pd.DataFrame:
    """Compute the 5 component scores and IPI for each zone.

    Expects columns: cantidad_siniestros, criticidad_total, criticidad_promedio,
    anios_activos, siniestros_con_muertos.

    Returns the dataframe with score_* and IPI columns added.
    """
    df = zonas.copy()
    df["score_volumen"] = df["cantidad_siniestros"].rank(pct=True)
    df["score_criticidad_total"] = df["criticidad_total"].rank(pct=True)
    df["score_severidad_promedio"] = df["criticidad_promedio"].rank(pct=True)
    df["score_persistencia"] = df["anios_activos"] / _N_ANIOS
    df["score_fatalidad"] = df["siniestros_con_muertos"].rank(pct=True)
    df["IPI"] = df[SCORES_COLS].mean(axis=1) * 100
    return df


def asignar_prioridad_ipi(rank: int) -> str:
    """Classify a zone into an intervention priority tier based on its IPI rank."""
    if rank <= 50:
        return "Prioridad 1 - Intervención prioritaria"
    elif rank <= 200:
        return "Prioridad 2 - Auditoría de seguridad vial"
    elif rank <= 500:
        return "Prioridad 3 - Monitoreo y gestión preventiva"
    return "Seguimiento"


def clasificar_familia_analitica(row: pd.Series) -> str:
    """Assign an analytical family based on IPI and sub-component ranks."""
    rank_ipi = row["rank_IPI"]
    rank_criticidad = row["rank_criticidad_total"]
    rank_muertes = row["rank_muertes"]

    if rank_ipi <= 200 and rank_criticidad <= 200:
        return "Hotspot robusto integral"
    elif rank_ipi <= 200 and rank_muertes <= 200 and rank_criticidad > 200:
        return "Hotspot de severidad/fatalidad"
    elif rank_criticidad <= 200 and rank_ipi > 200:
        return "Hotspot de carga acumulada"
    elif rank_ipi <= 500:
        return "Hotspot preventivo prioritario"
    return "Seguimiento"


def clasificar_hotspot(row: pd.Series) -> str:
    """Legacy hotspot classification used before IPI was introduced (NB02 early cells)."""
    cantidad = row["cantidad_siniestros"]
    criticidad_promedio = row["criticidad_promedio"]
    anios_activos = row["anios_activos"]

    if anios_activos >= 4 and cantidad >= 300:
        return "Hotspot estructural persistente"
    elif criticidad_promedio >= 2.0 and cantidad >= 150:
        return "Hotspot severo"
    elif cantidad >= 350 and criticidad_promedio < 1.7:
        return "Hotspot de alto volumen"
    elif anios_activos >= 3 and criticidad_promedio >= 1.7:
        return "Hotspot persistente con severidad media-alta"
    return "Hotspot exploratorio"


# ── B3.1: Sensibilidad EPDO ────────────────────────────────────────────────


def calcular_ipi_pesos_alternativos(
    df: pd.DataFrame,
    pesos: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Recompute IPI using alternative severity weights (default: EPDO 1/8/24).

    Derives n_solo_danos and n_con_heridos algebraically from the 1/3/5-weighted
    criticidad_total baseline. Adds IPI_alt, score_*_alt, and criticidad_*_alt
    columns without modifying existing IPI columns.

    Args:
        df: DataFrame with cantidad_siniestros, criticidad_total, criticidad_promedio,
            anios_activos, siniestros_con_muertos (same contract as calcular_ipi).
        pesos: Dict with keys solo_danos, con_heridos, con_muertos. Defaults to PESOS_EPDO.
    """
    if pesos is None:
        pesos = PESOS_EPDO

    df = df.copy()
    n_m = df["siniestros_con_muertos"].fillna(0.0)
    n_t = df["cantidad_siniestros"].fillna(0.0)
    c0 = df["criticidad_total"].fillna(0.0)

    # Algebra (1/3/5 baseline): n_heridos = (c0 - 4*n_muertos - n_total) / 2
    n_h = ((c0 - 4.0 * n_m - n_t) / 2.0).round().clip(lower=0).astype(int)
    n_s = (n_t - n_m - n_h).round().clip(lower=0).astype(int)

    crit_alt = (
        n_s * pesos["solo_danos"]
        + n_h * pesos["con_heridos"]
        + n_m * pesos["con_muertos"]
    )
    n_t_safe = n_t.where(n_t > 0)
    crit_prom_alt = (crit_alt / n_t_safe).fillna(0.0)

    df_temp = pd.DataFrame(
        {
            "cantidad_siniestros": df["cantidad_siniestros"].values,
            "criticidad_total": crit_alt.values,
            "criticidad_promedio": crit_prom_alt.values,
            "anios_activos": df["anios_activos"].values,
            "siniestros_con_muertos": df["siniestros_con_muertos"].values,
        },
        index=df.index,
    )
    df_ipi = calcular_ipi(df_temp)

    df["IPI_alt"] = df_ipi["IPI"].values
    for col in SCORES_COLS:
        df[f"{col}_alt"] = df_ipi[col].values
    df["criticidad_total_alt"] = crit_alt.values
    df["criticidad_promedio_alt"] = crit_prom_alt.values
    return df


def comparar_rankings_ipi(
    rank_base: pd.Series,
    rank_alt: pd.Series,
    top_n: int = 200,
) -> dict:
    """Concordance metrics between two IPI rankings over a shared index.

    Returns dict: top_n, n_en_comun, overlap_pct, n_difieren, spearman_rho.
    """
    en_base = set(rank_base[rank_base <= top_n].index)
    en_alt = set(rank_alt[rank_alt <= top_n].index)
    n_comun = len(en_base & en_alt)
    mask = rank_base.notna() & rank_alt.notna()
    rho = float(rank_base[mask].corr(rank_alt[mask], method="spearman"))
    return {
        "top_n": top_n,
        "n_en_comun": n_comun,
        "overlap_pct": round(n_comun / top_n * 100, 1),
        "n_difieren": top_n - n_comun,
        "spearman_rho": round(rho, 4),
    }


# ── B3.3: Normalización NB05 ───────────────────────────────────────────────


def calcular_tasas_exposicion(
    df: pd.DataFrame,
    epsilon_km: float = 0.05,
) -> pd.DataFrame:
    """Compute tasa_red (siniestros/km) and tasa_pob_100k (siniestros/100k hab).

    Expects: cantidad_siniestros_rec, km_red_osm, poblacion_2018.
    epsilon_km clips km_red_osm to prevent inflated rates for OSM-unmapped zones.
    """
    df = df.copy()
    km_safe = df["km_red_osm"].clip(lower=epsilon_km)
    df["tasa_red"] = df["cantidad_siniestros_rec"] / km_safe
    df["tasa_pob_100k"] = (df["cantidad_siniestros_rec"] / df["poblacion_2018"]) * 100_000
    df.loc[df["poblacion_2018"].isna(), "tasa_pob_100k"] = float("nan")
    return df


def calcular_rankings_duales(
    df: pd.DataFrame,
    ipi_col: str = "IPI",
    top_n: int = 200,
) -> pd.DataFrame:
    """Add dual-ranking columns for volumetric and exposure-normalized analysis.

    Adds rank_vol, rank_tasa_red, rank_tasa_pob, delta_rank, en_top_vol,
    en_top_tasa_red, en_top_tasa_pob. Expects ipi_col, tasa_red, tasa_pob_100k.
    """
    df = df.copy()

    def _rank_desc(s: pd.Series) -> pd.Series:
        return s.rank(ascending=False, method="min", na_option="bottom").astype(int)

    df["rank_vol"] = _rank_desc(df[ipi_col])
    df["rank_tasa_red"] = _rank_desc(df["tasa_red"])
    df["rank_tasa_pob"] = _rank_desc(df["tasa_pob_100k"])
    df["delta_rank"] = df["rank_vol"] - df["rank_tasa_red"]
    df["en_top_vol"] = df["rank_vol"] <= top_n
    df["en_top_tasa_red"] = df["rank_tasa_red"] <= top_n
    df["en_top_tasa_pob"] = df["rank_tasa_pob"] <= top_n
    return df


def asignar_tipologia_nb05(row: pd.Series) -> str:
    """Assign NB05 concordance typology from en_top_vol, en_top_tasa_red, en_top_tasa_pob flags."""
    if row["en_top_vol"] and row["en_top_tasa_red"]:
        return "Hotspot absoluto + relativo"
    if row["en_top_vol"]:
        return "Hotspot por volumen"
    if row["en_top_tasa_red"]:
        return "Hotspot relativo oculto"
    if row["en_top_tasa_pob"]:
        return "Alta tasa poblacional"
    return "Sin tipología NB05"
