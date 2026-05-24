"""
tests/test_data_loader.py — Smoke tests for app/data_loader.py

st.cache_data works outside a Streamlit runtime (MemoryCacheStorageManager).
No mocking needed — tests use real data files from outputs/.
"""

import logging
import sys
from pathlib import Path

import pandas as pd
import pytest

# conftest.py guarantees ROOT in sys.path; explicit here for standalone runs
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Guard 1: skip entire module if streamlit is not installed (CI test job)
pytest.importorskip("streamlit")

# Guard 2: skip if the full dataset is absent (CI stub or fresh clone)
from config import MAPS, REPORTS  # noqa: E402

_REQUIRED_FILES = [
    REPORTS / "zonas_criticas_IPI_completo_2016_2019.csv",
    REPORTS / "ipi_por_localidad_stats.csv",
    REPORTS / "top_vias_criticas_geoespacial.csv",
    REPORTS / "top_barrios_criticos_geoespacial.csv",
    MAPS / "mapa_top50_IPI_final_2016_2019.html",
]
if not all(p.exists() for p in _REQUIRED_FILES):
    pytest.skip("Dataset completo no disponible — ejecuta NB01-NB04", allow_module_level=True)

# Suppress Streamlit's "No runtime found" log message
logging.getLogger("streamlit").setLevel(logging.ERROR)

from app.data_loader import (  # noqa: E402
    cargar_gdf_hexagonos,
    cargar_gdf_localidades,
    cargar_ipi,
    cargar_ipi_por_localidad,
    cargar_top_barrios,
    cargar_top_vias,
    html_mapa,
    metricas_globales,
)


# ── cargar_ipi ─────────────────────────────────────────────────────────────


class TestCargarIPI:
    _COLS = (
        "IPI",
        "prioridad_IPI",
        "cantidad_siniestros",
        "siniestros_con_muertos",
        "anios_activos",
    )

    def test_retorna_dataframe(self):
        assert isinstance(cargar_ipi(), pd.DataFrame)

    def test_tiene_filas_suficientes(self):
        assert len(cargar_ipi()) > 1_000

    def test_columnas_clave_presentes(self):
        df = cargar_ipi()
        for col in self._COLS:
            assert col in df.columns, f"Falta columna: {col}"

    def test_ipi_en_rango_0_100(self):
        assert cargar_ipi()["IPI"].between(0, 100).all()

    def test_no_vacio(self):
        assert not cargar_ipi().empty


# ── cargar_ipi_por_localidad ─────────────��────────────────────���────────────


class TestCargarIPIPorLocalidad:
    _COLS = ("localidad", "n_zonas", "ipi_max", "ipi_medio")

    def test_retorna_dataframe(self):
        assert isinstance(cargar_ipi_por_localidad(), pd.DataFrame)

    def test_tiene_al_menos_10_localidades(self):
        assert len(cargar_ipi_por_localidad()) >= 10

    def test_columnas_clave_presentes(self):
        df = cargar_ipi_por_localidad()
        for col in self._COLS:
            assert col in df.columns, f"Falta columna: {col}"


# ── cargar_top_vias ───────────────────────���────────────────────────────────


class TestCargarTopVias:
    _COLS = ("via_predominante", "n_zonas", "ipi_max", "siniestros")

    def test_retorna_dataframe(self):
        assert isinstance(cargar_top_vias(), pd.DataFrame)

    def test_tiene_filas(self):
        assert len(cargar_top_vias()) > 0

    def test_columnas_clave_presentes(self):
        df = cargar_top_vias()
        for col in self._COLS:
            assert col in df.columns, f"Falta columna: {col}"


# ── cargar_top_barrios ───────────���─────────────────────────���───────────────


class TestCargarTopBarrios:
    _COLS = ("localidad_predominante", "barrio_predominante", "n_zonas", "ipi_max")

    def test_retorna_dataframe(self):
        assert isinstance(cargar_top_barrios(), pd.DataFrame)

    def test_tiene_filas(self):
        assert len(cargar_top_barrios()) > 0

    def test_columnas_clave_presentes(self):
        df = cargar_top_barrios()
        for col in self._COLS:
            assert col in df.columns, f"Falta columna: {col}"


# ── metricas_globales ───────────────���───────────────────────────────��──────


class TestMetricasGlobales:
    _CLAVES = (
        "total_zonas",
        "total_siniestros",
        "total_muertos",
        "zonas_p1",
        "ipi_max",
        "ipi_medio",
        "localidad_top",
        "via_top",
        "persistentes_4a",
    )

    def test_retorna_dict(self):
        assert isinstance(metricas_globales(), dict)

    def test_contiene_todas_las_claves(self):
        m = metricas_globales()
        for k in self._CLAVES:
            assert k in m, f"Falta clave: {k}"

    def test_total_siniestros_positivo(self):
        assert metricas_globales()["total_siniestros"] > 0

    def test_total_muertos_no_negativo(self):
        assert metricas_globales()["total_muertos"] >= 0

    def test_ipi_max_en_rango(self):
        assert 0 < metricas_globales()["ipi_max"] <= 100

    def test_zonas_p1_razonable(self):
        # P1 = top 50 por definición, no debería exceder 100
        assert 0 < metricas_globales()["zonas_p1"] <= 100

    def test_localidad_top_es_string_no_vacio(self):
        val = metricas_globales()["localidad_top"]
        assert isinstance(val, str) and len(val) > 0


# ── html_mapa ────────────────────────────────��─────────────────────────────


class TestHtmlMapa:
    _MAPA_REAL = "mapa_top50_IPI_final_2016_2019.html"

    def test_retorna_string_para_mapa_existente(self):
        assert isinstance(html_mapa(self._MAPA_REAL), str)

    def test_contenido_no_trivial(self):
        assert len(html_mapa(self._MAPA_REAL)) > 100

    def test_retorna_string_para_mapa_inexistente(self):
        assert isinstance(html_mapa("no_existe.html"), str)

    def test_fallback_indica_error(self):
        html = html_mapa("no_existe.html")
        assert "color:red" in html or "no encontrado" in html.lower()


# ── cargar_gdf_hexagonos / cargar_gdf_localidades ───────────────���─────────


class TestCargarGDFs:
    def test_hexagonos_retorna_geodataframe(self):
        gpd = pytest.importorskip("geopandas")
        gdf = cargar_gdf_hexagonos()
        assert isinstance(gdf, gpd.GeoDataFrame)

    def test_hexagonos_tiene_filas(self):
        pytest.importorskip("geopandas")
        assert len(cargar_gdf_hexagonos()) > 0

    def test_localidades_retorna_geodataframe(self):
        gpd = pytest.importorskip("geopandas")
        gdf = cargar_gdf_localidades()
        assert isinstance(gdf, gpd.GeoDataFrame)

    def test_localidades_geometrias_validas(self):
        pytest.importorskip("geopandas")
        gdf = cargar_gdf_localidades()
        assert gdf.geometry.is_valid.all()
