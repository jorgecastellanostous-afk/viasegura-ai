"""SIMUR ArcGIS FeatureServer download utilities (from NB01, NB04)."""

from __future__ import annotations

import time
from collections import Counter
from pathlib import Path

import pandas as pd
import requests

# Base URL for the SIMUR accident analysis service
BASE_URL = (
    "https://sig.simur.gov.co/arcgis/rest/services"
    "/Accidentalidad/AccidentalidadAnalisis/FeatureServer"
)

# Layer IDs within the FeatureServer
CAPAS: dict[str, int] = {
    "accidentes": 2,  # Main accident records
    "actor_vial": 3,  # VM_ACC_ACTOR_VIAL  (field: CONDICION)
    "vehiculo": 5,  # VM_ACC_VEHICULO    (field: CLASE)
    "causa": 4,  # VM_ACC_CAUSA       (field: NOMBRE)
    "via": 6,  # VM_ACC_VIA
}

CAMPO_JOIN = "FORMULARIO"

_DEFAULT_BATCH = 200
_DEFAULT_RETRIES = 5


def descargar_accidentes_por_anio_seguro(
    anio: int,
    registros_por_bloque: int = 1000,
    max_reintentos: int = _DEFAULT_RETRIES,
    ruta_chunks: Path | None = None,
) -> pd.DataFrame | None:
    """Download all accident records for a given year with chunked pagination and retry.

    Each chunk is saved to ruta_chunks as a CSV so progress survives interruptions.
    If ruta_chunks is None the function still works but offers no resume capability.

    Returns a DataFrame with all records, or None if the download failed entirely.
    """
    url_base = f"{BASE_URL}/{CAPAS['accidentes']}/query"
    where = f"ANO_OCURRENCIA_ACC = {anio}"

    total_resp = requests.get(
        url_base,
        params={"where": where, "returnCountOnly": "true", "f": "json"},
        timeout=60,
    ).json()
    total = total_resp.get("count", 0)
    print(f"\nAño {anio} — Total de registros: {total:,}")

    offset = 0
    chunks: list[pd.DataFrame] = []

    while offset < total:
        chunk_path = ruta_chunks / f"accidentes_{anio}_offset_{offset}.csv" if ruta_chunks else None

        if chunk_path and chunk_path.exists():
            print(f"  Año {anio} offset {offset} — cargando desde caché")
            chunks.append(pd.read_csv(chunk_path))
            offset += registros_por_bloque
            continue

        params = {
            "where": where,
            "outFields": "*",
            "f": "geojson",
            "resultRecordCount": registros_por_bloque,
            "resultOffset": offset,
            "orderByFields": "OBJECTID ASC",
        }

        exito = False
        for intento in range(1, max_reintentos + 1):
            try:
                response = requests.get(url_base, params=params, timeout=120)
                if response.status_code != 200:
                    print(f"  HTTP {response.status_code} — intento {intento}/{max_reintentos}")
                    time.sleep(5)
                    continue

                data = response.json()
                features = data.get("features", [])
                if not features:
                    print("  No llegaron más registros.")
                    return pd.concat(chunks, ignore_index=True) if chunks else None

                # Build DataFrame from GeoJSON features (attributes only)
                df_chunk = pd.DataFrame([f["properties"] for f in features])

                if chunk_path:
                    chunk_path.parent.mkdir(parents=True, exist_ok=True)
                    df_chunk.to_csv(chunk_path, index=False)

                chunks.append(df_chunk)
                print(f"  Año {anio} — {min(offset + registros_por_bloque, total):,}/{total:,}")
                exito = True
                break

            except Exception as exc:
                print(f"  Error intento {intento}/{max_reintentos}: {exc}")
                time.sleep(10)

        if not exito:
            print(f"  No se pudo descargar año {anio} offset {offset}. Deteniendo.")
            break

        offset += registros_por_bloque
        time.sleep(0.5)

    return pd.concat(chunks, ignore_index=True) if chunks else None


def descargar_por_formularios(
    layer_id: int,
    formularios: list[str],
    campos: str = "*",
    batch_size: int = _DEFAULT_BATCH,
    max_reintentos: int = _DEFAULT_RETRIES,
) -> pd.DataFrame:
    """Download records from a FeatureServer layer filtered by a list of FORMULARIOs.

    Uses POST requests with exponential backoff. Returns an empty DataFrame if
    all batches fail.
    """
    url_q = f"{BASE_URL}/{layer_id}/query"
    batches = [formularios[i : i + batch_size] for i in range(0, len(formularios), batch_size)]
    resultados: list[dict] = []

    print(
        f"  Layer {layer_id}: {len(formularios):,} FORMULARIOs → {len(batches)} batches ≤{batch_size}"
    )

    for idx, batch in enumerate(batches):
        forms_str = "','".join(batch)
        params = {
            "where": f"FORMULARIO IN ('{forms_str}')",
            "outFields": campos,
            "f": "json",
        }

        for intento in range(1, max_reintentos + 1):
            try:
                r = requests.post(url_q, data=params, timeout=60)
                features = r.json().get("features", [])
                resultados.extend([f["attributes"] for f in features])
                break
            except Exception as exc:
                if intento == max_reintentos:
                    print(f"    Batch {idx + 1} failed after {max_reintentos} attempts: {exc}")
                else:
                    time.sleep(2**intento)

        if (idx + 1) % 20 == 0 or (idx + 1) == len(batches):
            print(f"  [{idx + 1:>3}/{len(batches)}] registros acumulados: {len(resultados):,}")
        else:
            time.sleep(0.3)

    return pd.DataFrame(resultados)


def descargar_victimas_fatales_por_formulario(
    formularios: list[str],
    condicion_muerto: str = "MUERTO",
    batch_size: int = _DEFAULT_BATCH,
    max_reintentos: int = _DEFAULT_RETRIES,
) -> pd.DataFrame:
    """Count individual fatalities per accident from Layer 3 (actor_vial).

    Returns DataFrame with FORMULARIO and n_victimas_fatales.
    Accidents with no matching CONDICION are absent from the result.

    Context: siniestros_con_muertos counts accident events; this counts
    individual victims (SDM ratio ~2 victims per fatal event).
    """
    if not formularios:
        return pd.DataFrame(columns=[CAMPO_JOIN, "n_victimas_fatales"])

    df_actor = descargar_por_formularios(
        layer_id=CAPAS["actor_vial"],
        formularios=formularios,
        campos=f"{CAMPO_JOIN},CONDICION",
        batch_size=batch_size,
        max_reintentos=max_reintentos,
    )

    if df_actor.empty:
        return pd.DataFrame(columns=[CAMPO_JOIN, "n_victimas_fatales"])

    muertos = df_actor[df_actor["CONDICION"] == condicion_muerto]
    if muertos.empty:
        return pd.DataFrame(columns=[CAMPO_JOIN, "n_victimas_fatales"])

    return muertos.groupby(CAMPO_JOIN).size().reset_index(name="n_victimas_fatales")


def agregar_por_zona(
    df_capa: pd.DataFrame,
    campo_valor: str,
    zona_a_forms: dict[str, list[str]],
) -> dict[str, dict]:
    """Aggregate a field's distribution per zone using HHI concentration index.

    Returns a dict keyed by zone with: moda, distribucion (%), n_registros,
    cobertura_pct, hhi (Herfindahl-Hirschman Index × 10 000).

    HHI = 10 000 → single dominant value; low values → diverse distribution.
    """
    form_vals = df_capa.groupby(CAMPO_JOIN)[campo_valor].apply(list).to_dict()

    resultado: dict[str, dict] = {}
    for zona, forms in zona_a_forms.items():
        todos_vals: list = []
        forms_con_dato = 0

        for f in forms:
            vals = form_vals.get(f, [])
            limpios = [
                v for v in vals if v is not None and str(v).strip() not in ("", "nan", "None")
            ]
            if limpios:
                forms_con_dato += 1
                todos_vals.extend(limpios)

        cobertura = forms_con_dato / len(forms) * 100 if forms else 0
        conteo = Counter(todos_vals)
        total = sum(conteo.values())

        if total > 0:
            distribucion = {v: round(c / total * 100, 1) for v, c in conteo.most_common()}
            moda_val = conteo.most_common(1)[0][0]
            hhi = round(sum((c / total) ** 2 for c in conteo.values()) * 10_000, 1)
        else:
            distribucion = {}
            moda_val = None
            hhi = None

        resultado[zona] = {
            "moda": moda_val,
            "distribucion": distribucion,
            "n_registros": len(todos_vals),
            "cobertura_pct": round(cobertura, 1),
            "hhi": hhi,
        }

    return resultado
