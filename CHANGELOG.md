# Changelog — VíaSegura AI

> Registro cronológico de cambios significativos por fase de trabajo. Las fechas son aproximadas al mes de trabajo.

---

## [Fix IPI NB02] — 2026-05-08

### Corregido
- Bug ADR-06: celda `4e635223` en NB02 usaba pesos desiguales (`score_criticidad_total × 0.25`, `score_fatalidad × 0.15`) en lugar de `mean()` de 5 scores igualmente ponderados.
- Aplicado via `fix_ipi_nb02.py` (script standalone — workaround encoding Windows/conda).

### Outputs regenerados con pesos iguales
- `outputs/reports/zonas_criticas_IPI_completo_2016_2019.csv`
- `outputs/reports/top50_IPI_final_2016_2019.csv`
- `outputs/reports/top200_prioridad_intervencion_IPI_2016_2019.csv`
- `outputs/reports/zonas_criticas_IPI_familia_analitica_2016_2019.csv`
- `outputs/reports/resumen_familia_analitica_2016_2019.csv`
- `outputs/reports/resumen_concentracion_IPI_2016_2019_final.csv`
- `outputs/reports/zonas_sensibles_fatalidad_2016_2019.csv`
- `outputs/maps/mapa_top50_IPI_final_2016_2019.html`

### Nueva distribución de familias analíticas (post-fix)

| Familia | Zonas |
|---|---|
| Hotspot robusto integral | 45 |
| Hotspot de severidad/fatalidad | 68 |
| Hotspot de carga acumulada | 155 |
| Hotspot preventivo prioritario | 346 |
| Seguimiento | 16,516 |

### Impacto en NB03
NB03 fue ejecutado con el IPI anterior. El delta en valores IPI es ~0.03 pts en las zonas top. Los rankings y clasificaciones de persistencia no cambian de forma material. Se recomienda reejecutar NB03 antes de comenzar NB05.

---

## [NB02 completo] — 2025 Q1–Q2

### Añadido
- `notebooks/02_indice_criticidad_y_hotspots.ipynb` — Notebook completo del IPI.
- `outputs/reports/top50_IPI_final_2016_2019.csv` — Top 50 zonas por IPI (output operativo).
- `outputs/reports/top200_prioridad_intervencion_IPI_2016_2019.csv` — Top 200 extendido.
- `outputs/reports/zonas_criticas_IPI_completo_2016_2019.csv` — Todas las ~17,130 zonas con IPI completo.
- `outputs/reports/resumen_familia_analitica_2016_2019.csv` — Distribución de zonas por familia analítica.
- `outputs/reports/resumen_concentracion_IPI_2016_2019_final.csv` — Concentración de siniestros/muertes por corte Top N.
- `outputs/reports/zonas_sensibles_fatalidad_2016_2019.csv` — Zonas con presencia de siniestros con muertos.
- `outputs/reports/zonas_criticas_IPI_familia_analitica_2016_2019.csv` — Zonas clasificadas con familia.
- `outputs/maps/mapa_top50_IPI_final_2016_2019.html` — Mapa interactivo final del Top 50.
- `outputs/reports/resumen_ejecutivo_notebook_02.md` — Resumen ejecutivo del NB02.
- `outputs/reports/manifiesto_outputs_notebook_02.csv` — Lista de outputs con flag de existencia.

### Metodología incorporada
- Índice de Prioridad de Intervención (IPI): 5 scores normalizados promediados.
- Clasificación en 5 familias analíticas: robusto integral, severidad/fatalidad, carga acumulada, preventivo prioritario, seguimiento.
- Top 50 como output operativo de priorización.

### Resultado clave
El Top 50 IPI (0.29% de zonas) concentra el 6.39% de muertes del periodo. El Top 1000 (5.84% de zonas) concentra el 63.33% de muertes.

---

## [NB01 completo] — 2025 Q1

### Añadido
- `notebooks/01_exploracion_datos_siniestralidad.ipynb` — Notebook de exploración y descarga.
- `data/raw/accidentes_bogota_muestra_10000.csv` — Muestra exploratoria inicial.
- `data/raw/accidentes_bogota_2016_2019_raw.csv` — Base completa 2016–2019 descargada.
- `data/raw/chunks_accidentes_2016_2019/` — 262 chunks de descarga segura por año y bloque.
- `data/processed/accidentes_bogota_2016_2019_limpio.csv` — Base limpia con puntaje de gravedad.
- `outputs/reports/auditoria_conteo_siniestros_por_anio.csv` — Conteo oficial 2007–2026.
- `outputs/reports/resumen_calidad_datos_2016_2019.csv` — Métricas de calidad de la base.
- `outputs/reports/tabla_localidad_2016_2019.csv` — Siniestros y criticidad por localidad.
- `outputs/reports/tabla_gravedad_2016_2019.csv` — Distribución por gravedad.
- `outputs/reports/tabla_clase_accidente_2016_2019.csv` — Distribución por clase de accidente.
- `outputs/reports/tabla_anio_2016_2019.csv` — Distribución por año.
- `outputs/maps/mapa_calor_criticidad_siniestros_2016_2019.html` — Mapa de calor exploratorio.

### Validaciones realizadas
- Total descargado (260,831) coincide con conteo oficial del FeatureServer: diferencia = 0.
- Sin duplicados en OBJECTID, CODIGO_ACCIDENTE ni FORMULARIO.
- Sin nulos en coordenadas. Sin registros fuera del bounding box de Bogotá.
- Sin nulos en `puntaje_gravedad`.

---

## [Inicialización] — 2025 Q1

### Añadido
- Estructura de carpetas: `notebooks/`, `data/raw/`, `data/processed/`, `outputs/maps/`, `outputs/reports/`, `memory/`, `app/`, `sql/`.
- Archivos de memoria operativa: `memory/project_context.md`, `memory/methodology.md`, `memory/decisions_log.md`, `memory/code_log.md`, `memory/data_sources.md`.

---

## [NB03 Fase 2 completa] — 2026 Q2

### Añadido
- Secciones 5–10 de `notebooks/03_validacion_actualidad_y_enriquecimiento_simur.ipynb`
- `data/raw/chunks_accidentes_2020_2021/` — chunks de descarga del periodo reciente
- `data/raw/accidentes_bogota_reciente_raw.csv` — 72,903 registros crudos (2020–2021)
- `data/processed/accidentes_bogota_reciente_limpio.csv` — base procesada con puntaje de gravedad
- `outputs/reports/validacion_descarga_reciente_notebook_03.csv` — validación de integridad
- `outputs/reports/calidad_datos_reciente_notebook_03.csv` — métricas de calidad
- `outputs/reports/top50_IPI_reciente_notebook_03.csv` — Top 50 zonas priorizadas 2020–2021
- `outputs/reports/top200_IPI_reciente_notebook_03.csv` — Top 200 extendido reciente
- `outputs/reports/zonas_criticas_IPI_reciente_completo_notebook_03.csv` — todas las zonas con IPI reciente
- `outputs/reports/comparacion_IPI_base_vs_reciente_notebook_03.csv` — merge base vs reciente
- `outputs/reports/clasificacion_hotspots_persistencia_notebook_03.csv` — clasificación de 19,255 zonas
- `outputs/maps/mapa_comparacion_persistencia_notebook_03.html` — mapa Top 200 base (rojo) vs reciente (azul)
- `outputs/maps/mapa_clasificacion_persistencia_notebook_03.html` — mapa de clasificación por categoría
- `DECISIONS.md` ADR-10 — periodo de validación post-base 2020–2021 y exclusión de 2022–2025
- `run_sec9_10.py` — script standalone para Secciones 9–10 (workaround encoding Windows/conda)

### Decisión metodológica clave (ADR-10)
Los años 2022–2025 fueron excluidos del análisis IPI por presentar un ratio CON HERIDOS/SOLO DAÑOS de 11–14x respecto al periodo base, indicando un posible cambio de metodología de registro en SIMUR. Solo 2020–2021 superan los 4 criterios de integridad y se usan como "periodo de validación post-base".

### Resultados de la comparación (Secciones 9–10)

| Categoría | Zonas | Descripción |
|---|---|---|
| **Persistente** | **37** | En Top 200 de ambos periodos |
| **Emergente** | **163** | Top 200 reciente, fuera de Top 500 base |
| **Disminuido** | **35** | Top 50 base, fuera de Top 500 reciente |
| **Histórico** | **0** | Top 50 base sin actividad reciente |
| Sensibles a fatalidad | 2,211 | CON MUERTOS en cualquier periodo |

- Solapamiento Top 200 base vs reciente: **37 zonas (18.5%)**
- Del Top 50 base: **12 zonas (24%)** permanecen en Top 200 reciente
- Zonas persistentes más robustas: SANTA FE (4.611, -74.075), CHAPINERO (4.647, -74.065)
- Kennedy concentra 7 de las 10 zonas emergentes más altas

### Limitación crítica documentada
El bajo solapamiento (18.5%) y los 35 Disminuidos se explican parcialmente por la **pandemia COVID-19** en 2020–2021. Menos tráfico implica menos siniestros en todas las zonas. No se puede atribuir la disminución a intervenciones exitosas sin datos de exposición.

---

## [NB03 Fase 1 completa] — 2026 Q2

### Añadido
- Secciones 1–4 y Sección 11 de `notebooks/03_validacion_actualidad_y_enriquecimiento_simur.ipynb`
- `outputs/reports/auditoria_conteo_actualizada_notebook_03.csv`
- `outputs/reports/auditoria_cobertura_mensual_reciente_notebook_03.csv`
- `outputs/reports/auditoria_ratios_gravedad_notebook_03.csv`
- `outputs/reports/auditoria_cobertura_localidades_reciente_notebook_03.csv`
- `outputs/reports/diagnostico_integridad_datos_recientes_notebook_03.csv`
- `outputs/reports/auditoria_capas_hermanas_simur_notebook_03.csv`
- `outputs/reports/detalle_campos_capas_simur_notebook_03.csv`
- `outputs/reports/manifiesto_outputs_notebook_03_fase1.csv`

### Capas hermanas SIMUR auditadas
7 capas encontradas: MUERTO (15.6K), LESIONADO (475K), ACCIDENTE (900K), VM_ACC_ACTOR_VIAL (3.3M), VM_ACC_CAUSA (1.9M), VM_ACC_VEHICULO (2.8M), VM_ACC_VIA (961K). Clave de join: `FORMULARIO`.

---

## [NB03 completo] — 2026 Q2

### Añadido
- Secciones 12–13 de `notebooks/03_validacion_actualidad_y_enriquecimiento_simur.ipynb`
- `outputs/reports/esquema_integracion_nb04_notebook_03.csv` — contrato de integración para NB04 (4 capas VM_ACC_*)
- `outputs/reports/manifiesto_outputs_notebook_03_completo.csv` — manifiesto completo de 18 outputs del NB03
- `add_sections12_13.py` — script de inserción de celdas (workaround encoding Windows/conda)

### Sección 12 — Esquema de integración NB04
Documenta las 4 capas hermanas SIMUR para el siguiente notebook:

| Capa | ID | Registros | Prioridad NB04 |
|---|---|---|---|
| VM_ACC_ACTOR_VIAL | 3 | 3,267,086 | Alta |
| VM_ACC_CAUSA | 4 | 1,865,722 | Alta |
| VM_ACC_VEHICULO | 5 | 2,803,601 | Alta |
| VM_ACC_VIA | 6 | 961,101 | Media |

Estrategia NB04: para cada zona del Top 200 reciente, JOIN de FORMULARIOs → moda de tipo_actor, tipo_vehiculo, causa_accidente.

### Sección 13 — Manifiesto final
18 outputs documentados (reports + maps). Verifica existencia y tamaño de cada archivo.

### Corrección crítica aplicada
- Celdas `5829fb7d` y `ce83497a` (Sección 9): añadido bloque `zonas_base_m = zonas_base.copy()` con rename `LAT_ZONA→lat_grid`, `LON_ZONA→lon_grid`, `localidad_predominante→localidad_modal`. El merge fallaba silenciosamente porque NB02 usa nomenclatura distinta.
- `outputs/reports/resumen_ejecutivo_notebook_03.md` — resumen ejecutivo de 167 líneas

### Estado final del NB03
Todas las secciones 1–13 construidas y corregidas. 19 outputs generados.

---

## [Revisión pre-NB04 + NB03.5] — 2026-05-08

### Añadido
- `notebooks/03.5_sintesis_metodologica_y_documentacion.ipynb` — Notebook de referencia con síntesis metodológica completa de NB01–NB03. Explica cada variable derivada, los 5 scores del IPI, la comparación de índices de criticidad y sus límites. No genera outputs nuevos — solo documentación ejecutable.
- `scripts/generar_snapshot_metadata.py` — Script para calcular hash MD5 de archivos raw y guardarlos en `data/raw/_snapshot_metadata.json`.
- `data/raw/_snapshot_metadata.json` — Snapshot generado: 2016-2019 raw (260,831 filas, 69.0 MB, md5=88b1aa5e...), reciente raw (72,903 filas, 11.8 MB, md5=f39e9986...), muestra (10,000 filas, 2.6 MB).

### Modificado
- `DECISIONS.md` — Añadido ADR-11: parametrización futura de pesos del IPI. Documenta puntos de intervención exactos en el código (`PESOS_GRAVEDAD`, `PESOS_IPI`, `N_ANIOS_BASE`, `N_ANIOS_RECIENTES`) y escala comparativa de estándares internacionales.
- `memory/project_context.md` — Estado actualizado al cierre de NB03.5. Próximo paso corregido: NB04 (antes decía NB03).

### NB03.5 — Secciones incluidas

| Sección | Contenido |
|---|---|
| 0 | Propósito y navegación del notebook |
| 1 | Contexto de VíaSegura AI (qué es, qué no es, audiencia) |
| 2 | Fuente de datos: SIMUR ArcGIS FeatureServer (capas 0–6) |
| 3 | NB01: variables originales, descarga segura, limpieza, `puntaje_gravedad` |
| 4 | NB02: grilla 0.001°, variables por zona, 5 scores del IPI, clasificaciones |
| 5 | NB03: auditoría de años recientes, ADR-10, IPI reciente, persistencia, capas SIMUR |
| 6 | Comparación de índices de criticidad + estándares internacionales (EPDO, FHWA, OMS) |
| 7 | Limitaciones globales L1–L10 con severidad y estado |
| 8 | Hoja de ruta NB04–NB06 con insumos y secciones propuestas |

---

## Próxima entrada esperada

`[NB04 inicio]` — Enriquecimiento de hotspots con capas VM_ACC_ACTOR_VIAL, VM_ACC_CAUSA y VM_ACC_VEHICULO.
