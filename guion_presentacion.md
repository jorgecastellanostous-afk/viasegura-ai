# VíaSegura AI — Guión de presentación
**Audiencia:** Ingeniero civil con experiencia en transporte y vialidad  
**Duración estimada:** 20–30 minutos  
**App:** http://localhost:8501

---

## Apertura (2 min)

"Papá, lo que voy a mostrarte es un sistema de priorización espacial de
accidentalidad vial para Bogotá. La idea central es responder una pregunta
muy concreta que los tomadores de decisión en la SDM (Secretaría Distrital
de Movilidad) necesitan responder con recursos limitados:

**¿En cuál de las 17,130 zonas de Bogotá debo intervenir primero?**

No es un mapa de puntos negros tradicional. Es una metodología cuantitativa
que pondera volumen, severidad, persistencia y fatalidad para producir un
índice único por zona."

---

## 1. Los datos de base — SIMUR (3 min)

**Abre: Página principal → revisa los KPIs del hero**

"La fuente es SIMUR — el Sistema de Información para la Movilidad Urbana
y Regional de Bogotá, operado por la SDM. Cubre el período 2016–2019:

- **260,831 registros** de accidentes con coordenadas GPS
- Cada registro tiene: clase (choque, atropello, volcamiento…), gravedad
  (con muertos / con heridos / solo daños), actor vial, causa reportada
- Cobertura: las 20 localidades urbanas

Un detalle importante que vas a ver en la app: cuando diga 'accidentes
fatales' nos referimos a *eventos* clasificados como CON MUERTOS en SIMUR,
no víctimas individuales. SIMUR registra 4,197 de esos eventos; la SDM
confirma ~2,142 víctimas fatales en ese período — hay duplicados y
subregistro cruzado. Siempre hay que ser precisos con esto."

---

## 2. La grilla espacial — Por qué celdas y no puntos (3 min)

**Abre: Página 1 — Mapa Interactivo**

"El primer desafío metodológico fue la escala de análisis. Con 260k puntos
GPS, la densidad de eventos es muy alta en zonas céntricas y baja en la
periferia — un mapa de calor tradicional solo refleja la densidad
poblacional, no el riesgo real.

Solución: **grilla regular de celdas de 0.001° × 0.001°**, equivalente a
aproximadamente **111 m × 111 m** en latitud ecuatorial. Es lo suficientemente
pequeña para localizar una intersección específica, pero lo suficientemente
grande para agregar estadísticas significativas.

Resultado: **17,130 zonas** con al menos un siniestro registrado en el período.
Esto es operacionalmente útil porque una cuadrilla de mantenimiento puede
identificar la zona exacta sin ambigüedad."

**Muéstrale el mapa: activa/desactiva capas, haz zoom en Kennedy o Suba**

"Cada punto en el mapa es una zona. El color indica la prioridad:
- Rojo intenso → Prioridad 1 (top 50 zonas, intervención inmediata)
- Naranja → Prioridad 2 (auditoría de seguridad vial)
- Amarillo → Prioridad 3 (monitoreo periódico)"

---

## 3. El IPI — Índice de Prioridad de Intervención (5 min)

**Abre: Página 5 — Metodología → sección del IPI**

"El núcleo del sistema es el IPI. Es un índice compuesto de 5 dimensiones,
calculado para cada zona, en escala 0–100 donde 100 es la zona más crítica.

Las 5 dimensiones son:

| Dimensión | Qué mide | Peso relativo |
|-----------|----------|---------------|
| **Volumen** | Total de siniestros en la zona | Base del ranking |
| **Criticidad** | Puntos de gravedad: Muertos=5, Heridos=3, Solo Daños=1 | Amplifica severidad |
| **Severidad promedio** | Criticidad / número de eventos | Detecta zonas con pocos pero muy graves accidentes |
| **Persistencia** | ¿En cuántos de los 4 años ocurrieron siniestros? | Filtra eventos atípicos aislados |
| **Fatalidad** | Proporción de eventos con muertos | Da peso adicional a las zonas con fallecidos |

Cada dimensión produce un score normalizado [0,1] — percentil dentro del
universo de 17,130 zonas. El IPI final es una combinación ponderada de
los 5 scores.

**Por qué este diseño y no solo 'más accidentes = más prioritario':**

Una zona con 50 accidentes leves en un solo año puntúa diferente a una con
20 accidentes graves cada año durante 4 años. La segunda es estructuralmente
peligrosa — el riesgo es sistémico, no aleatorio. El IPI lo captura."

---

## 4. Zonas Críticas — El ranking operativo (3 min)

**Abre: Página 2 — Zonas Críticas**

"Esta es la interfaz operativa. Un tomador de decisión en la SDM puede:

1. Filtrar por prioridad, localidad y tipo de accidente
2. Ver la tabla ordenada por IPI
3. Descargar el CSV para su sistema GIS

**Muéstrale el radar chart de la Zona #1:**
'Mira este gráfico polar — cada eje es una de las 5 dimensiones del IPI.
Una zona que sea máxima en todos los ejes tiene riesgo multidimensional:
alto volumen, alta severidad, persistente y con muertes. Eso es lo que
define Prioridad 1.'

**La nota metodológica importante:** el umbral 'Prioridad 1 = top 50' es
una decisión operativa, no un corte estadístico natural. Las zonas en
posiciones 48–55 tienen IPIs casi idénticos (diferencia < 0.5 puntos).
Esto es honesto — preferimos decirlo explícitamente en la app."

---

## 5. Análisis por localidad (2 min)

**Abre: Página 3 — Por Localidad → selecciona Kennedy**

"Kennedy concentra la mayor cantidad de zonas Prioridad 1 de la ciudad.
Es la localidad más poblada y tiene una red vial mixta: arteriales
principales, vías secundarias y barrios de alta densidad peatonal.

El gráfico de línea temporal muestra cómo evolucionó la criticidad año
a año en esa localidad — si hay una tendencia ascendente, el riesgo está
empeorando; si baja, las intervenciones anteriores pueden estar teniendo
efecto.

El mapa de la localidad permite ubicar las zonas exactas dentro de Kennedy
para cruzarlas con proyectos de infraestructura vial existentes."

---

## 6. La Limitación L1 y NB06 — La parte más técnica (5 min)

**Abre: Página 5 — Metodología → sección Limitaciones → L1**

"Aquí viene la parte que creo que te va a interesar más como ingeniero.

Identificamos 6 limitaciones del IPI base. La más importante — marcada
como Alta — es la **L1: ausencia de normalización por exposición vehicular**.

¿Qué significa? Una zona sobre la Av. NQS con 10 accidentes y 100,000
vehículos/día tiene un riesgo relativo mucho menor que una zona en una
calle residencial con 10 accidentes y 1,000 vehículos/día. El IPI trata
ambas igual porque solo ve el numerador (accidentes), no el denominador
(exposición).

**El estándar internacional PIARC/Vision Zero** para medir este riesgo es:
siniestros por **10^9 vehículo-kilómetros**. Es la misma métrica que usan
Suecia, Noruega y los estudios de la Accident Analysis & Prevention.

**El problema:** no existe un inventario público de TPDA (Tráfico Promedio
Diario Anual) por segmento vial para Bogotá 2016–2019. Los datos del CGT
(Centro de Gestión de Tráfico) son internos a la SDM.

**La solución NB06:** usamos el tag `highway` de OpenStreetMap — que ya
teníamos descargado — para asignar pesos TPDA proxy por jerarquía vial:

| Tipo OSM | TPDA proxy asignado |
|----------|---------------------|
| motorway / trunk | 90,000–120,000 veh/día |
| primary (Av. NQS, Av. 68…) | 50,000 veh/día |
| secondary | 20,000 veh/día |
| tertiary | 8,000 veh/día |
| residential | 2,500 veh/día |

Con esto calculamos `vm_dia` (vehículo-metros/día) por zona y la tasa:

    tasa_vehkm = siniestros / (vm_dia × 365 días × 4 años / 10^9)

**Resultado:** identificamos **194 zonas 'hotspot oculto ponderado'** —
zonas que no aparecen en el top 200 por volumen absoluto pero que tienen
tasas de riesgo por veh·km extremadamente altas. Son zonas de baja
jerarquía vial con alta accidentalidad relativa — exactamente el tipo de
zona que un análisis volumétrico puro deja fuera de la agenda de intervención.

**Limitación que reconocemos:** los pesos son ordinales, no exactos.
El error esperado es ±30–50% por tipo de vía. Para resolución completa
se requiere una solicitud formal de datos TPDA a la SDM bajo Ley 1712/2014
(acceso a información pública)."

---

## 7. El Agente IA (3 min)

**Abre: Página 4 — Agente IA**

"El último módulo es un agente conversacional conectado a Claude (el modelo
de Anthropic). Tiene acceso completo al dataset:

- Top 200 zonas por IPI con todos sus atributos
- Ranking de las 20 localidades
- Top 20 vías críticas y barrios
- Tipología NB05 y NB06

Usa *prompt caching* — el contexto de 17,130 zonas se envía una vez y
queda en caché, reduciendo el costo de tokens en llamadas sucesivas.

Probémoslo: pregúntale algo."

**Sugerencias de preguntas para mostrar:**
- "¿Cuáles son las 3 zonas más urgentes y por qué?"
- "Dame recomendaciones para Kennedy"
- "¿Qué tipo de accidentes predomina en Prioridad 1?"

---

## Preguntas técnicas que puede hacer (respuestas preparadas)

**"¿Por qué celdas de 111m y no hexágonos H3?"**
→ H3 fue evaluado (resolución 9, ~174m). La grilla regular de 0.001° es
más simple de explicar a decisores no técnicos y más fácil de cruzar con
el catastro y los planos urbanísticos de Bogotá, que usan coordenadas
geográficas WGS84.

**"¿Validaron el IPI contra intervenciones reales?"**
→ Es la validación pendiente más importante (Limitación L4 en la metodología).
Requiere el inventario de obras SDM/IDU post-2019 para comparar si las zonas
intervenidas coinciden con las de alto IPI. El IDU tiene una capa pública
de inventario vial con el campo CIV (Código de Identificación Vial) que
permite el cruce.

**"¿Qué tan confiable es la geocodificación de SIMUR?"**
→ El NB03 del pipeline hace una auditoría de cobertura: 91.3% de los
registros tienen coordenadas válidas dentro del perímetro urbano. El 8.7%
restante se excluye del análisis espacial pero se incluye en los conteos
de cobertura temporal.

**"¿La causa del accidente se usa en el IPI?"**
→ No en el IPI base, por razones de calidad de datos: el campo 'causa'
tiene 62% de registros como 'OTRA CAUSA' — prácticamente no accionable.
Existe un rescate parcial (NB04.5) que identifica la causa_top2 cuando
la principal es 'OTRA', extrayendo causas accionables como 'No ceder paso',
'Exceso de velocidad', etc. Esta información aparece en el módulo de Agente.

**"¿Esto se puede usar para priorizar el presupuesto de señalización?"**
→ Sí, directamente. La recomendación del agente clasifica intervenciones
en tres categorías: Ingeniería vial (infraestructura), Fiscalización
(control de tránsito) y Educación vial. Un análisis por clase de accidente
(atropello vs choque vs volcamiento) en cada zona orienta cuál categoría
aplicar.

---

## Cierre (1 min)

"El sistema está construido sobre datos públicos SIMUR, herramientas open
source (Python, GeoPandas, OSMnx, Streamlit, Folium, H3) y un modelo
de IA (Claude Haiku 4.5). El costo mensual para mantenerlo activo es bajo
— básicamente el costo de API de Anthropic para el agente conversacional.

Lo que falta para ser una herramienta de gestión real:
1. Datos TPDA reales de la SDM (solicitud Ley 1712)
2. Integración con el inventario IDU de obras (cruce por CIV)
3. Actualización con datos SIMUR post-2019 (2020–2024)
4. Validación contra intervenciones ejecutadas

¿Preguntas?"

---

*Generado el 25 de mayo de 2026 — VíaSegura AI v2*
