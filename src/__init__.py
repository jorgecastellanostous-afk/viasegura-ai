"""VíaSegura AI — reusable utilities extracted from notebooks."""

from .ipi_utils import calcular_ipi, asignar_prioridad_ipi, clasificar_familia_analitica
from .data_utils import limpiar_siniestros, validar_coordenadas, calcular_puntaje_gravedad
from .geo_utils import h3_to_polygon, asignar_h3, agregar_por_hexagono, clasificar_hex
from .simur_client import (
    descargar_accidentes_por_anio_seguro,
    descargar_por_formularios,
    agregar_por_zona,
)

__all__ = [
    "calcular_ipi",
    "asignar_prioridad_ipi",
    "clasificar_familia_analitica",
    "limpiar_siniestros",
    "validar_coordenadas",
    "calcular_puntaje_gravedad",
    "h3_to_polygon",
    "asignar_h3",
    "agregar_por_hexagono",
    "clasificar_hex",
    "descargar_accidentes_por_anio_seguro",
    "descargar_por_formularios",
    "agregar_por_zona",
]
