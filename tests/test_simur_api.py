"""
tests/test_simur_api.py — Tests de conectividad con el API REST de SIMUR
=========================================================================
Estos tests requieren conexión a Internet y acceso a sig.simur.gov.co.
Se marcan con pytest.mark.network para poder excluirlos en CI sin red:

    pytest -m "not network"           # omite tests de red
    pytest -m network                 # solo tests de red
"""

import os
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SIMUR_URL = (
    "https://sig.simur.gov.co/arcgis/rest/services/"
    "Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query"
)
TIMEOUT_S = 20


def _simur_get(params: dict) -> dict:
    defaults = {"f": "json", "outFields": "*", "returnGeometry": "false"}
    resp = requests.get(SIMUR_URL, params={**defaults, **params}, timeout=TIMEOUT_S)
    resp.raise_for_status()
    return resp.json()


# ── Fixture: verificar conectividad ─────────────────────────────────────


@pytest.fixture(scope="module")
def simur_disponible():
    """Salta todos los tests de red si SIMUR no responde o si se ejecuta en CI."""
    if os.environ.get("CI"):
        pytest.skip("SIMUR network tests omitidos en CI (API geo-restringida fuera de Colombia)")

    try:
        resp = requests.get(
            SIMUR_URL,
            params={"f": "json", "where": "1=0", "returnCountOnly": "true"},
            timeout=TIMEOUT_S,
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            pytest.skip(f"SIMUR retornó error: {data['error']}")
        # Verify actual data is accessible (not just connectivity)
        probe = requests.get(
            SIMUR_URL,
            params={"f": "json", "where": "ANIO_ACCIDENTE = 2019", "returnCountOnly": "true"},
            timeout=TIMEOUT_S,
        )
        if probe.json().get("count", 0) == 0:
            pytest.skip("SIMUR responde pero no retorna datos (posible restricción geográfica)")
    except Exception as exc:
        pytest.skip(f"SIMUR no disponible: {exc}")
    return True


# ── Marca de red ─────────────────────────────────────────────────────────

network = pytest.mark.network


@network
class TestSimurConectividad:
    """Verifica que el FeatureServer de SIMUR responde correctamente."""

    def test_endpoint_responde(self, simur_disponible):
        data = _simur_get({"where": "1=0", "returnCountOnly": "true"})
        assert "count" in data, f"Respuesta inesperada: {data}"

    def test_cuenta_2016(self, simur_disponible):
        data = _simur_get(
            {
                "where": "ANIO_ACCIDENTE = 2016",
                "returnCountOnly": "true",
            }
        )
        count = data.get("count", 0)
        # En 2016 hubo ~62,000 accidentes según nuestros datos
        assert count > 50_000, f"Cuenta 2016 inesperadamente baja: {count}. ¿Cambió el API?"
        assert count < 100_000, f"Cuenta 2016 inesperadamente alta: {count}. ¿Cambió el API?"

    def test_retorna_features_con_campos(self, simur_disponible):
        data = _simur_get(
            {
                "where": "ANIO_ACCIDENTE = 2019",
                "resultRecordCount": 5,
                "orderByFields": "OBJECTID DESC",
            }
        )
        features = data.get("features", [])
        assert len(features) > 0, "No se retornaron features"
        attrs = features[0]["attributes"]
        # Campos mínimos requeridos
        for campo in ["ANIO_ACCIDENTE", "GRAVEDAD_ACCIDENTE", "CLASE_ACCIDENTE"]:
            assert campo in attrs, f"Campo '{campo}' no encontrado en respuesta"

    def test_filtro_gravedad(self, simur_disponible):
        data = _simur_get(
            {
                "where": "ANIO_ACCIDENTE = 2019 AND GRAVEDAD_ACCIDENTE = 'CON MUERTOS'",
                "returnCountOnly": "true",
            }
        )
        count = data.get("count", 0)
        assert count > 0, "No se encontraron accidentes con muertos en 2019"
        # En 2019 debería haber menos muertos que heridos
        data_heridos = _simur_get(
            {
                "where": "ANIO_ACCIDENTE = 2019 AND GRAVEDAD_ACCIDENTE = 'CON HERIDOS'",
                "returnCountOnly": "true",
            }
        )
        assert count < data_heridos.get("count", 0), (
            "Muertos > Heridos en 2019, inconsistencia en el API"
        )

    def test_estadisticas_por_localidad(self, simur_disponible):
        import json

        data = _simur_get(
            {
                "where": "ANIO_ACCIDENTE = 2019",
                "groupByFieldsForStatistics": "LOCALIDAD_ACCIDENTE",
                "outStatistics": json.dumps(
                    [
                        {
                            "statisticType": "count",
                            "onStatisticField": "OBJECTID",
                            "outStatisticFieldName": "n",
                        }
                    ]
                ),
            }
        )
        features = data.get("features", [])
        # Bogotá tiene 20 localidades (incluyendo Sumapaz rural)
        assert len(features) >= 15, f"Se esperan ≥15 localidades, encontradas: {len(features)}"


@network
class TestSimurIntegridadDatos:
    """Verifica la integridad de los datos actuales vs período base."""

    def test_tendencia_registros_por_anio(self, simur_disponible):
        """
        Verifica que la tendencia de registros por año sea razonable.
        Entre 2016-2019 debe haber decenas de miles por año.
        """
        import json

        data = _simur_get(
            {
                "where": "ANIO_ACCIDENTE IN (2016, 2017, 2018, 2019)",
                "groupByFieldsForStatistics": "ANIO_ACCIDENTE",
                "outStatistics": json.dumps(
                    [
                        {
                            "statisticType": "count",
                            "onStatisticField": "OBJECTID",
                            "outStatisticFieldName": "n",
                        }
                    ]
                ),
                "orderByFields": "ANIO_ACCIDENTE ASC",
            }
        )
        features = data.get("features", [])
        assert len(features) == 4, (
            f"Se esperan datos para 4 años (2016-2019), obtenidos: {len(features)}"
        )
        for f in features:
            anio = f["attributes"]["ANIO_ACCIDENTE"]
            n = f["attributes"]["n"]
            assert n > 40_000, f"Año {anio}: {n} registros, esperados >40,000"
