"""Test: execute_interactive con WindowsSelectorEventLoopPolicy."""
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import sys, time
import jupyter_client
from jupyter_core.paths import jupyter_runtime_dir
from pathlib import Path

rt = Path(jupyter_runtime_dir())
files = sorted(rt.glob("kernel-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
if not files:
    print("No hay kernel activo")
    sys.exit(1)

conn_file = str(files[0])
print(f"Usando: {files[0].name}")

kc = jupyter_client.BlockingKernelClient()
kc.load_connection_file(conn_file)
kc.start_channels()
kc.wait_for_ready(timeout=30)
print("Listo. Probando execute_interactive ...")

out = []
def hook(msg):
    mt = msg["msg_type"]
    if mt == "stream":
        out.append(msg["content"]["text"])
        print("STREAM:", msg["content"]["text"].strip())

kc.execute_interactive("import pandas as pd; print('pd OK', pd.__version__)", timeout=30, output_hook=hook)
print("Salida capturada:", out)

# Segunda celda - pd deberia seguir en namespace
out2 = []
def hook2(msg):
    if msg["msg_type"] == "stream":
        out2.append(msg["content"]["text"])
        print("STREAM2:", msg["content"]["text"].strip())

kc.execute_interactive("print('pd still:', pd.__version__)", timeout=30, output_hook=hook2)
print("Salida2:", out2)

kc.stop_channels()
