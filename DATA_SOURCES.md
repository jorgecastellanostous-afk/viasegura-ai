# Fuentes de datos — VíaSegura AI

> Documentación formal de todas las fuentes de datos usadas o planeadas. Actualizar cada vez que se incorpore una fuente nueva.

---

## Fuente activa: SIMUR — Secretaría Distrital de Movilidad

### Descripción

La Secretaría Distrital de Movilidad (SDM) de Bogotá publica datos de accidentalidad vial a través del Sistema de Información de Movilidad Urbana Regional (SIMUR). El servicio de consulta es una API ArcGIS REST sobre FeatureServer.

### Datos de acceso

| Campo | Valor |
|---|---|
| Organismo | Secretaría Distrital de Movilidad — Bogotá D.C. |
| Sistema | SIMUR — Sistema de Información de Movilidad Urbana Regional |
| Tipo de servicio | ArcGIS FeatureServer (REST API) |
| URL base del servicio | `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer` |
| Capa usada | `/2` — Tabla **ACCIDENTE** |
| URL de consulta | `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query` |
| CRS reportado | EPSG:4686 (MAGNA-SIRGAS lat/lon) |
| Acceso | Público, sin autenticación |

### Cobertura temporal auditada

| Año | Registros |
|---|---|
| 2007 | 59,766 |
| 2008 | 57,148 |
| 2009 | 44,456 |
| 2010 | 53,852 |
| 2011 | 55,886 |
| 2012 | 58,190 |
| 2013 | 58,338 |
| 2014 | 56,608 |
| 2015 | 55,822 |
| **2016** | **63,932** |
| **2017** | **64,828** |
| **2018** | **66,816** |
| **2019** | **65,255** |
| 2020 | 44,240 |
| 2021 | 28,855 |
| 2022 | 25,453 |
| 2023 | 14,115 |
| 2024 | 14,020 |
| 2025 | 12,378 |
| 2026 | 3,180 |
| **Total** | **904,424** |

Auditoría ejecutada en NB01. Los conteos bajos de 2022–2024 están bajo investigación (ver Nota 1).

### Periodo descargado para el análisis base

| Campo | Valor |
|---|---|
| Periodo | 2016–2019 |
| Total de registros | 260,831 |
| Validación | Diferencia con conteo oficial = 0 |
| Archivos crudos | `data/raw/accidentes_bogota_2016_2019_raw.csv` (66 MB) |
| Chunks de descarga | `data/raw/chunks_accidentes_2016_2019/` (262 archivos) |
| Base procesada | `data/processed/accidentes_bogota_2016_2019_limpio.csv` (47 MB, 19 col) |

### Estructura del dataset (columnas clave)

| Columna | Tipo | Descripción |
|---|---|---|
| OBJECTID | int | Identificador único del registro |
| FORMULARIO | str | Número de formulario de registro |
| CODIGO_ACCIDENTE | int | Código del siniestro |
| FECHA_OCURRENCIA_ACC | datetime | Fecha del siniestro (epoch ms convertido) |
| ANO_OCURRENCIA_ACC | int | Año del siniestro |
| MES_OCURRENCIA_ACC | str | Mes (texto, MAYÚSCULAS) |
| DIA_OCURRENCIA_ACC | str | Día de la semana (MAYÚSCULAS) |
| HORA_OCURRENCIA_ACC | str | Hora HH:MM:SS |
| GRAVEDAD | str | SOLO DANOS / CON HERIDOS / CON MUERTOS |
| CLASE_ACC | str | CHOQUE / ATROPELLO / CAIDA DE OCUPANTE / etc. |
| LOCALIDAD | str | Localidad de Bogotá (MAYÚSCULAS) |
| BARRIO | str | Barrio (MAYÚSCULAS) |
| MVINOMBRE | str | Nombre de la vía (MAYÚSCULAS) |
| LATITUD | float | Latitud decimal (MAGNA-SIRGAS) |
| LONGITUD | float | Longitud decimal (MAGNA-SIRGAS) |
| DISTANCIA_VIA | float | Distancia al eje de la vía (m) |
| puntaje_gravedad | int | Derivado: 1 / 3 / 5 según GRAVEDAD |

### Calidad de los datos (periodo base)

| Métrica | Valor |
|---|---|
| Duplicados en OBJECTID | 0 |
| Duplicados en CODIGO_ACCIDENTE | 0 |
| Duplicados en FORMULARIO | 0 |
| Nulos en LATITUD | 0 |
| Nulos en LONGITUD | 0 |
| Registros fuera del bbox de Bogotá | 0 |
| Nulos en puntaje_gravedad | 0 |

### Capas hermanas no exploradas (pendiente NB03)

El FeatureServer `AccidentalidadAnalisis` tiene múltiples capas. Se sabe de la existencia de al menos:

| Capa | Nombre probable | Estado |
|---|---|---|
| /0 | Desconocida | No auditada |
| /1 | Desconocida | No auditada |
| /2 | ACCIDENTE | En uso |
| /3 | Posiblemente ACTOR_VIAL | No auditada |
| /4 | Posiblemente VEHICULO | No auditada |
| /5+ | Desconocidas | No auditadas |

La auditoría completa de capas hermanas es el objetivo de la Sección 6 del NB03.

---

## Nota 1 — Alerta sobre datos recientes (2022–2024)

Los conteos de 2022–2024 son notablemente más bajos que el promedio del periodo base (~65,000/año vs ~14,000–25,000/año reciente). Esta diferencia podría indicar:

1. Datos aún no cargados en el FeatureServer para esos años.
2. Cambio de plataforma o metodología de registro en SIMUR.
3. Otra capa o servicio con datos más completos para años recientes.

**Acción:** el NB03 debe auditar esta discrepancia antes de cualquier descarga masiva de datos recientes.

---

## Fuentes planeadas (no descargadas)

| Fuente | Organismo | Para qué | Prioridad |
|---|---|---|---|
| Capa de localidades de Bogotá | IDU / IDECA | Cruce espacial para agregaciones por localidad | Alta |
| Capa UPZ | SDM / IDECA | Granularidad intermedia entre barrio y localidad | Alta |
| Población por UPZ o localidad | DANE — Censo 2018 | Normalización por exposición poblacional | Alta |
| Red vial de Bogotá | OSM o IGAC | Longitud de tramo para normalización | Media |
| datos.gov.co — accidentalidad | Gobierno de Colombia | Comparador y alternativa a SIMUR | Media |
| ANSV / Observatorio vial | ANSV | Comparador con cifras nacionales | Media |
| DANE — mortalidad CIE-10 V01–V99 | DANE | Validación cruzada de muertes viales | Baja |
| Forensis — Medicina Legal | INMLCF | Fuente independiente de muertes en vía | Baja |

---

## Reproducibilidad

⚠️ **Pendiente:** crear `data/raw/_snapshot_metadata.json` con fecha de descarga, hash MD5 del archivo crudo y versión de Python. La fuente SIMUR es una API viva que puede actualizar datos históricos, por lo que el snapshot es necesario para garantizar reproducibilidad exacta.
