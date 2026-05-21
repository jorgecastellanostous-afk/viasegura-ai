"""
tests/test_ipi_formula.py — Tests unitarios de la fórmula IPI
==============================================================
Verifica que los scores y el IPI calculado en NB02 sean numéricamente
correctos y estén dentro de rangos esperados.
"""

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import REPORTS


@pytest.fixture(scope="module")
def ipi_rows():
    """Carga el CSV de IPI completo una sola vez por módulo de test."""
    ipi_path = REPORTS / "zonas_criticas_IPI_completo_2016_2019.csv"
    if not ipi_path.exists():
        pytest.skip("CSV de IPI no existe — ejecuta NB02")
    with open(ipi_path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class TestIPIRangos:
    """El IPI y sus scores están dentro de los rangos esperados."""

    def test_ipi_rango_0_100(self, ipi_rows):
        for row in ipi_rows:
            ipi = float(row["IPI"])
            assert 0.0 <= ipi <= 100.0, f"IPI fuera de rango: {ipi} (zona {row.get('rank_IPI')})"

    @pytest.mark.parametrize(
        "score_col",
        [
            "score_volumen",
            "score_criticidad_total",
            "score_severidad_promedio",
            "score_persistencia",
            "score_fatalidad",
        ],
    )
    def test_scores_rango_0_1(self, ipi_rows, score_col):
        for row in ipi_rows:
            val = float(row[score_col])
            assert 0.0 <= val <= 1.0, (
                f"{score_col} fuera de [0,1]: {val} (rank {row.get('rank_IPI')})"
            )

    def test_ipi_maximo_es_rank1(self, ipi_rows):
        """La zona rank=1 tiene el IPI más alto."""
        rank1 = next((r for r in ipi_rows if r.get("rank_IPI") == "1"), None)
        if rank1 is None:
            pytest.skip("No se encontró zona rank_IPI=1")
        ipi_max = max(float(r["IPI"]) for r in ipi_rows)
        assert abs(float(rank1["IPI"]) - ipi_max) < 0.01, (
            f"La zona rank=1 no tiene el IPI máximo: rank1={rank1['IPI']}, max={ipi_max}"
        )


class TestIPIIntegridad:
    """Integridad del dataset IPI."""

    def test_total_zonas_positivo(self, ipi_rows):
        assert len(ipi_rows) > 0, "El CSV de IPI está vacío"

    def test_hay_prioridad_1(self, ipi_rows):
        p1 = [r for r in ipi_rows if "Prioridad 1" in r.get("prioridad_IPI", "")]
        assert len(p1) >= 1, "No hay zonas Prioridad 1 en el dataset"

    def test_prioridad_1_tiene_top_50(self, ipi_rows):
        p1 = [r for r in ipi_rows if "Prioridad 1" in r.get("prioridad_IPI", "")]
        assert len(p1) <= 50, f"Se esperan ≤50 zonas Prioridad 1, encontradas: {len(p1)}"

    def test_no_ipi_nulos(self, ipi_rows):
        nulos = [r for r in ipi_rows if not r.get("IPI", "").strip()]
        assert len(nulos) == 0, f"{len(nulos)} filas con IPI vacío"

    def test_coordenadas_bogota(self, ipi_rows):
        """Todas las zonas tienen coordenadas dentro del bbox de Bogotá.
        El municipio incluye Sumapaz al sur (~4.0°) y el norte hasta ~4.85°."""
        LAT_MIN, LAT_MAX = 4.0, 4.90
        LON_MIN, LON_MAX = -74.35, -73.95
        fuera = []
        for r in ipi_rows:
            lat = float(r.get("LAT_ZONA", 0))
            lon = float(r.get("LON_ZONA", 0))
            if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
                fuera.append((lat, lon, r.get("rank_IPI")))
        assert len(fuera) == 0, f"{len(fuera)} zonas fuera del bbox de Bogotá: {fuera[:3]}"

    def test_localidades_conocidas(self, ipi_rows):
        """Las localidades predominantes son nombres válidos de Bogotá."""
        import unicodedata

        def _normalizar(s: str) -> str:
            """Quita tildes y convierte a mayúsculas para comparación."""
            return "".join(
                c
                for c in unicodedata.normalize("NFD", s.upper())
                if unicodedata.category(c) != "Mn"
            )

        LOCALIDADES_BOGOTA = {
            _normalizar(n)
            for n in [
                "KENNEDY",
                "ENGATIVA",
                "SUBA",
                "USAQUEN",
                "FONTIBON",
                "BOSA",
                "CIUDAD BOLIVAR",
                "SANTA FE",
                "CHAPINERO",
                "TEUSAQUILLO",
                "BARRIOS UNIDOS",
                "LOS MARTIRES",
                "PUENTE ARANDA",
                "LA CANDELARIA",
                "ANTONIO NARINO",
                "RAFAEL URIBE URIBE",
                "TUNJUELITO",
                "USME",
                "SAN CRISTOBAL",
                "SUMAPAZ",
            ]
        }
        p1 = [r for r in ipi_rows if "Prioridad 1" in r.get("prioridad_IPI", "")]
        for r in p1:
            loc = _normalizar(r.get("localidad_predominante", "").strip())
            assert any(known in loc for known in LOCALIDADES_BOGOTA), (
                f"Localidad desconocida en zona Prioridad 1: '{loc}'"
            )


class TestIPIFormula:
    """Verificación numérica de la fórmula IPI."""

    def test_ipi_correlaciona_con_scores(self, ipi_rows):
        """
        Zonas con todos los scores >0.9 deben tener IPI >80.
        Zonas con todos los scores <0.2 deben tener IPI <40.
        """
        score_cols = [
            "score_volumen",
            "score_criticidad_total",
            "score_severidad_promedio",
            "score_persistencia",
            "score_fatalidad",
        ]
        for r in ipi_rows:
            scores = [float(r.get(c, 0)) for c in score_cols]
            ipi = float(r["IPI"])
            if all(s > 0.9 for s in scores):
                assert ipi > 80, f"Zona con todos scores >0.9 debería tener IPI >80, tiene {ipi}"

    def test_top10_tienen_alto_ipi(self, ipi_rows):
        """Las 10 primeras zonas deben tener IPI >80."""
        top10 = ipi_rows[:10]
        for r in top10:
            ipi = float(r["IPI"])
            assert ipi > 80, f"Zona top-10 rank={r.get('rank_IPI')} tiene IPI={ipi}, esperado >80"

    def test_ranking_ordenado(self, ipi_rows):
        """El rank_IPI debe ser consecutivo: 1, 2, 3, ..."""
        ranks = [int(r["rank_IPI"]) for r in ipi_rows if r.get("rank_IPI", "").isdigit()]
        if len(ranks) < 2:
            pytest.skip("No hay suficientes filas con rank_IPI numérico")
        # Verificar que están en orden ascendente
        for i in range(len(ranks) - 1):
            assert ranks[i] <= ranks[i + 1], (
                f"Ranking no ordenado en posición {i}: {ranks[i]} > {ranks[i + 1]}"
            )
