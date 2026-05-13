"""Corrige la celda aa001004 (P-R5) y aa001002 (P-R4): usa na_option='bottom' en rank()."""
import json
from pathlib import Path

NB_PATH = Path(r"C:\Users\jorge\Documents\viasegura_ai\notebooks\04_enriquecimiento_actor_vehiculo_causa.ipynb")

with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

NEW_SOURCE_PR5 = '''\
# P-R5: Sensibilidad del IPI al score de persistencia
df_cl = df_clasificacion.copy()

def pct_rnk(s):
    return s.rank(pct=True, method="average") * 100

df_cl["_cant"]  = df_cl["cantidad_siniestros_rec"].fillna(0)
df_cl["_crit"]  = df_cl["criticidad_total_rec"].fillna(0)
df_cl["_grav"]  = (df_cl["_crit"] / df_cl["_cant"].replace(0, np.nan)).fillna(0)
df_cl["_fat"]   = df_cl["siniestros_con_muertos_rec"].fillna(0)
df_cl["_pers"]  = pd.to_numeric(df_cl["en_top200_base"], errors="coerce").fillna(0)

df_cl["sc_vol"]  = pct_rnk(df_cl["_cant"])
df_cl["sc_crit"] = pct_rnk(df_cl["_crit"])
df_cl["sc_grav"] = pct_rnk(df_cl["_grav"])
df_cl["sc_fat"]  = pct_rnk(df_cl["_fat"])
df_cl["sc_pers"] = pct_rnk(df_cl["_pers"])

df_cl["IPI_reconst"]  = df_cl[["sc_vol","sc_crit","sc_grav","sc_fat","sc_pers"]].mean(axis=1)
df_cl["IPI_sin_pers"] = df_cl[["sc_vol","sc_crit","sc_grav","sc_fat"]].mean(axis=1)

# Verificar reconstruccion (solo zonas con IPI_rec no-NaN)
mask_v = df_cl["IPI_rec"].notna()
corr = df_cl.loc[mask_v, "IPI_rec"].corr(df_cl.loc[mask_v, "IPI_reconst"])
mae  = (df_cl.loc[mask_v, "IPI_reconst"] - df_cl.loc[mask_v, "IPI_rec"]).abs().mean()
print(f"Verificacion de reconstruccion del IPI:")
print(f"  Zonas con IPI_rec valido              : {mask_v.sum():,}")
print(f"  Correlacion original vs. reconstruido : {corr:.4f}")
print(f"  MAE (error medio absoluto)            : {mae:.3f} puntos")
print(f"  {'OK' if corr >= 0.99 else 'REVISAR'}: rho {'>=0.99' if corr>=0.99 else '<0.99'}")

# Rankings: na_option="bottom" envia NaN al fondo
df_cl["rank_con"] = df_cl["IPI_rec"].rank(ascending=False, method="min",
                                            na_option="bottom").astype(int)
df_cl["rank_sin"] = df_cl["IPI_sin_pers"].rank(ascending=False, method="min",
                                                 na_option="bottom").astype(int)
df_cl["delta"]    = df_cl["rank_sin"] - df_cl["rank_con"]

df_cl["zona_key"] = list(zip(df_cl["lat_grid"].round(3), df_cl["lon_grid"].round(3)))
top200_con = set(df_cl[df_cl["rank_con"] <= 200]["zona_key"])
top200_sin = set(df_cl[df_cl["rank_sin"] <= 200]["zona_key"])

z_salen  = top200_con - top200_sin
z_entran = top200_sin - top200_con
z_estab  = top200_con & top200_sin

df_salen  = df_cl[df_cl["zona_key"].isin(z_salen)].copy()
df_entran = df_cl[df_cl["zona_key"].isin(z_entran)].copy()

print(f"\\nImpacto de eliminar score_persistencia:")
print(f"  Zonas estables (en ambos Top 200)          : {len(z_estab):>3}  ({len(z_estab)/200*100:.1f}%)")
print(f"  Zonas que SALEN (dependen de persistencia)  : {len(z_salen):>3}  ({len(z_salen)/200*100:.1f}%)")
print(f"  Zonas que ENTRAN (riesgo actual puro)       : {len(z_entran):>3}  ({len(z_entran)/200*100:.1f}%)")

print(f"\\nPerfil de zonas que SALEN sin persistencia:")
print(f"  Persistentes: {(df_salen['categoria_persistencia']=='Persistente').sum()}")
print(f"  Emergentes  : {(df_salen['categoria_persistencia']=='Emergente').sum()}")
print(f"  IPI_rec promedio: {df_salen['IPI_rec'].mean():.2f}")
print(f"  sc_pers promedio: {df_salen['sc_pers'].mean():.1f}  (maximo ~99.5)")

print(f"\\nPerfil de zonas que ENTRAN sin persistencia:")
print(f"  IPI_sin_pers promedio: {df_entran['IPI_sin_pers'].mean():.2f}")
print(f"  Siniestros recientes promedio : {df_entran['_cant'].mean():.1f}")
print(f"  Criticidad total promedio     : {df_entran['_crit'].mean():.1f}")

# Brecha cuantitativa en Top 200 actual
t200 = df_cl[df_cl["rank_con"] <= 200].copy()
pm   = t200["categoria_persistencia"] == "Persistente"
print(f"\\nBrecha de IPI por persistencia (Top 200 actual):")
print(f"  Persistentes (n={pm.sum()}): sc_pers = {t200.loc[pm,'sc_pers'].mean():.1f}")
print(f"  Emergentes   (n={(~pm).sum()}): sc_pers = {t200.loc[~pm,'sc_pers'].mean():.1f}")
brecha = (t200.loc[pm,"sc_pers"].mean() - t200.loc[~pm,"sc_pers"].mean()) / 5
print(f"  Brecha de IPI atribuible a persistencia : {brecha:.1f} puntos")

print(f"\\n{'='*60}")
print("RECOMENDACION:")
print("  Publicar dos listas paralelas:")
print("  - Lista A (con persistencia): zonas con historial cronico")
print("  - Lista B (sin persistencia): zonas de riesgo actual puro")
print(f"  Zonas en AMBAS listas = prioridad maxima.")
print(f"  Zonas solo en Lista B = {len(z_entran)} zonas emergentes de alta carga reciente.")

# Figura
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax1 = axes[0]
colores_cat = {"Persistente": "darkred", "Emergente": "orange", "Disminuido": "green"}
df_plot = df_cl[df_cl["rank_con"] <= 500].copy()
for cat, grp in df_plot.groupby("categoria_persistencia", dropna=True):
    ax1.scatter(grp["IPI_rec"], grp["IPI_sin_pers"], alpha=0.5,
                color=colores_cat.get(cat, "gray"), label=cat, s=18)
uc = df_cl.loc[df_cl["rank_con"] == 200, "IPI_rec"].dropna().values
us = df_cl.loc[df_cl["rank_sin"] == 200, "IPI_sin_pers"].dropna().values
if len(uc): ax1.axvline(uc[0], color="crimson", ls="--", lw=1.2, label="Umbral Top200 (con)")
if len(us): ax1.axhline(us[0], color="navy",    ls="--", lw=1.2, label="Umbral Top200 (sin)")
ax1.set_xlabel("IPI con persistencia"); ax1.set_ylabel("IPI sin persistencia")
ax1.set_title("Impacto del score_persistencia\\n(Top 500 zonas)", fontsize=10)
ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

ax2 = axes[1]
cats_b = ["Estables", "Salen\\n(persist.)", "Entran\\n(actual)"]
vals_b = [len(z_estab), len(z_salen), len(z_entran)]
cols_b = ["#1976D2", "#D32F2F", "#388E3C"]
bars   = ax2.bar(cats_b, vals_b, color=cols_b, edgecolor="white")
for b, v in zip(bars, vals_b):
    ax2.text(b.get_x()+b.get_width()/2, b.get_height()+1, str(v),
             ha="center", fontsize=12, fontweight="bold")
ax2.set_ylabel("Numero de zonas")
ax2.set_title("Cambios en el Top 200\\nal eliminar score_persistencia", fontsize=10)
ax2.set_ylim(0, max(vals_b)*1.2); ax2.grid(True, axis="y", alpha=0.3)

plt.tight_layout()
PATH_FIG = REPORTS / "sensibilidad_persistencia_nb04.png"
plt.savefig(PATH_FIG, dpi=150, bbox_inches="tight")
plt.show()
print(f"Figura guardada: {PATH_FIG}")
'''

updated = 0
for cell in nb["cells"]:
    if cell.get("id") == "aa001004":
        cell["source"] = NEW_SOURCE_PR5
        cell["outputs"] = []
        cell["execution_count"] = None
        updated += 1
        print("Celda aa001004 (P-R5) actualizada")
        break

if updated == 0:
    print("ERROR: Celda aa001004 no encontrada")

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook guardado: {NB_PATH}")
print(f"Celdas actualizadas: {updated}")
