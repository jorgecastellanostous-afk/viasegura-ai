"""Debug: conecta al kernel via WebSocket y muestra todos los mensajes."""
import sys, uuid, json, time
import requests
import websocket
from datetime import datetime, timezone

TOKEN    = "7f27308e79644eb6a968c1fdce4935e3c0dd2d3cd5056268"
BASE_URL = "http://localhost:8888"
WS_URL   = "ws://localhost:8888"
HEADERS  = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}

# Obtener kernels activos
sessions = requests.get(f"{BASE_URL}/api/sessions", headers=HEADERS, timeout=10).json()
if not sessions:
    print("No hay sesiones activas. Crea una primero.")
    sys.exit(1)

# Usar el primer kernel disponible
s = sessions[0]
kernel_id  = s["kernel"]["id"]
session_id = s["id"]
print(f"Usando kernel: {kernel_id[:8]}...")

# Conectar WebSocket
ws = websocket.create_connection(
    f"{WS_URL}/api/kernels/{kernel_id}/channels?token={TOKEN}",
    timeout=10
)
print("WebSocket conectado.")

# Enviar execute_request
client_session = str(uuid.uuid4())
msg_id = str(uuid.uuid4())
msg = {
    "header": {
        "msg_id": msg_id,
        "msg_type": "execute_request",
        "username": "debug",
        "session": client_session,
        "version": "5.3",
        "date": datetime.now(timezone.utc).isoformat(),
    },
    "parent_header": {},
    "metadata": {},
    "content": {
        "code": "print('DEBUG HELLO'); import pandas; print('pd:', pandas.__version__)",
        "silent": False,
        "store_history": True,
        "user_expressions": {},
        "allow_stdin": False,
        "stop_on_error": True,
    },
    "channel": "shell",
    "buffers": [],
}
print(f"Enviando msg_id: {msg_id[:8]}...")
ws.send(json.dumps(msg))

# Leer respuestas (sin filtro, ver TODO)
ws.settimeout(3)
start = time.time()
count = 0
while time.time() - start < 30:
    try:
        raw = ws.recv()
    except websocket.WebSocketTimeoutException:
        if count > 0:
            print("  [timeout - no mas mensajes por 3s]")
            break
        continue
    except Exception as e:
        print(f"  [error recv: {e}]")
        break

    count += 1
    try:
        data = json.loads(raw)
    except Exception:
        print(f"  MSG[{count}] BINARY/no-JSON: {raw[:100]}")
        continue

    pmid = data.get("parent_header", {}).get("msg_id", "??")[:8]
    mt   = data.get("msg_type", "?")
    ch   = data.get("channel", "?")
    cont = data.get("content", {})

    match = "MATCH" if pmid == msg_id[:8] else "other"
    print(f"  MSG[{count}] type={mt} ch={ch} parent={pmid} [{match}]", flush=True)
    if mt == "stream":
        print(f"    text: {cont.get('text','')[:80]}")
    elif mt == "status":
        print(f"    state: {cont.get('execution_state','?')}")
    elif mt == "error":
        print(f"    {cont.get('ename')}: {cont.get('evalue')}")
    elif mt == "execute_reply":
        print(f"    status: {cont.get('status')} exec_count: {cont.get('execution_count')}")

    if mt == "status" and cont.get("execution_state") == "idle" and pmid == msg_id[:8]:
        print("  [idle recibido - fin de ejecucion]")
        break

print(f"\nTotal mensajes: {count}")
ws.close()
