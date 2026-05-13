"""
Genera data/raw/_snapshot_metadata.json con hash MD5, conteo de filas
y tamaño en bytes de cada archivo raw principal.

Ejecutar desde la raíz del proyecto:
    python scripts/generar_snapshot_metadata.py
"""

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ARCHIVOS_RAW = [
    "accidentes_bogota_2016_2019_raw.csv",
    "accidentes_bogota_reciente_raw.csv",
    "accidentes_bogota_muestra_10000.csv",
]

CHUNK_SIZE = 8 * 1024  # 8 KB


def md5_archivo(ruta: Path) -> str:
    h = hashlib.md5()
    with ruta.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def contar_filas(ruta: Path) -> int:
    # Cuenta líneas del CSV sin cargarlo en memoria
    count = 0
    with ruta.open("r", encoding="utf-8", errors="replace") as f:
        for _ in f:
            count += 1
    return max(0, count - 1)  # descontar encabezado


def main():
    raiz = Path(__file__).parent.parent
    ruta_raw = raiz / "data" / "raw"
    salida = ruta_raw / "_snapshot_metadata.json"

    registros = []
    for nombre in ARCHIVOS_RAW:
        ruta = ruta_raw / nombre
        if not ruta.exists():
            print(f"  OMITIDO (no existe): {nombre}")
            continue
        print(f"  Procesando: {nombre} ...", end=" ", flush=True)
        md5 = md5_archivo(ruta)
        filas = contar_filas(ruta)
        bytes_ = ruta.stat().st_size
        registros.append({
            "nombre": nombre,
            "md5": md5,
            "filas": filas,
            "bytes": bytes_,
        })
        print(f"{filas:,} filas | {bytes_/1e6:.1f} MB | md5={md5[:8]}...")

    metadata = {
        "fecha_generacion": str(date.today()),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "nota": "Hash MD5 calculado sobre el archivo crudo completo. Regenerar si se modifican los archivos raw.",
        "archivos": registros,
    }

    salida.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado en: {salida}")


if __name__ == "__main__":
    main()
