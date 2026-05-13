# VíaSegura AI — Documento de comunicación para audiencia distrital

> **Para:** Secretaría Distrital de Movilidad (SDM), ANSV, IDU, tomadores de decisión en seguridad vial  
> **Nivel:** No técnico. Sin fórmulas ni código.  
> **Versión:** 1.0 — 2026-05-12

---

## ¿Qué es VíaSegura AI?

VíaSegura AI es una herramienta de análisis espacial que identifica, de manera sistemática y reproducible, **las zonas de Bogotá donde ocurren más accidentes de tránsito graves y con más frecuencia**, para orientar decisiones de intervención vial.

No reemplaza el juicio técnico del ingeniero de tránsito. Lo complementa: en lugar de que un analista revise manualmente miles de accidentes, el sistema produce una lista priorizada de zonas con información suficiente para saber **dónde mirar primero y qué tipo de problema hay**.

---

## ¿Por qué usamos datos de 2020 y 2021?

Esta es la pregunta más frecuente y merece una respuesta honesta.

Los datos de SIMUR (Secretaría Distrital de Movilidad) cubren desde 2007 hasta hoy. Sin embargo, al revisar los registros año por año, encontramos lo siguiente:

| Periodo | Problema |
|---|---|
| 2022–2025 | La estructura de los registros cambió radicalmente: la proporción de accidentes con heridos vs. solo daños pasó de ~0.4 a más de 4. Eso no refleja una mejora real en seguridad vial — refleja un cambio en cómo la policía registra los accidentes. Usar estos datos produciría resultados distorsionados. |
| 2020–2021 | Años de pandemia. La movilidad fue más baja que un año normal, pero **la estructura del registro es comparable al periodo base 2016–2019**. Por eso los usamos como periodo de validación. |
| 2016–2019 | Periodo base. Datos limpios, completos y comparables: ~65,000 accidentes por año. |

**La decisión no fue arbitraria.** Está documentada formalmente en el registro de decisiones técnicas del proyecto (ADR-10). Los resultados del análisis se presentan como un diagnóstico de patrones históricos, no como el estado actual de Bogotá en 2026.

**¿Qué significa esto para las conclusiones?** Las zonas identificadas como críticas son lugares donde **históricamente se concentran los accidentes graves**. Si una zona aparece tanto en 2016–2019 como en 2020–2021, la evidencia de que es un punto problemático es más sólida, independientemente de los volúmenes de tráfico de la pandemia.

---

## ¿Qué encontramos?

### Las 200 zonas más críticas de Bogotá

El análisis identificó **200 zonas de 111m × 111m** con la mayor concentración de accidentes graves y persistentes. De esas 200:

- **35 zonas (17.5%) son Persistentes:** aparecen como críticas tanto en 2016–2019 como en 2020–2021. Estas son las zonas que requieren intervención más urgente — el problema no desapareció con el tiempo.
- **165 zonas (82.5%) son Emergentes:** zonas críticas en el periodo reciente que no estaban en el top histórico. Pueden ser zonas afectadas por cambios en movilidad, nuevas rutas de transporte o transformaciones urbanas.

### ¿Quiénes están involucrados?

En las 200 zonas más críticas, la composición de vehículos es:

| Tipo de vehículo | Participación promedio por zona |
|---|---|
| Automóvil | 31.5% |
| Motocicleta | 24.9% |
| Bus / TransMilenio | 10.6% |
| Camioneta | 10.3% |
| Bicicleta | 8.8% |

**La moto no es un problema marginal.** En promedio, 1 de cada 4 vehículos involucrados en accidentes en estas zonas es una motocicleta. Esto tiene implicaciones directas para el tipo de intervención: los controles de velocidad, la señalización horizontal de carriles y las campañas de comportamiento deben incluir explícitamente a motociclistas.

### ¿Qué causa los accidentes?

En el 55% de las zonas con causa identificada, el patrón es claro:

| Causa principal | Zonas | Tipo de intervención sugerida |
|---|---|---|
| No mantener distancia / Adelantar cerrando | 53 zonas | Radar, reductor de velocidad, señalización |
| Semáforo en rojo / Desobedecer señales | 28 zonas | Cámara semafórica, resincronización |
| Maniobras peligrosas | ~15 zonas | Separador físico, geometría de intersección |
| Infraestructura vial (huecos, señalización) | ~8 zonas | Mantenimiento, bacheo |

El 45% restante tiene causa registrada como "OTRA", que es un problema de calidad del registro policial, no del análisis. Se recomienda que la SDM revise los protocolos de registro en campo para mejorar la especificidad.

---

## ¿Qué se puede hacer con estos resultados?

### Para la SDM y el IDU:

1. **Priorizar el presupuesto de seguridad vial.** En lugar de distribuir intervenciones por localidad o por solicitud ciudadana, las 200 zonas identificadas ofrecen una base técnica para asignar recursos donde el impacto esperado es mayor.

2. **Diseñar intervenciones específicas.** Una zona con alta participación de motos y causa "adelantar cerrando" necesita una respuesta diferente a una zona con alta participación de peatones y causa "semáforo en rojo". El análisis provee esa distinción por zona.

3. **Evaluar intervenciones pasadas.** Si el IDU o la SDM ejecutaron obras en alguna de las zonas identificadas entre 2016 y 2021, se puede verificar si la siniestralidad bajó. Este tipo de evaluación de impacto es la siguiente etapa del proyecto.

### Para el ANSV:

Los resultados son comparables con las metodologías de **Red de Vías de Alta Accidentalidad (HIN)** usadas internacionalmente. Una verificación cruzada con los tramos críticos identificados por el ANSV a nivel nacional permitiría validar la metodología y fortalecer la evidencia.

---

## Limitaciones honestas

Presentamos estas limitaciones no para debilitar los resultados, sino porque creemos que un análisis útil es un análisis honesto.

| Limitación | Impacto | Propuesta de mejora |
|---|---|---|
| Sin normalización por exposición | Las zonas de alto tráfico aparecen más que las zonas de alto riesgo relativo | Incluir aforos vehiculares o tráfico medio diario (TMD) como denominador |
| Unidad espacial: cuadrícula 111m × 111m | No coincide con intersecciones o segmentos específicos | Migrar a red vial IDECA como unidad de análisis |
| Periodo de validación (2020-2021) | Movilidad reducida por pandemia | Actualizar cuando los datos 2022+ sean comparables metodológicamente |
| Causa "OTRA" en 45% de zonas | No se puede recomendar intervención en esas zonas | Mejorar protocolo de registro policial; cruzar con informes SDM |
| Solo 2 periodos históricos | Persistencia no puede graduarse (crónico vs. reciente) | Agregar periodos adicionales cuando los datos sean consistentes |
| Sin datos hospitalarios | Solo accidentes reportados a la policía; hay subregistro | Cruzar con registros de urgencias (SIVIGILA, EPS) |

---

## ¿Cómo obtener más información?

El proyecto está completamente documentado y es reproducible:

- **Código fuente:** disponible en Python (Jupyter Notebooks)
- **Registro de decisiones:** cada parámetro tiene una justificación formal escrita
- **Datos:** provenientes directamente de la API SIMUR de la SDM

Para una presentación técnica detallada, demostración del sistema o propuesta de colaboración, contactar al equipo del proyecto.

---

*VíaSegura AI — Análisis de siniestralidad vial en Bogotá*  
*Metodología: IPI (Índice de Prioridad de Intervención) — Basado en datos SIMUR / SDM*
