"""
tests/test_ipi_utils.py — Unit tests for src/ipi_utils.py
"""

import pandas as pd
import pytest

from src.ipi_utils import (
    SCORES_COLS,
    asignar_prioridad_ipi,
    calcular_ipi,
    clasificar_familia_analitica,
    clasificar_hotspot,
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
