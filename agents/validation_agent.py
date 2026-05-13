"""
ValidationAgent — revisa que el fix propuesto por ErrorReviewAgent sea correcto.
Actúa como segunda opinión antes de aplicar cualquier cambio al código.
"""
from __future__ import annotations
import ast

from .base import client, FixProposal, SessionLog

SYSTEM_PROMPT = """Eres un revisor de código Python senior para el proyecto VíaSegura AI.
Tu única responsabilidad: evaluar si un fix propuesto es correcto, seguro y mínimo.

Criterios de aprobación:
1. El replacement es sintácticamente válido en Python.
2. El fix resuelve el error descrito sin introducir nuevos problemas.
3. El cambio es mínimo (no refactoriza innecesariamente).
4. No hay riesgos de seguridad (no ejecuta comandos externos no relacionados, etc.).

Si el fix es "reemplazar con código vacío" o "eliminar líneas críticas", recházalo.
Responde SOLO con JSON, sin texto adicional.
"""


class ValidationAgent:
    """Valida que un fix propuesto sea correcto antes de aplicarlo."""

    def __init__(self, log: SessionLog):
        self.log = log

    def validate(self, proposal: FixProposal) -> FixProposal:
        """
        Evalúa la propuesta. Retorna la misma propuesta con approved=True/False.
        """
        self.log.log(f"[ValidationAgent] Validando fix para: {proposal.file_path}")

        # Verificación de sintaxis rápida (sin Claude)
        syntax_ok, syntax_err = self._check_syntax(proposal.replacement)
        if not syntax_ok:
            proposal.approved = False
            proposal.rejection_reason = f"Sintaxis inválida: {syntax_err}"
            self.log.log(f"[ValidationAgent] RECHAZADO (sintaxis): {syntax_err}")
            return proposal

        if not proposal.original.strip() or not proposal.replacement.strip():
            proposal.approved = False
            proposal.rejection_reason = "El fix está vacío — no hay cambio concreto."
            self.log.log("[ValidationAgent] RECHAZADO: fix vacío")
            return proposal

        # Evaluación con Claude
        prompt = f"""Evalúa este fix de código Python:

## Problema
{proposal.reasoning}

## Código ORIGINAL (a reemplazar)
```python
{proposal.original}
```

## Código PROPUESTO (replacement)
```python
{proposal.replacement}
```

¿Es este fix correcto, seguro y mínimo?

Responde con este JSON exacto:
{{
  "aprobado": true,
  "razon": "<1 oración explicando por qué apruebas o rechazas>"
}}
"""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()

        try:
            import json, re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group() if match else raw)
        except Exception:
            proposal.approved = False
            proposal.rejection_reason = "No se pudo parsear la evaluación del agente."
            self.log.log("[ValidationAgent] RECHAZADO: error de parseo")
            return proposal

        proposal.approved = bool(data.get("aprobado", False))
        razon = data.get("razon", "")
        if proposal.approved:
            self.log.log(f"[ValidationAgent] APROBADO: {razon}")
        else:
            proposal.rejection_reason = razon
            self.log.log(f"[ValidationAgent] RECHAZADO: {razon}")

        return proposal

    @staticmethod
    def _check_syntax(code: str) -> tuple[bool, str]:
        """Verifica sintaxis Python sin ejecutar nada."""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, str(e)
