"""
ExecutionAgent — corre scripts y notebooks, retorna errores estructurados.
No usa la API de Claude: solo ejecuta código y reporta resultados.
"""
from __future__ import annotations
import sys, io, uuid, traceback
from pathlib import Path
import nbformat

from .base import ExecutionError, SessionLog, PROJECT_ROOT, PYTHON


class ExecutionAgent:
    """Ejecuta un script Python o un notebook y retorna errores estructurados."""

    def __init__(self, log: SessionLog):
        self.log = log

    # ── Ejecutar script Python ──────────────────────────────────────────────
    def run_script(self, script_path: str) -> tuple[bool, str, list[ExecutionError]]:
        """
        Corre script_path con exec() en un namespace limpio.
        Retorna (ok, stdout_completo, lista_de_errores).
        """
        path = Path(script_path)
        self.log.log(f"[ExecutionAgent] Corriendo script: {path.name}")
        src = path.read_text(encoding="utf-8")

        captured = io.StringIO()
        old_stdout, sys.stdout = sys.stdout, captured
        errors: list[ExecutionError] = []

        namespace: dict = {"__name__": "__main__", "display": print}
        try:
            exec(compile(src, str(path), "exec"), namespace)
        except Exception as exc:
            tb = traceback.format_exc()
            errors.append(ExecutionError(
                celda=0,
                ename=type(exc).__name__,
                evalue=str(exc),
                source=src,
                traceback=tb,
            ))
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        ok = len(errors) == 0
        self.log.log(f"[ExecutionAgent] {'OK' if ok else 'ERROR'} — {len(errors)} error(s)")
        return ok, output, errors

    # ── Ejecutar notebook celda a celda ────────────────────────────────────
    def run_notebook(self, nb_path: str) -> tuple[bool, list[ExecutionError]]:
        """
        Corre cada celda de código del notebook en un namespace compartido.
        Retorna (ok, lista_de_errores).
        """
        path = Path(nb_path)
        self.log.log(f"[ExecutionAgent] Corriendo notebook: {path.name}")

        nb = nbformat.read(path.open(encoding="utf-8"), as_version=4)
        code_cells = [c for c in nb.cells if c["cell_type"] == "code"]

        import os
        os.chdir(path.parent)

        namespace: dict = {"__name__": "__main__", "display": print}
        errors: list[ExecutionError] = []
        cell_num = 0

        for cell in nb.cells:
            if cell["cell_type"] != "code":
                continue
            src = cell["source"] if isinstance(cell["source"], str) else "".join(cell["source"])
            if not src.strip():
                continue
            cell_num += 1

            captured = io.StringIO()
            old_stdout, sys.stdout = sys.stdout, captured
            try:
                exec(compile(src, f"<celda {cell_num}>", "exec"), namespace)
                output = captured.getvalue()
                cell["outputs"] = [nbformat.v4.new_output("stream", name="stdout", text=output)] if output else []
            except Exception as exc:
                output = captured.getvalue()
                tb = traceback.format_exc()
                err = ExecutionError(
                    celda=cell_num,
                    ename=type(exc).__name__,
                    evalue=str(exc),
                    source=src,
                    traceback=tb,
                )
                errors.append(err)
                cell["outputs"] = [nbformat.v4.new_output("error",
                    ename=err.ename, evalue=err.evalue, traceback=tb.splitlines())]
                self.log.log(f"  Celda {cell_num} ERROR: {err.ename}: {err.evalue}")
            finally:
                sys.stdout = old_stdout
                cell["execution_count"] = cell_num

        nbformat.write(nb, path.open("w", encoding="utf-8"))

        ok = len(errors) == 0
        self.log.log(f"[ExecutionAgent] {'OK' if ok else f'{len(errors)} error(s)'} en {cell_num} celdas")
        return ok, errors
