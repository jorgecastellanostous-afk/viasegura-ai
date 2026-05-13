# Resumen del Notebook 02 — Índice de Prioridad de Intervención (IPI)

> **Para qué sirve este archivo:** documentar qué hizo el Notebook 02, por qué fue un avance significativo, y qué produjo. Es la memoria operativa del salto de "mapa descriptivo" a "sistema de priorización".

---

## Nombre del notebook

`notebooks/02_indice_criticidad_y_hotspots.ipynb`

---

## Punto de partida

- Base limpia: `data/processed/accidentes_bogota_2016_2019_limpio.csv`
- 260,831 siniestros georreferenciados, 2016–2019
- Columna `puntaje_gravedad` ya calculada (1/3/5)

---

## Qué construyó el Notebook 02

### Fase 1 — Agregación espacial

Redondeó coordenadas a 3 decimales (`round(3)` → 0.001°), creando celdas de ~111 m × ~111 m sobre Bogotá. Los 260,831 siniestros se agruparon en ~17,130 zonas únicas.

Para cada zona se calculó:

- `cantidad_siniestros` — volumen total
- `criticidad_total` — suma de puntajes 1/3/5
- `criticidad_promedio` — criticidad_total / cantidad_siniestros
- `criticidad_{año}` — criticidad por cada uno de los 4 años (2016, 2017, 2018, 2019)
- `anios_activos` — cuántos de los 4 años tuvo al menos un siniestro
- `siniestros_solo_danos`, `siniestros_con_heridos`, `siniestros_con_muertos`
- `localidad_predominante`, `barrio_predominante`, `via_predominante`, etc.

### Fase 2 — Construcción del IPI

El **Índice de Prioridad de Intervención (IPI)** combina 5 componentes normalizados por rango percentil (o ratio directo en el caso de persistencia), promediados y escalados a 0–100:

```
IPI = mean(score_volumen,
           score_criticidad_total,
           score_severidad_promedio,
           score_persistencia,
           score_fatalidad) × 100
```

| Score | Qué mide | Normalización |
|---|---|---|
| `score_volumen` | Cantidad de siniestros | Percentil de rango entre todas las zonas |
| `score_criticidad_total` | Suma ponderada de gravedad | Percentil de rango |
| `score_severidad_promedio` | Criticidad media (severidad por siniestro) | Percentil de rango |
| `score_persistencia` | `anios_activos / 4` | Ratio directo (máximo = 1.0 con 4 de 4 años) |
| `score_fatalidad` | Presencia y magnitud de muertos | Percentil de rango sobre siniestros_con_muertos |

**Efecto clave del diseño:** una zona con pocos siniestros pero todos con muertos, presente los 4 años, puede superar en IPI a zonas con mayor volumen bruto. El IPI captura criticidad compuesta, no solo volumen.

### Fase 3 — Clasificación por tipo de hotspot

Cada zona recibió un `tipo_hotspot` descriptivo:

- `Hotspot severo` — volumen y criticidad máximos
- `Hotspot persistente con severidad media-alta` — activo los 4 años, criticidad promedio relevante
- `Hotspot exploratorio` — patrón incipiente, mérito investigativo

### Fase 4 — Familias analíticas

Clasificación superior que agrupa zonas por perfil de riesgo:

| Familia | Zonas | Siniestros | Muertes | IPI promedio |
|---|---|---|---|---|
| Hotspot robusto integral | 45 | 6,406 | 268 | 92.9 |
| Hotspot de severidad/fatalidad | 64 | 3,300 | 302 | 92.7 |
| Hotspot preventivo prioritario | 344 | 17,078 | 867 | 89.9 |
| Hotspot de carga acumulada | 155 | 32,449 | 371 | 85.0 |
| Seguimiento | 16,522 | 201,598 | 2,389 | 50.6 |

### Fase 5 — Top 50 y mapa final

El **Top 50 IPI** es el output operativo principal: 50 zonas que concentran el 6.39% de todas las muertes registradas en el periodo, siendo apenas el 0.29% de las zonas totales.

| Corte | % zonas | % siniestros | % criticidad | % muertes |
|---|---|---|---|---|
| Top 50 | 0.29% | 1.70% | 2.27% | **6.39%** |
| Top 200 | 1.17% | 5.53% | 7.03% | 17.92% |
| Top 500 | 2.92% | 13.80% | 15.94% | 38.69% |
| Top 1000 | 5.84% | 27.43% | 29.07% | 63.33% |

---

## Hallazgos geográficos

**Ejes dominantes en el Top 50:**
- Av. Caracas (corre N-S, atraviesa Santa Fe, Antonio Nariño, Rafael Uribe, Usme)
- Av. Fernando Mazuera (paralela a la Caracas hacia el sur)
- Av. Ciudad de Villavicencio (salida suroriental, Ciudad Bolívar)
- Av. Boyacá (corre N-S al occidente)
- Av. Ciudad de Cali (Kennedy occidental)

**Zona #1 (IPI 96.25):** Av. Ciudad de Villavicencio / Verona, Ciudad Bolívar — 108 siniestros, 18 muertos, activa los 4 años.

---

## Outputs generados

| Archivo | Descripción |
|---|---|
| `outputs/reports/top50_IPI_final_2016_2019.csv` | Lista operativa Top 50 |
| `outputs/reports/top200_prioridad_intervencion_IPI_2016_2019.csv` | Lista extendida Top 200 |
| `outputs/reports/zonas_criticas_IPI_completo_2016_2019.csv` | Todas las ~17,130 zonas con IPI |
| `outputs/reports/resumen_familia_analitica_2016_2019.csv` | Agregados por familia |
| `outputs/reports/resumen_concentracion_IPI_2016_2019_final.csv` | Concentración Top 50/200/500/1000 |
| `outputs/reports/zonas_sensibles_fatalidad_2016_2019.csv` | Zonas con siniestros con muertos |
| `outputs/maps/mapa_top50_IPI_final_2016_2019.html` | Mapa interactivo final |
| `outputs/reports/resumen_ejecutivo_notebook_02.md` | Resumen para presentación |
| `outputs/reports/manifiesto_outputs_notebook_02.csv` | Lista de outputs con flag existe/no |

---

## Limitación fundamental (no olvidar)

El IPI **no mide riesgo real**. No hay normalización por:
- Flujo vehicular
- Población expuesta
- Longitud de red vial
- Geometría de la vía
- Condiciones de infraestructura

El IPI mide **prioridad exploratoria de intervención**: dónde tiene más sentido mirar primero dado el volumen, la severidad, la persistencia y la presencia de fatalidades. Es el primer filtro, no el diagnóstico final.

---

## Por qué fue un salto metodológico

Antes del NB02, el proyecto tenía un mapa de calor descriptivo (NB01). El NB02 convirtió eso en una **lista ranqueada y defendible** de zonas con criterios explícitos, reproducibles y ajustables. El IPI no es la única fórmula posible, pero sí una fórmula documentada que permite discutir los supuestos.
