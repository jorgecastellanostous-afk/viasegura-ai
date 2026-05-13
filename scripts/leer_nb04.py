import pandas as pd

df = pd.read_csv(r"C:\Users\jorge\Documents\viasegura_ai\outputs\reports\hotspots_enriquecidos_nb04.csv")
enr = df[df["actor_predominante"].notna()].copy()
print("=== HOTSPOTS ENRIQUECIDOS NB04 ===")
print("Total zonas en clasificacion:", len(df))
print("Zonas Top 200 enriquecidas:", len(enr))
print()
print("--- Actor predominante (Top 5) ---")
print(enr["actor_predominante"].value_counts().head(5).to_string())
print()
print("--- Vehiculo predominante (Top 5) ---")
print(enr["vehiculo_predominante"].value_counts().head(5).to_string())
print()
print("--- Causa predominante (Top 5) ---")
print(enr["causa_predominante"].value_counts().head(5).to_string())
print()
print("--- Por categoria persistencia ---")
res = enr.groupby("categoria_persistencia").agg(
    n=("lat_grid","count"),
    actor=("actor_predominante", lambda x: x.value_counts().index[0]),
    vehiculo=("vehiculo_predominante", lambda x: x.value_counts().index[0]),
    causa=("causa_predominante", lambda x: x.value_counts().index[0])
).reset_index()
print(res.to_string(index=False))
print()
print("--- Cobertura FORMULARIO ---")
print("  Actor:   ", round(enr["cobertura_actor_pct"].mean(),1), "%")
print("  Vehiculo:", round(enr["cobertura_vehiculo_pct"].mean(),1), "%")
print("  Causa:   ", round(enr["cobertura_causa_pct"].mean(),1), "%")
