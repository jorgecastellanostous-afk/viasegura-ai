"""
Ejecuta NB03.5 con exec() en Python puro (sin kernel de Jupyter).
Cada celda se ejecuta en un namespace compartido.
Uso: python -u scripts\ejecutar_nb035.py
"""
import sys, uuid, io, traceback
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import nbformat
from pathlib import Path

NB_PATH = Path(__file__).parent.parent / "notebooks" / "03.5_sintesis_metodologica_y_documentacion.ipynb"

# -- 1. Cargar notebook -------------------------------------------------------
print("Cargando notebook ...", flush=True)
with NB_PATH.open(encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

for cell in nb.cells:
    if not cell.get("id"):
        cell["id"] = uuid.uuid4().hex[:8]

code_cells = [c for c in nb.cells if c["cell_type"] == "code"]
print(f"  {len(nb.cells)} celdas | {len(code_cells)} de codigo", flush=True)

# -- 2. Namespace compartido --------------------------------------------------
import os
os.chdir(NB_PATH.parent)  # replica el working dir del kernel

# Definir display() como fallback (muestra DataFrame como texto)
def _display(obj):
    try:
        print(obj.to_string())
    except AttributeError:
        print(repr(obj))

namespace = {
    "__name__": "__main__",
    "display": _display,
}

# -- 3. Ejecutar celdas -------------------------------------------------------
errores  = []
cell_num = 0

for cell in nb.cells:
    if cell["cell_type"] != "code":
        continue
    src = cell["source"] if isinstance(cell["source"], str) else "".join(cell["source"])
    if not src.strip():
        continue
    cell_num += 1
    print(f"\n--- Celda {cell_num}/{len(code_cells)} ---", flush=True)

    outputs = []
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        exec(compile(src, f"<celda {cell_num}>", "exec"), namespace)
        captured = buf.getvalue()
    except Exception as exc:
        captured = buf.getvalue()
        ename  = type(exc).__name__
        evalue = str(exc)
        tb     = traceback.format_exc().splitlines()
        outputs.append(nbformat.v4.new_output("error",
            ename=ename, evalue=evalue, traceback=tb))
        errores.append((cell_num, ename, evalue))
    finally:
        sys.stdout = old_stdout

    if captured:
        outputs.append(nbformat.v4.new_output("stream",
            name="stdout", text=captured))
        print(captured, end="", flush=True)
    elif not any(o.get("output_type") == "error" for o in outputs):
        pass  # celda sin output (normal en imports)

    if any(o.get("output_type") == "error" for o in outputs):
        err = next(o for o in outputs if o.get("output_type") == "error")
        print(f"  ERROR: {err['ename']}: {err['evalue']}", flush=True)

    cell["outputs"]         = outputs
    cell["execution_count"] = cell_num

# -- 4. Guardar notebook ------------------------------------------------------
print("\nGuardando notebook ...", flush=True)
with NB_PATH.open("w", encoding="utf-8") as f:
    nbformat.write(nb, f)
print("Guardado.", flush=True)

if errores:
    print(f"\nERRORES en {len(errores)} celda(s):")
    for n, en, ev in errores:
        print(f"  Celda {n}: {en}: {ev}")
    sys.exit(1)
else:
    print(f"\nOK - {cell_num} celdas ejecutadas sin errores.")
