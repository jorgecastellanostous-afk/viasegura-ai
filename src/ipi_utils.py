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
