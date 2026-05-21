"""Utilities for cleaning and validating accident records (from NB01)."""

from __future__ import annotations

import pandas as pd

# Bogotá bounding box
_LAT_MIN, _LAT_MAX = 4.0, 5.0
_LON_MIN, _LON_MAX = -75.0, -73.0

PUNTAJE_GRAVEDAD: dict[str, int] = {
    "SOLO DANOS": 1,
    "SOLO DAÑOS": 1,
    "CON HERIDOS": 3,
    "CON MUERTOS": 5,
}

# EPDO weights (Equivalentes de Peatón Muerto)
PUNTAJE_EPDO: dict[str, int] = {
    "SOLO DANOS": 1,
    "SOLO DAÑOS": 1,
    "CON HERIDOS": 8,
    "CON MUERTOS": 24,
}


def validar_coordenadas(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with coordinates outside Bogotá's bounding box."""
    mask = df["LATITUD"].between(_LAT_MIN, _LAT_MAX) & df["LONGITUD"].between(_LON_MIN, _LON_MAX)
    return df[mask].copy()


def calcular_puntaje_gravedad(
    df: pd.DataFrame,
    columna: str = "GRAVEDAD",
    epdo: bool = False,
) -> pd.Series:
    """Map GRAVEDAD strings to numeric severity scores."""
    tabla = PUNTAJE_EPDO if epdo else PUNTAJE_GRAVEDAD
    return df[columna].map(tabla).fillna(1).astype(int)


def limpiar_siniestros(df: pd.DataFrame) -> pd.DataFrame:
    """Full cleaning pipeline applied in NB01.

    Steps:
    - Parse FECHA_OCURRENCIA_ACC (ms epoch → datetime)
    - Drop rows outside Bogotá bounding box
    - Add puntaje_gravedad column
    - Reset index
    """
    df = df.copy()

    # Date parsing: try epoch-ms first, then string
    if pd.api.types.is_numeric_dtype(df["FECHA_OCURRENCIA_ACC"]):
        df["FECHA_OCURRENCIA_ACC"] = pd.to_datetime(
            df["FECHA_OCURRENCIA_ACC"], unit="ms", errors="coerce"
        )
    else:
        df["FECHA_OCURRENCIA_ACC"] = pd.to_datetime(df["FECHA_OCURRENCIA_ACC"], errors="coerce")

    df = validar_coordenadas(df)
    df["puntaje_gravedad"] = calcular_puntaje_gravedad(df)
    df = df.reset_index(drop=True)
    return df
