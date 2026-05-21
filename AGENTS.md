# VíaSegura AI — Agent instructions

## Project
Road safety analysis for Bogotá using SIMUR data. Streamlit dashboard + Jupyter notebooks + reusable `src/` module.

## Commands

```powershell
# Run the app
run.bat
# or manually:
.venv\Scripts\streamlit.exe run app/main.py

# Python environment
.venv\Scripts\python.exe   # always use this, not system Python or Anaconda

# Install dependencies
.venv\Scripts\pip install -r requirements.txt
# or with uv:
uv sync
```

<!-- /aprende 2026-05-21 -->

## Conventions

- Run app via `run.bat` or `.venv\Scripts\streamlit.exe run app/main.py` — NOT system `streamlit` (Anaconda). <!-- /aprende 2026-05-21 -->
- Never commit `.env` — it contains `ANTHROPIC_API_KEY`. Already in `.gitignore`. <!-- /aprende 2026-05-21 -->
- Always commit and push to GitHub after completing each task. <!-- /aprende 2026-05-21 -->

## Architecture

```
app/          Streamlit multipage app (main.py + pages/1-4 + styles.py)
src/          Reusable Python utilities extracted from notebooks (DT-01)
notebooks/    Sequential analysis: NB01 → NB02 → NB03 → NB04 → NB04.5
mcp_simur/    MCP server with 6 tools for SIMUR API
agents/       6 Claude Code sub-agents with role-based permissions
data/         raw/ chunks + processed/ clean CSV
outputs/      maps/ GeoJSON+HTML, reports/ CSV+PNG
```

## Key gotchas

- geopandas: import lazily inside functions only — top-level import crashes on Anaconda env. <!-- /aprende 2026-05-21 -->
- pydeck `get_fill_color`: no JS syntax (`.includes()` etc.) — pre-compute color column in Python. <!-- /aprende 2026-05-21 -->
- pydeck tooltips: no Python format specifiers (`{col:.1f}`) — pre-format as string column. <!-- /aprende 2026-05-21 -->
- Claude Haiku 4.5: does NOT accept `thinking=` parameter — only Opus/Sonnet support it. <!-- /aprende 2026-05-21 -->
- SIMUR API: `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query`
