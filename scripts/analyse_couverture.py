import pandas as pd
import os

# Charger le fichier final
file_path = "../data/final/final_dataset.csv"
df = pd.read_csv(file_path)

# Nombre total de lignes
total_rows = len(df)

# Calcul du taux de complétude pour chaque colonne (hors colonnes de clé)
colonnes_utiles = [col for col in df.columns if col not in ["code_departement", "annee", "nom_candidat", "tour"]]
couverture_par_colonne = df[colonnes_utiles].notna().sum() / total_rows

# Score global de couverture
score_global = round(couverture_par_colonne.mean() * 100, 2)

# Colonnes les moins bien remplies
colonnes_vides = couverture_par_colonne.sort_values().head(5)

# Résultats
print("📊 Analyse de la couverture du fichier final_dataset.csv")
print(f"🔢 Nombre total de lignes : {total_rows}")
print(f"✅ Score global de couverture des données : {score_global} %\n")

print("📉 Colonnes les moins remplies :")
for col, taux in colonnes_vides.items():
    print(f"  - {col} : {round(taux * 100, 2)} % de valeurs présentes")
