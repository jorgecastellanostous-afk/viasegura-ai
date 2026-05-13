# Fuentes de datos — memoria operativa

> **Para qué sirve este archivo:** resumen rápido de qué fuentes están en uso, dónde viven los archivos en disco y cómo volver a llamarlas. Para la versión formal y completa, ver `DATA_SOURCES.md` en la raíz.

---

## Fuente principal en uso

### Secretaría Distrital de Movilidad — SIMUR (ArcGIS FeatureServer)

- **Servicio:** `Accidentalidad / AccidentalidadAnalisis / FeatureServer`
- **Capa principal usada:** capa `2` (tabla **ACCIDENTE**)
- **URL de query:**
  `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query`
- **Total de registros en la capa (auditoría):** 904,424 (todos los años, hasta el momento de descarga)
- **Periodo descargado:** 2016–2019
- **Total de registros descargados:** 260,831
- **Diferencia frente a conteo oficial del servidor:** 0
- **CRS reportado:** EPSG:4686 (MAGNA-SIRGAS lat/lon)

---

## Archivos en disco

| Archivo | Ruta | Tamaño | Filas | Estado |
|---|---|---|---|---|
| Base cruda 2016–2019 | `data/raw/accidentes_bogota_2016_2019_raw.csv` | 66 MB | 260,831 | inmutable |
| Chunks de descarga | `data/raw/chunks_accidentes_2016_2019/` (262 archivos) | — | — | inmutable |
| Muestra exploratoria | `data/raw/accidentes_bogota_muestra_10000.csv` | 2.6 MB | 10,000 | apoyo |
| Base limpia 2016–2019 | `data/processed/accidentes_bogota_2016_2019_limpio.csv` | 47 MB | 260,831 | con `puntaje_gravedad` |

---

## Columnas en el CSV limpio

```
OBJECTID, FORMULARIO, CODIGO_ACCIDENTE,
FECHA_OCURRENCIA_ACC, HORA_OCURRENCIA_ACC,
ANO_OCURRENCIA_ACC, MES_OCURRENCIA_ACC, DIA_OCURRENCIA_ACC,
DIRECCION, GRAVEDAD, CLASE_ACC,
LOCALIDAD, MUNICIPIO,
LATITUD, LONGITUD, BARRIO, MVINOMBRE, DISTANCIA_VIA,
puntaje_gravedad
```

---

## Distribución del periodo

| Año | Registros |
|---|---|
| 2016 | 63,932 |
| 2017 | 64,828 |
| 2018 | 66,816 |
| 2019 | 65,255 |
| **Total** | **260,831** |

---

## Capas hermanas no exploradas todavía

El servicio `AccidentalidadAnalisis` tiene varias capas en `FeatureServer/0`, `/1`, `/3`, `/4`, etc., que probablemente contienen tablas relacionadas:

- `ACTOR_VIAL` — rol del actor (peatón, conductor, pasajero)
- `VEHICULO` — tipo, modalidad, gravedad por vehículo
- Posibles: `CAUSA_PROBABLE`, `HIPOTESIS`

**Acción pendiente (Fase 3):** probar consultas tipo `f=json&returnCountOnly=true&where=1=1` contra `/0`, `/1`, `/3`, `/4` y mapear el contenido.

---

## Fuentes complementarias planeadas (no descargadas todavía)

| Fuente | Para qué | Prioridad |
|---|---|---|
| Capa de localidades de Bogotá | Cruce espacial | Alta |
| Capa UPZ Bogotá | Granularidad fina | Alta |
| Población DANE por UPZ | Normalización por exposición | Alta |
| Red vial Bogotá (OSM o IGAC) | Snap-to-network | Media |
| Datos abiertos Colombia (`datos.gov.co`) | Alternativas y comparadores | Media |
| ANSV / Observatorio | Comparador con cifras oficiales | Media |
| DANE — mortalidad CIE-10 V01–V99 | Validación cruzada de muertes viales | Baja |
| Forensis (Medicina Legal) | Comparador independiente | Baja |

---

## Snapshot y reproducibilidad

⚠️ **Pendiente:** crear `data/raw/_snapshot_metadata.json` con:

- Fecha de descarga.
- Hash MD5 del CSV crudo final.
- Conteo total reportado por la API ese día (904,424).
- Versión de Python y `requests` usada.

Esto blindará la reproducibilidad si SIMUR actualiza años pasados (que sí pasa con datos administrativos).
