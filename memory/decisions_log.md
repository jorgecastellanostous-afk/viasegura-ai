# Bitácora de decisiones — VíaSegura AI

> **Para qué sirve este archivo:** registrar decisiones técnicas y metodológicas con contexto narrativo. Para la versión formal en formato ADR (Architecture Decision Record) ver `DECISIONS.md` en la raíz.

> **Regla:** las decisiones no se borran. Si una decisión cambia, se agrega una nueva entrada que la supersede y se referencia la anterior.

---

## D1 — Trabajar localmente, sin Google Drive

**Cuándo:** inicio del proyecto.
**Contexto:** se evaluó usar Google Drive para sincronización entre máquinas.
**Decisión:** trabajar localmente con Anaconda + JupyterLab.
**Razón:** límites de almacenamiento de Drive y latencia de sincronización con archivos pesados (la base cruda pesa 66 MB; los chunks 262 archivos).
**Implicación:** el proyecto vive en `C:\Users\jorge\Documents\viasegura_ai`. La portabilidad se logra con Git, no con Drive.

---

## D2 — Usar la fuente oficial SIMUR (ArcGIS) y no archivos planos

**Cuándo:** inicio del proyecto.
**Contexto:** se podía optar por descargas estáticas en `datos.gov.co` o por la API ArcGIS de SDM.
**Decisión:** usar la API ArcGIS `AccidentalidadAnalisis/FeatureServer/2`.
**Razón:** es la fuente que la SDM publica oficialmente y se actualiza más rápido que los datasets estáticos. Permite reproducibilidad por consulta.
**Implicación:** dependemos de la disponibilidad del servidor. Hay que blindar con descarga por chunks reanudable y guardar snapshot.

---

## D3 — Periodo MVP: 2016–2019

**Cuándo:** después de la auditoría por año.
**Contexto:** la base completa va de 2007 a 2026 con 904,424 registros, pero algunos años están incompletos (2025–2026) o subreportados (2023–2024).
**Decisión:** trabajar con 2016–2019 (260,831 registros).
**Razón:** periodo cerrado, completo, pre-pandemia.
**Implicación:** los hallazgos son representativos del Bogotá pre-2020. No se pueden extrapolar al Bogotá actual sin matices.

---

## D4 — Descarga por año y bloques de 1,000 (no 2,000)

**Cuándo:** primer intento de descarga.
**Contexto:** un primer intento con bloques de 2,000 falló a las ~196,000 filas con `RemoteDisconnected`.
**Decisión:** bajar a 1,000 registros por bloque, descargar año por año, guardar cada bloque como CSV individual y permitir reanudación.
**Razón:** robustez frente a interrupciones del servidor, no problema del código.
**Implicación:** quedaron 262 archivos chunk en `data/raw/chunks_accidentes_2016_2019/`. La unión final coincide con el conteo oficial.

---

## D5 — Índice de criticidad por gravedad: 1 / 3 / 5

**Cuándo:** durante la limpieza.
**Contexto:** se necesitaba un puntaje sintético para ordenar zonas críticas.
**Decisión:** asignar:

```
SOLO DAÑOS  = 1
CON HERIDOS = 3
CON MUERTOS = 5
```

**Razón:** índice sencillo, defendible para un MVP, fácil de explicar.
**Limitación conocida:** estos pesos son **bajos** comparados con prácticas internacionales (NHTSA usa aprox. 1:8:24 en EPDO; FHWA llega a 1:5:542 con costos económicos). Esto significa que con 1:3:5 un siniestro fatal pesa relativamente poco frente a uno con heridos.
**Acción futura:** documentar como ADR explícito en `DECISIONS.md`, hacer los pesos parametrizables en código, y correr análisis de sensibilidad mostrando cómo cambia el ranking si se usan pesos 1:5:25.
**Estado:** aceptado para MVP, pendiente de revisión metodológica.

---

## D6 — Agregación espacial inicial por redondeo a 3 decimales

**Cuándo:** durante la construcción del mapa de calor.
**Contexto:** se necesitaba reducir 260,831 puntos a celdas para visualizar densidad.
**Decisión:** redondear `LATITUD` y `LONGITUD` a 3 decimales (≈ 100 m × 100 m en Bogotá).
**Razón:** simple, rápido, geográficamente interpretable.
**Limitación conocida:** un grid arbitrario no respeta la red vial. Una intersección real puede caer en la frontera entre 4 celdas y partirse.
**Acción futura:** comparar con métodos alternativos (H3, DBSCAN, snap-to-network) en el notebook 02. Ver `memory/next_steps.md`.

---

## D7 — Filtro de coordenadas con bounding box de Bogotá

**Cuándo:** durante la limpieza.
**Contexto:** descartar puntos fuera de Bogotá (errores de geocoding, valores cero).
**Decisión:** filtro:

```python
LATITUD ∈ (4.0, 5.0) y LONGITUD ∈ (-75.0, -73.0)
```

**Razón:** rango simple, abarca todas las localidades urbanas y rurales de Bogotá.
**Resultado observado:** **0 filas eliminadas**. La fuente venía limpia.
**Acción de validación pendiente:** confirmar `LATITUD.min()`, `.max()`, `LONGITUD.min()`, `.max()` y existencia de `(0, 0)` antes del `dropna`. Ver `memory/limitations.md`.

---

## D8 — Texto en MAYÚSCULAS y sin espacios laterales

**Cuándo:** durante la limpieza.
**Contexto:** las categóricas (LOCALIDAD, BARRIO, GRAVEDAD, etc.) venían inconsistentes.
**Decisión:** `.str.strip().str.upper()`.
**Razón:** estandariza para `groupby` y comparaciones.
**Implicación:** todas las tablas de análisis muestran los nombres en mayúsculas. Para visualizaciones públicas habrá que retitular.

---

## D9 — Separación `src/` (futura) vs `app/` (futura)

**Cuándo:** organización del repo.
**Decisión:** `src/` reservado para código de librería (carga, limpieza, modelos), `app/` reservado para dashboard Streamlit.
**Razón:** evita acoplamiento entre lógica de datos y UI.
**Estado:** ambas carpetas vacías por ahora. Se poblarán en fases siguientes.

---

## D10 — `data/raw/` es inmutable

**Cuándo:** organización del repo.
**Decisión:** ningún script ni notebook escribe sobre `data/raw/`. Toda transformación va a `data/processed/` o (eventualmente) `data/interim/`.
**Razón:** reproducibilidad. Si algo se rompe, siempre se puede regenerar desde el raw original.

---

## D11 — Documentación distribuida en raíz y `memory/`

**Cuándo:** hoy.
**Contexto:** se quiso evitar un solo archivo `MEMORY.md` mastodonte.
**Decisión:** la raíz tiene `.md` formales (README, PLAN, DATA_SOURCES, DECISIONS, CHANGELOG); la carpeta `memory/` tiene `.md` operativos y narrativos en español.
**Razón:** los archivos de la raíz son para extraños (recruiters, GitHub); los de `memory/` son para retomar la sesión.

---

---

## D12 — Mantener la grilla de 0.001° del NB01 como unidad espacial del IPI

**Cuándo:** inicio del NB02.
**Contexto:** se evaluaron métodos alternativos (H3, DBSCAN, snap-to-network) pero no se implementaron para el MVP.
**Decisión:** continuar con el redondeo a 3 decimales (celdas ~111 m × 111 m) para mantener consistencia con el mapa de calor del NB01.
**Razón:** permite comparar directamente la fase exploratoria (NB01) con la fase de priorización (NB02) sobre la misma grilla. Introducir un cambio de método en el NB02 habría requerido re-validar el NB01.
**Limitación conocida:** grilla arbitraria que no respeta la red vial. Ver `memory/limitations.md` L4.
**Acción futura:** comparación de métodos en un notebook de validación metodológica.

---

## D13 — IPI como promedio simple de 5 scores normalizados

**Cuándo:** diseño del IPI en NB02.
**Contexto:** se consideró usar pesos diferenciales por componente (por ejemplo, dar más peso a fatalidad).
**Decisión:** IPI = mean(5 scores) × 100. Todos los componentes con el mismo peso implícito.
**Razón:** la igualdad de pesos es defendible en la ausencia de evidencia empírica que justifique una ponderación diferente. Un promedio simple es transparente y replicable.
**Limitación conocida:** un siniestro con muertos podría merecer más peso en el score_fatalidad.
**Acción futura:** análisis de sensibilidad explorando pesos diferenciales.

---

## D14 — Normalización por percentil de rango (no min-max)

**Cuándo:** implementación de los scores del IPI.
**Contexto:** se evaluó normalización min-max vs normalización por rango percentil.
**Decisión:** percentil de rango (`rank(x) / n`) para score_volumen, score_criticidad_total, score_severidad_promedio y score_fatalidad.
**Razón:** la normalización min-max es sensible a outliers extremos (una zona con 500 siniestros vs el resto con <200 comprimiría todo el espacio). La normalización por rango es robusta a outliers y garantiza distribución uniforme.
**Excepción:** `score_persistencia` usa ratio directo (`anios_activos / 4`), no percentil, porque solo tiene 4 valores posibles (0.25, 0.50, 0.75, 1.00).

---

## D15 — Top 50 como output operativo principal

**Cuándo:** cierre del NB02.
**Contexto:** se generaron Top 50, Top 200 y la tabla completa (~17,130 zonas).
**Decisión:** el Top 50 es el output operativo presentable. El Top 200 es el output analítico extendido.
**Razón:** 50 zonas es un número manejable para una reunión técnica o un informe ejecutivo. El Top 200 está disponible pero no es el "producto" principal.
**Implicación:** el mapa interactivo final (`mapa_top50_IPI_final_2016_2019.html`) muestra solo el Top 50. El Top 200 vive en CSV.

---

## D16 — 5 familias analíticas como clasificación cualitativa

**Cuándo:** NB02, fase de clasificación.
**Contexto:** el IPI da un ranking continuo pero no una interpretación cualitativa.
**Decisión:** clasificar zonas en 5 familias: Hotspot robusto integral, Hotspot de severidad/fatalidad, Hotspot de carga acumulada, Hotspot preventivo prioritario, Seguimiento.
**Razón:** permite comunicar el perfil de la zona más allá del número. Una zona "de severidad/fatalidad" necesita intervenciones distintas a una "de carga acumulada".
**Implicación:** las familias no son mutuamente excluyentes por lógica del IPI; son asignadas por reglas de clasificación basadas en el perfil de scores.

---

## D17 — Período 2016–2019 descrito siempre como "periodo base", no como diagnóstico actual

**Cuándo:** definición del lenguaje del proyecto.
**Contexto:** los resultados podrían presentarse erróneamente como el estado actual de Bogotá.
**Decisión:** toda comunicación de resultados debe enmarcar explícitamente el periodo 2016–2019 como "periodo base para construir y validar la metodología".
**Razón:** honestidad metodológica y credibilidad técnica. Un análisis de 2016–2019 que se presenta como "Bogotá hoy" pierde validez ante cualquier revisor técnico.
**Aplicación:** no decir "estas zonas son peligrosas hoy"; decir "en el periodo base 2016–2019, estas zonas presentaron alta concentración de siniestros". La validación de actualidad es el objetivo del NB03.

_(siguientes decisiones se agregan cronológicamente con prefijo D18, D19, etc.)_
