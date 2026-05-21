"""
tests/test_config.py — Tests de config.py y estructura del proyecto
====================================================================
Verifica que las rutas del proyecto sean correctas y que los datos
base ya descargados existan.
"""
import sys
from pathlib import Path

import pytest

# ── Asegurar que la raíz del proyecto está en el path ───────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import (
    PROJECT_ROOT,
    DATA_RAW,
    DATA_PROCESSED,
    REPORTS,
    MAPS,
    NOTEBOOKS,
    APP,
    SQL,
)


class TestConfigRutas:
    """config.py retorna rutas absolutas y correctas."""

    def test_project_root_es_absoluto(self):
        assert PROJECT_ROOT.is_absolute()

    def test_project_root_contiene_config_py(self):
        assert (PROJECT_ROOT / "config.py").exists()

    def test_data_raw_existe(self):
        assert DATA_RAW.exists(), f"Carpeta no existe: {DATA_RAW}"

    def test_data_processed_existe(self):
        assert DATA_PROCESSED.exists(), f"Carpeta no existe: {DATA_PROCESSED}"

    def test_reports_existe(self):
        assert REPORTS.exists(), f"Carpeta no existe: {REPORTS}"

    def test_maps_existe(self):
        assert MAPS.exists(), f"Carpeta no existe: {MAPS}"

    def test_notebooks_existe(self):
        assert NOTEBOOKS.exists()

    def test_rutas_son_absolutas(self):
        for p in [DATA_RAW, DATA_PROCESSED, REPORTS, MAPS, NOTEBOOKS, APP, SQL]:
            assert p.is_absolute(), f"No es absoluta: {p}"


class TestDatosBase:
    """Los archivos de datos base (2016-2019) existen en disco."""

    def test_csv_limpio_existe(self):
        csv = DATA_PROCESSED / "accidentes_bogota_2016_2019_limpio.csv"
        assert csv.exists(), (
            f"CSV limpio no encontrado en {csv}. "
            "Ejecuta NB01 para generarlo."
        )

    def test_csv_limpio_no_vacio(self):
        csv = DATA_PROCESSED / "accidentes_bogota_2016_2019_limpio.csv"
        if not csv.exists():
            pytest.skip("CSV limpio no existe — ejecuta NB01")
        assert csv.stat().st_size > 1_000_000, (
            f"CSV limpio parece vacío: {csv.stat().st_size} bytes"
        )

    def test_chunks_folder_existe(self):
        chunks = DATA_RAW / "chunks_accidentes_2016_2019"
        assert chunks.exists(), f"Carpeta de chunks no existe: {chunks}"

    def test_chunks_tienen_archivos(self):
        chunks = DATA_RAW / "chunks_accidentes_2016_2019"
        if not chunks.exists():
            pytest.skip("Carpeta de chunks no existe")
        csvs = list(chunks.glob("accidentes_201*.csv"))
        assert len(csvs) >= 4, (
            f"Se esperan ≥4 chunks (uno por año), encontrados: {len(csvs)}"
        )

    def test_ipi_csv_existe(self):
        ipi = REPORTS / "zonas_criticas_IPI_completo_2016_2019.csv"
        assert ipi.exists(), (
            f"CSV de IPI no encontrado en {ipi}. "
            "Ejecuta NB02 para generarlo."
        )

    def test_ipi_top50_existe(self):
        top50 = REPORTS / "top50_IPI_final_2016_2019.csv"
        assert top50.exists(), (
            f"CSV top50 no encontrado en {top50}. Ejecuta NB02."
        )


class TestNotebooks:
    """Los notebooks del proyecto existen."""

    @pytest.mark.parametrize("nb_name", [
        "01_exploracion_datos_siniestralidad.ipynb",
        "02_indice_criticidad_y_hotspots.ipynb",
        "03_validacion_actualidad_y_enriquecimiento_simur.ipynb",
        "03.5_sintesis_metodologica_y_documentacion.ipynb",
    ])
    def test_notebook_existe(self, nb_name):
        nb_path = NOTEBOOKS / nb_name
        assert nb_path.exists(), f"Notebook no encontrado: {nb_path}"
