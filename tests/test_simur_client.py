"""
tests/test_simur_client.py — Unit tests for src/simur_client.py

HTTP calls are mocked so no network is needed.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.simur_client import agregar_por_zona, CAMPO_JOIN


# ── agregar_por_zona ──────────────────────────────────────────────────────


class TestAgregarPorZona:
    @pytest.fixture
    def df_actor(self):
        """Datos mínimos: 2 zonas, 4 formularios, campo CONDICION."""
        return pd.DataFrame(
            {
                CAMPO_JOIN: ["F001", "F001", "F002", "F003"],
                "CONDICION": ["CONDUCTOR", "CONDUCTOR", "PEATÓN", "CONDUCTOR"],
            }
        )

    @pytest.fixture
    def zona_a_forms(self):
        return {
            "zona_A": ["F001", "F002"],
            "zona_B": ["F003"],
            "zona_C": ["F999"],  # formulario sin datos
        }

    def test_retorna_dict(self, df_actor, zona_a_forms):
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        assert isinstance(result, dict)

    def test_claves_son_las_zonas(self, df_actor, zona_a_forms):
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        assert set(result.keys()) == set(zona_a_forms.keys())

    def test_estructura_por_zona(self, df_actor, zona_a_forms):
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        for zona, data in result.items():
            assert "moda" in data
            assert "distribucion" in data
            assert "n_registros" in data
            assert "cobertura_pct" in data
            assert "hhi" in data

    def test_moda_zona_a(self, df_actor, zona_a_forms):
        """zona_A: F001→CONDUCTOR×2, F002→PEATÓN×1 → moda=CONDUCTOR."""
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        assert result["zona_A"]["moda"] == "CONDUCTOR"

    def test_n_registros_zona_a(self, df_actor, zona_a_forms):
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        assert result["zona_A"]["n_registros"] == 3  # 2 de F001 + 1 de F002

    def test_cobertura_100_pct_cuando_todos_tienen_datos(self, df_actor, zona_a_forms):
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        # zona_A tiene F001 y F002, ambos con datos
        assert result["zona_A"]["cobertura_pct"] == 100.0

    def test_zona_sin_datos_tiene_none(self, df_actor, zona_a_forms):
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        assert result["zona_C"]["moda"] is None
        assert result["zona_C"]["hhi"] is None
        assert result["zona_C"]["n_registros"] == 0

    def test_cobertura_0_pct_cuando_nadie_tiene_datos(self, df_actor, zona_a_forms):
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        assert result["zona_C"]["cobertura_pct"] == 0.0

    def test_hhi_monopolio_es_10000(self):
        """Si todos los registros son del mismo valor, HHI = 10000."""
        df = pd.DataFrame(
            {
                CAMPO_JOIN: ["F001", "F001", "F001"],
                "CONDICION": ["CONDUCTOR", "CONDUCTOR", "CONDUCTOR"],
            }
        )
        zona_a_forms = {"zona_X": ["F001"]}
        result = agregar_por_zona(df, "CONDICION", zona_a_forms)
        assert result["zona_X"]["hhi"] == 10000.0

    def test_hhi_distribucion_uniforme_es_menor_a_10000(self):
        """Con 2 valores iguales (50/50) el HHI = 5000."""
        df = pd.DataFrame(
            {
                CAMPO_JOIN: ["F001", "F001"],
                "CONDICION": ["CONDUCTOR", "PEATÓN"],
            }
        )
        zona_a_forms = {"zona_X": ["F001"]}
        result = agregar_por_zona(df, "CONDICION", zona_a_forms)
        assert result["zona_X"]["hhi"] == pytest.approx(5000.0)

    def test_distribucion_suma_100(self, df_actor, zona_a_forms):
        result = agregar_por_zona(df_actor, "CONDICION", zona_a_forms)
        for zona, data in result.items():
            if data["distribucion"]:
                total = sum(data["distribucion"].values())
                assert abs(total - 100.0) < 0.2, f"Distribución de {zona} no suma 100%: {total}"

    def test_ignora_valores_nulos(self):
        """None y cadenas vacías no deben contar como valores válidos."""
        df = pd.DataFrame(
            {
                CAMPO_JOIN: ["F001", "F001", "F001"],
                "CONDICION": ["CONDUCTOR", None, ""],
            }
        )
        zona_a_forms = {"zona_X": ["F001"]}
        result = agregar_por_zona(df, "CONDICION", zona_a_forms)
        assert result["zona_X"]["n_registros"] == 1
        assert result["zona_X"]["moda"] == "CONDUCTOR"


# ── descargar_por_formularios (mocked HTTP) ───────────────────────────────


class TestDescargarPorFormularios:
    def test_retorna_dataframe_vacio_si_no_hay_features(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"features": []}

        with patch("src.simur_client.requests.post", return_value=mock_response):
            from src.simur_client import descargar_por_formularios

            result = descargar_por_formularios(
                layer_id=3,
                formularios=["F001", "F002"],
            )
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_retorna_dataframe_con_atributos(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "features": [
                {"attributes": {"FORMULARIO": "F001", "CONDICION": "CONDUCTOR"}},
                {"attributes": {"FORMULARIO": "F002", "CONDICION": "PEATÓN"}},
            ]
        }

        with patch("src.simur_client.requests.post", return_value=mock_response):
            from src.simur_client import descargar_por_formularios

            result = descargar_por_formularios(
                layer_id=3,
                formularios=["F001", "F002"],
            )
        assert len(result) == 2
        assert "CONDICION" in result.columns

    def test_lista_vacia_retorna_dataframe_vacio(self):
        with patch("src.simur_client.requests.post") as mock_post:
            from src.simur_client import descargar_por_formularios

            result = descargar_por_formularios(layer_id=3, formularios=[])
        mock_post.assert_not_called()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# ── descargar_accidentes_por_anio_seguro (mocked HTTP) ────────────────────


class TestDescargarAccidentesPorAnio:
    def _make_count_response(self, count):
        m = MagicMock()
        m.json.return_value = {"count": count}
        return m

    def _make_features_response(self, rows):
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = {"features": [{"properties": r} for r in rows]}
        return m

    def _make_empty_response(self):
        m = MagicMock()
        m.status_code = 200
        m.json.return_value = {"features": []}
        return m

    def test_retorna_none_si_total_cero(self):
        with patch("src.simur_client.requests.get", return_value=self._make_count_response(0)):
            from src.simur_client import descargar_accidentes_por_anio_seguro

            result = descargar_accidentes_por_anio_seguro(anio=2019)
        assert result is None

    def test_descarga_pagina_unica(self):
        rows = [{"FORMULARIO": f"F{i:04}", "GRAVEDAD": "CON HERIDOS"} for i in range(5)]
        responses = [
            self._make_count_response(5),
            self._make_features_response(rows),
            self._make_empty_response(),
        ]
        with (
            patch("src.simur_client.requests.get", side_effect=responses),
            patch("src.simur_client.time.sleep"),
        ):
            from src.simur_client import descargar_accidentes_por_anio_seguro

            result = descargar_accidentes_por_anio_seguro(
                anio=2019,
                registros_por_bloque=10,
            )
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert "GRAVEDAD" in result.columns

    def test_descarga_multiples_paginas(self):
        rows_p1 = [{"FORMULARIO": f"F{i:04}"} for i in range(3)]
        rows_p2 = [{"FORMULARIO": f"F{i:04}"} for i in range(3, 5)]
        responses = [
            self._make_count_response(5),
            self._make_features_response(rows_p1),
            self._make_features_response(rows_p2),
            self._make_empty_response(),
        ]
        with (
            patch("src.simur_client.requests.get", side_effect=responses),
            patch("src.simur_client.time.sleep"),
        ):
            from src.simur_client import descargar_accidentes_por_anio_seguro

            result = descargar_accidentes_por_anio_seguro(
                anio=2019,
                registros_por_bloque=3,
            )
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5

    def test_carga_desde_cache(self, tmp_path):
        cache_file = tmp_path / "accidentes_2019_offset_0.csv"
        pd.DataFrame({"FORMULARIO": ["F001"], "GRAVEDAD": ["CON MUERTOS"]}).to_csv(
            cache_file, index=False
        )
        count_resp = self._make_count_response(1)
        with (
            patch("src.simur_client.requests.get", return_value=count_resp),
            patch("src.simur_client.time.sleep"),
        ):
            from src.simur_client import descargar_accidentes_por_anio_seguro

            result = descargar_accidentes_por_anio_seguro(
                anio=2019,
                ruta_chunks=tmp_path,
            )
        assert result is not None
        assert result["GRAVEDAD"].iloc[0] == "CON MUERTOS"

    def test_retorna_none_si_todos_los_intentos_fallan(self):
        error_response = MagicMock()
        error_response.status_code = 500
        error_response.json.return_value = {}
        responses = [
            self._make_count_response(10),
            *[error_response] * 5,  # max_reintentos=5 failures
        ]
        with (
            patch("src.simur_client.requests.get", side_effect=responses),
            patch("src.simur_client.time.sleep"),
        ):
            from src.simur_client import descargar_accidentes_por_anio_seguro

            result = descargar_accidentes_por_anio_seguro(
                anio=2019,
                registros_por_bloque=10,
                max_reintentos=5,
            )
        assert result is None
