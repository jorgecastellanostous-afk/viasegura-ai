"""
SupervisorAgent — orquesta ExecutionAgent, ErrorReviewAgent y ValidationAgent.

Flujo:
  1. ExecutionAgent corre el target (notebook o script)
  2. Si hay errores → ErrorReviewAgent propone fix
  3. ValidationAgent evalúa el fix
  4. Si aprobado → aplica fix y vuelve a correr (máx MAX_RETRIES veces)
  5. Reporta resultado final
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

from .base import SessionLog, FixProposal, PROJECT_ROOT
from .execution_agent import ExecutionAgent
from .error_review_agent import ErrorReviewAgent
from .validation_agent import ValidationAgent

MAX_RETRIES = 3
LOG_DIR = PROJECT_ROOT / "agents" / "logs"


class SupervisorAgent:
    """Coordina el ciclo ejecutar → revisar error → validar fix → aplicar → repetir."""

    def __init__(self):
        self.log = SessionLog()
        self.execution = ExecutionAgent(self.log)
        self.review    = ErrorReviewAgent(self.log)
        self.validator = ValidationAgent(self.log)

    # ── Punto de entrada principal ──────────────────────────────────────────
    def run(self, target: str) -> bool:
        """
        Corre `target` (ruta a un .ipynb o .py) con corrección automática.
        Retorna True si terminó sin errores.
        """
        path = Path(target)
        self.log.log(f"[Supervisor] Iniciando: {path.name}")
        self.log.log(f"[Supervisor] Tipo: {'notebook' if path.suffix == '.ipynb' else 'script'}")

        for intento in range(1, MAX_RETRIES + 1):
            self.log.log(f"\n[Supervisor] ── Intento {intento}/{MAX_RETRIES} ──")

            # 1. Ejecutar
            if path.suffix == ".ipynb":
                ok, errors = self.execution.run_notebook(str(path))
            else:
                ok, _, errors = self.execution.run_script(str(path))

            if ok:
                self.log.log(f"[Supervisor] Ejecución exitosa en intento {intento}.")
                self.log.success = True
                self._save_log()
                return True

            # 2. Revisar errores
            self.log.errors_found.extend(errors)
            self.log.log(f"[Supervisor] {len(errors)} error(s) encontrado(s). Enviando a ErrorReviewAgent...")

            fixes_aplicados = 0
            for err in errors:
                self.log.log(f"\n[Supervisor] Error en celda {err.celda}: {err.ename}: {err.evalue}")

                # 3. Proponer fix
                proposal = self.review.review(err, str(path))
                if proposal is None:
                    self.log.log("[Supervisor] ErrorReviewAgent: no hay fix de código posible.")
                    continue

                self.log.fixes_proposed.append(proposal)

                # 4. Validar fix
                proposal = self.validator.validate(proposal)
                if not proposal.approved:
                    self.log.log(f"[Supervisor] Fix rechazado: {proposal.rejection_reason}")
                    continue

                # 5. Aplicar fix
                aplicado = self._apply_fix(proposal, path)
                if aplicado:
                    fixes_aplicados += 1
                    self.log.fixes_applied += 1

            if fixes_aplicados == 0:
                self.log.log("[Supervisor] No se pudieron aplicar fixes. Deteniendo.")
                break

        self.log.success = False
        self.log.log(f"\n[Supervisor] FALLIDO después de {MAX_RETRIES} intentos.")
        self._save_log()
        return False

    # ── Aplicar fix al archivo ──────────────────────────────────────────────
    def _apply_fix(self, proposal: FixProposal, path: Path) -> bool:
        """Reemplaza `original` por `replacement` en el archivo indicado."""
        target = Path(proposal.file_path)

        if target.suffix == ".ipynb":
            return self._apply_fix_notebook(proposal, target)
        else:
            return self._apply_fix_file(proposal, target)

    def _apply_fix_file(self, proposal: FixProposal, target: Path) -> bool:
        src = target.read_text(encoding="utf-8")
        if proposal.original not in src:
            self.log.log(f"[Supervisor] Fix no aplicable: fragmento original no encontrado en {target.name}")
            return False
        new_src = src.replace(proposal.original, proposal.replacement, 1)
        target.write_text(new_src, encoding="utf-8")
        self.log.log(f"[Supervisor] Fix aplicado en {target.name}")
        return True

    def _apply_fix_notebook(self, proposal: FixProposal, target: Path) -> bool:
        import nbformat
        nb = nbformat.read(target.open(encoding="utf-8"), as_version=4)
        applied = False
        for cell in nb.cells:
            if cell["cell_type"] != "code":
                continue
            src = cell["source"] if isinstance(cell["source"], str) else "".join(cell["source"])
            if proposal.original in src:
                cell["source"] = src.replace(proposal.original, proposal.replacement, 1)
                applied = True
                break
        if applied:
            nbformat.write(nb, target.open("w", encoding="utf-8"))
            self.log.log(f"[Supervisor] Fix aplicado en celda del notebook {target.name}")
        else:
            self.log.log(f"[Supervisor] Fragmento original no encontrado en el notebook")
        return applied

    # ── Guardar log de sesión ───────────────────────────────────────────────
    def _save_log(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = LOG_DIR / f"session_{ts}.json"
        data = {
            "started_at": self.log.started_at,
            "success": self.log.success,
            "fixes_applied": self.log.fixes_applied,
            "steps": self.log.steps,
            "errors_found": [
                {"celda": e.celda, "ename": e.ename, "evalue": e.evalue}
                for e in self.log.errors_found
            ],
            "fixes_proposed": [
                {"approved": f.approved, "reasoning": f.reasoning,
                 "rejection_reason": f.rejection_reason}
                for f in self.log.fixes_proposed
            ],
        }
        log_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log.log(f"[Supervisor] Log guardado: {log_path.name}")
