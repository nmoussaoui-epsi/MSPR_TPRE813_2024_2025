import pandas as pd
import os

# Répertoires
input_dir = "../data/raw/chomage"
output_dir = "../data/clean"
os.makedirs(output_dir, exist_ok=True)

# Liste pour stocker tous les DataFrames
all_data = []

# Liste des années électorales à garder
annees_cibles = [2002, 2007, 2012, 2017, 2022]

# Boucle sur les fichiers
for file in os.listdir(input_dir):
    if file.endswith(".csv") and file.startswith("chomage_"):
        code_dept = file.replace("chomage_", "").replace(".csv", "")
        path = os.path.join(input_dir, file)

        df = pd.read_csv(path)
        df.columns = df.columns.str.lower().str.strip()

        if "année" in df.columns and "taux_chomage" in df.columns:
            df = df[["année", "taux_chomage"]].copy()
            df["code_departement"] = code_dept

            # Extraire l'année depuis le format 2022-Q1
            df["annee"] = df["année"].str.extract(r"^(\d{4})")
            df = df.dropna(subset=["annee"])
            df["annee"] = df["annee"].astype(int)

            # Garder uniquement les années électorales
            df = df[df["annee"].isin(annees_cibles)]

            # Moyenne par département et année
            df["taux_chomage"] = pd.to_numeric(df["taux_chomage"], errors="coerce")
            df = df.dropna(subset=["taux_chomage"])
            df = df.groupby(["code_departement", "annee"], as_index=False)["taux_chomage"].mean()

            all_data.append(df)

# Fusionner tout
final_df = pd.concat(all_data)
final_df = final_df.sort_values(["code_departement", "annee"])
final_df.to_csv(os.path.join(output_dir, "chomage_2002_2022.csv"), index=False)

print("✅ Nettoyage terminé : data/clean/chomage_2002_2022.csv")
