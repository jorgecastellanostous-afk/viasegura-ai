"""
crear_nb04.py — Genera el notebook 04_enriquecimiento_actor_vehiculo_causa.ipynb
Ejecutar desde la raíz del proyecto: python scripts/crear_nb04.py
"""

import json
import uuid
from pathlib import Path

def uid():
    return uuid.uuid4().hex[:8]

def md(source):
    return {"cell_type": "markdown", "id": uid(), "metadata": {}, "source": source}

def code(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": uid(),
        "metadata": {},
        "outputs": [],
        "source": source,
    }

# ---------------------------------------------------------------------------
cells = []

# ── TÍTULO ──────────────────────────────────────────────────────────────────
cells.append(md(
    "# VíaSegura AI — Notebook 04\n"
    "## Enriquecimiento: actores viales, vehículos y causas\n"
    "\n"
    "**Proyecto:** VíaSegura AI  \n"
    "**Notebook:** 04  \n"
    "**Periodo de análisis:** 2020–2021 (reciente)  \n"
    "**Objetivo:** Enriquecer el Top 200 de zonas críticas recientes con el perfil predominante "
    "de actor vial, vehículo y causa del siniestro, usando las capas hermanas del servicio SIMUR "
    "(layers 3, 4 y 5), vinculadas por la clave `FORMULARIO`."
))

# ── CONTEXTO ────────────────────────────────────────────────────────────────
cells.append(md(
    "## Contexto\n"
    "\n"
    "El Notebook 03 construyó el **IPI reciente** sobre 72,903 siniestros del periodo 2020–2021 "
    "y clasificó 19,255 zonas de la grilla en categorías de persistencia. "
    "El resultado central es el **Top 200 de zonas priorizadas**, con 37 Persistentes y 163 Emergentes.\n"
    "\n"
    "Este notebook responde la pregunta complementaria:\n"
    "> **¿Qué tipo de intervención requiere cada zona? "
    "¿Es un problema de peatones, de motos, de infraestructura?**\n"
    "\n"
    "Para eso integra tres capas hermanas del FeatureServer SIMUR mediante la clave `FORMULARIO`:\n"
    "\n"
    "| Layer | Tabla | Campo de interés | Pregunta |\n"
    "|---|---|---|---|\n"
    "| 3 | VM_ACC_ACTOR_VIAL | `CONDICION` | ¿Quién está involucrado? (peatón, ciclista, conductor…) |\n"
    "| 5 | VM_ACC_VEHICULO | `CLASE` | ¿Qué vehículo predomina? (moto, automóvil, bus…) |\n"
    "| 4 | VM_ACC_CAUSA | `NOMBRE` | ¿Qué causa fue registrada con más frecuencia? |\n"
    "\n"
    "**Estrategia:** se construye primero el índice `FORMULARIO → zona` a partir de la base "
    "reciente limpia. Solo se descargan registros de las capas hermanas cuyos `FORMULARIO` "
    "pertenecen a una zona del Top 200. Esto reduce el volumen de ~3 M a ~3,000–6,000 registros "
    "por capa, haciendo la descarga manejable."
))

# ── ESTRUCTURA ──────────────────────────────────────────────────────────────
cells.append(md(
    "## Estructura del notebook\n"
    "\n"
    "| Sección | Contenido | Descarga |\n"
    "|---|---|---|\n"
    "| 1 | Setup: imports, config, parámetros globales | No |\n"
    "| 2 | Carga y validación de insumos NB03 | No |\n"
    "| 3 | Índice FORMULARIO → zona (lat_grid, lon_grid) | No |\n"
    "| 4 | Auditoría previa de capas hermanas SIMUR | Solo conteos |\n"
    "| **5** | **Descarga VM_ACC_ACTOR_VIAL (layer 3)** | **Sí** |\n"
    "| **6** | **Descarga VM_ACC_VEHICULO (layer 5)** | **Sí** |\n"
    "| **7** | **Descarga VM_ACC_CAUSA (layer 4)** | **Sí** |\n"
    "| 8 | Verificación VM_ACC_VIA (layer 6) | Sondeo ligero |\n"
    "| 9 | Join y moda por zona | No |\n"
    "| 10 | Enriquecimiento del DataFrame de hotspots | No |\n"
    "| 11 | Mapa interactivo enriquecido | No |\n"
    "| 12 | Manifiesto y resumen ejecutivo | No |"
))

# ── CONVENCIONES ────────────────────────────────────────────────────────────
cells.append(md(
    "## Convenciones y limitaciones\n"
    "\n"
    "**Moda por zona:** cuando un siniestro tiene múltiples actores/vehículos (cardinalidad N:1), "
    "todos se incluyen en el JOIN. La moda refleja el tipo más frecuente en el conjunto de "
    "siniestros de la zona, no por siniestro individual.\n"
    "\n"
    "**Cobertura de FORMULARIO:** puede ser <100% en las capas hermanas. "
    "Se reporta la cobertura real en la Sección 9.\n"
    "\n"
    "**Layer 6 (VM_ACC_VIA):** devolvió 0 registros en la muestra de NB03. "
    "Se verifica nuevamente en la Sección 8 antes de incluir o excluir.\n"
    "\n"
    "**Usar:** actor vial predominante · perfil de zona · composición de actores · "
    "distribución de causas · tipo de vehículo modal  \n"
    "**Evitar:** 'causa del accidente' como determinista · afirmaciones causales "
    "sin datos de exposición"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — SETUP
# ════════════════════════════════════════════════════════════════════════════
cells.append(md("## Sección 1 — Setup: imports, config y parámetros globales"))

cells.append(code(
    "import pandas as pd\n"
    "import numpy as np\n"
    "import requests\n"
    "import folium\n"
    "from folium import IFrame\n"
    "import matplotlib.pyplot as plt\n"
    "import matplotlib.ticker as mticker\n"
    "from pathlib import Path\n"
    "import time\n"
    "import json\n"
    "import sys\n"
    "from datetime import datetime\n"
    "from collections import Counter\n"
    "\n"
    "# Config del proyecto\n"
    "_root = next(\n"
    "    (c for c in [Path.cwd(), Path.cwd().parent] if (c / 'config.py').exists()),\n"
    "    Path.cwd()\n"
    ")\n"
    "if str(_root) not in sys.path:\n"
    "    sys.path.insert(0, str(_root))\n"
    "from config import PROJECT_ROOT, DATA_RAW, DATA_PROCESSED, REPORTS, MAPS\n"
    "\n"
    "print('VíaSegura AI — Notebook 04 iniciado.')\n"
    "print(f'Raíz del proyecto: {PROJECT_ROOT}')\n"
    "print(f'pandas {pd.__version__} | numpy {np.__version__}')"
))

cells.append(code(
    "# ============================================================\n"
    "# PARÁMETROS GLOBALES — NB04\n"
    "# Modificar aquí para análisis de sensibilidad\n"
    "# ============================================================\n"
    "\n"
    "BASE_URL = (\n"
    "    'https://sig.simur.gov.co/arcgis/rest/services'\n"
    "    '/Accidentalidad/AccidentalidadAnalisis/FeatureServer'\n"
    ")\n"
    "\n"
    "ANIOS_RECIENTES = [2020, 2021]\n"
    "\n"
    "# Capas hermanas de interés\n"
    "CAPAS = {\n"
    "    'actor_vial': 3,   # VM_ACC_ACTOR_VIAL  → campo CONDICION\n"
    "    'vehiculo':   5,   # VM_ACC_VEHICULO    → campo CLASE\n"
    "    'causa':      4,   # VM_ACC_CAUSA       → campo NOMBRE\n"
    "    'via':        6,   # VM_ACC_VIA         → verificar cobertura\n"
    "}\n"
    "\n"
    "CAMPO_JOIN     = 'FORMULARIO'\n"
    "CAMPO_ACTOR    = 'CONDICION'\n"
    "CAMPO_VEHICULO = 'CLASE'\n"
    "CAMPO_CAUSA    = 'NOMBRE'\n"
    "\n"
    "BATCH_SIZE = 200    # FORMULARIOs por consulta IN ()\n"
    "TOP_N      = 200    # Zonas a enriquecer\n"
    "MAX_REINTENTOS = 5\n"
    "\n"
    "# Rutas de insumos NB03\n"
    "PATH_CLASIFICACION  = REPORTS / 'clasificacion_hotspots_persistencia_notebook_03.csv'\n"
    "PATH_TOP200_REC     = REPORTS / 'top200_IPI_reciente_notebook_03.csv'\n"
    "PATH_ACCIDENTES_REC = DATA_PROCESSED / 'accidentes_bogota_reciente_limpio.csv'\n"
    "PATH_ESQUEMA_NB04   = REPORTS / 'esquema_integracion_nb04_notebook_03.csv'\n"
    "\n"
    "# Rutas de outputs NB04\n"
    "PATH_ACTOR_RAW    = DATA_RAW / 'actor_vial_top200_reciente.csv'\n"
    "PATH_VEHICULO_RAW = DATA_RAW / 'vehiculo_top200_reciente.csv'\n"
    "PATH_CAUSA_RAW    = DATA_RAW / 'causa_top200_reciente.csv'\n"
    "PATH_HOTSPOTS_ENR = REPORTS  / 'hotspots_enriquecidos_nb04.csv'\n"
    "PATH_MAPA_ENR     = MAPS     / 'mapa_hotspots_enriquecidos_nb04.html'\n"
    "PATH_RESUMEN_EJ   = REPORTS  / 'resumen_ejecutivo_notebook_04.md'\n"
    "\n"
    "print('Parámetros globales cargados ✅')\n"
    "print(f'  BATCH_SIZE   = {BATCH_SIZE}')\n"
    "print(f'  TOP_N        = {TOP_N}')\n"
    "print(f'  Años recientes: {ANIOS_RECIENTES}')"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — CARGA DE INSUMOS
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 2 — Carga y validación de insumos NB03\n"
    "\n"
    "Se verifican los cuatro archivos generados en NB03 que son insumo de este notebook."
))

cells.append(code(
    "# Verificar existencia de insumos\n"
    "insumos = {\n"
    "    'clasificacion_hotspots': PATH_CLASIFICACION,\n"
    "    'top200_reciente':        PATH_TOP200_REC,\n"
    "    'accidentes_reciente':    PATH_ACCIDENTES_REC,\n"
    "    'esquema_nb04':           PATH_ESQUEMA_NB04,\n"
    "}\n"
    "\n"
    "print('Verificando insumos NB03...\\n')\n"
    "todos_ok = True\n"
    "for nombre, ruta in insumos.items():\n"
    "    existe = ruta.exists()\n"
    "    tam_kb = ruta.stat().st_size // 1024 if existe else 0\n"
    "    estado = '✅' if existe else '❌ NO ENCONTRADO'\n"
    "    print(f'  {estado}  {nombre:<26}  {str(ruta.name):<55}  {tam_kb:>6} KB')\n"
    "    if not existe:\n"
    "        todos_ok = False\n"
    "\n"
    "if not todos_ok:\n"
    "    raise FileNotFoundError('Faltan insumos de NB03. Ejecutar NB03 primero.')\n"
    "print('\\nTodos los insumos presentes ✅')"
))

cells.append(code(
    "# Cargar insumos\n"
    "df_clasificacion = pd.read_csv(PATH_CLASIFICACION)\n"
    "df_top200        = pd.read_csv(PATH_TOP200_REC)\n"
    "df_acc_rec       = pd.read_csv(PATH_ACCIDENTES_REC, low_memory=False)\n"
    "df_esquema       = pd.read_csv(PATH_ESQUEMA_NB04)\n"
    "\n"
    "print('DataFrames cargados:')\n"
    "print(f'  clasificacion_hotspots : {len(df_clasificacion):>6,} filas × {df_clasificacion.shape[1]} cols')\n"
    "print(f'  top200_reciente        : {len(df_top200):>6,} filas × {df_top200.shape[1]} cols')\n"
    "print(f'  accidentes_reciente    : {len(df_acc_rec):>6,} filas × {df_acc_rec.shape[1]} cols')\n"
    "print(f'  esquema_nb04           : {len(df_esquema):>6,} filas × {df_esquema.shape[1]} cols')\n"
    "print()\n"
    "\n"
    "# Validaciones básicas\n"
    "assert 'lat_grid' in df_top200.columns and 'lon_grid' in df_top200.columns, \\\n"
    "    'top200 debe tener lat_grid y lon_grid'\n"
    "assert 'FORMULARIO' in df_acc_rec.columns, 'accidentes_reciente debe tener FORMULARIO'\n"
    "assert df_acc_rec['FORMULARIO'].isna().sum() == 0, \\\n"
    "    f'FORMULARIO tiene nulos: {df_acc_rec[\"FORMULARIO\"].isna().sum()}'\n"
    "\n"
    "print('Validaciones básicas pasadas ✅')\n"
    "print(f'\\nEsquema de integración NB04:')\n"
    "print(df_esquema[['capa_id','nombre','registros_totales','campos_disponibles']].to_string(index=False))"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — ÍNDICE FORMULARIO → ZONA
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 3 — Índice FORMULARIO → zona (lat_grid, lon_grid)\n"
    "\n"
    "Se asigna cada siniestro de la base reciente a su celda de grilla "
    "redondeando las coordenadas a 3 decimales (resolución ≈ 111 m × 111 m). "
    "Luego se filtra al subconjunto de FORMULARIOs cuya zona pertenece al Top 200 reciente. "
    "Este conjunto es la lista de consulta para las capas hermanas."
))

cells.append(code(
    "# Asignar cada siniestro a su celda de grilla\n"
    "df_acc_rec = df_acc_rec.copy()\n"
    "df_acc_rec['lat_grid'] = df_acc_rec['LATITUD'].round(3)\n"
    "df_acc_rec['lon_grid'] = df_acc_rec['LONGITUD'].round(3)\n"
    "\n"
    "# Crear diccionario FORMULARIO → (lat_grid, lon_grid)\n"
    "formulario_zona = dict(\n"
    "    zip(df_acc_rec['FORMULARIO'],\n"
    "        zip(df_acc_rec['lat_grid'], df_acc_rec['lon_grid']))\n"
    ")\n"
    "print(f'Índice FORMULARIO → zona: {len(formulario_zona):,} entradas')\n"
    "\n"
    "# Coordenadas del Top 200\n"
    "zonas_top200 = set(\n"
    "    zip(df_top200['lat_grid'].round(3), df_top200['lon_grid'].round(3))\n"
    ")\n"
    "print(f'Zonas en el Top 200: {len(zonas_top200)}')\n"
    "\n"
    "# FORMULARIOs cuyos siniestros caen en Top 200\n"
    "formularios_top200 = [\n"
    "    form for form, zona in formulario_zona.items()\n"
    "    if zona in zonas_top200\n"
    "]\n"
    "print(f'FORMULARIOs en zonas Top 200: {len(formularios_top200):,}')\n"
    "print(f'  (de {len(df_acc_rec):,} siniestros totales recientes — '\n"
    "      f'{len(formularios_top200)/len(df_acc_rec)*100:.1f}%)')\n"
    "\n"
    "# Verificación: cuántos siniestros por zona (Top 200)\n"
    "zona_a_forms = {}\n"
    "for form, zona in formulario_zona.items():\n"
    "    if zona in zonas_top200:\n"
    "        zona_a_forms.setdefault(zona, []).append(form)\n"
    "\n"
    "siniestros_por_zona = [len(v) for v in zona_a_forms.values()]\n"
    "print(f'\\nSiniestros por zona (Top 200):')\n"
    "print(f'  Mínimo : {min(siniestros_por_zona)}')\n"
    "print(f'  Mediana: {np.median(siniestros_por_zona):.0f}')\n"
    "print(f'  Máximo : {max(siniestros_por_zona)}')\n"
    "print(f'  Total  : {sum(siniestros_por_zona):,}')"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — AUDITORÍA DE CAPAS
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 4 — Auditoría previa de capas hermanas SIMUR\n"
    "\n"
    "Se consulta el conteo de registros para una muestra de FORMULARIOs del Top 200 "
    "en cada capa hermana. Confirma que el join FORMULARIO funciona antes de lanzar "
    "la descarga completa."
))

cells.append(code(
    "# Tomar muestra de FORMULARIOs para sondeo\n"
    "N_MUESTRA = 10\n"
    "sample_forms = formularios_top200[:N_MUESTRA]\n"
    "forms_str = \"','\".join(sample_forms)\n"
    "where_sample = f\"FORMULARIO IN ('{forms_str}')\"\n"
    "\n"
    "print(f'Sondeando {N_MUESTRA} FORMULARIOs de muestra en capas 3, 4, 5, 6...\\n')\n"
    "print(f'WHERE: {where_sample[:80]}...\\n')\n"
    "\n"
    "auditoria = []\n"
    "for nombre, layer_id in CAPAS.items():\n"
    "    url_q = f'{BASE_URL}/{layer_id}/query'\n"
    "    try:\n"
    "        r = requests.get(\n"
    "            url_q,\n"
    "            params={'where': where_sample, 'returnCountOnly': 'true', 'f': 'json'},\n"
    "            timeout=30\n"
    "        )\n"
    "        data = r.json()\n"
    "        count = data.get('count')\n"
    "        if count is not None:\n"
    "            estado = '✅'\n"
    "            count_str = str(count)\n"
    "        else:\n"
    "            err = data.get('error', {}).get('message', 'sin conteo')\n"
    "            estado = '⚠️'\n"
    "            count_str = f'ERROR: {err}'\n"
    "    except Exception as e:\n"
    "        estado = '❌'\n"
    "        count_str = str(e)\n"
    "        count = None\n"
    "    auditoria.append({'capa': nombre, 'layer_id': layer_id,\n"
    "                      'estado': estado, 'registros_muestra': count_str})\n"
    "    print(f'  {estado} Layer {layer_id} ({nombre:<12}): {count_str} registros para {N_MUESTRA} FORMULARIOs')\n"
    "    time.sleep(0.5)\n"
    "\n"
    "df_audit = pd.DataFrame(auditoria)\n"
    "print('\\nAuditoría completada.')\n"
    "print('Si Layer 6 (via) devuelve 0, se investiga en Sección 8.')"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — DESCARGA ACTOR VIAL (Layer 3)
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 5 — Descarga VM_ACC_ACTOR_VIAL (layer 3)\n"
    "\n"
    "Se descargan todos los registros de VM_ACC_ACTOR_VIAL cuyo `FORMULARIO` "
    "pertenece a una zona del Top 200. La consulta se hace en batches de `BATCH_SIZE` "
    "FORMULARIOs para evitar límites de longitud de URL.\n"
    "\n"
    "**Campo de interés:** `CONDICION` — tipo de actor vial "
    "(CONDUCTOR, PASAJERO, PEATON, CICLISTA, etc.)\n"
    "\n"
    "**Si el archivo ya existe**, se carga directamente sin redescargar."
))

cells.append(code(
    "def descargar_por_formularios(layer_id, formularios, campos='*',\n"
    "                               batch_size=BATCH_SIZE, max_reintentos=MAX_REINTENTOS):\n"
    "    \"\"\"Descarga registros de una capa filtrando por lista de FORMULARIOs.\"\"\"\n"
    "    url_q   = f'{BASE_URL}/{layer_id}/query'\n"
    "    total   = len(formularios)\n"
    "    batches = [formularios[i:i + batch_size] for i in range(0, total, batch_size)]\n"
    "    resultados = []\n"
    "\n"
    "    print(f'  Layer {layer_id}: {total:,} FORMULARIOs → {len(batches)} batches de ≤{batch_size}')\n"
    "\n"
    "    for idx, batch in enumerate(batches):\n"
    "        forms_str = \"','\".join(batch)\n"
    "        where = f\"FORMULARIO IN ('{forms_str}')\"\n"
    "        params = {\n"
    "            'where':    where,\n"
    "            'outFields': campos,\n"
    "            'f':        'json',\n"
    "        }\n"
    "        for intento in range(1, max_reintentos + 1):\n"
    "            try:\n"
    "                r = requests.post(url_q, data=params, timeout=60)\n"
    "                features = r.json().get('features', [])\n"
    "                resultados.extend([f['attributes'] for f in features])\n"
    "                break\n"
    "            except Exception as e:\n"
    "                if intento == max_reintentos:\n"
    "                    print(f'    ❌ Batch {idx+1} fallido tras {max_reintentos} intentos: {e}')\n"
    "                else:\n"
    "                    time.sleep(2 ** intento)\n"
    "\n"
    "        if (idx + 1) % 20 == 0 or (idx + 1) == len(batches):\n"
    "            print(f'  [{idx+1:>3}/{len(batches)}] acumulado: {len(resultados):,} registros')\n"
    "        else:\n"
    "            time.sleep(0.3)\n"
    "\n"
    "    return pd.DataFrame(resultados)\n"
    "\n"
    "print('Función descargar_por_formularios definida ✅')"
))

cells.append(code(
    "# Descarga Layer 3 — VM_ACC_ACTOR_VIAL\n"
    "CAMPOS_ACTOR = 'OBJECTID,FORMULARIO,CONDICION,ESTADO,GENERO,EDAD'\n"
    "\n"
    "if PATH_ACTOR_RAW.exists():\n"
    "    print(f'Archivo ya existe — cargando desde disco:')\n"
    "    print(f'  {PATH_ACTOR_RAW}')\n"
    "    df_actor = pd.read_csv(PATH_ACTOR_RAW, low_memory=False)\n"
    "    print(f'  {len(df_actor):,} registros cargados.')\n"
    "else:\n"
    "    print('Descargando VM_ACC_ACTOR_VIAL (layer 3)...')\n"
    "    t0 = time.time()\n"
    "    df_actor = descargar_por_formularios(\n"
    "        layer_id=CAPAS['actor_vial'],\n"
    "        formularios=formularios_top200,\n"
    "        campos=CAMPOS_ACTOR,\n"
    "    )\n"
    "    elapsed = time.time() - t0\n"
    "    print(f'\\nDescarga completada en {elapsed:.0f}s — {len(df_actor):,} registros')\n"
    "    df_actor.to_csv(PATH_ACTOR_RAW, index=False)\n"
    "    print(f'Guardado en: {PATH_ACTOR_RAW}')\n"
    "\n"
    "print(f'\\nColumnas: {df_actor.columns.tolist()}')\n"
    "print(f'Nulos en CONDICION: {df_actor[\"CONDICION\"].isna().sum()}')\n"
    "print(f'\\nTop 10 valores de CONDICION:')\n"
    "print(df_actor['CONDICION'].value_counts().head(10).to_string())"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6 — DESCARGA VEHÍCULO (Layer 5)
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 6 — Descarga VM_ACC_VEHICULO (layer 5)\n"
    "\n"
    "Se descargan los registros de VM_ACC_VEHICULO para los mismos FORMULARIOs del Top 200.\n"
    "\n"
    "**Campo de interés:** `CLASE` — tipo de vehículo "
    "(MOTOCICLETA, AUTOMOVIL, BUS, BICICLETA, etc.)\n"
    "\n"
    "**Si el archivo ya existe**, se carga directamente."
))

cells.append(code(
    "# Descarga Layer 5 — VM_ACC_VEHICULO\n"
    "CAMPOS_VEHICULO = 'OBJECTID,FORMULARIO,CLASE,SERVICIO,MODALIDAD'\n"
    "\n"
    "if PATH_VEHICULO_RAW.exists():\n"
    "    print(f'Archivo ya existe — cargando desde disco:')\n"
    "    print(f'  {PATH_VEHICULO_RAW}')\n"
    "    df_vehiculo = pd.read_csv(PATH_VEHICULO_RAW, low_memory=False)\n"
    "    print(f'  {len(df_vehiculo):,} registros cargados.')\n"
    "else:\n"
    "    print('Descargando VM_ACC_VEHICULO (layer 5)...')\n"
    "    t0 = time.time()\n"
    "    df_vehiculo = descargar_por_formularios(\n"
    "        layer_id=CAPAS['vehiculo'],\n"
    "        formularios=formularios_top200,\n"
    "        campos=CAMPOS_VEHICULO,\n"
    "    )\n"
    "    elapsed = time.time() - t0\n"
    "    print(f'\\nDescarga completada en {elapsed:.0f}s — {len(df_vehiculo):,} registros')\n"
    "    df_vehiculo.to_csv(PATH_VEHICULO_RAW, index=False)\n"
    "    print(f'Guardado en: {PATH_VEHICULO_RAW}')\n"
    "\n"
    "print(f'\\nColumnas: {df_vehiculo.columns.tolist()}')\n"
    "print(f'Nulos en CLASE: {df_vehiculo[\"CLASE\"].isna().sum()}')\n"
    "print(f'\\nTop 10 valores de CLASE:')\n"
    "print(df_vehiculo['CLASE'].value_counts().head(10).to_string())"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 7 — DESCARGA CAUSA (Layer 4)
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 7 — Descarga VM_ACC_CAUSA (layer 4)\n"
    "\n"
    "Se descargan los registros de VM_ACC_CAUSA para los mismos FORMULARIOs del Top 200.\n"
    "\n"
    "**Campo de interés:** `NOMBRE` — causa registrada del siniestro "
    "(DESOBEDECER SEÑALES, EXCESO DE VELOCIDAD, etc.)\n"
    "\n"
    "**Si el archivo ya existe**, se carga directamente."
))

cells.append(code(
    "# Descarga Layer 4 — VM_ACC_CAUSA\n"
    "CAMPOS_CAUSA = 'OBJECTID,FORMULARIO,NOMBRE,TIPO,TIPO_CAUSA'\n"
    "\n"
    "if PATH_CAUSA_RAW.exists():\n"
    "    print(f'Archivo ya existe — cargando desde disco:')\n"
    "    print(f'  {PATH_CAUSA_RAW}')\n"
    "    df_causa = pd.read_csv(PATH_CAUSA_RAW, low_memory=False)\n"
    "    print(f'  {len(df_causa):,} registros cargados.')\n"
    "else:\n"
    "    print('Descargando VM_ACC_CAUSA (layer 4)...')\n"
    "    t0 = time.time()\n"
    "    df_causa = descargar_por_formularios(\n"
    "        layer_id=CAPAS['causa'],\n"
    "        formularios=formularios_top200,\n"
    "        campos=CAMPOS_CAUSA,\n"
    "    )\n"
    "    elapsed = time.time() - t0\n"
    "    print(f'\\nDescarga completada en {elapsed:.0f}s — {len(df_causa):,} registros')\n"
    "    df_causa.to_csv(PATH_CAUSA_RAW, index=False)\n"
    "    print(f'Guardado en: {PATH_CAUSA_RAW}')\n"
    "\n"
    "print(f'\\nColumnas: {df_causa.columns.tolist()}')\n"
    "print(f'Nulos en NOMBRE: {df_causa[\"NOMBRE\"].isna().sum()}')\n"
    "print(f'\\nTop 10 valores de NOMBRE:')\n"
    "print(df_causa['NOMBRE'].value_counts().head(10).to_string())"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 8 — VERIFICACIÓN VM_ACC_VIA (Layer 6)
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 8 — Verificación VM_ACC_VIA (layer 6)\n"
    "\n"
    "En NB03, la muestra de 3 FORMULARIOs devolvió 0 registros para layer 6. "
    "Se investiga con una muestra más amplia y se decide si integrar o documentar "
    "como no disponible para el periodo 2020–2021."
))

cells.append(code(
    "# Sondear Layer 6 con muestra amplia\n"
    "N_SONDEO_VIA = min(50, len(formularios_top200))\n"
    "sample_via = formularios_top200[:N_SONDEO_VIA]\n"
    "forms_str_via = \"','\".join(sample_via)\n"
    "\n"
    "url_via = f'{BASE_URL}/{CAPAS[\"via\"]}/query'\n"
    "print(f'Sondeando Layer 6 (VM_ACC_VIA) con {N_SONDEO_VIA} FORMULARIOs...')\n"
    "\n"
    "try:\n"
    "    # Conteo\n"
    "    r_count = requests.post(\n"
    "        url_via,\n"
    "        data={'where': f\"FORMULARIO IN ('{forms_str_via}')\",\n"
    "              'returnCountOnly': 'true', 'f': 'json'},\n"
    "        timeout=30\n"
    "    )\n"
    "    count_via = r_count.json().get('count', 'ERROR')\n"
    "    print(f'  Conteo para {N_SONDEO_VIA} FORMULARIOs: {count_via}')\n"
    "\n"
    "    # Muestra de registros si hay datos\n"
    "    if isinstance(count_via, int) and count_via > 0:\n"
    "        r_sample = requests.post(\n"
    "            url_via,\n"
    "            data={'where': f\"FORMULARIO IN ('{forms_str_via}')\",\n"
    "                  'outFields': '*', 'resultRecordCount': 5, 'f': 'json'},\n"
    "            timeout=30\n"
    "        )\n"
    "        feats = r_sample.json().get('features', [])\n"
    "        df_via_muestra = pd.DataFrame([f['attributes'] for f in feats])\n"
    "        print(f'  Muestra de registros:')\n"
    "        print(df_via_muestra.to_string())\n"
    "        VIA_DISPONIBLE = True\n"
    "    else:\n"
    "        print('  Layer 6 devuelve 0 registros para la muestra de FORMULARIOs del Top 200.')\n"
    "        print('  Posible causa: los datos de VM_ACC_VIA para 2020–2021 no están en SIMUR,')\n"
    "        print('  o la clave FORMULARIO no aplica para esta capa.')\n"
    "        VIA_DISPONIBLE = False\n"
    "        # Verificar conteo total de la capa\n"
    "        r_total = requests.get(url_via, params={'where': '1=1', 'returnCountOnly': 'true', 'f': 'json'}, timeout=30)\n"
    "        total_via = r_total.json().get('count', 'ERROR')\n"
    "        print(f'  Registros totales en la capa (WHERE 1=1): {total_via}')\n"
    "\n"
    "except Exception as e:\n"
    "    print(f'  Error al consultar Layer 6: {e}')\n"
    "    VIA_DISPONIBLE = False\n"
    "\n"
    "print(f'\\nDecisión — VM_ACC_VIA integrable: {VIA_DISPONIBLE}')\n"
    "if not VIA_DISPONIBLE:\n"
    "    print('  → Se documenta como L-8 (limitación) y se excluye del enriquecimiento.')"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 9 — JOIN Y MODA POR ZONA
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 9 — Join y moda por zona\n"
    "\n"
    "Para cada zona del Top 200 se obtienen los FORMULARIOs de sus siniestros, "
    "se filtran los registros descargados de cada capa, y se calcula la **moda** "
    "del campo de interés. También se reporta la cobertura real (% de FORMULARIOs "
    "con registro en cada capa)."
))

cells.append(code(
    "def moda_serie(serie):\n"
    "    \"\"\"Retorna la moda (más frecuente, excluyendo nulos).\"\"\"\n"
    "    s = serie.dropna()\n"
    "    if s.empty:\n"
    "        return None\n"
    "    return s.value_counts().index[0]\n"
    "\n"
    "\n"
    "def agregar_por_zona(df_capa, campo_valor, zona_a_forms):\n"
    "    \"\"\"\n"
    "    Para cada zona en zona_a_forms, extrae registros del capa DataFrame\n"
    "    y calcula la moda del campo_valor.\n"
    "    Retorna dict {zona: (moda, cobertura_pct)}.\n"
    "    \"\"\"\n"
    "    # Índice rápido: FORMULARIO → lista de valores\n"
    "    form_vals = df_capa.groupby(CAMPO_JOIN)[campo_valor].apply(list).to_dict()\n"
    "\n"
    "    resultado = {}\n"
    "    for zona, forms in zona_a_forms.items():\n"
    "        todos_vals = []\n"
    "        forms_con_dato = 0\n"
    "        for f in forms:\n"
    "            vals = form_vals.get(f, [])\n"
    "            if vals:\n"
    "                forms_con_dato += 1\n"
    "                todos_vals.extend(vals)\n"
    "        cobertura = forms_con_dato / len(forms) * 100 if forms else 0\n"
    "        moda_val = Counter(v for v in todos_vals if v is not None\n"
    "                           and str(v).strip() not in ('', 'nan', 'None')\n"
    "                           ).most_common(1)\n"
    "        resultado[zona] = {\n"
    "            'moda': moda_val[0][0] if moda_val else None,\n"
    "            'n_registros': len(todos_vals),\n"
    "            'cobertura_pct': round(cobertura, 1),\n"
    "        }\n"
    "    return resultado\n"
    "\n"
    "\n"
    "print('Funciones de agregación definidas ✅')"
))

cells.append(code(
    "# Agregar las tres capas por zona\n"
    "print('Calculando moda por zona para cada capa...\\n')\n"
    "\n"
    "t0 = time.time()\n"
    "resultado_actor    = agregar_por_zona(df_actor,   CAMPO_ACTOR,    zona_a_forms)\n"
    "resultado_vehiculo = agregar_por_zona(df_vehiculo, CAMPO_VEHICULO, zona_a_forms)\n"
    "resultado_causa    = agregar_por_zona(df_causa,   CAMPO_CAUSA,    zona_a_forms)\n"
    "print(f'Agregación completada en {time.time()-t0:.1f}s')\n"
    "\n"
    "# Reporte de cobertura\n"
    "def resumen_cobertura(resultado, nombre):\n"
    "    coberturas = [v['cobertura_pct'] for v in resultado.values()]\n"
    "    print(f'  {nombre:<16}: cobertura promedio {np.mean(coberturas):.1f}% '\n"
    "          f'| min {min(coberturas):.1f}% | med {np.median(coberturas):.1f}%')\n"
    "\n"
    "print('\\nCobertura de FORMULARIO por capa:')\n"
    "resumen_cobertura(resultado_actor,    'actor_vial (L3)')\n"
    "resumen_cobertura(resultado_vehiculo, 'vehiculo   (L5)')\n"
    "resumen_cobertura(resultado_causa,    'causa      (L4)')\n"
    "\n"
    "# Modas más frecuentes globales\n"
    "print('\\nModas globales (Top 5):')\n"
    "for nombre, resultado, campo in [\n"
    "    ('CONDICION (actor)',   resultado_actor,    'actor_vial'),\n"
    "    ('CLASE (vehículo)',    resultado_vehiculo, 'vehiculo'),\n"
    "    ('NOMBRE (causa)',      resultado_causa,    'causa'),\n"
    "]:\n"
    "    conteo = Counter(v['moda'] for v in resultado.values() if v['moda'])\n"
    "    top5 = conteo.most_common(5)\n"
    "    print(f'  {nombre}:')\n"
    "    for val, cnt in top5:\n"
    "        print(f'    {val:<35} → {cnt:>3} zonas ({cnt/len(resultado)*100:.1f}%)')"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 10 — ENRIQUECIMIENTO DEL DATAFRAME
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 10 — Enriquecimiento del DataFrame de hotspots\n"
    "\n"
    "Se añaden las columnas `actor_predominante`, `vehiculo_predominante` y "
    "`causa_predominante` al DataFrame de clasificación de hotspots "
    "(`clasificacion_hotspots_persistencia_notebook_03.csv`).\n"
    "\n"
    "Solo las 200 zonas del Top 200 reciente reciben estos valores; "
    "el resto queda como `NaN`."
))

cells.append(code(
    "# Construir DataFrame auxiliar con las modas\n"
    "rows_enriq = []\n"
    "for zona, forms in zona_a_forms.items():\n"
    "    lat, lon = zona\n"
    "    rows_enriq.append({\n"
    "        'lat_grid': lat,\n"
    "        'lon_grid': lon,\n"
    "        'actor_predominante':    resultado_actor.get(zona,    {}).get('moda'),\n"
    "        'vehiculo_predominante': resultado_vehiculo.get(zona, {}).get('moda'),\n"
    "        'causa_predominante':    resultado_causa.get(zona,    {}).get('moda'),\n"
    "        'n_siniestros_zona':     len(forms),\n"
    "        'cobertura_actor_pct':    resultado_actor.get(zona,    {}).get('cobertura_pct'),\n"
    "        'cobertura_vehiculo_pct': resultado_vehiculo.get(zona, {}).get('cobertura_pct'),\n"
    "        'cobertura_causa_pct':    resultado_causa.get(zona,    {}).get('cobertura_pct'),\n"
    "    })\n"
    "\n"
    "df_enriq = pd.DataFrame(rows_enriq)\n"
    "print(f'DataFrame de enriquecimiento: {len(df_enriq)} zonas')\n"
    "\n"
    "# Merge con la clasificación completa\n"
    "df_hotspots_enr = df_clasificacion.merge(\n"
    "    df_enriq,\n"
    "    on=['lat_grid', 'lon_grid'],\n"
    "    how='left'\n"
    ")\n"
    "\n"
    "# También merge con top200 para tener IPI_rec y rank\n"
    "df_hotspots_enr = df_hotspots_enr.merge(\n"
    "    df_top200[['lat_grid', 'lon_grid', 'rank_IPI', 'IPI', 'familia_analitica']]\n"
    "            .rename(columns={'rank_IPI': 'rank_IPI_rec_top200',\n"
    "                             'IPI': 'IPI_rec_top200',\n"
    "                             'familia_analitica': 'familia_top200'}),\n"
    "    on=['lat_grid', 'lon_grid'],\n"
    "    how='left'\n"
    ")\n"
    "\n"
    "zonas_enriquecidas = df_hotspots_enr['actor_predominante'].notna().sum()\n"
    "print(f'Zonas con datos de enriquecimiento: {zonas_enriquecidas}')\n"
    "print(f'\\nColumnas del DataFrame final:')\n"
    "print(df_hotspots_enr.columns.tolist())\n"
    "print(f'\\nEjemplo (primeras 5 zonas enriquecidas):')\n"
    "cols_show = ['lat_grid','lon_grid','categoria_persistencia',\n"
    "             'actor_predominante','vehiculo_predominante','causa_predominante']\n"
    "print(df_hotspots_enr[df_hotspots_enr['actor_predominante'].notna()][cols_show].head().to_string())"
))

cells.append(code(
    "# Guardar outputs\n"
    "df_hotspots_enr.to_csv(PATH_HOTSPOTS_ENR, index=False)\n"
    "print(f'Guardado: {PATH_HOTSPOTS_ENR}')\n"
    "print(f'  {len(df_hotspots_enr):,} filas × {df_hotspots_enr.shape[1]} columnas')\n"
    "\n"
    "# Tabla resumen por categoría de persistencia\n"
    "print('\\nResumen por categoría de persistencia (Top 200):')\n"
    "df_top200_enr = df_hotspots_enr[df_hotspots_enr['actor_predominante'].notna()].copy()\n"
    "resumen_cat = df_top200_enr.groupby('categoria_persistencia').agg(\n"
    "    n_zonas=('lat_grid', 'count'),\n"
    "    actor_top=('actor_predominante', lambda x: x.value_counts().index[0] if len(x) > 0 else None),\n"
    "    vehiculo_top=('vehiculo_predominante', lambda x: x.value_counts().index[0] if len(x) > 0 else None),\n"
    "    causa_top=('causa_predominante', lambda x: x.value_counts().index[0] if len(x) > 0 else None),\n"
    ").reset_index()\n"
    "print(resumen_cat.to_string(index=False))"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 11 — MAPA INTERACTIVO
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 11 — Mapa interactivo enriquecido\n"
    "\n"
    "Mapa Folium con las 200 zonas del Top 200 reciente. "
    "Cada punto muestra en el popup: rank IPI, IPI, categoría de persistencia, "
    "actor predominante, vehículo predominante y causa predominante."
))

cells.append(code(
    "# Paleta de colores por categoría de persistencia\n"
    "COLOR_CATEGORIA = {\n"
    "    'Persistente':              'darkred',\n"
    "    'Emergente':                'orange',\n"
    "    'Disminuido':               'green',\n"
    "    'Sin categoría prioritaria': 'gray',\n"
    "}\n"
    "\n"
    "# Centrar el mapa en Bogotá\n"
    "mapa = folium.Map(location=[4.65, -74.1], zoom_start=12, tiles='CartoDB positron')\n"
    "\n"
    "df_mapa = df_hotspots_enr[df_hotspots_enr['actor_predominante'].notna()].copy()\n"
    "\n"
    "for _, row in df_mapa.iterrows():\n"
    "    cat  = row.get('categoria_persistencia', 'Sin categoría prioritaria')\n"
    "    color = COLOR_CATEGORIA.get(cat, 'gray')\n"
    "\n"
    "    popup_html = (\n"
    "        f\"<b>Zona #{int(row['rank_IPI_rec_top200']) if pd.notna(row.get('rank_IPI_rec_top200')) else '—'}</b><br>\"\n"
    "        f\"IPI reciente: {row.get('IPI_rec_top200', '—'):.1f}<br>\"\n"
    "        f\"Categoría: <b>{cat}</b><br>\"\n"
    "        f\"Familia: {row.get('familia_top200', '—')}<br>\"\n"
    "        f\"<hr style='margin:4px 0'>\"\n"
    "        f\"🧍 Actor: <b>{row.get('actor_predominante', '—')}</b><br>\"\n"
    "        f\"🚗 Vehículo: <b>{row.get('vehiculo_predominante', '—')}</b><br>\"\n"
    "        f\"⚠️ Causa: <b>{row.get('causa_predominante', '—')}</b><br>\"\n"
    "        f\"Siniestros en zona: {int(row['n_siniestros_zona']) if pd.notna(row.get('n_siniestros_zona')) else '—'}\"\n"
    "    )\n"
    "\n"
    "    folium.CircleMarker(\n"
    "        location=[row['lat_grid'], row['lon_grid']],\n"
    "        radius=7,\n"
    "        color=color,\n"
    "        fill=True,\n"
    "        fill_color=color,\n"
    "        fill_opacity=0.7,\n"
    "        popup=folium.Popup(popup_html, max_width=300),\n"
    "        tooltip=f\"#{int(row['rank_IPI_rec_top200']) if pd.notna(row.get('rank_IPI_rec_top200')) else '—'} | {cat[:15]}\",\n"
    "    ).add_to(mapa)\n"
    "\n"
    "# Leyenda\n"
    "legend_html = '''\n"
    "<div style=\"position:fixed; bottom:30px; left:30px; z-index:1000;\n"
    "     background:white; padding:10px; border:1px solid #ccc; border-radius:5px;\n"
    "     font-size:13px; line-height:1.8\">\n"
    "  <b>Categoría de persistencia</b><br>\n"
    "  <span style='color:darkred'>●</span> Persistente<br>\n"
    "  <span style='color:orange'>●</span> Emergente<br>\n"
    "  <span style='color:green'>●</span> Disminuido<br>\n"
    "  <span style='color:gray'>●</span> Sin categoría prioritaria\n"
    "</div>\n"
    "'''\n"
    "mapa.get_root().html.add_child(folium.Element(legend_html))\n"
    "\n"
    "mapa.save(PATH_MAPA_ENR)\n"
    "print(f'Mapa guardado: {PATH_MAPA_ENR}')\n"
    "mapa"
))

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 12 — MANIFIESTO Y RESUMEN EJECUTIVO
# ════════════════════════════════════════════════════════════════════════════
cells.append(md(
    "## Sección 12 — Manifiesto y resumen ejecutivo\n"
    "\n"
    "Se registran los outputs generados y se redacta el resumen metodológico del notebook."
))

cells.append(code(
    "# Manifiesto de outputs NB04\n"
    "outputs_nb04 = [\n"
    "    ('data/raw', PATH_ACTOR_RAW.name,    'VM_ACC_ACTOR_VIAL descargado para Top 200'),\n"
    "    ('data/raw', PATH_VEHICULO_RAW.name, 'VM_ACC_VEHICULO descargado para Top 200'),\n"
    "    ('data/raw', PATH_CAUSA_RAW.name,    'VM_ACC_CAUSA descargado para Top 200'),\n"
    "    ('outputs/reports', PATH_HOTSPOTS_ENR.name,\n"
    "     'Hotspots clasificación + actor/vehículo/causa predominante'),\n"
    "    ('outputs/maps',    PATH_MAPA_ENR.name,\n"
    "     'Mapa interactivo con popup enriquecido por zona'),\n"
    "    ('outputs/reports', PATH_RESUMEN_EJ.name,\n"
    "     'Resumen ejecutivo NB04 (texto metodológico)'),\n"
    "]\n"
    "\n"
    "rows_manifest = []\n"
    "print('Outputs NB04:\\n')\n"
    "for carpeta, nombre, descripcion in outputs_nb04:\n"
    "    ruta_abs = PROJECT_ROOT / carpeta / nombre\n"
    "    existe = ruta_abs.exists()\n"
    "    tam_kb = ruta_abs.stat().st_size // 1024 if existe else 0\n"
    "    estado = '✅' if existe else '⚠️ ausente'\n"
    "    print(f'  {estado}  {carpeta}/{nombre}')\n"
    "    print(f'       {descripcion} ({tam_kb} KB)')\n"
    "    rows_manifest.append({\n"
    "        'notebook': 'NB04',\n"
    "        'carpeta': carpeta,\n"
    "        'archivo': nombre,\n"
    "        'descripcion': descripcion,\n"
    "        'existe': existe,\n"
    "        'tam_kb': tam_kb,\n"
    "        'fecha_verificacion': datetime.now().strftime('%Y-%m-%d %H:%M'),\n"
    "    })\n"
    "\n"
    "df_manifest = pd.DataFrame(rows_manifest)\n"
    "ruta_manifest = REPORTS / 'manifiesto_outputs_notebook_04.csv'\n"
    "df_manifest.to_csv(ruta_manifest, index=False)\n"
    "print(f'\\nManifiesto guardado: {ruta_manifest}')"
))

cells.append(code(
    "# Resumen ejecutivo\n"
    "n_enriq      = df_hotspots_enr['actor_predominante'].notna().sum()\n"
    "actor_top    = df_top200_enr['actor_predominante'].value_counts()\n"
    "vehiculo_top = df_top200_enr['vehiculo_predominante'].value_counts()\n"
    "causa_top    = df_top200_enr['causa_predominante'].value_counts()\n"
    "\n"
    "cob_actor    = df_top200_enr['cobertura_actor_pct'].mean()\n"
    "cob_vehiculo = df_top200_enr['cobertura_vehiculo_pct'].mean()\n"
    "cob_causa    = df_top200_enr['cobertura_causa_pct'].mean()\n"
    "\n"
    "resumen_md = f'''# Resumen ejecutivo — Notebook 04\n"
    "## VíaSegura AI | Enriquecimiento actor vial, vehículo y causa\n"
    "\n"
    "**Fecha:** {datetime.now().strftime('%Y-%m-%d')}  \n"
    "**Periodo de análisis:** 2020–2021 (reciente)  \n"
    "**Zonas enriquecidas:** {n_enriq} de {TOP_N} Top 200 reciente\n"
    "\n"
    "## Cobertura de datos\n"
    "\n"
    "| Capa | Layer | Cobertura promedio |\n"
    "|---|---|---|\n"
    "| VM_ACC_ACTOR_VIAL | 3 | {cob_actor:.1f}% |\n"
    "| VM_ACC_VEHICULO | 5 | {cob_vehiculo:.1f}% |\n"
    "| VM_ACC_CAUSA | 4 | {cob_causa:.1f}% |\n"
    "| VM_ACC_VIA | 6 | No integrable (0 registros) |\n"
    "\n"
    "## Actor vial predominante (Top 5 entre zonas)\n"
    "\n"
    "{actor_top.head(5).to_markdown()}\n"
    "\n"
    "## Vehículo predominante (Top 5)\n"
    "\n"
    "{vehiculo_top.head(5).to_markdown()}\n"
    "\n"
    "## Causa predominante (Top 5)\n"
    "\n"
    "{causa_top.head(5).to_markdown()}\n"
    "\n"
    "## Limitaciones\n"
    "\n"
    "- VM_ACC_VIA (layer 6) no devuelve registros para los FORMULARIOs del periodo reciente — excluida.\n"
    "- La moda es un estimador central; zonas con distribución equiprobable pueden tener empates.\n"
    "- La cobertura <100% en capas hermanas implica que algunos siniestros no tienen actor/vehículo/causa registrado.\n"
    "- Los datos son registros policiales administrativos, no reconstrucciones de accidente.\n"
    "\n"
    "## Próximo paso\n"
    "\n"
    "**NB05 — Normalización por exposición:** calcular tasas de siniestralidad\n"
    "por 10,000 habitantes (DANE) y por km de red vial (OSM),\n"
    "para distinguir zonas con muchos siniestros por alta exposición\n"
    "vs. zonas con alta accidentalidad relativa.\n"
    "'''\n"
    "\n"
    "with open(PATH_RESUMEN_EJ, 'w', encoding='utf-8') as f:\n"
    "    f.write(resumen_md)\n"
    "print(f'Resumen ejecutivo guardado: {PATH_RESUMEN_EJ}')\n"
    "print()\n"
    "print(resumen_md)"
))

# ════════════════════════════════════════════════════════════════════════════
# BUILD NOTEBOOK JSON
# ════════════════════════════════════════════════════════════════════════════
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "version": "3.11.0"
        }
    },
    "cells": cells
}

output_path = Path(__file__).resolve().parent.parent / 'notebooks' / '04_enriquecimiento_actor_vehiculo_causa.ipynb'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print(f'Notebook generado: {output_path}')
print(f'  {len(cells)} celdas ({sum(1 for c in cells if c["cell_type"]=="code")} código, '
      f'{sum(1 for c in cells if c["cell_type"]=="markdown")} markdown)')
