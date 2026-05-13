"""
ErrorReviewAgent — analiza errores con Claude y propone fixes concretos.
"""
from __future__ import annotations
from pathlib import Path

from .base import client, ExecutionError, FixProposal, SessionLog, PROJECT_ROOT

SYSTEM_PROMPT = """Eres un experto en Python y ciencia de datos especializado en el proyecto VíaSegura AI.
VíaSegura AI analiza siniestralidad vial en Bogotá usando pandas, geopandas y folium.
El proyecto está en C:/Users/jorge/Documents/viasegura_ai con entorno .venv (Python 3.11).

Tu tarea: analizar un error en una celda de notebook o script y proponer un fix CONCRETO y MÍNIMO.

Reglas:
- El fix debe ser el cambio más pequeño posible que resuelve el error.
- No refactorices código que funciona.
- Si el error es un archivo faltante, dilo claramente (no hay fix de código).
- Responde SIEMPRE en el formato JSON exacto que se te pide.
"""


class ErrorReviewAgent:
    """Usa Claude para analizar errores y proponer correcciones."""

    def __init__(self, log: SessionLog):
        self.log = log

    def review(self, error: ExecutionError, file_path: str) -> FixProposal | None:
        """
        Analiza un error y retorna una FixProposal o None si no hay fix de código.
        """
        self.log.log(f"[ErrorReviewAgent] Analizando: {error.ename} en celda {error.celda}")

        prompt = f"""Analiza este error de Python y propone un fix.

## Error
- Tipo: {error.ename}
- Mensaje: {error.evalue}
- Celda número: {error.celda}

## Código que falló
```python
{error.source[:2000]}
```

## Traceback
```
{error.traceback[:1500]}
```

## Archivo
{file_path}

Responde ÚNICAMENTE con este JSON (sin markdown, sin texto extra):
{{
  "puede_repararse_con_codigo": true,
  "original": "<fragmento exacto del código a reemplazar, o '' si no aplica>",
  "replacement": "<fragmento corregido, o '' si no aplica>",
  "reasoning": "<explicación en 1-2 oraciones de por qué funciona>"
}}

Si el error es por archivo faltante, ruta incorrecta, o problema de entorno, pon `false` en `puede_repararse_con_codigo`.
"""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        self.log.log(f"[ErrorReviewAgent] Respuesta recibida ({len(raw)} chars)")

        try:
            import json
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Intentar extraer JSON si Claude añadió texto extra
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not match:
                self.log.log("[ErrorReviewAgent] No se pudo parsear JSON de la respuesta")
                return None
            data = json.loads(match.group())

        if not data.get("puede_repararse_con_codigo"):
            self.log.log(f"[ErrorReviewAgent] Error no reparable con código: {data.get('reasoning', '')}")
            return None

        proposal = FixProposal(
            file_path=file_path,
            original=data.get("original", ""),
            replacement=data.get("replacement", ""),
            reasoning=data.get("reasoning", ""),
        )
        self.log.log(f"[ErrorReviewAgent] Fix propuesto: {proposal.reasoning}")
        return proposal
