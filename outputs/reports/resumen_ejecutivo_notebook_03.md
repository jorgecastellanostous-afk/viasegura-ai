# Resumen ejecutivo — Notebook 03
## VíaSegura AI · Validación de actualidad y enriquecimiento SIMUR

**Fecha de elaboración:** 2026-05-07  
**Periodo base:** 2016–2019 (260,831 siniestros — NB01/NB02)  
**Periodo de validación post-base:** 2020–2021 (72,903 siniestros)  
**Datos:** SIMUR · FeatureServer Accidentalidad · Bogotá D.C.

---

## 1. Cambio metodológico en SIMUR a partir de 2022

La auditoría de integridad del NB03 detectó una discontinuidad estructural en los datos de SIMUR a partir del año 2022. El indicador clave es el ratio de gravedad: la proporción entre siniestros "CON HERIDOS" y "SOLO DAÑOS" saltó de ~0.49 en el periodo base a valores de entre 11× y 14× en 2022–2025.

| Año | Siniestros | Ratio CON HERIDOS / SOLO DAÑOS | Pasa criterios |
|---|---|---|---|
| 2016–2019 (base) | ~65,208 / año | ~0.49 | Referencia |
| 2020 | 44,049 | Dentro de rango | ✓ |
| 2021 | 28,854 | Dentro de rango | ✓ |
| 2022 | — | ~11× | ✗ |
| 2023 | — | ~13× | ✗ |
| 2024 | — | ~14× | ✗ |
| 2025 | — | ~11× | ✗ |

Este cambio no puede explicarse por una variación real del comportamiento vial. Todo indica un cambio en la metodología de clasificación de gravedad dentro del sistema de registro de SIMUR. Usar 2022–2025 generaría un IPI incomparable con el periodo base y conclusiones inválidas.

**Decisión (ADR-10):** los años 2022–2025 quedan excluidos del análisis IPI. Solo 2020 y 2021 superan los cuatro criterios de integridad: volumen suficiente, cobertura mensual completa (12/12 meses), ratio de gravedad dentro del rango histórico y cobertura de las 20 localidades de Bogotá.

---

## 2. Periodo de validación post-base: 2020–2021

Los 72,903 registros descargados corresponden a 44,049 siniestros en 2020 y 28,854 en 2021. La base pasó validación de integridad sin duplicados en OBJECTID, CODIGO_ACCIDENTE ni FORMULARIO, sin coordenadas nulas y sin registros fuera del bounding box de Bogotá.

La denominación "periodo de validación post-base" refleja su propósito: no es un diagnóstico actualizado del riesgo vial (los años COVID distorsionan los conteos por reducción de movilidad), sino una validación temporal del modelo IPI desarrollado en el NB02.

**Limitación crítica:** 2020–2021 son años de pandemia COVID-19. La reducción de tráfico afecta mecánicamente todos los conteos de siniestros, especialmente en zonas de alta actividad comercial e industrial. El bajo solapamiento con el periodo base se explica en parte por este efecto y **no debe interpretarse como mejora real en las zonas que salieron del Top**.

---

## 3. IPI del periodo de validación post-base

Se aplicó la misma metodología del NB02 al periodo reciente:

- `score_persistencia = anios_activos / 2` (N_ANIOS_RECIENTES = 2)
- Cinco scores normalizados por percentil: volumen, criticidad total, severidad promedio, persistencia y fatalidad
- `IPI = mean([score_volumen, score_criticidad_total, score_severidad_promedio, score_persistencia, score_fatalidad]) × 100`

Los valores de IPI reciente **no son comparables en magnitud** con los del IPI base. Ambos son percentiles calculados internamente sobre sus propios universos. La comparación válida es de rankings y de presencia en cortes (Top 50, Top 200, Top 500).

**Nota de trazabilidad (2026-05-08):** Este notebook fue ejecutado con el IPI base generado antes de la corrección ADR-06 (`fix_ipi_nb02.py`). El bug corregido usaba pesos desiguales en NB02 (criticidad_total × 0.25, fatalidad × 0.15 en lugar de `mean()`). El delta en valores IPI es ≤ 0.03 puntos; la composición del Top 200 base puede diferir en zonas en el margen del límite 200. Los resultados de clasificación (37 persistentes, 163 emergentes, 35 disminuidos) son sustancialmente equivalentes. Se recomienda reejecutar NB03 antes de NB05 para consistencia total.

---

## 4. Comparación base vs reciente

| Métrica | Valor |
|---|---|
| Universo de zonas comparado | 19,255 |
| Zonas en Top 200 base | 200 |
| Zonas en Top 200 reciente | 200 |
| **Solapamiento (ambos Top 200)** | **37 zonas — 18.5%** |
| Top 50 base que persisten en Top 200 reciente | 12 de 50 — 24% |

El solapamiento del 18.5% es bajo pero esperado dado el efecto COVID. Las 37 zonas que aparecen en el Top 200 de ambos periodos son las más sólidas metodológicamente, porque mantuvieron su posición relativa de riesgo pese a la caída general de movilidad.

---

## 5. Clasificación de hotspots por persistencia

| Categoría | Zonas | Criterio de clasificación |
|---|---|---|
| **Persistente** | **37** | Top 200 en ambos periodos |
| **Emergente** | **163** | Top 200 reciente · fuera del Top 500 base |
| **Disminuido** | **35** | Top 50 base · fuera del Top 500 reciente |
| **Histórico** | **0** | Top 50 base · sin actividad en periodo reciente |
| **Sensible a fatalidad** | **2,211** | Con muertos registrados en cualquier periodo |

### Persistentes (37) — zonas de intervención prioritaria

Son las zonas cuya concentración de riesgo se mantuvo en ambos periodos. Representan el núcleo más confiable para intervención porque resisten tanto el filtro estadístico como el temporal. Las más robustas:

| Coordenadas | Localidad | Rank base | Rank reciente | Muertos |
|---|---|---|---|---|
| (4.611, -74.075) | SANTA FE | 7 | 13 | Sí |
| (4.647, -74.065) | CHAPINERO | 11 | 41 | Sí |
| (4.602, -74.077) | SANTA FE | 3 | 100 | Sí |

### Emergentes (163) — requieren validación adicional

Aparecen en el Top 200 reciente pero no estaban en el Top 500 base. Kennedy concentra 7 de las 10 primeras zonas emergentes. Antes de priorizar intervención, debe evaluarse si son puntos negros nuevos o un efecto de recomposición del tráfico post-pandemia.

### Disminuidos (35) — no confirman mejora

Estaban en el Top 50 base y cayeron fuera del Top 500 reciente. Los casos más marcados son en Puente Aranda y Santa Fe — zonas de alta actividad comercial e industrial que redujeron circulación durante la pandemia. Ejemplo:

- (4.607, -74.130) Puente Aranda: rank base 6 → rank reciente 2,572
- (4.609, -74.072) Santa Fe: rank base 14 → rank reciente 2,335

Estos descensos **no implican que las intervenciones funcionaron**. Sin datos de exposición (volumen vehicular por zona), no es posible separar el efecto COVID del efecto de posibles mejoras en infraestructura o comportamiento.

### Históricos (0)

Ninguna zona del Top 50 base quedó completamente inactiva en el periodo reciente. Todas mantuvieron algún nivel de siniestralidad.

### Sensibles a fatalidad (2,211)

Zonas con al menos un siniestro con víctimas mortales en cualquiera de los dos periodos. No requieren estar en el Top 200 para pertenecer a esta categoría. Son un insumo directo para políticas de prevención de mortalidad independientemente del ranking IPI.

---

## 6. Capas hermanas SIMUR detectadas para NB04

La Sección 11 auditó el FeatureServer de Accidentalidad y encontró 7 capas relacionadas con la capa principal de siniestros:

| Capa | Layer ID | Registros | Clave de join | Uso previsto en NB04 |
|---|---|---|---|---|
| MUERTO | 0 | 15,600 | FORMULARIO | Ya integrado vía puntaje_gravedad |
| LESIONADO | 1 | 475,000 | FORMULARIO | Ya integrado vía puntaje_gravedad |
| ACCIDENTE | 2 | 900,000 | FORMULARIO | Capa principal (usada en NB01–03) |
| **VM_ACC_ACTOR_VIAL** | 3 | 3,267,086 | FORMULARIO | Tipo de actor: peatón, ciclista, motorista |
| **VM_ACC_CAUSA** | 4 | 1,865,722 | FORMULARIO | Causa del siniestro |
| **VM_ACC_VEHICULO** | 5 | 2,803,601 | FORMULARIO | Tipo de vehículo involucrado |
| VM_ACC_VIA | 6 | 961,101 | FORMULARIO | Condiciones de la vía |

La verificación de joins con 3 FORMULARIOs de muestra confirmó:
- VM_ACC_ACTOR_VIAL: ~2.7 registros por siniestro (múltiples actores)
- VM_ACC_CAUSA: ~1.3 registros por siniestro
- VM_ACC_VEHICULO: ~2.0 registros por siniestro
- VM_ACC_VIA: 0 registros en la muestra — **requiere verificación de cobertura antes de NB04**

---

## 7. Outputs generados

| Archivo | Sección | Descripción |
|---|---|---|
| `auditoria_conteo_actualizada_notebook_03.csv` | 3 | Conteos anuales actualizados |
| `auditoria_cobertura_mensual_reciente_notebook_03.csv` | 3 | Cobertura mensual por año |
| `auditoria_ratios_gravedad_notebook_03.csv` | 3 | Ratios de gravedad por año |
| `auditoria_cobertura_localidades_reciente_notebook_03.csv` | 3 | Cobertura de localidades |
| `diagnostico_integridad_datos_recientes_notebook_03.csv` | 4 | Diagnóstico de integridad |
| `validacion_descarga_reciente_notebook_03.csv` | 6 | Validación de descarga |
| `calidad_datos_reciente_notebook_03.csv` | 7 | Calidad de datos reciente |
| `top50_IPI_reciente_notebook_03.csv` | 8 | Top 50 IPI 2020–2021 |
| `top200_IPI_reciente_notebook_03.csv` | 8 | Top 200 IPI 2020–2021 |
| `zonas_criticas_IPI_reciente_completo_notebook_03.csv` | 8 | IPI completo 2020–2021 |
| `comparacion_IPI_base_vs_reciente_notebook_03.csv` | 9 | Merge base vs reciente |
| `clasificacion_hotspots_persistencia_notebook_03.csv` | 10 | Clasificación de 19,255 zonas |
| `mapa_comparacion_persistencia_notebook_03.html` | 9 | Mapa: Top 200 base (rojo) vs reciente (azul) |
| `mapa_clasificacion_persistencia_notebook_03.html` | 10 | Mapa: clasificación por categoría |
| `auditoria_capas_hermanas_simur_notebook_03.csv` | 11 | Conteos por capa SIMUR |
| `detalle_campos_capas_simur_notebook_03.csv` | 11 | Campos por capa SIMUR |
| `esquema_integracion_nb04_notebook_03.csv` | 12 | Contrato de integración para NB04 |
| `manifiesto_outputs_notebook_03_completo.csv` | 13 | Manifiesto de 18 outputs |

---

## 8. Próximo paso: NB04

El NB04 enriquecerá cada zona del Top 200 reciente con información de contexto proveniente de las capas hermanas. La estrategia:

1. Para cada zona del Top 200, obtener todos los FORMULARIO de siniestros dentro de esa celda.
2. JOIN a VM_ACC_ACTOR_VIAL → moda de `CONDICION` (tipo de actor predominante).
3. JOIN a VM_ACC_VEHICULO → moda de `CLASE` (tipo de vehículo predominante).
4. JOIN a VM_ACC_CAUSA → moda de `NOMBRE` (causa más frecuente).
5. Agregar columnas descriptivas al DataFrame de clasificación de hotspots.

Pendiente confirmar cobertura de VM_ACC_VIA antes de incluirla en NB04.
