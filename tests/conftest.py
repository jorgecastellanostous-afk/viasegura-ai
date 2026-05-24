"""
tests/conftest.py — Configuración global de pytest para VíaSegura AI
"""

import os
import sys
from pathlib import Path

# Garantizar que la raíz del proyecto está en sys.path para todos los tests
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Excluir test_data_loader.py en CI: requiere streamlit + dataset completo
# Esto opera ANTES de que pytest intente importar el archivo (pre-colección)
if os.environ.get("CI"):
    collect_ignore = [str(Path(__file__).parent / "test_data_loader.py")]


def pytest_configure(config):
    """Registrar marks personalizados."""
    config.addinivalue_line(
        "markers",
        "network: test que requiere conexión a Internet (SIMUR API)",
    )
    config.addinivalue_line(
        "markers",
        "slow: test de larga duración (ejecutar notebooks completos)",
    )
