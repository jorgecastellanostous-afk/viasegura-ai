# Bitácora de código — VíaSegura AI

> **Para qué sirve este archivo:** snippets clave que ya están en el notebook 01 y que se consultan a menudo. No es código nuevo, es un índice de lo que ya existe.

---

## Entorno

```bash
# Crear entorno
conda create -n viasegura python=3.11 pandas geopandas folium matplotlib requests shapely jupyterlab notebook -c conda-forge

# Activar
conda activate viasegura

# Iniciar JupyterLab
jupyter lab
```

---

## Imports estándar usados en el notebook 01

```python
import pandas as pd
import geopandas as gpd
import requests
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
from shapely.geometry import Point
from pathlib import Path
import time
```

---

## URL base de la API SIMUR

```python
url_accidentes = "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query"
```

---

## Conteo total

```python
params_count = {
    "where": "1=1",
    "returnCountOnly": "true",
    "f": "json",
}
total = requests.get(url_accidentes, params=params_count).json()["count"]
# Resultado: 904,424
```

---

## Conteo por año (loop)

```python
anios = list(range(2007, 2027))
conteo_anios = []
for anio in anios:
    params = {
        "where": f"ANO_OCURRENCIA_ACC = {anio}",
        "returnCountOnly": "true",
        "f": "json",
    }
    count = requests.get(url_accidentes, params=params).json().get("count", 0)
    conteo_anios.append({"anio": anio, "cantidad_siniestros": count})

df_conteo_anios = pd.DataFrame(conteo_anios)
```

---

## Descarga segura por año y bloques

```python
def descargar_accidentes_por_anio_seguro(
    url_base, anio, registros_por_bloque=1000, max_reintentos=5
):
    """
    Descarga accidentes de un año desde ArcGIS.
    Guarda cada bloque como CSV para no perder avance si falla la conexión.
    """
    where = f"ANO_OCURRENCIA_ACC = {anio}"
    params_count = {"where": where, "returnCountOnly": "true", "f": "json"}
    total = requests.get(url_base, params=params_count, timeout=60).json()["count"]
    print(f"\nAño {anio} - Total: {total}")

    offset = 0
    while offset < total:
        archivo_chunk = ruta_chunks / f"accidentes_{anio}_offset_{offset}.csv"
        if archivo_chunk.exists():
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

        for intento in range(1, max_reintentos + 1):
            try:
                response = requests.get(url_base, params=params, timeout=120)
                if response.status_code != 200:
                    time.sleep(5)
                    continue
                data = response.json()
                if "features" not in data or len(data["features"]) == 0:
                    return
                gdf_temp = gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4686")
                gdf_temp.to_csv(archivo_chunk, index=False)
                break
            except Exception as e:
                print(f"Fallo año {anio} offset {offset} intento {intento}: {e}")
                time.sleep(10)

        offset += registros_por_bloque
        time.sleep(0.5)
```

---

## Unión de chunks

```python
ruta_chunks = Path("../data/raw/chunks_accidentes_2016_2019")
archivos = list(ruta_chunks.glob("*.csv"))
# 262 archivos
df_raw = pd.concat([pd.read_csv(f) for f in archivos], ignore_index=True)
# 260,831 filas
```

---

## Conversión de fecha epoch ms

```python
df_limpia["FECHA_OCURRENCIA_ACC"] = pd.to_datetime(
    df_limpia["FECHA_OCURRENCIA_ACC"], unit="ms", errors="coerce"
)
```

---

## Filtro de bounding box Bogotá

```python
df_limpia = df_limpia.dropna(subset=["LATITUD", "LONGITUD"])
df_limpia = df_limpia[
    (df_limpia["LATITUD"] > 4.0) & (df_limpia["LATITUD"] < 5.0)
    & (df_limpia["LONGITUD"] > -75.0) & (df_limpia["LONGITUD"] < -73.0)
]
```

---

## Índice de criticidad

```python
puntaje_gravedad = {
    "SOLO DANOS": 1,
    "SOLO DAÑOS": 1,
    "CON HERIDOS": 3,
    "CON MUERTOS": 5,
}
df_limpia["puntaje_gravedad"] = df_limpia["GRAVEDAD"].map(puntaje_gravedad)
```

---

## Tabla por localidad

```python
tabla_localidad = (
    df_limpia
    .groupby("LOCALIDAD")
    .agg(
        cantidad_siniestros=("OBJECTID", "count"),
        criticidad_total=("puntaje_gravedad", "sum"),
        criticidad_promedio=("puntaje_gravedad", "mean"),
    )
    .reset_index()
    .sort_values("criticidad_total", ascending=False)
)
```

---

## Mapa de calor

```python
df_mapa = df_limpia.copy()
df_mapa["LAT_REDONDEADA"] = df_mapa["LATITUD"].round(3)
df_mapa["LON_REDONDEADA"] = df_mapa["LONGITUD"].round(3)

puntos_calor = (
    df_mapa
    .groupby(["LAT_REDONDEADA", "LON_REDONDEADA"])
    .agg(
        cantidad_siniestros=("OBJECTID", "count"),
        criticidad_total=("puntaje_gravedad", "sum"),
    )
    .reset_index()
)

mapa_calor = folium.Map(location=[4.65, -74.08], zoom_start=11, tiles="CartoDB positron")
datos_heatmap = puntos_calor[["LAT_REDONDEADA", "LON_REDONDEADA", "criticidad_total"]].values.tolist()
HeatMap(datos_heatmap, radius=12, blur=15, max_zoom=13).add_to(mapa_calor)
mapa_calor.save("../outputs/maps/mapa_calor_criticidad_siniestros_2016_2019.html")
```

---

## Función "valor más frecuente" (para tabla de zonas críticas — propuesta, no ejecutada todavía)

```python
def valor_mas_frecuente(serie):
    moda = serie.mode()
    return moda.iloc[0] if len(moda) > 0 else None
```

---

---

## Notebook 02 — IPI y hotspots

### Imports adicionales (NB02)

```python
import numpy as np
from scipy import stats  # si se usó para percentiles
```

### Agregación espacial de siniestros por grilla 0.001°

```python
df["LAT_ZONA"] = df["LATITUD"].round(3)
df["LON_ZONA"] = df["LONGITUD"].round(3)

# Función para valor más frecuente (moda)
def valor_mas_frecuente(serie):
    moda = serie.mode()
    return moda.iloc[0] if len(moda) > 0 else None

zonas = (
    df
    .groupby(["LAT_ZONA", "LON_ZONA"])
    .agg(
        cantidad_siniestros=("OBJECTID", "count"),
        criticidad_total=("puntaje_gravedad", "sum"),
        criticidad_promedio=("puntaje_gravedad", "mean"),
        criticidad_2016=("puntaje_gravedad_2016", "sum"),  # columna derivada
        anios_activos=("ANO_OCURRENCIA_ACC", "nunique"),
        siniestros_solo_danos=("es_solo_danos", "sum"),
        siniestros_con_heridos=("es_con_heridos", "sum"),
        siniestros_con_muertos=("es_con_muertos", "sum"),
        localidad_predominante=("LOCALIDAD", valor_mas_frecuente),
        barrio_predominante=("BARRIO", valor_mas_frecuente),
        via_predominante=("MVINOMBRE", valor_mas_frecuente),
        clase_predominante=("CLASE_ACC", valor_mas_frecuente),
        gravedad_predominante=("GRAVEDAD", valor_mas_frecuente),
    )
    .reset_index()
)
```

### Construcción de los 5 scores del IPI

```python
n = len(zonas)

zonas["score_volumen"] = zonas["cantidad_siniestros"].rank() / n
zonas["score_criticidad_total"] = zonas["criticidad_total"].rank() / n
zonas["score_severidad_promedio"] = zonas["criticidad_promedio"].rank() / n
zonas["score_persistencia"] = zonas["anios_activos"] / 4
zonas["score_fatalidad"] = zonas["siniestros_con_muertos"].rank() / n
```

### Cálculo del IPI

```python
zonas["IPI"] = zonas[[
    "score_volumen",
    "score_criticidad_total",
    "score_severidad_promedio",
    "score_persistencia",
    "score_fatalidad"
]].mean(axis=1) * 100

zonas["rank_IPI"] = zonas["IPI"].rank(ascending=False).astype(int)
```

### Análisis de concentración

```python
for top_n in [50, 200, 500, 1000]:
    subset = zonas.nlargest(top_n, "IPI")
    pct_zonas = top_n / len(zonas) * 100
    pct_siniestros = subset["cantidad_siniestros"].sum() / zonas["cantidad_siniestros"].sum() * 100
    pct_criticidad = subset["criticidad_total"].sum() / zonas["criticidad_total"].sum() * 100
    pct_muertes = subset["siniestros_con_muertos"].sum() / zonas["siniestros_con_muertos"].sum() * 100
```

### Mapa Top 50 con CircleMarker

```python
mapa = folium.Map(location=[4.65, -74.08], zoom_start=11, tiles="CartoDB positron")

COLORES_FAMILIA = {
    "Hotspot robusto integral": "#d32f2f",
    "Hotspot de severidad/fatalidad": "#e64a19",
    "Hotspot preventivo prioritario": "#f57c00",
    "Hotspot de carga acumulada": "#fbc02d",
    "Seguimiento": "#388e3c",
}

for _, fila in top50.iterrows():
    folium.CircleMarker(
        location=[fila["LAT_ZONA"], fila["LON_ZONA"]],
        radius=8 + (fila["IPI"] - 90) * 0.5,
        color=COLORES_FAMILIA.get(fila["familia_analitica"], "#999"),
        fill=True,
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>Rank {fila['rank_IPI']}</b><br>"
            f"IPI: {fila['IPI']:.1f}<br>"
            f"Siniestros: {fila['cantidad_siniestros']}<br>"
            f"Muertos: {fila['siniestros_con_muertos']}<br>"
            f"{fila['via_predominante']}<br>"
            f"{fila['barrio_predominante']}, {fila['localidad_predominante']}",
            max_width=250
        )
    ).add_to(mapa)

mapa.save("../outputs/maps/mapa_top50_IPI_final_2016_2019.html")
```

### Cargar outputs del NB02 en NB03 (snippet de inicio)

```python
from pathlib import Path
import pandas as pd

ruta_reports = Path("../outputs/reports")

top50_base = pd.read_csv(ruta_reports / "top50_IPI_final_2016_2019.csv")
# Para la tabla completa (5.5 MB):
zonas_completas = pd.read_csv(ruta_reports / "zonas_criticas_IPI_completo_2016_2019.csv")
familias = pd.read_csv(ruta_reports / "resumen_familia_analitica_2016_2019.csv")
concentracion = pd.read_csv(ruta_reports / "resumen_concentracion_IPI_2016_2019_final.csv")
```

### Auditoría de capas hermanas SIMUR (para NB03)

```python
url_base_simur = "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer"

for capa_id in [0, 1, 2, 3, 4, 5]:
    url_capa = f"{url_base_simur}/{capa_id}/query"
    params = {"where": "1=1", "returnCountOnly": "true", "f": "json"}
    try:
        r = requests.get(url_capa, params=params, timeout=30)
        count = r.json().get("count", "Error")
        print(f"Capa {capa_id}: {count} registros")
    except Exception as e:
        print(f"Capa {capa_id}: no responde — {e}")
```
