"""Geospatial utilities: H3 hexagonal grid, spatial joins (from NB04.5)."""

from __future__ import annotations

import pandas as pd

try:
    import h3 as _h3
    import geopandas as gpd
    from shapely.geometry import Polygon

    _GEO_AVAILABLE = True
except ImportError:
    _GEO_AVAILABLE = False

RES_H3 = 8  # ~460 m diameter hexagons — appropriate for urban Bogotá analysis

# IPI category labels (used for coloring in maps)
CATEGORIAS_IPI = {
    "Crítico (IPI≥90)": "#d73027",
    "Alto (75≤IPI<90)": "#fc8d59",
    "Medio (50≤IPI<75)": "#fee08b",
    "Bajo (IPI<50)": "#91bfdb",
}


def _require_geo() -> None:
    if not _GEO_AVAILABLE:
        raise ImportError("geopandas, h3, and shapely are required for geo_utils")


def h3_to_polygon(h3_id: str) -> "Polygon":
    """Convert an H3 cell ID to a Shapely Polygon (lon, lat order)."""
    _require_geo()
    boundary = _h3.cell_to_boundary(h3_id)  # returns list of (lat, lon)
    return Polygon([(lon, lat) for lat, lon in boundary])


def asignar_h3(df: pd.DataFrame, lat_col: str = "LATITUD", lon_col: str = "LONGITUD") -> pd.Series:
    """Return a Series of H3 cell IDs at RES_H3 for each row in df."""
    _require_geo()
    return df.apply(
        lambda row: _h3.latlng_to_cell(row[lat_col], row[lon_col], RES_H3),
        axis=1,
    )


def agregar_por_hexagono(
    gdf_zonas: "gpd.GeoDataFrame",
    h3_col: str = "h3_id",
) -> "gpd.GeoDataFrame":
    """Aggregate zone-level IPI data to H3 hexagon level.

    Returns a GeoDataFrame with one row per hexagon and polygon geometry.
    """
    _require_geo()

    agg = (
        gdf_zonas.groupby(h3_col)
        .agg(
            n_zonas=("IPI", "count"),
            IPI_hex=("IPI", "max"),
            ipi_mean=("IPI", "mean"),
            ipi_sum=("IPI", "sum"),
            siniestros_total=("cantidad_siniestros", "sum"),
            criticidad_total=("criticidad_total", "sum"),
            siniestros_muertos=("siniestros_con_muertos", "sum"),
            localidad=("localidad_predominante", lambda x: x.value_counts().idxmax()),
            prioridad_dominante=("prioridad_IPI", lambda x: x.value_counts().idxmax()),
        )
        .reset_index()
    )

    agg["geometry"] = agg[h3_col].apply(h3_to_polygon)
    agg["centroid_lat"] = agg["geometry"].apply(lambda g: g.centroid.y)
    agg["centroid_lon"] = agg["geometry"].apply(lambda g: g.centroid.x)
    agg["categoria"] = agg["IPI_hex"].apply(clasificar_hex)

    return gpd.GeoDataFrame(agg, geometry="geometry", crs="EPSG:4326")


def clasificar_hex(ipi: float) -> str:
    """Classify a hexagon by its max IPI value into a display category."""
    if ipi >= 90:
        return "Crítico (IPI≥90)"
    elif ipi >= 75:
        return "Alto (75≤IPI<90)"
    elif ipi >= 50:
        return "Medio (50≤IPI<75)"
    return "Bajo (IPI<50)"
