"""Tipos compartidos y cliente Anthropic para todos los agentes."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic

# Cliente único compartido — usa ANTHROPIC_API_KEY del entorno
client = Anthropic()

PYTHON = str(Path(__file__).parent.parent / ".venv" / "Scripts" / "python.exe")
PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class ExecutionError:
    """Un error de una celda o script."""
    celda: int
    ename: str
    evalue: str
    source: str          # código de la celda que falló
    traceback: str = ""


@dataclass
class FixProposal:
    """Propuesta de corrección generada por ErrorReviewAgent."""
    file_path: str
    original: str        # fragmento de código original
    replacement: str     # fragmento corregido
    reasoning: str       # por qué funciona el fix
    approved: bool = False
    rejection_reason: str = ""


@dataclass
class SessionLog:
    """Log de la sesión actual del supervisor."""
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    steps: list[str] = field(default_factory=list)
    errors_found: list[ExecutionError] = field(default_factory=list)
    fixes_proposed: list[FixProposal] = field(default_factory=list)
    fixes_applied: int = 0
    success: bool = False

    def log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self.steps.append(line)
        print(line, flush=True)
