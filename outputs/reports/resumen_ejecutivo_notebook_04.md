# Resumen ejecutivo — Notebook 04
## VíaSegura AI | Enriquecimiento actor vial, vehículo y causa

**Fecha:** 2026-05-12
**Periodo de análisis:** 2020–2021 (reciente)
**Zonas enriquecidas:** 200 de 200 (Top 200 reciente)

## Advertencia metodológica clave

> **CONDICION ≠ tipo de vehículo.**
> El campo CONDICION (Layer 3) registra el **rol** del actor:
> CONDUCTOR, PASAJERO, PEATÓN, CICLISTA, MOTOCICLISTA.
> Un conductor de automóvil y un conductor de moto aparecen ambos como "CONDUCTOR".
> El tipo de vehículo real proviene de CLASE (Layer 5 — VM_ACC_VEHICULO).

## Cobertura de datos

| Capa | Layer | Cobertura promedio |
|---|---|---|
| VM_ACC_ACTOR_VIAL (CONDICION/rol) | 3 | 99.9% |
| VM_ACC_VEHICULO (CLASE) | 5 | 98.6% |
| VM_ACC_CAUSA (NOMBRE) | 4 | 96.1% |
| VM_ACC_VIA | 6 | No integrable (0 registros para 2020–2021) |

## Composición de vehículos en el Top 200

| Clase | % zonas con modal | % promedio por zona |
|---|---|---|
| AUTOMOVIL | 60.0% (120 zonas) | 31.5% |
| MOTOCICLETA | 29.0% (58 zonas) | 24.9% |
| CAMIONETA | 3.0% (6 zonas) | 10.3% |
| BUS | 5.0% (10 zonas) | 10.6% |
| BICICLETA | 1.5% (3 zonas) | 8.8% |

**Lectura:** Automóvil y Motocicleta concentran ~53% de los registros,
con motos involucradas en ~22% de los siniestros del Top 200.
Buses aportan ~10%. La combinación auto+moto+bus supera el 60%.

## Causas más frecuentes (causa #1 por zona)

| Causa | Zonas donde es #1 | % |
|---|---|---|
| OTRA | 90 | 45.0% |
| NO MANTENER DISTANCIA DE SEGURIDAD | 53 | 26.5% |
| ADELANTAR CERRANDO | 18 | 9.0% |
| DESOBEDECER SEÑALES | 15 | 7.5% |
| SEMÁFORO EN ROJO | 13 | 6.5% |

**Nota:** "OTRA" es un cajón de sastre; la segunda causa real es
"NO MANTENER DISTANCIA DE SEGURIDAD" → intervenciones de velocidad/distancia.

## Concentración por zona (HHI)

| Dimensión | HHI promedio | Interpretación |
|---|---|---|
| Rol/CONDICION | 4863 | Alta concentración en CONDUCTOR (esperado) |
| Vehículo/CLASE | 2569 | Distribución más diversa — varias clases presentes |
| Causa | 2576 | Alta dispersión — causas heterogéneas por zona |

## Limitaciones (L-7, L-8)

- **L-7 (cardinalidad N:1):** un siniestro puede tener múltiples actores/vehículos.
  Los porcentajes reflejan presencia relativa en el conjunto de siniestros,
  no la contribución individual de cada evento.
- **L-8 (VM_ACC_VIA):** Layer 6 tiene 961,227 registros totales pero devuelve 0
  para los FORMULARIOs del periodo 2020–2021. Posible desconexión de clave.
- Los datos son registros administrativos policiales — subregistro probable
  especialmente en siniestros con solo daños materiales.

## Próximo paso

**NB05 — Normalización por exposición:**
calcular tasas de siniestralidad por 10,000 habitantes (DANE censo 2018)
y por km de red vial (OSM), para distinguir zonas con alta accidentalidad
absoluta vs. alta accidentalidad relativa a la exposición.
