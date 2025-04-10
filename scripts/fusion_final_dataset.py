import pandas as pd
import os

# Chemin d'entrée
data_dir = "../data/clean"

# Lecture des fichiers
elections = pd.read_csv(os.path.join(data_dir, "elections_2002_2022.csv"))
chomage = pd.read_csv(os.path.join(data_dir, "chomage_2002_2022.csv"))
criminalite = pd.read_csv(os.path.join(data_dir, "criminalite_2002_2022.csv"))
pauvrete = pd.read_csv(os.path.join(data_dir, "pauvrete_2002_2022.csv"))
population = pd.read_csv(os.path.join(data_dir, "population_2002_2022.csv"))
revenu = pd.read_csv(os.path.join(data_dir, "revenu_2002_2022.csv"))
logements = pd.read_csv(os.path.join(data_dir, "logements_sociaux_2002_2022.csv"))

# Fusion progressive sur code_departement et annee
base = elections.copy()

# Ajout des autres datasets par merge
base = base.merge(chomage, on=["code_departement", "annee"], how="left")
base = base.merge(criminalite, on=["code_departement", "annee"], how="left")
base = base.merge(pauvrete, on=["code_departement", "annee"], how="left")
base = base.merge(population, on=["code_departement", "annee"], how="left")
base = base.merge(revenu, on=["code_departement", "annee"], how="left")
base = base.merge(logements, on=["code_departement", "annee"], how="left")

# Création du dossier final s'il n'existe pas
new_data_dir = "../data/final"
os.makedirs(new_data_dir, exist_ok=True)

# Sauvegarde du fichier final
output_path = os.path.join(new_data_dir, "final_dataset.csv")
base.to_csv(output_path, index=False)

print(f"✅ Fichier final généré : {output_path}")

