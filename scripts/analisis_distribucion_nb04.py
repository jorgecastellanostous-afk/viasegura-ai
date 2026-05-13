import pandas as pd
import numpy as np

# Cargar datos crudos descargados
df_actor    = pd.read_csv(r"C:\Users\jorge\Documents\viasegura_ai\data\raw\actor_vial_top200_reciente.csv")
df_vehiculo = pd.read_csv(r"C:\Users\jorge\Documents\viasegura_ai\data\raw\vehiculo_top200_reciente.csv")
df_causa    = pd.read_csv(r"C:\Users\jorge\Documents\viasegura_ai\data\raw\causa_top200_reciente.csv")

print("=== DISTRIBUCION REAL DE ACTORES (todos los registros, no solo moda) ===")
print(df_actor["CONDICION"].value_counts(normalize=True).mul(100).round(1).to_string())

print()
print("=== DISTRIBUCION REAL DE VEHICULOS ===")
print(df_vehiculo["CLASE"].value_counts(normalize=True).mul(100).round(1).to_string())
print()
print("Conteos absolutos:")
print(df_vehiculo["CLASE"].value_counts().to_string())

print()
print("=== DISTRIBUCION REAL DE CAUSAS ===")
print(df_causa["NOMBRE"].value_counts(normalize=True).mul(100).round(1).to_string())

print()
print("=== ZONAS CON MOTOCICLETA COMO VEHICULO PREDOMINANTE ===")
df_enr = pd.read_csv(r"C:\Users\jorge\Documents\viasegura_ai\outputs\reports\hotspots_enriquecidos_nb04.csv")
enr = df_enr[df_enr["vehiculo_predominante"].notna()]
moto_zones = enr[enr["vehiculo_predominante"] == "MOTOCICLETA"]
auto_zones  = enr[enr["vehiculo_predominante"] == "AUTOMOVIL"]
print(f"Zonas con moda MOTOCICLETA: {len(moto_zones)} ({len(moto_zones)/len(enr)*100:.1f}%)")
print(f"Zonas con moda AUTOMOVIL:   {len(auto_zones)} ({len(auto_zones)/len(enr)*100:.1f}%)")

# Cuantas zonas tienen motos como 2do vehiculo?
print()
print("=== SEGUNDA FRECUENCIA DE VEHICULO POR ZONA (moto como 2do?) ===")
# Cargar accidentes recientes para hacer join
df_acc = pd.read_csv(r"C:\Users\jorge\Documents\viasegura_ai\data\processed\accidentes_bogota_reciente_limpio.csv", low_memory=False)
df_top200 = pd.read_csv(r"C:\Users\jorge\Documents\viasegura_ai\outputs\reports\top200_IPI_reciente_notebook_03.csv")

df_acc["lat_grid"] = df_acc["LATITUD"].round(3)
df_acc["lon_grid"] = df_acc["LONGITUD"].round(3)
zonas_top200 = set(zip(df_top200["lat_grid"].round(3), df_top200["lon_grid"].round(3)))
df_acc_top = df_acc[df_acc.apply(lambda r: (r["lat_grid"], r["lon_grid"]) in zonas_top200, axis=1)]
forms_top200 = set(df_acc_top["FORMULARIO"])

df_veh_top = df_vehiculo[df_vehiculo["FORMULARIO"].isin(forms_top200)]
print(f"Registros de vehiculo en Top 200: {len(df_veh_top):,}")
print()
print("Distribucion de CLASE en Top 200 (todos los registros):")
dist = df_veh_top["CLASE"].value_counts()
total = len(df_veh_top)
for clase, cnt in dist.head(8).items():
    bar = "#" * int(cnt/total*40)
    print(f"  {clase:<20} {cnt:>5} ({cnt/total*100:>5.1f}%)  {bar}")
