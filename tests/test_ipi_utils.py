"""
tests/test_ipi_utils.py — Unit tests for src/ipi_utils.py
"""

import pandas as pd
import pytest

from src.ipi_utils import (
    PESOS_1_3_5,
    PESOS_EPDO,
    SCORES_COLS,
    asignar_prioridad_ipi,
    asignar_tipologia_nb05,
    calcular_ipi,
    calcular_ipi_pesos_alternativos,
    calcular_rankings_duales,
    calcular_tasas_exposicion,
    clasificar_familia_analitica,
    clasificar_hotspot,
    comparar_rankings_ipi,
)


# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def zonas_simple():
    """5 zonas con valores monotónicamente crecientes para facilitar verificación."""
    return pd.DataFrame(
        {
            "cantidad_siniestros": [10, 50, 100, 200, 500],
            "criticidad_total": [30, 150, 300, 600, 1500],
            "criticidad_promedio": [3.0, 3.0, 3.0, 3.0, 3.0],
            "anios_activos": [1, 2, 3, 4, 4],
            "siniestros_con_muertos": [0, 2, 5, 10, 20],
        }
    )


# ── calcular_ipi ──────────────────────────────────────────────────────────


class TestCalcularIPI:
    def test_retorna_dataframe(self, zonas_simple):
        result = calcular_ipi(zonas_simple)
        assert isinstance(result, pd.DataFrame)

    def test_columnas_scores_presentes(self, zonas_simple):
        result = calcular_ipi(zonas_simple)
        for col in SCORES_COLS:
            assert col in result.columns, f"Falta columna: {col}"

    def test_columna_ipi_presente(self, zonas_simple):
        result = calcular_ipi(zonas_simple)
        assert "IPI" in result.columns

    def test_ipi_en_rango_0_100(self, zonas_simple):
        result = calcular_ipi(zonas_simple)
        assert (result["IPI"] >= 0).all()
        assert (result["IPI"] <= 100).all()

    def test_scores_en_rango_0_1(self, zonas_simple):
        result = calcular_ipi(zonas_simple)
        for col in SCORES_COLS:
            assert (result[col] >= 0).all(), f"{col} tiene valores <0"
            assert (result[col] <= 1).all(), f"{col} tiene valores >1"

    def test_mayor_volumen_mayor_ipi(self, zonas_simple):
        result = calcular_ipi(zonas_simple)
        # La zona con más siniestros (idx 4) debe tener el IPI más alto
        assert result["IPI"].idxmax() == 4

    def test_menor_volumen_menor_ipi(self, zonas_simple):
        result = calcular_ipi(zonas_simple)
        assert result["IPI"].idxmin() == 0

    def test_no_modifica_original(self, zonas_simple):
        original_cols = list(zonas_simple.columns)
        calcular_ipi(zonas_simple)
        assert list(zonas_simple.columns) == original_cols

    def test_ipi_es_media_scores_por_100(self, zonas_simple):
        result = calcular_ipi(zonas_simple)
        for idx, row in result.iterrows():
            expected = row[SCORES_COLS].mean() * 100
            assert abs(row["IPI"] - expected) < 1e-9, (
                f"Fila {idx}: IPI={row['IPI']:.4f}, esperado={expected:.4f}"
            )

    def test_una_zona(self):
        df = pd.DataFrame(
            {
                "cantidad_siniestros": [100],
                "criticidad_total": [300],
                "criticidad_promedio": [3.0],
                "anios_activos": [4],
                "siniestros_con_muertos": [5],
            }
        )
        result = calcular_ipi(df)
        assert len(result) == 1
        # Con una sola zona, rank(pct=True) = 1.0 para todos los rank-based scores
        assert result["IPI"].iloc[0] > 0


# ── asignar_prioridad_ipi ─────────────────────────────────────────────────


class TestAsignarPrioridadIPI:
    @pytest.mark.parametrize(
        "rank,expected_prefix",
        [
            (1, "Prioridad 1"),
            (50, "Prioridad 1"),
            (51, "Prioridad 2"),
            (200, "Prioridad 2"),
            (201, "Prioridad 3"),
            (500, "Prioridad 3"),
            (501, "Seguimiento"),
            (9999, "Seguimiento"),
        ],
    )
    def test_limites_de_prioridad(self, rank, expected_prefix):
        result = asignar_prioridad_ipi(rank)
        assert result.startswith(expected_prefix), (
            f"rank={rank}: esperado '{expected_prefix}', obtenido '{result}'"
        )

    def test_retorna_string(self):
        assert isinstance(asignar_prioridad_ipi(1), str)

    def test_p1_tiene_50_zonas_max(self):
        """Exactamente 50 zonas deben ser Prioridad 1 (ranks 1-50)."""
        p1 = [asignar_prioridad_ipi(r) for r in range(1, 10001)]
        count_p1 = sum(1 for s in p1 if s.startswith("Prioridad 1"))
        assert count_p1 == 50

    def test_p2_tiene_150_zonas(self):
        """Zonas 51-200 son Prioridad 2 → 150 zonas."""
        p2 = [asignar_prioridad_ipi(r) for r in range(1, 10001)]
        count_p2 = sum(1 for s in p2 if s.startswith("Prioridad 2"))
        assert count_p2 == 150

    def test_p3_tiene_300_zonas(self):
        """Zonas 201-500 son Prioridad 3 → 300 zonas."""
        p3 = [asignar_prioridad_ipi(r) for r in range(1, 10001)]
        count_p3 = sum(1 for s in p3 if s.startswith("Prioridad 3"))
        assert count_p3 == 300


# ── clasificar_familia_analitica ──────────────────────────────────────────


class TestClasificarFamiliaAnalitica:
    def _row(self, rank_ipi, rank_criticidad, rank_muertes=9999, rank_volumen=9999):
        return pd.Series(
            {
                "rank_IPI": rank_ipi,
                "rank_criticidad_total": rank_criticidad,
                "rank_muertes": rank_muertes,
                "rank_volumen": rank_volumen,
            }
        )

    def test_robusto_integral(self):
        row = self._row(rank_ipi=100, rank_criticidad=100)
        assert clasificar_familia_analitica(row) == "Hotspot robusto integral"

    def test_severidad_fatalidad(self):
        row = self._row(rank_ipi=100, rank_criticidad=300, rank_muertes=100)
        assert clasificar_familia_analitica(row) == "Hotspot de severidad/fatalidad"

    def test_carga_acumulada(self):
        row = self._row(rank_ipi=300, rank_criticidad=100)
        assert clasificar_familia_analitica(row) == "Hotspot de carga acumulada"

    def test_preventivo_prioritario(self):
        row = self._row(rank_ipi=400, rank_criticidad=300, rank_muertes=400)
        assert clasificar_familia_analitica(row) == "Hotspot preventivo prioritario"

    def test_seguimiento(self):
        row = self._row(rank_ipi=600, rank_criticidad=600)
        assert clasificar_familia_analitica(row) == "Seguimiento"

    def test_retorna_string(self):
        row = self._row(rank_ipi=1, rank_criticidad=1)
        assert isinstance(clasificar_familia_analitica(row), str)


# ── clasificar_hotspot (legacy) ───────────────────────────────────────────


class TestClasificarHotspot:
    def _row(self, cantidad, criticidad_promedio, anios_activos):
        return pd.Series(
            {
                "cantidad_siniestros": cantidad,
                "criticidad_promedio": criticidad_promedio,
                "anios_activos": anios_activos,
            }
        )

    def test_estructural_persistente(self):
        row = self._row(cantidad=350, criticidad_promedio=1.5, anios_activos=4)
        assert clasificar_hotspot(row) == "Hotspot estructural persistente"

    def test_severo(self):
        row = self._row(cantidad=200, criticidad_promedio=2.5, anios_activos=2)
        assert clasificar_hotspot(row) == "Hotspot severo"

    def test_alto_volumen(self):
        row = self._row(cantidad=400, criticidad_promedio=1.5, anios_activos=2)
        assert clasificar_hotspot(row) == "Hotspot de alto volumen"

    def test_persistente_media_alta(self):
        row = self._row(cantidad=200, criticidad_promedio=1.8, anios_activos=3)
        assert clasificar_hotspot(row) == "Hotspot persistente con severidad media-alta"

    def test_exploratorio(self):
        row = self._row(cantidad=10, criticidad_promedio=1.2, anios_activos=1)
        assert clasificar_hotspot(row) == "Hotspot exploratorio"


# ── B3.1: calcular_ipi_pesos_alternativos ─────────────────────────────────


class TestCalcularIPIPesosAlternativos:
    @pytest.fixture
    def zonas_simple(self):
        return pd.DataFrame(
            {
                "cantidad_siniestros": [10, 50, 100, 200, 500],
                "criticidad_total": [30, 150, 300, 600, 1500],
                "criticidad_promedio": [3.0, 3.0, 3.0, 3.0, 3.0],
                "anios_activos": [1, 2, 3, 4, 4],
                "siniestros_con_muertos": [0, 2, 5, 10, 20],
            }
        )

    def test_retorna_dataframe_con_ipi_alt(self, zonas_simple):
        result = calcular_ipi_pesos_alternativos(zonas_simple)
        assert "IPI_alt" in result.columns

    def test_ipi_alt_en_rango_0_100(self, zonas_simple):
        result = calcular_ipi_pesos_alternativos(zonas_simple)
        assert (result["IPI_alt"] >= 0).all()
        assert (result["IPI_alt"] <= 100).all()

    def test_no_modifica_columnas_ipi_original(self, zonas_simple):
        result = calcular_ipi_pesos_alternativos(zonas_simple)
        assert "IPI" not in result.columns

    def test_no_modifica_dataframe_original(self, zonas_simple):
        original_cols = list(zonas_simple.columns)
        calcular_ipi_pesos_alternativos(zonas_simple)
        assert list(zonas_simple.columns) == original_cols

    def test_pesos_1_3_5_reproduce_mismo_ranking(self, zonas_simple):
        """Using PESOS_1_3_5 must yield the same rank order as calcular_ipi."""
        result_orig = calcular_ipi(zonas_simple)
        result_alt = calcular_ipi_pesos_alternativos(zonas_simple, PESOS_1_3_5)
        rank_orig = result_orig["IPI"].rank(ascending=False, method="min")
        rank_alt = result_alt["IPI_alt"].rank(ascending=False, method="min")
        assert (rank_orig == rank_alt).all()

    def test_epdo_cambia_ranking_zona_con_muchos_muertos(self):
        """EPDO (1/8/24) must rank high-fatality zone above high-injury zone."""
        # zona 0: 100 heridos, 0 muertos → crit_1_3_5=300, crit_epdo=800
        # zona 1:   0 heridos,50 muertos → crit_1_3_5=250, crit_epdo=1200
        df = pd.DataFrame(
            {
                "cantidad_siniestros": [100, 50],
                "criticidad_total": [300, 250],
                "criticidad_promedio": [3.0, 5.0],
                "anios_activos": [4, 4],
                "siniestros_con_muertos": [0, 50],
            }
        )
        result = calcular_ipi_pesos_alternativos(df, PESOS_EPDO)
        assert result["IPI_alt"].iloc[1] > result["IPI_alt"].iloc[0]

    def test_scores_alt_presentes(self, zonas_simple):
        result = calcular_ipi_pesos_alternativos(zonas_simple)
        for col in SCORES_COLS:
            assert f"{col}_alt" in result.columns

    def test_criticidad_total_alt_presente(self, zonas_simple):
        result = calcular_ipi_pesos_alternativos(zonas_simple)
        assert "criticidad_total_alt" in result.columns


# ── B3.1: comparar_rankings_ipi ───────────────────────────────────────────


class TestCompararRankingsIPI:
    def test_ranking_identico_da_100_pct_overlap(self):
        rank = pd.Series([1, 2, 3, 4, 5])
        result = comparar_rankings_ipi(rank, rank, top_n=3)
        assert result["overlap_pct"] == 100.0
        assert result["n_difieren"] == 0
        assert result["spearman_rho"] == pytest.approx(1.0)

    def test_ranking_sin_solapamiento(self):
        rank_a = pd.Series([1, 2, 3, 4, 5])
        rank_b = pd.Series([4, 5, 3, 1, 2])  # top 2 b son idx 3,4 vs top 2 a son idx 0,1
        result = comparar_rankings_ipi(rank_a, rank_b, top_n=2)
        assert result["n_en_comun"] == 0
        assert result["n_difieren"] == 2

    def test_overlap_parcial(self):
        # top 3 a: idx 0,1,2; top 3 b: idx 0,1,4 → 2 en comun
        rank_a = pd.Series([1, 2, 3, 4, 5])
        rank_b = pd.Series([1, 2, 5, 4, 3])
        result = comparar_rankings_ipi(rank_a, rank_b, top_n=3)
        assert result["n_en_comun"] == 2
        assert result["overlap_pct"] == pytest.approx(66.7, abs=0.1)

    def test_estructura_del_resultado(self):
        rank = pd.Series([1, 2, 3])
        result = comparar_rankings_ipi(rank, rank, top_n=2)
        for key in ("top_n", "n_en_comun", "overlap_pct", "n_difieren", "spearman_rho"):
            assert key in result

    def test_n_difieren_es_complemento_de_n_comun(self):
        rank_a = pd.Series([1, 2, 3, 4, 5])
        rank_b = pd.Series([1, 2, 5, 3, 4])
        result = comparar_rankings_ipi(rank_a, rank_b, top_n=3)
        assert result["n_en_comun"] + result["n_difieren"] == result["top_n"]


# ── B3.3: calcular_tasas_exposicion ───────────────────────────────────────


class TestCalcularTasasExposicion:
    @pytest.fixture
    def df_exp(self):
        return pd.DataFrame(
            {
                "cantidad_siniestros_rec": [10.0, 0.0, 5.0],
                "km_red_osm": [2.0, 0.01, 1.0],
                "poblacion_2018": [100_000.0, 50_000.0, None],
            }
        )

    def test_tasa_red_correcta(self, df_exp):
        result = calcular_tasas_exposicion(df_exp)
        assert result["tasa_red"].iloc[0] == pytest.approx(10 / 2.0)

    def test_epsilon_evita_division_por_cero(self, df_exp):
        result = calcular_tasas_exposicion(df_exp, epsilon_km=0.05)
        # km_red=0.01 clipped to 0.05
        assert result["tasa_red"].iloc[1] == pytest.approx(0.0 / 0.05)

    def test_tasa_pob_correcta(self, df_exp):
        result = calcular_tasas_exposicion(df_exp)
        assert result["tasa_pob_100k"].iloc[0] == pytest.approx(10.0 / 100_000 * 100_000)

    def test_tasa_pob_nan_sin_poblacion(self, df_exp):
        result = calcular_tasas_exposicion(df_exp)
        assert pd.isna(result["tasa_pob_100k"].iloc[2])

    def test_no_modifica_dataframe_original(self, df_exp):
        original_cols = list(df_exp.columns)
        calcular_tasas_exposicion(df_exp)
        assert list(df_exp.columns) == original_cols

    def test_columnas_nuevas_presentes(self, df_exp):
        result = calcular_tasas_exposicion(df_exp)
        assert "tasa_red" in result.columns
        assert "tasa_pob_100k" in result.columns


# ── B3.3: calcular_rankings_duales ────────────────────────────────────────


class TestCalcularRankingsDuales:
    @pytest.fixture
    def df_rankings(self):
        return pd.DataFrame(
            {
                "IPI": [90.0, 80.0, 70.0, 60.0, 50.0],
                "tasa_red": [5.0, 3.0, 10.0, 1.0, 8.0],
                "tasa_pob_100k": [10.0, 5.0, 15.0, 20.0, 2.0],
            }
        )

    def test_rank_vol_min_es_1(self, df_rankings):
        result = calcular_rankings_duales(df_rankings)
        assert result["rank_vol"].min() == 1

    def test_rank_vol_correcto_orden(self, df_rankings):
        result = calcular_rankings_duales(df_rankings)
        # IPI descending: idx 0 > 1 > 2 > 3 > 4
        assert result["rank_vol"].iloc[0] == 1
        assert result["rank_vol"].iloc[4] == 5

    def test_en_top_vol_correcto(self, df_rankings):
        result = calcular_rankings_duales(df_rankings, top_n=3)
        assert result["en_top_vol"].iloc[0]
        assert result["en_top_vol"].iloc[2]
        assert not result["en_top_vol"].iloc[3]

    def test_delta_rank_es_rank_vol_menos_rank_tasa_red(self, df_rankings):
        result = calcular_rankings_duales(df_rankings)
        expected = result["rank_vol"] - result["rank_tasa_red"]
        assert (result["delta_rank"] == expected).all()

    def test_columnas_requeridas_presentes(self, df_rankings):
        result = calcular_rankings_duales(df_rankings)
        for col in (
            "rank_vol",
            "rank_tasa_red",
            "rank_tasa_pob",
            "delta_rank",
            "en_top_vol",
            "en_top_tasa_red",
            "en_top_tasa_pob",
        ):
            assert col in result.columns

    def test_no_modifica_dataframe_original(self, df_rankings):
        original_cols = list(df_rankings.columns)
        calcular_rankings_duales(df_rankings)
        assert list(df_rankings.columns) == original_cols

    def test_ipi_col_alternativa(self, df_rankings):
        df = df_rankings.rename(columns={"IPI": "IPI_rec"})
        result = calcular_rankings_duales(df, ipi_col="IPI_rec")
        assert result["rank_vol"].min() == 1


# ── B3.3: asignar_tipologia_nb05 ──────────────────────────────────────────


class TestAsignarTipologiaNB05:
    def _row(self, en_top_vol, en_top_tasa_red, en_top_tasa_pob):
        return pd.Series(
            {
                "en_top_vol": en_top_vol,
                "en_top_tasa_red": en_top_tasa_red,
                "en_top_tasa_pob": en_top_tasa_pob,
            }
        )

    def test_hotspot_absoluto_relativo(self):
        assert asignar_tipologia_nb05(self._row(True, True, False)) == "Hotspot absoluto + relativo"

    def test_hotspot_por_volumen(self):
        assert asignar_tipologia_nb05(self._row(True, False, False)) == "Hotspot por volumen"

    def test_hotspot_relativo_oculto(self):
        assert asignar_tipologia_nb05(self._row(False, True, False)) == "Hotspot relativo oculto"

    def test_alta_tasa_poblacional(self):
        assert asignar_tipologia_nb05(self._row(False, False, True)) == "Alta tasa poblacional"

    def test_sin_tipologia(self):
        assert asignar_tipologia_nb05(self._row(False, False, False)) == "Sin tipología NB05"

    def test_retorna_string(self):
        assert isinstance(asignar_tipologia_nb05(self._row(True, True, True)), str)

    def test_top_vol_y_tasa_red_tiene_prioridad_sobre_tasa_pob(self):
        # Si en_top_vol y en_top_tasa_red, debe ser "absoluto + relativo" aunque en_top_tasa_pob=True
        row = self._row(True, True, True)
        assert asignar_tipologia_nb05(row) == "Hotspot absoluto + relativo"
