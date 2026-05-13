# Próximos pasos — VíaSegura AI

> **Para qué sirve este archivo:** saber qué hacer cuando se retoma el proyecto. Se actualiza al cerrar cada notebook.

---

## Estado actual (al cierre de revisión pre-NB04 — 2026-05-08)

- [x] NB01 — Exploración y validación de datos SIMUR 2016–2019
- [x] NB02 — IPI, familias analíticas, Top 50, mapa final **(corregido: pesos iguales via fix_ipi_nb02.py)**
- [x] NB03 — Validación de actualidad + exploración de capas complementarias SIMUR
- [x] NB03.5 — Síntesis metodológica: variables, IPI, índices de criticidad, limitaciones
- [x] Snapshot MD5 generado: `data/raw/_snapshot_metadata.json`
- [x] ADR-11 documentado: puntos de intervención para parametrizar pesos del IPI
- [ ] NB04 — Enriquecimiento con actores viales, vehículos, causas ← **PRÓXIMO**
- [ ] NB05 — Normalización por exposición (población, red vial)
- [ ] NB06 — Dashboard Streamlit + síntesis final

**Nota NB02→NB03:** El fix cambió ligeramente los valores IPI (~0.03 pts en top zonas). NB03 fue ejecutado con el IPI anterior. La composición del top 200 base puede diferir en zonas marginales. Considerar reejecutar NB03 antes de NB05 para consistencia total.

---

## Próximo paso inmediato: Notebook 04

**Archivo:** `notebooks/04_enriquecimiento_actor_vehiculo_causa.ipynb`

**Objetivo:** Para cada zona del Top 200 reciente, identificar el tipo de actor vial predominante, el tipo de vehículo y la causa más frecuente, usando las capas hermanas de SIMUR.

### Insumos listos

| Archivo | Descripción |
|---|---|
| `outputs/reports/clasificacion_hotspots_persistencia_notebook_03.csv` | 19,255 zonas clasificadas con rank y categoría |
| `outputs/reports/top200_IPI_reciente_notebook_03.csv` | Top 200 zonas del periodo reciente |
| `data/processed/accidentes_bogota_reciente_limpio.csv` | 72,903 siniestros con FORMULARIO |
| `outputs/reports/esquema_integracion_nb04_notebook_03.csv` | Contrato de integración: capas, campos y cardinalidad |

### Secciones propuestas para NB04

**Sección 1 — Setup y carga de insumos NB03**
- Verificar que los 4 archivos anteriores existen y tienen integridad
- Cargar `clasificacion_hotspots_persistencia_notebook_03.csv`

**Sección 2 — Construcción del índice FORMULARIO → zona**
- Para cada siniestro en `accidentes_bogota_reciente_limpio.csv`, asignar su celda de grilla `(round(LATITUD,3), round(LONGITUD,3))`
- Crear dict `{formulario: (lat_grid, lon_grid)}` para el join inverso

**Sección 3 — Descarga de VM_ACC_ACTOR_VIAL (layer 3)**
- Auditar conteo por año antes de descargar
- Descargar en chunks por año (2020 y 2021)
- Verificar cobertura de FORMULARIO vs la base de siniestros

**Sección 4 — Descarga de VM_ACC_VEHICULO (layer 5)**
- Mismo proceso que Sección 3

**Sección 5 — Descarga de VM_ACC_CAUSA (layer 4)**
- Mismo proceso que Sección 3

**Sección 6 — Verificación VM_ACC_VIA (layer 6)**
- Investigar por qué devolvió 0 en la muestra de NB03
- Decidir si incluirla o documentarla como no integrable

**Sección 7 — Join y agregación por zona**
- Para cada zona del Top 200: obtener FORMULARIOs → join a capas → calcular moda por zona
- Campos objetivo: `CONDICION` (actor), `CLASE` (vehículo), `NOMBRE` (causa)

**Sección 8 — Enriquecimiento del DataFrame de hotspots**
- Añadir columnas `actor_predominante`, `vehiculo_predominante`, `causa_predominante` a `clasificacion_hotspots`
- Generar mapa interactivo con popup completo por zona

**Sección 9 — Manifiesto y resumen ejecutivo**

---

## Deuda técnica pendiente

- `data/raw/_snapshot_metadata.json` con hash MD5 del raw, fecha descarga, versión Python.
- Parametrizar pesos del IPI (actualmente fijos 1/3/5) para análisis de sensibilidad.
- Comparar métodos de agregación espacial: 3-decimal vs H3 vs DBSCAN.
- Mover funciones repetidas a `src/` cuando el código se estabilice.
- `app/` — directorio vacío, Streamlit planificado para NB06.

---

## Hoja de ruta completa

| Notebook | Nombre | Estado |
|---|---|---|
| NB01 | Exploración y validación de datos SIMUR | ✅ Completado |
| NB02 | Índice de criticidad y hotspots (IPI) | ✅ Completado |
| NB03 | Validación de actualidad + exploración SIMUR | ✅ Completado |
| NB04 | Enriquecimiento con actores, vehículos, causas | ⏳ Próximo |
| NB05 | Normalización por exposición (población, red vial) | Pendiente |
| NB06 | Dashboard Streamlit + síntesis final | Pendiente |
