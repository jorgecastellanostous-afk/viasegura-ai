"""
tests/test_data_utils.py — Unit tests for src/data_utils.py
"""
import pandas as pd
import pytest

from src.data_utils import (
    PUNTAJE_EPDO,
    calcular_puntaje_gravedad,
    limpiar_siniestros,
    validar_coordenadas,
)


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def df_valido():
    """DataFrame con coordenadas válidas dentro de Bogotá."""
    return pd.DataFrame({
        "LATITUD": [4.65, 4.72, 4.60],
        "LONGITUD": [-74.08, -74.05, -74.12],
        "GRAVEDAD": ["CON MUERTOS", "CON HERIDOS", "SOLO DAÑOS"],
        "FECHA_OCURRENCIA_ACC": [1483228800000, 1514764800000, 1546300800000],
    })


@pytest.fixture
def df_con_invalidos(df_valido):
    """Añade filas fuera del bbox de Bogotá."""
    extras = pd.DataFrame({
        "LATITUD": [6.0, 4.65, 0.0],      # 6.0 y 0.0 fuera de Bogotá
        "LONGITUD": [-74.08, -72.0, -74.08],  # -72.0 fuera
        "GRAVEDAD": ["SOLO DAÑOS", "SOLO DAÑOS", "SOLO DAÑOS"],
        "FECHA_OCURRENCIA_ACC": [0, 0, 0],
    })
    return pd.concat([df_valido, extras], ignore_index=True)


# ── validar_coordenadas ───────────────────────────────────────────────────

class TestValidarCoordenadas:
    def test_mantiene_filas_validas(self, df_valido):
        result = validar_coordenadas(df_valido)
        assert len(result) == len(df_valido)

    def test_elimina_fuera_de_bogota(self, df_con_invalidos):
        result = validar_coordenadas(df_con_invalidos)
        assert len(result) == 3  # solo las 3 válidas del df_valido

    def test_todos_fuera_retorna_vacio(self):
        df = pd.DataFrame({
            "LATITUD": [10.0, -5.0],
            "LONGITUD": [80.0, -80.0],
        })
        result = validar_coordenadas(df)
        assert len(result) == 0

    def test_no_modifica_original(self, df_con_invalidos):
        original_len = len(df_con_invalidos)
        validar_coordenadas(df_con_invalidos)
        assert len(df_con_invalidos) == original_len

    def test_preserva_otras_columnas(self, df_valido):
        result = validar_coordenadas(df_valido)
        assert "GRAVEDAD" in result.columns


# ── calcular_puntaje_gravedad ─────────────────────────────────────────────

class TestCalcularPuntajeGravedad:
    @pytest.mark.parametrize("gravedad,esperado", [
        ("SOLO DAÑOS",   1),
        ("SOLO DANOS",   1),
        ("CON HERIDOS",  3),
        ("CON MUERTOS",  5),
    ])
    def test_mapeo_correcto(self, gravedad, esperado):
        df = pd.DataFrame({"GRAVEDAD": [gravedad]})
        result = calcular_puntaje_gravedad(df)
        assert result.iloc[0] == esperado

    def test_valor_desconocido_default_1(self):
        df = pd.DataFrame({"GRAVEDAD": ["DESCONOCIDO", ""]})
        result = calcular_puntaje_gravedad(df)
        assert (result == 1).all()

    def test_epdo_muertos_vale_24(self):
        df = pd.DataFrame({"GRAVEDAD": ["CON MUERTOS"]})
        result = calcular_puntaje_gravedad(df, epdo=True)
        assert result.iloc[0] == PUNTAJE_EPDO["CON MUERTOS"]

    def test_retorna_series(self):
        df = pd.DataFrame({"GRAVEDAD": ["CON HERIDOS"]})
        result = calcular_puntaje_gravedad(df)
        assert isinstance(result, pd.Series)

    def test_tipo_int(self):
        df = pd.DataFrame({"GRAVEDAD": ["CON MUERTOS", "CON HERIDOS"]})
        result = calcular_puntaje_gravedad(df)
        assert result.dtype == int

    def test_columna_personalizada(self):
        df = pd.DataFrame({"TIPO": ["CON MUERTOS"]})
        result = calcular_puntaje_gravedad(df, columna="TIPO")
        assert result.iloc[0] == 5


# ── limpiar_siniestros ────────────────────────────────────────────────────

class TestLimpiarSiniestros:
    def test_agrega_columna_puntaje(self, df_valido):
        result = limpiar_siniestros(df_valido)
        assert "puntaje_gravedad" in result.columns

    def test_fecha_epoch_se_convierte(self, df_valido):
        result = limpiar_siniestros(df_valido)
        assert pd.api.types.is_datetime64_any_dtype(result["FECHA_OCURRENCIA_ACC"])

    def test_fecha_string_se_convierte(self):
        df = pd.DataFrame({
            "LATITUD": [4.65],
            "LONGITUD": [-74.08],
            "GRAVEDAD": ["CON HERIDOS"],
            "FECHA_OCURRENCIA_ACC": ["2019-06-15"],
        })
        result = limpiar_siniestros(df)
        assert pd.api.types.is_datetime64_any_dtype(result["FECHA_OCURRENCIA_ACC"])

    def test_elimina_coordenadas_invalidas(self, df_con_invalidos):
        result = limpiar_siniestros(df_con_invalidos)
        assert len(result) == 3

    def test_index_reset(self, df_con_invalidos):
        result = limpiar_siniestros(df_con_invalidos)
        assert list(result.index) == list(range(len(result)))

    def test_no_modifica_original(self, df_valido):
        original = df_valido.copy()
        limpiar_siniestros(df_valido)
        pd.testing.assert_frame_equal(df_valido, original)

    def test_puntaje_gravedad_valores(self, df_valido):
        result = limpiar_siniestros(df_valido)
        assert set(result["puntaje_gravedad"].unique()).issubset({1, 3, 5})
