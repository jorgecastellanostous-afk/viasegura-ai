
# Resumen Ejecutivo - Notebook 02

## Proyecto
VíaSegura AI

## Notebook
02_indice_criticidad_y_hotspots.ipynb

## Periodo analizado
2016–2019

## Base utilizada
data/processed/accidentes_bogota_2016_2019_limpio.csv

## Registros analizados
260,831 siniestros viales georreferenciados.

## Objetivo del notebook
Construir un sistema preliminar de priorización espacial de zonas críticas de siniestralidad vial en Bogotá mediante el Índice de Prioridad de Intervención, IPI.

## Variables consideradas en el IPI
- Volumen de siniestros.
- Criticidad total.
- Severidad promedio.
- Persistencia temporal.
- Presencia de siniestros con muertos.

## Resultado principal
El análisis permitió pasar de una visualización descriptiva de siniestros a un sistema de priorización espacial. El IPI permite identificar zonas que no necesariamente tienen el mayor volumen de siniestros, pero sí presentan una combinación crítica de persistencia, severidad y presencia de siniestros con muertos.

## Concentración del Top 50 IPI
- Zonas priorizadas: 50.
- Porcentaje de zonas: 0.29%.
- Siniestros acumulados: 4,426.
- Criticidad acumulada: 10,138.
- Siniestros con muertos acumulados: 270.

## Familias analíticas
Se clasificaron las zonas en:
- Hotspot robusto integral.
- Hotspot de severidad/fatalidad.
- Hotspot de carga acumulada.
- Hotspot preventivo prioritario.
- Seguimiento.

## Limitaciones
Los resultados no representan una medición definitiva de riesgo vial. Para estimar riesgo real se requiere incorporar exposición, población, flujos vehiculares, longitud de red vial, velocidad, geometría, infraestructura peatonal, semaforización y condiciones urbanas.

## Siguiente paso recomendado
Construir el Notebook 03 para validar relevancia actual mediante datos recientes, idealmente 2022–2024 o 2023–2025, y comparar la persistencia de los hotspots identificados en el periodo base 2016–2019.
