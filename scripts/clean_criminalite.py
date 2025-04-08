import pandas as pd
import os

# Répertoires d'entrée et de sortie
input_dir = "../data/raw/criminalite"
output_dir = "../data/clean"
os.makedirs(output_dir, exist_ok=True)

# Années électorales
annees_cibles = [2002, 2007, 2012, 2017, 2022]

# Liste pour stocker les DataFrames départementaux
all_data = []

# Lire les fichiers criminalité
for file in os.listdir(input_dir):
    if file.endswith(".csv") and file.startswith("criminalite_"):
        code_dept = file.replace("criminalite_", "").replace(".csv", "")
        path = os.path.join(input_dir, file)

        df = pd.read_csv(path)
        df.columns = df.columns.str.lower().str.strip()

        if "année" in df.columns and "nombre_auteurs_poursuivables" in df.columns:
            df = df[["année", "nombre_auteurs_poursuivables"]].copy()
            df["code_departement"] = code_dept

            df = df[df["année"].isin(annees_cibles)]

            all_data.append(df)

# Fusionner tous les départements
final_df = pd.concat(all_data, ignore_index=True)

# Créer la grille complète (20 départements x 5 années)
departements = final_df["code_departement"].unique()
grille_complete = pd.MultiIndex.from_product(
    [departements, annees_cibles],
    names=["code_departement", "année"]
).to_frame(index=False)

# Fusion avec les vraies données
final_df = pd.merge(grille_complete, final_df, how="left", on=["code_departement", "année"])

# Sauvegarder
final_df.to_csv(os.path.join(output_dir, "criminalite_2002_2022.csv"), index=False)


print("✅ Nettoyage terminé : data/clean/criminalite_2002_2022.csv")
