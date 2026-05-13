# Metodología — qué se hizo y cómo

> **Para qué sirve este archivo:** documentar paso a paso lo que ya se ejecutó, en orden cronológico y con detalle suficiente para reproducir.

---

## Pasos ejecutados (orden cronológico)

### 1. Conexión a la API SIMUR

- Probada con `requests.get(url, params={"f":"geojson", "where":"1=1", "resultRecordCount":10})`.
- Status 200 confirmado.

### 2. Auditoría del total

- Query con `returnCountOnly=true&f=json` → **904,424 registros** en la capa completa (todos los años).

### 3. Auditoría por año

- Loop sobre años 2007–2026 con `where=ANO_OCURRENCIA_ACC = {anio}`.
- Resultado guardado en `outputs/reports/auditoria_conteo_siniestros_por_anio.csv`.
- Identificación visual del periodo estable: **2016–2019**.

### 4. Selección de periodo

- Decisión: **2016–2019**, total esperado **260,831 registros**.
- Justificación: completo, pre-pandemia, evita años con subreporte.

### 5. Descarga segura por año y bloques

- Función `descargar_accidentes_por_anio_seguro(url, anio, registros_por_bloque=1000, max_reintentos=5)`.
- Descarga en bloques de 1,000 registros (no 2,000 como intento inicial, que falló por `RemoteDisconnected`).
- Cada bloque se guarda como CSV individual en `data/raw/chunks_accidentes_2016_2019/`.
- Si un bloque ya existe, se omite (descarga reanudable).
- Reintentos hasta 5 veces con `time.sleep(10)` entre fallos.

### 6. Unión de chunks

- 262 chunks unidos con `pd.concat`.
- Resultado: 260,831 filas → coincide con conteo del servidor (diferencia = 0).
- Guardado en `data/raw/accidentes_bogota_2016_2019_raw.csv`.

### 7. Validación de duplicados (en raw)

| Columna | Duplicados |
|---|---|
| OBJECTID | 0 |
| CODIGO_ACCIDENTE | 0 |
| FORMULARIO | 0 |

### 8. Limpieza

Aplicada sobre una copia (`df_limpia = accidentes_2016_2019_raw.copy()`).

#### 8.1 Selección de columnas útiles

18 columnas seleccionadas (ver `memory/data_sources.md`).

#### 8.2 Conversión de tipos

- `FECHA_OCURRENCIA_ACC`: epoch ms → `datetime` con `pd.to_datetime(unit="ms", errors="coerce")`.
- `LATITUD`, `LONGITUD`: a numérico con `pd.to_numeric(errors="coerce")`.

#### 8.3 Limpieza de texto

Aplicado a 9 columnas (`MES_OCURRENCIA_ACC`, `DIA_OCURRENCIA_ACC`, `DIRECCION`, `GRAVEDAD`, `CLASE_ACC`, `LOCALIDAD`, `MUNICIPIO`, `BARRIO`, `MVINOMBRE`):

```python
df_limpia[col] = df_limpia[col].astype("string").str.strip().str.upper()
```

#### 8.4 Filtro de bounding box Bogotá

```python
df_limpia.dropna(subset=["LATITUD", "LONGITUD"])
df_limpia = df_limpia[
    (df_limpia["LATITUD"] > 4.0) & (df_limpia["LATITUD"] < 5.0) &
    (df_limpia["LONGITUD"] > -75.0) & (df_limpia["LONGITUD"] < -73.0)
]
```

**Resultado:** 0 filas eliminadas. La fuente ya estaba dentro del bbox sin nulos. Ver advertencia en `memory/limitations.md`.

### 9. Índice preliminar de criticidad

```python
puntaje_gravedad = {
    "SOLO DANOS": 1,
    "SOLO DAÑOS": 1,
    "CON HERIDOS": 3,
    "CON MUERTOS": 5
}
df_limpia["puntaje_gravedad"] = df_limpia["GRAVEDAD"].map(puntaje_gravedad)
```

Validación: 0 nulos en `puntaje_gravedad`.

### 10. Guardado del limpio

`data/processed/accidentes_bogota_2016_2019_limpio.csv`

### 11. Resumen de calidad

Construcción manual de `outputs/reports/resumen_calidad_datos_2016_2019.csv` con:

- filas_raw, filas_limpias
- duplicados por OBJECTID
- nulos en lat, lon, puntaje_gravedad

### 12. Tablas de análisis

Generadas con `groupby + agg`:

- `tabla_localidad_2016_2019.csv` (cantidad, criticidad total, criticidad promedio)
- `tabla_gravedad_2016_2019.csv`
- `tabla_clase_accidente_2016_2019.csv`
- `tabla_anio_2016_2019.csv`

### 13. Mapa de calor

- Coordenadas redondeadas a 3 decimales (≈ 100 m).
- Agregación: cantidad y criticidad total.
- `folium.Map(tiles="CartoDB positron")` + `HeatMap(radius=12, blur=15)`.
- Guardado: `outputs/maps/mapa_calor_criticidad_siniestros_2016_2019.html`.

### 14. Versión exploratoria de hotspots (NB02, fase temprana)

Primera versión de zonas críticas producida al inicio del NB02:

- `zonas_criticas_siniestros_2016_2019.csv` — ✅ existe (versión inicial simple)
- `top20_zonas_criticas_siniestros_2016_2019.csv` — ✅ existe
- `mapa_top50_zonas_criticas_siniestros_2016_2019.html` — ✅ existe

Estas versiones usaron solo volumen y criticidad total, sin el IPI completo. Son superadas por la versión final descrita abajo.

---

## Notebook 02 — Índice de Prioridad de Intervención (IPI)

### 15. Carga de la base limpia

```python
df_limpia = pd.read_csv("../data/processed/accidentes_bogota_2016_2019_limpio.csv")
# 260,831 filas, 19 columnas
```

### 16. Agregación espacial por grilla 0.001°

Redondeo de coordenadas a 3 decimales → celdas de ~111 m × ~111 m.

```python
df_limpia["LAT_ZONA"] = df_limpia["LATITUD"].round(3)
df_limpia["LON_ZONA"] = df_limpia["LONGITUD"].round(3)
```

Agrupación por `(LAT_ZONA, LON_ZONA)` para calcular:
- `cantidad_siniestros`, `criticidad_total`, `criticidad_promedio`
- Criticidad desglosada por año: `criticidad_2016`, `criticidad_2017`, `criticidad_2018`, `criticidad_2019`
- `anios_activos` (número de años con al menos un siniestro)
- `siniestros_solo_danos`, `siniestros_con_heridos`, `siniestros_con_muertos`
- `localidad_predominante`, `barrio_predominante`, `via_predominante`, `clase_predominante`, `gravedad_predominante`

Resultado: ~17,130 zonas únicas.

### 17. Clasificación por tipo de hotspot

```python
# Lógica basada en umbrales de criticidad, volumen y presencia de muertos
tipo_hotspot: "Hotspot severo" | "Hotspot persistente con severidad media-alta" | "Hotspot exploratorio"
```

### 18. Construcción de los 5 scores del IPI

Cada score normaliza su métrica por rango percentil entre todas las ~17,130 zonas (excepto `score_persistencia`):

```python
score_volumen          = rank(cantidad_siniestros) / n_zonas
score_criticidad_total = rank(criticidad_total) / n_zonas
score_severidad_promedio = rank(criticidad_promedio) / n_zonas
score_persistencia     = anios_activos / 4      # ratio directo, no percentil
score_fatalidad        = rank(siniestros_con_muertos) / n_zonas
```

### 19. Cálculo del IPI

```python
IPI = mean([score_volumen,
            score_criticidad_total,
            score_severidad_promedio,
            score_persistencia,
            score_fatalidad]) * 100
```

Rango teórico: 0–100. El Top 50 tiene IPI entre 93.27 y 96.25.

### 20. Prioridad de intervención y familia analítica

Cada zona recibe dos clasificaciones adicionales:

**`prioridad_IPI`** (basada en el valor del IPI):
- Prioridad 1 — Intervención prioritaria
- Prioridad 2 — Auditoría de seguridad vial
- Prioridad 3 — Monitoreo y gestión preventiva
- etc.

**`familia_analitica`** (clasificación cualitativa por perfil):
- Hotspot robusto integral
- Hotspot de severidad/fatalidad
- Hotspot de carga acumulada
- Hotspot preventivo prioritario
- Seguimiento

### 21. Generación del Top 50, Top 200 y tabla completa

```python
top50  = zonas.sort_values("IPI", ascending=False).head(50)
top200 = zonas.sort_values("IPI", ascending=False).head(200)
# Tabla completa: todas las ~17,130 zonas
```

### 22. Análisis de concentración

Cálculo de qué porcentaje de siniestros, criticidad y muertes concentran los cortes Top 50 / 200 / 500 / 1000 frente al total. Ver `resumen_concentracion_IPI_2016_2019_final.csv`.

### 23. Mapa final interactivo

```python
mapa = folium.Map(location=[4.65, -74.08], zoom_start=11, tiles="CartoDB positron")
# CircleMarker por cada zona Top 50, radio proporcional a IPI,
# color según familia_analitica, popup con datos de la zona
mapa.save("../outputs/maps/mapa_top50_IPI_final_2016_2019.html")
```

### 24. Outputs del NB02

Todos los CSV en `outputs/reports/` y el mapa en `outputs/maps/`. Ver `manifiesto_outputs_notebook_02.csv` para la lista completa con flag de existencia.

---

## Convenciones aplicadas

- **Texto en mayúsculas y sin espacios laterales** (categóricas).
- **`COPY` antes de transformar:** `df_limpia = df.copy()` — no se modifica el raw.
- **Validación contra conteo del servidor** después de cada descarga grande.
- **Outputs intermedios versionados** (eventualmente con sufijo `_v1`, `_v2`).

---

## Lo que NO se ha hecho todavía (metodológicamente importante)

- Validación de actualidad del IPI con periodo reciente (objetivo del NB03).
- Exploración de capas hermanas SIMUR: actores viales, vehículos, causas (NB03/NB04).
- Análisis temporal (hora del día, día de la semana, temporada).
- Integración de actores viales (peatón, motociclista, ciclista, conductor).
- Integración de tipo de vehículo.
- Normalización por población o exposición (NB05).
- Comparación entre métodos de agregación espacial (3-decimal vs H3 vs DBSCAN vs snap-to-network).
- Análisis de sensibilidad del puntaje de gravedad (1/3/5 vs pesos EPDO vs pesos por costos económicos).
- Detección de cambio estructural pre/post-pandemia.
- Creación de snapshot con hash MD5 de la descarga.

Ver `memory/next_steps.md` para el orden de ataque.
