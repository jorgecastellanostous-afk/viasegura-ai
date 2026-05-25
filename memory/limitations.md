# Limitaciones conocidas — VíaSegura AI

> **Para qué sirve este archivo:** evitar afirmaciones incorrectas y guiar el discurso metodológico. Leer antes de presentar resultados o escribir conclusiones.
>
> **Última actualización:** 2026-05-24

---

## Tabla formal de limitaciones

| ID | Limitación | Impacto en resultados | Propuesta de mejora | Esfuerzo estimado |
|---|---|---|---|---|
| L1 | Sin datos de exposición vehicular (TPDA/TPDS) | El IPI no mide riesgo real: identifica concentración de siniestros, no la probabilidad de accidente por vehículo-km. Una vía con 1,000 veh/día y 10 accidentes es más peligrosa que una con 100,000 veh/día y 10 accidentes, pero el IPI las trata igual. | Integrar TPDA de puntos de aforo IDU o modelos de demanda de TransMilenio/SDM como denominador de la tasa. NB05 usa km de red vial OSM y población DANE como proxies. | 2-3 meses (requiere acceso a datos de aforo) |
| L2 | Grilla 0.001° (~111 m) no es unidad estándar de transporte | Los ingenieros de transporte trabajan con intersecciones, segmentos y tramos, no con celdas de grilla regulares. Una intersección real puede caer en la frontera entre 2-4 celdas y partirse, diluyendo su señal. El ranking del top 50 es sensible al método de agregación. | Evaluar snap-to-network (agregar sobre segmentos de la red vial) o DBSCAN (clustering por densidad sin grilla predefinida). H3 ya implementado en NB04.5 como alternativa parcial. | 3-4 semanas |
| L3 | Periodo de validación 2020-2021 corresponde a años pandemia | La validación del IPI con datos recientes se hizo sobre 2020-2021, donde la movilidad fue atípica (-30% a -60% en tráfico). Un modelo calibrado en pandemia puede no generalizar al comportamiento post-pandemia. Comunicacionalmente complejo al presentar resultados. | Usar 2022 o 2023 para validación (en cuanto se confirme el cambio estructural en SIMUR — ver L8). Alternativamente, normalizar por índice de movilidad APPLE/Google durante ese periodo. | 2-3 semanas (acceso a datos) |
| L4 | Causa "OTRA" es la más frecuente en 45% de las zonas del top 200 | Los datos SIMUR de causa tienen alta tasa de respuesta "OTRA" (sin clasificar), lo que impide diseñar intervenciones específicas para el 45% de las zonas prioritarias. El campo causa no es accionable para ingeniería vial. | Solicitar al SDM/SIMUR los datos desagregados por causa real, o cruzar con informes de Policía de Tránsito (que tiene mayor detalle en causa). | 1-2 meses (gestión institucional) |
| L5 | Score de persistencia es cuasi-binario con solo n=2 periodos | La persistencia se calcula con 2 periodos (base 2016-2018 y reciente 2019-2021, o equivalente). Con solo 2 puntos, el score es prácticamente binario: persistente o no. No captura tendencias (mejorando, empeorando, fluctuando). | Incorporar más periodos temporales (ej. 2016, 2017, 2018, 2019 como cuatro periodos independientes) para calcular tendencia con regresión. Requiere redefinir la ventana de persistencia. | 3-4 semanas |
| L6 | Población DANE 2018 a nivel localidad (no UPZ) | La normalización por población en NB05 usa datos DANE del Censo 2018 a nivel localidad (20 unidades), no a nivel UPZ (112 unidades). Esto sobreestima la densidad poblacional en zonas de baja densidad dentro de una localidad y subest. en zonas de alta densidad. | Usar proyecciones DANE a nivel UPZ o manzana (disponibles en datos.gov.co). Alternativamente, usar densidad poblacional de WorldPop (resolución 100m). | 2-3 semanas |
| L7 | Análisis de sensibilidad EPDO vs 1/3/5 muestra 84.5% de estabilidad (ADR-12) | El 15.5% de las zonas del top 50 cambia al usar pesos EPDO internacionales (1:8:24) en lugar de los actuales (1:3:5). Esto significa que aproximadamente 8 de las 50 zonas Prioridad 1 podrían ser desplazadas por zonas con alta fatalidad pero bajo volumen. | Los pesos ya son parametrizables en el código (ADR-11). Implementar selector de escala en la app Streamlit para que el usuario elija entre 1/3/5, EPDO (1/8/24) o FHWA (1/5/542). | 1-2 semanas |
| L8 | Años 2022-2025 excluidos por cambio estructural en clasificación de gravedad SIMUR (ADR-10) | Los datos 2022-2025 muestran una caída del 61-78% en registros frente al periodo base. No está confirmado si es subreporte, cambio de plataforma o cambio metodológico en SIMUR. Esto impide validar el IPI con datos post-pandemia. Hasta que se confirme la causa, el modelo no tiene validación temporal externa. | Contactar al SDM/SIMUR para obtener explicación oficial del cambio. Si es cambio metodológico, solicitar tabla de equivalencias. Documentar en ADR-10 la conclusión cuando esté disponible. | 1-2 meses (gestión institucional) |

| L9 | Discrepancia de universo entre notebooks: NB04.5 = 17,130 zonas vs NB04/NB05 = 19,255 zonas | Comparaciones cruzadas entre notebooks usan universos incompatibles. NB04.5 opera sobre el periodo base 2016-2019 (17,130 zonas activas); NB04/NB05 integran también el periodo de validación 2020-2021 (19,255 zonas totales). Un usuario que compare IPI_base con el choropleth por localidad obtendrá denominadores distintos sin saberlo. | Documentar explícitamente en cada notebook qué universo usa. Agregar disclaimers en la UI. Considerar generar una versión de NB04.5 sobre las 19,255 zonas para el análisis espacial. | 1-2 días |
| L-NB04.5-B | Sin umbral mínimo de actividad en el análisis espacial | Los hexágonos H3 y el choropleth por localidad incluyen zonas con solo 1-2 siniestros. Un hexágono con IPI_hex alto basado en 1 zona con siniestro de alta gravedad puede aparecer destacado aunque no sea estadísticamente significativo. | Aplicar umbral mínimo de n_zonas ≥ 3 o siniestros_total ≥ 5 antes de colorear hexágonos. Mostrar badge de "datos insuficientes" en el mapa para hexágonos debajo del umbral. | 2-3 horas |
| L-PR4-A | Pandemia como confusor severo en el análisis de impacto de obras IDU (PR-4) | El periodo de datos disponible (2020-2021) coincide con la pandemia COVID-19, cuando el tráfico cayó 30-60%. Cualquier delta_IPI calculado entre una zona antes/después de una obra IDU absorbería el efecto pandemia, haciendo imposible atribuir causalidad a la obra. Los 35 casos "persistentes" sobreviven pandemia, pero el análisis cuantitativo de impacto está severamente confundido. | Usar datos pre-pandemia 2016-2019 para el análisis de impacto. Alternativamente, normalizar por índice de movilidad Google Mobility o Apple Mobility durante el periodo. | 2-3 semanas |
| L-PR2-A | ANSV TCA solo cubre vías arteriales, no la red local | Si se usa el sistema TCA (Tráfico, Condición, Accidentalidad) de la ANSV como fuente de validación PR-2, este solo tiene cobertura de la red vial arteria (autopistas, vías primarias y secundarias). Las vías locales, donde se concentra una fracción del Top 200, no tienen cobertura. El análisis PR-2 estaría sesgado a favor de zonas en arterias. | Complementar con datos IDU de intervenciones a nivel de segmento (disponibles en datos abiertos). Usar CIV como campo de join exacto entre SIMUR Layer 2 y obras IDU. | 2 semanas |

---

## Notas metodológicas complementarias

### El IPI no mide riesgo real — lenguaje correcto

El Índice de Prioridad de Intervención (IPI) identifica zonas donde los datos de siniestralidad presentan una combinación crítica de volumen, severidad, persistencia y fatalidad. **No es** una medición de probabilidad de accidente por vehículo-km expuesto.

**Lenguaje prohibido:** "zonas más peligrosas", "riesgo real", afirmaciones causales sin respaldo de datos adicionales.

**Lenguaje correcto:** "zonas priorizadas", "concentración de siniestros", "hotspot persistente", "prioridad exploratoria de intervención".

### El periodo base es 2016–2019, no Bogotá actual

Los resultados representan un periodo cerrado, estable y pre-pandemia. No son un diagnóstico del Bogotá de 2026.

**Uso correcto:** "En el periodo base 2016–2019, estas zonas presentaron..." No: "Estas son las zonas más críticas de Bogotá hoy."

### Reproducibilidad

La base cruda se descargó del FeatureServer de SIMUR, fuente viva que puede actualizar registros históricos. El snapshot fue guardado con hash MD5 en `data/raw/_snapshot_metadata.json`. Si SIMUR actualiza datos del 2016–2019, una nueva descarga puede diferir.
