"""
tests/test_geo_utils.py — Unit tests for src/geo_utils.py
"""

import pandas as pd
import pytest

from src.geo_utils import clasificar_hex, _GEO_AVAILABLE


# ── clasificar_hex ────────────────────────────────────────────────────────


class TestClasificarHex:
    @pytest.mark.parametrize(
        "ipi,expected",
        [
            (90.0, "Crítico (IPI≥90)"),
            (95.5, "Crítico (IPI≥90)"),
            (100.0, "Crítico (IPI≥90)"),
            (89.9, "Alto (75≤IPI<90)"),
            (75.0, "Alto (75≤IPI<90)"),
            (74.9, "Medio (50≤IPI<75)"),
            (50.0, "Medio (50≤IPI<75)"),
            (49.9, "Bajo (IPI<50)"),
            (0.0, "Bajo (IPI<50)"),
        ],
    )
    def test_limites(self, ipi, expected):
        assert clasificar_hex(ipi) == expected

    def test_retorna_string(self):
        assert isinstance(clasificar_hex(80.0), str)

    def test_categorias_son_cuatro(self):
        categorias = {clasificar_hex(ipi) for ipi in [10, 55, 80, 95]}
        assert len(categorias) == 4


# ── h3_to_polygon (solo si geopandas/h3 disponibles) ─────────────────────


@pytest.mark.skipif(not _GEO_AVAILABLE, reason="geopandas/h3 no disponibles")
class TestH3ToPolygon:
    SAMPLE_H3 = "8866e091cdfffff"  # hexágono real en Ciudad Bolívar, Bogotá

    def test_retorna_polygon(self):
        from shapely.geometry import Polygon
        from src.geo_utils import h3_to_polygon

        result = h3_to_polygon(self.SAMPLE_H3)
        assert isinstance(result, Polygon)

    def test_tiene_6_vertices(self):
        from src.geo_utils import h3_to_polygon

        result = h3_to_polygon(self.SAMPLE_H3)
        # H3 hexágono → 6 vértices + cierre = 7 coords en el exterior ring
        coords = list(result.exterior.coords)
        assert len(coords) == 7

    def test_coordenadas_en_bogota(self):
        from src.geo_utils import h3_to_polygon

        result = h3_to_polygon(self.SAMPLE_H3)
        lon_min, lat_min, lon_max, lat_max = result.bounds
        assert -74.5 < lon_min < -73.5, f"Longitud mínima fuera de Bogotá: {lon_min}"
        assert 4.0 < lat_min < 5.0, f"Latitud mínima fuera de Bogotá: {lat_min}"

    def test_es_valido(self):
        from src.geo_utils import h3_to_polygon

        result = h3_to_polygon(self.SAMPLE_H3)
        assert result.is_valid

    def test_no_vacio(self):
        from src.geo_utils import h3_to_polygon

        result = h3_to_polygon(self.SAMPLE_H3)
        assert not result.is_empty


# ── asignar_h3 ────────────────────────────────────────────────────────────


@pytest.mark.skipif(not _GEO_AVAILABLE, reason="geopandas/h3 no disponibles")
class TestAsignarH3:
    def test_retorna_series_strings(self):
        import pandas as pd
        from src.geo_utils import asignar_h3

        df = pd.DataFrame(
            {
                "LATITUD": [4.651, 4.720],
                "LONGITUD": [-74.082, -74.050],
            }
        )
        result = asignar_h3(df)
        assert len(result) == 2
        assert all(isinstance(v, str) for v in result)

    def test_mismo_punto_mismo_h3(self):
        import pandas as pd
        from src.geo_utils import asignar_h3

        df = pd.DataFrame(
            {
                "LATITUD": [4.651, 4.651],
                "LONGITUD": [-74.082, -74.082],
            }
        )
        result = asignar_h3(df)
        assert result.iloc[0] == result.iloc[1]

    def test_puntos_lejanos_diferentes_h3(self):
        import pandas as pd
        from src.geo_utils import asignar_h3

        # Bogotá norte vs sur — deben caer en hexágonos distintos
        df = pd.DataFrame(
            {
                "LATITUD": [4.80, 4.45],
                "LONGITUD": [-74.05, -74.12],
            }
        )
        result = asignar_h3(df)
        assert result.iloc[0] != result.iloc[1]


# ── agregar_por_hexagono ──────────────────────────────────────────────────


@pytest.mark.skipif(not _GEO_AVAILABLE, reason="geopandas/h3 no disponibles")
class TestAgregarPorHexagono:
    @pytest.fixture
    def gdf_zonas(self):
        import geopandas as gpd
        from shapely.geometry import Point
        from src.geo_utils import asignar_h3

        df = pd.DataFrame(
            {
                "LATITUD": [4.651, 4.652, 4.720],
                "LONGITUD": [-74.082, -74.083, -74.050],
                "IPI": [90.0, 85.0, 70.0],
                "cantidad_siniestros": [100, 80, 50],
                "criticidad_total": [300, 240, 150],
                "siniestros_con_muertos": [5, 3, 1],
                "localidad_predominante": ["SANTA FE", "SANTA FE", "KENNEDY"],
                "prioridad_IPI": [
                    "Prioridad 1 - Intervención prioritaria",
                    "Prioridad 1 - Intervención prioritaria",
                    "Prioridad 2 - Auditoría de seguridad vial",
                ],
            }
        )
        df["h3_id"] = asignar_h3(df, lat_col="LATITUD", lon_col="LONGITUD")
        geometry = [Point(lon, lat) for lat, lon in zip(df["LATITUD"], df["LONGITUD"])]
        return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    def test_retorna_geodataframe(self, gdf_zonas):
        import geopandas as gpd
        from src.geo_utils import agregar_por_hexagono

        result = agregar_por_hexagono(gdf_zonas)
        assert isinstance(result, gpd.GeoDataFrame)

    def test_una_fila_por_hexagono(self, gdf_zonas):
        from src.geo_utils import agregar_por_hexagono

        result = agregar_por_hexagono(gdf_zonas)
        n_hexagonos = gdf_zonas["h3_id"].nunique()
        assert len(result) == n_hexagonos

    def test_columnas_presentes(self, gdf_zonas):
        from src.geo_utils import agregar_por_hexagono

        result = agregar_por_hexagono(gdf_zonas)
        for col in ["IPI_hex", "siniestros_total", "localidad", "categoria", "geometry"]:
            assert col in result.columns

    def test_ipi_hex_es_maximo(self, gdf_zonas):
        from src.geo_utils import agregar_por_hexagono

        result = agregar_por_hexagono(gdf_zonas)
        # IPI_hex debe ser el máximo de las zonas en el hexágono
        for _, row in result.iterrows():
            zonas_en_hex = gdf_zonas[gdf_zonas["h3_id"] == row["h3_id"]]
            assert row["IPI_hex"] == pytest.approx(zonas_en_hex["IPI"].max())

    def test_crs_epsg4326(self, gdf_zonas):
        from src.geo_utils import agregar_por_hexagono

        result = agregar_por_hexagono(gdf_zonas)
        assert result.crs.to_epsg() == 4326


# ── _require_geo error path ───────────────────────────────────────────────


def test_require_geo_raises_when_unavailable():
    import src.geo_utils as geo

    original = geo._GEO_AVAILABLE
    geo._GEO_AVAILABLE = False
    try:
        with pytest.raises(ImportError, match="geopandas"):
            geo._require_geo()
    finally:
        geo._GEO_AVAILABLE = original
