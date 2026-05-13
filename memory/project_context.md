# Contexto del proyecto — VíaSegura AI

> **Para qué sirve este archivo:** dar contexto narrativo y propósito a cualquier persona (o IA) que retome el proyecto. No es documentación técnica, es la historia y el "para qué".

---

## Frase central

> **VíaSegura AI usa datos oficiales de siniestralidad vial de Bogotá para identificar patrones espaciales y temporales, clasificar zonas críticas y generar recomendaciones preliminares de intervención para apoyar decisiones de seguridad vial urbana.**

---

## ¿Qué es VíaSegura AI?

Una herramienta exploratoria y técnica que combina ingeniería civil, transporte, GIS, análisis de datos e IA generativa para apoyar la toma de decisiones en seguridad vial urbana en Bogotá.

**No es:**

- Un modelo predictivo de accidentes.
- Una herramienta de evaluación definitiva de riesgo vial.
- Un producto comercial cerrado.

**Sí es:**

- Una herramienta exploratoria que identifica zonas con alta concentración y criticidad de siniestros.
- Un proyecto de portafolio profesional, defendible técnicamente.
- Una base sobre la que se puede construir un producto futuro aplicado al sector transporte en Colombia.

---

## ¿Por qué Bogotá?

- Es la ciudad con más siniestros viales reportados en el país.
- Tiene una infraestructura de datos abiertos relativamente madura (SDM/SIMUR/ArcGIS).
- Permite desarrollar el MVP con una geografía manejable antes de pensar en alcance nacional.
- Hay capas hermanas (UPZ, localidades, red vial) que pueden integrarse en fases posteriores.

---

## ¿Por qué 2016–2019?

- Es un periodo cerrado, completo y consistente.
- Antes de la pandemia (que distorsiona patrones de movilidad).
- Se evitaron 2025 y 2026 por estar incompletos.
- Se evitaron 2023 y 2024 por evidencia de subreporte (ver `memory/limitations.md`).

---

## Audiencia objetivo del producto

1. **Académica / portafolio:** profesores, evaluadores, recruiters técnicos.
2. **Profesional:** secretarías de movilidad, consultoras de transporte, ANSV.
3. **Comunidad open source:** GitHub público.

---

## Disciplinas que el proyecto integra

- Ingeniería civil y de transporte (entender qué causa siniestros y qué los previene).
- Ciencia de datos (estadística, validación, modelado).
- GIS (análisis espacial, mapeo, sistemas de coordenadas).
- Ingeniería de software (estructura modular, reproducibilidad).
- IA generativa (apoyo a redacción de recomendaciones, no a inferencia).

---

## Roles internos del proyecto

Estos no son procesos automatizados; son **mentalidades** que se asumen al entrar a una tarea.

| Rol | Responsabilidad |
|---|---|
| **Ingeniero civil / transporte** | Entender qué tiene sentido en términos de seguridad vial. Validar criterios de criticidad. |
| **Científico de datos** | Limpiar, validar, transformar, modelar. Reportar calidad. |
| **Especialista GIS** | Manejar CRS, capas, mapas, agregaciones espaciales. |
| **Arquitecto de software** | Mantener estructura modular, reproducibilidad, separación `src/` vs `app/`. |
| **Investigador de fuentes** | Buscar, validar y documentar fuentes oficiales adicionales. |
| **Documentador técnico** | Mantener este `memory/` y todos los `.md` de gobernanza al día. |

---

## Estado actual (resumen ejecutivo)

- [x] Estructura de carpetas creada.
- [x] Base oficial 2016–2019 descargada (260,831 registros) y validada contra el conteo del servidor.
- [x] Base limpia con puntaje de gravedad (1/3/5) guardada en `data/processed/`.
- [x] Tablas por localidad, gravedad, clase y año generadas.
- [x] Mapa de calor exploratorio generado.
- [x] Índice de Prioridad de Intervención (IPI) construido sobre ~17,130 zonas.
- [x] Top 50 IPI generado como lista operativa de priorización.
- [x] Familias analíticas clasificadas (5 categorías).
- [x] Mapa interactivo final del Top 50 generado.
- [x] Resumen ejecutivo y manifiesto de outputs del NB02 guardados.
- [x] Bug ADR-06 corregido: pesos IPI igualados a `mean()` via `fix_ipi_nb02.py` (delta máx. ~0.03 pts).
- [x] NB03 completado: 72,903 siniestros 2020–2021, solapamiento Top 200 base vs reciente 18.5% (37 zonas).
- [x] Clasificación de hotspots por persistencia: 37 Persistentes / 163 Emergentes / 35 Disminuidos.
- [x] 7 capas hermanas SIMUR auditadas; esquema de integración NB04 documentado.
- [x] NB03.5 — Síntesis metodológica creado (documentación de referencia, no genera outputs nuevos).
- [ ] NB04 — Enriquecimiento con actores viales, vehículos y causas ← **PRÓXIMO**

**Próximo paso:** NB04 — enriquecer el Top 200 reciente con capas hermanas SIMUR (actores, vehículos, causas). Ver `memory/next_steps.md`.

---

## Cómo retomar este proyecto si te pierdes

1. Lee este archivo (`memory/project_context.md`).
2. Lee `memory/methodology.md` para entender qué se hizo y cómo.
3. Lee `memory/decisions_log.md` para entender el por qué de las cosas.
4. Lee `memory/next_steps.md` para saber qué sigue.
5. Lee `memory/limitations.md` para no decir tonterías.
6. Lee `memory/notebook_02_summary.md` para el detalle del IPI.
7. Mira `data/raw/` y `data/processed/` para ver qué datos hay.
8. Mira `outputs/reports/` para ver todos los CSV generados.
9. Abre `outputs/maps/mapa_top50_IPI_final_2016_2019.html` para ver el mapa final.
