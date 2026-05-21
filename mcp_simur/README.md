# MCP Server SIMUR — VíaSegura AI

Servidor MCP que expone los datos de accidentalidad vial de Bogotá (SIMUR)
y los índices IPI calculados como herramientas que Claude puede invocar directamente.

## Herramientas disponibles

| Herramienta | Descripción |
|---|---|
| `simur_contar_registros(anio)` | Cuenta registros en SIMUR para un año (auditoría rápida) |
| `simur_descargar_muestra(anio, n, where_extra)` | Descarga N registros con filtros opcionales |
| `simur_localidades_activas(anio)` | Lista localidades con accidentes en ese año |
| `simur_estadisticas_zona(lat, lon, radio)` | Stats de una zona geográfica |
| `ipi_top_zonas(n, prioridad)` | Top N zonas del IPI histórico 2016-2019 |
| `ipi_resumen_ejecutivo()` | Resumen ejecutivo del IPI listo para Claude |

## Recursos disponibles

| Recurso | Descripción |
|---|---|
| `simur://metodologia` | Documentación de la metodología IPI |
| `simur://estructura-campos` | Campos del FeatureServer SIMUR |

## Instalación

```bash
# El paquete mcp ya está instalado en .venv
# Verificar:
python -c "from mcp.server.fastmcp import FastMCP; print('OK')"
```

## Registro en Claude Code

Agrega esto a `~/.claude/claude_desktop_config.json` (o al settings de Claude Code):

```json
{
  "mcpServers": {
    "viasegura-simur": {
      "command": "C:\\Users\\jorge\\Documents\\viasegura_ai\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_simur.server"],
      "cwd": "C:\\Users\\jorge\\Documents\\viasegura_ai"
    }
  }
}
```

O desde la terminal de Claude Code:
```
/mcp add viasegura-simur python -m mcp_simur.server
```

## Uso directo (prueba)

```bash
cd C:\Users\jorge\Documents\viasegura_ai
.venv\Scripts\python.exe -m mcp_simur.server
```

El servidor espera en stdio — úsalo desde un cliente MCP.

## Ejemplo de consulta (sin MCP, Python directo)

```python
import sys; sys.path.insert(0, "C:/Users/jorge/Documents/viasegura_ai")
from mcp_simur.server import ipi_resumen_ejecutivo, simur_contar_registros

# Resumen ejecutivo del IPI
print(ipi_resumen_ejecutivo())

# Auditoría de datos recientes
print(simur_contar_registros(2024))
```
