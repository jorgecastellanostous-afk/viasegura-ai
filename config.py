"""
config.py — VíaSegura AI
========================
Fuente de verdad de rutas del proyecto.

Usa Path(__file__) para que las rutas sean siempre absolutas,
sin importar desde qué directorio se ejecute el código
(VS Code, JupyterLab, scripts, tests, etc.).

Uso en notebooks:
    import sys
    from pathlib import Path
    _root = next(c for c in [Path.cwd(), Path.cwd().parent] if (c / 'config.py').exists())
    if str(_root) not in sys.path: sys.path.insert(0, str(_root))
    from config import PROJECT_ROOT, DATA_RAW, DATA_PROCESSED, REPORTS, MAPS
"""

from pathlib import Path

# Raíz del proyecto = directorio donde vive este archivo
PROJECT_ROOT   = Path(__file__).resolve().parent

DATA_RAW       = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED = PROJECT_ROOT / 'data' / 'processed'
REPORTS        = PROJECT_ROOT / 'outputs' / 'reports'
MAPS           = PROJECT_ROOT / 'outputs' / 'maps'
NOTEBOOKS      = PROJECT_ROOT / 'notebooks'
APP            = PROJECT_ROOT / 'app'
SQL            = PROJECT_ROOT / 'sql'

# Crear carpetas si no existen
for _folder in [DATA_RAW, DATA_PROCESSED, REPORTS, MAPS]:
    _folder.mkdir(parents=True, exist_ok=True)
