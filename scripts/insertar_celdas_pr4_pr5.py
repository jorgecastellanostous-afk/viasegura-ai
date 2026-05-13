"""Inserta las celdas P-R4 y P-R5 en NB04 después de la celda 020d3303."""
import json, uuid
from pathlib import Path

NB_PATH = Path(r"C:\Users\jorge\Documents\viasegura_ai\notebooks\04_enriquecimiento_actor_vehiculo_causa.ipynb")

with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

def new_cell(cell_type, source, cell_id=None):
    cid = cell_id or str(uuid.uuid4())[:8]
    cell = {"id": cid, "metadata": {}, "source": source}
    if cell_type == "markdown":
        cell["cell_type"] = "markdown"
    else:
        cell["cell_type"] = "code"
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell

# ── Contenido de las 4 celdas nuevas ─────────────────────────────────────────

MD_PR4 = """\
### 13.4 — P-R4: Zonas con causa accionable — sub-ranking de intervención

El 45% de las zonas del Top 200 tiene "OTRA" como causa principal, lo que impide
recomendar intervención concreta. Se clasifica la causa identificada por tipo de
intervención vial estándar y se genera un sub-ranking de **zonas donde SÍ hay diagnóstico
accionable** con medida específica (radar, semáforo, geometría, mantenimiento)."""

CODE_PR4 = '''\
# ── P-R4: Zonas con causa accionable ─────────────────────────────────────────
# Mapa de causas a categoría de intervención vial estándar
MAPA_INTERVENCIONES = {
    # Velocidad / distancia
    'NO MANTENER DISTANCIA DE SEGURIDAD': 'VELOCIDAD/DISTANCIA',
    'ADELANTAR CERRANDO':                 'VELOCIDAD/DISTANCIA',
    'EXCESO DE VELOCIDAD':                'VELOCIDAD/DISTANCIA',
    'ADELANTAR EN CURVA':                 'VELOCIDAD/DISTANCIA',
    'ADELANTAR EN DOBLE LÍNEA':           'VELOCIDAD/DISTANCIA',
    # Control semafórico
    'SEMÁFORO EN ROJO':                   'CONTROL_SEMAFÓRICO',
    'DESOBEDECER SEÑALES':                'CONTROL_SEMAFÓRICO',
    'NO RESPETAR SEMÁFORO':               'CONTROL_SEMAFÓRICO',
    # Maniobras peligrosas
    'TRANSITAR ENTRE VEHICULOS':          'MANIOBRA_PELIGROSA',
    'REVERSO IMPRUDENTE':                 'MANIOBRA_PELIGROSA',
    'NO RESPETAR PRELACIÓN':              'MANIOBRA_PELIGROSA',
    'PONER EN MARCHA UN VEHICULO SIN PRECAUCIONES': 'MANIOBRA_PELIGROSA',
    'TRANSITAR EN CONTRAVIA':             'MANIOBRA_PELIGROSA',
    # Infraestructura
    'HUECOS':                             'INFRAESTRUCTURA_VÍA',
    'SEÑALIZACIÓN DEFICIENTE':            'INFRAESTRUCTURA_VÍA',
    'VÍA EN MAL ESTADO':                  'INFRAESTRUCTURA_VÍA',
    # Alcohol
    'CONDUCIR BAJO EFECTOS DEL ALCOHOL':  'ALCOHOL/DROGAS',
    'CONDUCIR BAJO EFECTOS DE DROGAS':    'ALCOHOL/DROGAS',
}

NO_ACCIONABLE = {'OTRA', 'OTRAS', ''}

DESCRIP_INTERV = {
    'VELOCIDAD/DISTANCIA': 'Radar fijo/móvil, reductor de velocidad, señalización de distancia mínima',
    'CONTROL_SEMAFÓRICO':  'Cámara semafórica, resincronización de fase, rediseño de ciclo',
    'MANIOBRA_PELIGROSA':  'Separador físico, señalización horizontal, prohibición de maniobra',
    'INFRAESTRUCTURA_VÍA': 'Bacheo, mantenimiento de superficie, renovación señalización vertical',
    'ALCOHOL/DROGAS':      'Operativo nocturno, punto de control, campaña distrital',
}

def clasificar_causa(causa):
    if pd.isna(causa) or str(causa).strip().upper() in NO_ACCIONABLE:
        return None
    return MAPA_INTERVENCIONES.get(str(causa).strip().upper())

df_t = df_top200_enr.copy()
df_t['tipo_intervencion'] = df_t['causa_top1'].apply(clasificar_causa)

n_total       = len(df_t)
n_accionable  = df_t['tipo_intervencion'].notna().sum()
n_no_accion   = n_total - n_accionable

print('Accionabilidad de la causa principal (Top 200 zonas)')
print('─' * 50)
print(f'  Con causa accionable identificada : {n_accionable:>3} zonas  ({n_accionable/n_total*100:.1f}%)')
print(f'  Sin causa accionable (OTRA/OTRAS) : {n_no_accion:>3} zonas  ({n_no_accion/n_total*100:.1f}%)')

# Distribución por tipo de intervención
print()
print('Distribución por tipo de intervención:')
dist = df_t[df_t['tipo_intervencion'].notna()].groupby('tipo_intervencion').agg(
    n_zonas           = ('lat_grid', 'count'),
    rank_IPI_medio    = ('rank_IPI_rec_top200', 'mean'),
    pct_persistentes  = ('categoria_persistencia',
                         lambda x: (x == 'Persistente').mean() * 100),
    pct_moto_medio    = ('pct_motocicleta', 'mean'),
).sort_values('n_zonas', ascending=False)
print(dist.to_string())

print()
print('Descripción de cada tipo:')
for tip, desc in DESCRIP_INTERV.items():
    n = dist.loc[tip, 'n_zonas'] if tip in dist.index else 0
    print(f'  [{tip}] ({n} zonas): {desc}')

# Sub-ranking de zonas accionables
df_accionable = df_t[df_t['tipo_intervencion'].notna()].copy()
df_accionable = df_accionable.sort_values('rank_IPI_rec_top200')
print(f'\\nTop 15 zonas con causa accionable:')
cols_r = ['rank_IPI_rec_top200','lat_grid','lon_grid','categoria_persistencia',
          'tipo_intervencion','causa_top1','causa_top1_pct','vehiculo_predominante',
          'pct_motocicleta','pct_bus']
print(df_accionable.head(15)[cols_r].to_string(index=False))

# Guardar CSV
PATH_ACCIONABLE = REPORTS / 'top_zonas_accionables_nb04.csv'
df_accionable.to_csv(PATH_ACCIONABLE, index=False)
print(f'\\nGuardado: {PATH_ACCIONABLE}  ({len(df_accionable)} zonas)')

# ── Figura ──────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Pie: accionabilidad
ax1.pie(
    [n_accionable, n_no_accion],
    labels=[f'Causa accionable\\n({n_accionable} zonas)', f'OTRA / sin dato\\n({n_no_accion} zonas)'],
    colors=['#1976D2', '#BDBDBD'],
    autopct='%1.1f%%', startangle=90, pctdistance=0.75,
)
ax1.set_title('Accionabilidad de la causa\\nTop 200 zonas críticas', fontsize=11)

# Barras: tipo de intervención
colores_bar = ['#D32F2F', '#F57C00', '#1976D2', '#388E3C', '#7B1FA2']
interv_n = dist['n_zonas']
ax2.barh(interv_n.index, interv_n.values, color=colores_bar[:len(interv_n)])
ax2.set_xlabel('Número de zonas')
ax2.set_title('Tipo de intervención requerida\\n(zonas con causa identificada)', fontsize=11)
for i, v in enumerate(interv_n.values):
    ax2.text(v + 0.3, i, str(v), va='center', fontsize=9)
ax2.grid(True, axis='x', alpha=0.3)

plt.tight_layout()
PATH_FIG_INTERV = REPORTS / 'distribucion_intervenciones_nb04.png'
plt.savefig(PATH_FIG_INTERV, dpi=150, bbox_inches='tight')
plt.show()
print(f'Figura guardada: {PATH_FIG_INTERV}')
'''

MD_PR5 = """\
### 13.5 — P-R5: Sensibilidad del IPI al score de persistencia

Con n=2 periodos, el `score_persistencia` es efectivamente binario: una zona Persistente
recibe ~99.5 puntos y una Emergente ~49.5 puntos, una brecha de ~50 puntos que equivale
a **~10 puntos IPI** (1/5 del total). Se cuantifica el impacto eliminando ese componente
y se muestra qué zonas entran/salen del Top 200."""

CODE_PR5 = '''\
# ── P-R5: Sensibilidad del IPI al score de persistencia ──────────────────────

df_cl = df_clasificacion.copy()

def pct_rnk(s):
    return s.rank(pct=True, method='average') * 100

# Reconstruir los 5 componentes del IPI reciente
df_cl['_cant']  = df_cl['cantidad_siniestros_rec'].fillna(0)
df_cl['_crit']  = df_cl['criticidad_total_rec'].fillna(0)
df_cl['_grav']  = (df_cl['_crit'] / df_cl['_cant'].replace(0, np.nan)).fillna(0)
df_cl['_fat']   = df_cl['siniestros_con_muertos_rec'].fillna(0)
df_cl['_pers']  = pd.to_numeric(df_cl['en_top200_base'], errors='coerce').fillna(0)

df_cl['sc_vol']  = pct_rnk(df_cl['_cant'])
df_cl['sc_crit'] = pct_rnk(df_cl['_crit'])
df_cl['sc_grav'] = pct_rnk(df_cl['_grav'])
df_cl['sc_fat']  = pct_rnk(df_cl['_fat'])
df_cl['sc_pers'] = pct_rnk(df_cl['_pers'])

df_cl['IPI_reconst']  = df_cl[['sc_vol','sc_crit','sc_grav','sc_fat','sc_pers']].mean(axis=1)
df_cl['IPI_sin_pers'] = df_cl[['sc_vol','sc_crit','sc_grav','sc_fat']].mean(axis=1)

# Verificar reconstrucción
corr = df_cl['IPI_rec'].corr(df_cl['IPI_reconst'])
mae  = (df_cl['IPI_reconst'] - df_cl['IPI_rec']).abs().mean()
print(f'Verificación de reconstrucción del IPI:')
print(f'  Correlación original vs. reconstruido : {corr:.4f}')
print(f'  MAE (error medio absoluto)            : {mae:.3f} puntos')
if corr >= 0.99:
    print(f'  ✅ Reconstrucción aceptable (ρ ≥ 0.99)')
else:
    print(f'  ⚠️  Reconstrucción aproximada — verificar componentes NB02/NB03')

# Rankings
df_cl['rank_con'] = df_cl['IPI_rec'].rank(ascending=False, method='min').astype(int)
df_cl['rank_sin'] = df_cl['IPI_sin_pers'].rank(ascending=False, method='min').astype(int)
df_cl['delta']    = df_cl['rank_sin'] - df_cl['rank_con']  # positivo = baja sin persist.

df_cl['zona_key'] = list(zip(df_cl['lat_grid'].round(3), df_cl['lon_grid'].round(3)))
top200_con = set(df_cl[df_cl['rank_con'] <= 200]['zona_key'])
top200_sin = set(df_cl[df_cl['rank_sin'] <= 200]['zona_key'])

zonas_salen_k  = top200_con - top200_sin
zonas_entran_k = top200_sin - top200_con
estables_k     = top200_con & top200_sin

df_salen  = df_cl[df_cl['zona_key'].isin(zonas_salen_k)].copy()
df_entran = df_cl[df_cl['zona_key'].isin(zonas_entran_k)].copy()

print(f\'\\nImpacto de eliminar score_persistencia:\')
print(f\'  Zonas estables (en ambos Top 200)        : {len(estables_k):>3}  ({len(estables_k)/200*100:.1f}%)\')
print(f\'  Zonas que SALEN (dependen de persistencia): {len(zonas_salen_k):>3}  ({len(zonas_salen_k)/200*100:.1f}%)\')
print(f\'  Zonas que ENTRAN (riesgo actual puro)     : {len(zonas_entran_k):>3}  ({len(zonas_entran_k)/200*100:.1f}%)\')

print(f\'\\nPerfil de zonas que SALEN sin persistencia:\')
print(f\'  Persistentes: {(df_salen["categoria_persistencia"]=="Persistente").sum()}\')
print(f\'  Emergentes  : {(df_salen["categoria_persistencia"]=="Emergente").sum()}\')
print(f\'  IPI_rec promedio: {df_salen["IPI_rec"].mean():.2f}\')
print(f\'  sc_persistencia promedio: {df_salen["sc_pers"].mean():.1f}  (máximo posible ≈ 99.5)\')

print(f\'\\nPerfil de zonas que ENTRAN sin persistencia (riesgo actual puro):\')
print(f\'  IPI_sin_pers promedio : {df_entran["IPI_sin_pers"].mean():.2f}\')
print(f\'  Siniestros recientes promedio: {df_entran["_cant"].mean():.1f}\')
print(f\'  Criticidad total promedio: {df_entran["_crit"].mean():.1f}\')

# Impacto cuantitativo en Persistentes vs Emergentes
top200_rec = df_cl[df_cl[\'rank_con\'] <= 200].copy()
pers_mask  = top200_rec[\'categoria_persistencia\'] == \'Persistente\'
print(f\'\\nImpacto medio del score_persistencia en el IPI (Top 200):\')
print(f\'  Zonas Persistentes (n={pers_mask.sum()}): sc_pers = {top200_rec.loc[pers_mask,"sc_pers"].mean():.1f}\')
print(f\'  Zonas Emergentes   (n={(~pers_mask).sum()}): sc_pers = {top200_rec.loc[~pers_mask,"sc_pers"].mean():.1f}\')
brecha = (top200_rec.loc[pers_mask,"sc_pers"].mean() - top200_rec.loc[~pers_mask,"sc_pers"].mean()) / 5
print(f\'  Brecha de IPI atribuible a persistencia : {brecha:.1f} puntos\')

# Recomendación operativa
print(f\'\\n{"─"*60}\')
print(\'RECOMENDACIÓN (P-R5):\')
print(\'  Publicar SIEMPRE dos listas paralelas:\')
print(\'  • Lista A — IPI completo: zonas con historial crónico (incluye persistencia)\')
print(\'  • Lista B — IPI volumétrico: zonas de riesgo actual puro (sin persistencia)\')
print(\'  Zonas en AMBAS listas → prioridad máxima de intervención.\')
print(f\'  Zonas solo en Lista B → {len(zonas_entran_k)} zonas emergentes de alta carga reciente.\')

# ── Figura ──────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Panel izquierdo: scatter IPI_con vs IPI_sin (Top 500)
ax1 = axes[0]
colores_cat = {\'Persistente\': \'darkred\', \'Emergente\': \'orange\', \'Disminuido\': \'green\'}
df_plot = df_cl[df_cl[\'rank_con\'] <= 500].copy()
for cat, grp in df_plot.groupby(\'categoria_persistencia\', dropna=True):
    ax1.scatter(grp[\'IPI_rec\'], grp[\'IPI_sin_pers\'], alpha=0.5,
                color=colores_cat.get(cat, \'gray\'), label=cat, s=18)
# Líneas de corte
umbral_con = df_cl.loc[df_cl[\'rank_con\'] == 200, \'IPI_rec\'].values
umbral_sin = df_cl.loc[df_cl[\'rank_sin\'] == 200, \'IPI_sin_pers\'].values
if len(umbral_con): ax1.axvline(umbral_con[0], color=\'crimson\', ls=\'--\', lw=1.2, label=\'Umbral con pers.\')
if len(umbral_sin): ax1.axhline(umbral_sin[0], color=\'navy\', ls=\'--\', lw=1.2, label=\'Umbral sin pers.\')
ax1.set_xlabel(\'IPI con persistencia\'); ax1.set_ylabel(\'IPI sin persistencia\')
ax1.set_title(\'Impacto del score_persistencia\\n(Top 500 zonas)\', fontsize=10)
ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

# Panel derecho: cuántos salen/entran
ax2 = axes[1]
categorias_bar = [\'Estables\', \'Salen\\n(dependen\\npersist.)\', \'Entran\\n(riesgo\\nactual)\']
valores_bar    = [len(estables_k), len(zonas_salen_k), len(zonas_entran_k)]
colores_bar2   = [\'#1976D2\', \'#D32F2F\', \'#388E3C\']
bars = ax2.bar(categorias_bar, valores_bar, color=colores_bar2, edgecolor=\'white\')
for bar, v in zip(bars, valores_bar):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             str(v), ha=\'center\', fontsize=12, fontweight=\'bold\')
ax2.set_ylabel(\'Número de zonas\')
ax2.set_title(f\'Cambios en el Top 200\\nal eliminar score_persistencia\', fontsize=10)
ax2.set_ylim(0, max(valores_bar) * 1.2)
ax2.grid(True, axis=\'y\', alpha=0.3)

plt.tight_layout()
PATH_FIG_PERS = REPORTS / \'sensibilidad_persistencia_nb04.png\'
plt.savefig(PATH_FIG_PERS, dpi=150, bbox_inches=\'tight\')
plt.show()
print(f\'Figura guardada: {PATH_FIG_PERS}\')
'''

# ── Insertar celdas después de 020d3303 ───────────────────────────────────────
nuevas = [
    new_cell("markdown", MD_PR4, "aa001001"),
    new_cell("code",     CODE_PR4, "aa001002"),
    new_cell("markdown", MD_PR5, "aa001003"),
    new_cell("code",     CODE_PR5, "aa001004"),
]

# Encontrar índice de la celda 020d3303
idx_ref = next(i for i, c in enumerate(nb["cells"]) if c.get("id") == "020d3303")
print(f"Celda de referencia '020d3303' encontrada en índice {idx_ref}")

for i, celda in enumerate(nuevas):
    nb["cells"].insert(idx_ref + 1 + i, celda)
    print(f"  Insertada celda '{celda['id']}' ({celda['cell_type']}) en posición {idx_ref+1+i}")

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\nNotebook actualizado: {NB_PATH}")
print(f"Total de celdas ahora: {len(nb['cells'])}")
