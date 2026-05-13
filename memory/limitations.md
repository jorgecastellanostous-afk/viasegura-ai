# Limitaciones conocidas — VíaSegura AI

> **Para qué sirve este archivo:** evitar afirmaciones incorrectas. Leer antes de presentar resultados o escribir conclusiones.

---

## L1 — El IPI no mide riesgo real

El Índice de Prioridad de Intervención (IPI) **no es una medición de riesgo vial**.

Mide prioridad exploratoria de intervención: identifica zonas donde los datos de siniestralidad presentan una combinación crítica de volumen, severidad, persistencia y fatalidad.

**Para medir riesgo real** se necesitaría incorporar (al menos):
- Flujo vehicular (TPDA, TPDS)
- Población peatonal expuesta
- Longitud de tramo o segmento vial
- Velocidad de operación
- Geometría e infraestructura de la vía
- Semaforización y tiempos de ciclo
- Condiciones de iluminación y señalización

**Lenguaje prohibido:** "zonas más peligrosas", "riesgo real", afirmaciones causales sin respaldo de datos adicionales.

**Lenguaje correcto:** "zonas priorizadas", "concentración de siniestros", "hotspot persistente", "prioridad exploratoria de intervención".

---

## L2 — El periodo base es 2016–2019, no Bogotá actual

Los resultados representan el periodo **2016–2019**, un periodo cerrado, estable y pre-pandemia.

No son un diagnóstico del Bogotá de 2026. La movilidad, la infraestructura y los patrones de siniestralidad han cambiado desde entonces.

**Uso correcto:** "En el periodo base 2016–2019, estas zonas presentaron..." No: "Estas son las zonas más críticas de Bogotá hoy."

---

## L3 — Caída inexplicada en datos recientes (2022–2024)

La auditoría por año mostró una reducción severa en registros recientes:

| Año | Siniestros | Reducción frente a base |
|---|---|---|
| 2016–2019 | ~65,000/año | — |
| 2022 | 25,453 | −61% |
| 2023 | 14,115 | −78% |
| 2024 | 14,020 | −78% |

Esta caída **no ha sido explicada**. Hipótesis posibles:
1. Datos aún no cargados en el FeatureServer para esos años.
2. Cambio de metodología de registro o plataforma SIMUR.
3. Cambio real en siniestralidad (menos probable dado el salto).

**Implicación:** los datos de 2022–2024 no son directamente comparables con el periodo base sin investigar primero la causa. El NB03 debe auditar esto antes de descargar masivamente.

---

## L4 — Agregación espacial por grilla arbitraria

Las zonas se construyeron redondeando coordenadas a 3 decimales (celdas de ~111 m × ~111 m). Esta grilla es arbitraria: no respeta la red vial, los tramos, ni las intersecciones reales.

Una intersección vial real puede caer en la frontera entre 2 o 4 celdas y partirse entre ellas, diluyendo su señal.

**Métodos alternativos** no evaluados todavía:
- H3 (índice hexagonal de Uber) — hexágonos uniformes en área
- Snap-to-network — agregar sobre segmentos de la red vial
- DBSCAN — clustering basado en densidad, sin grilla predefinida

**Implicación:** el Top 50 es sensible a la elección de la grilla. Una intersección fronteriza podría aparecer en el Top 20 con un método diferente.

---

## L5 — Pesos del índice de criticidad no validados empíricamente

Los pesos `SOLO DAÑOS = 1`, `CON HERIDOS = 3`, `CON MUERTOS = 5` son una escala ordinal simple, elegida para el MVP.

En la literatura internacional los pesos son notablemente distintos:

| Fuente | Solo daños | Con heridos | Con muertos |
|---|---|---|---|
| VíaSegura AI (actual) | 1 | 3 | 5 |
| NHTSA (EPDO) | 1 | ~8 | ~24 |
| FHWA (costos económicos) | 1 | ~5 | ~542 |

Con la escala actual, un accidente fatal equivale a solo 5 accidentes materiales. Con EPDO sería equivalente a 24.

**Implicación:** el ranking del IPI podría cambiar significativamente con pesos alternativos. El NB03 o NB04 debería incluir un análisis de sensibilidad.

---

## L6 — Validación del filtro de bounding box no confirmada completamente

El filtro de coordenadas eliminó 0 filas (la fuente venía limpia). Sin embargo, no se confirmó explícitamente:
- Si existían registros con `LATITUD = 0` o `LONGITUD = 0` antes del `dropna`.
- El mínimo y máximo exacto de lat/lon en el raw.

**Implicación menor:** la limpieza fue aparentemente exitosa, pero la validación formal queda pendiente.

---

## L7 — Sin integración de actores viales ni tipo de vehículo

El análisis actual usa solo la tabla `ACCIDENTE` del FeatureServer SIMUR. No se ha integrado:
- Tabla de actores viales (peatones, motociclistas, ciclistas, conductores)
- Tabla de vehículos involucrados
- Causa probable del siniestro

**Implicación:** no se puede distinguir si una zona concentra atropellos a peatones, choques de motos, o caídas de ocupante. Esta distinción es fundamental para diseñar intervenciones específicas.

---

## L8 — Snapshot de descarga no asegurado con hash

La base cruda se descargó del FeatureServer de SIMUR, que es una fuente viva. SIMUR puede actualizar registros históricos (correcciones administrativas). No se guardó un hash MD5 del archivo crudo ni un timestamp formal de la descarga.

**Implicación:** si SIMUR actualiza datos del 2016–2019 en el futuro, la descarga actual podría diferir de una nueva descarga. La reproducibilidad exacta no está garantizada hasta que se cree `_snapshot_metadata.json`.
