import pandas as pd
import os

# Fichiers
input_file = "../data/raw/logements/logements_sociaux.csv"
output_dir = "../data/clean"
os.makedirs(output_dir, exist_ok=True)

# Années d'élections
annees_cibles = [2002, 2007, 2012, 2017, 2022]

# Départements utilisés dans le projet
departements_cibles = [
    "01", "02", "06", "13", "17", "21", "29", "31", "33", "34",
    "38", "44", "54", "59", "60", "62", "69", "75", "83", "974"
]

# Charger le fichier brut (point-virgule)
df = pd.read_csv(input_file, sep=";", encoding="utf-8")

# 🧹 Garde les colonnes utiles
df_clean = df[[
    "année_publication",
    "code_departement",
    "Parc social - Nombre de logements"
]].copy()

# Renommer pour standardiser
df_clean.columns = ["annee", "code_departement", "logements_sociaux"]

# Filtrer sur années et départements souhaités
df_clean = df_clean[df_clean["annee"].isin(annees_cibles)]
df_clean = df_clean[df_clean["code_departement"].isin(departements_cibles)]

# Convertir types
df_clean["annee"] = df_clean["annee"].astype(int)
df_clean["logements_sociaux"] = pd.to_numeric(df_clean["logements_sociaux"], errors="coerce")

# Créer grille complète des combinaisons
grille_complete = pd.MultiIndex.from_product(
    [departements_cibles, annees_cibles],
    names=["code_departement", "annee"]
).to_frame(index=False)

# Fusion pour garder NaN si données absentes
df_final = pd.merge(grille_complete, df_clean, how="left", on=["code_departement", "annee"])
df_final = df_final.sort_values(["code_departement", "annee"])

# Sauvegarder
df_final.to_csv(os.path.join(output_dir, "logements_sociaux_2002_2022.csv"), index=False)

print("✅ Nettoyage terminé avec 20 départements : data/clean/logements_sociaux_2002_2022.csv")
