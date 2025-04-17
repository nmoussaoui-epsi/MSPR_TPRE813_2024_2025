import pandas as pd
import os

# === Dossiers ===
data_dir = "../data/clean"
output_dir = "../data/final"
os.makedirs(output_dir, exist_ok=True)

# === Chargement des fichiers ===
elections = pd.read_csv(os.path.join(data_dir, "elections_2002_2022.csv"))
chomage = pd.read_csv(os.path.join(data_dir, "chomage_2002_2022.csv"))
criminalite = pd.read_csv(os.path.join(data_dir, "criminalite_2002_2022.csv"))
pauvrete = pd.read_csv(os.path.join(data_dir, "pauvrete_2002_2022.csv"))
population = pd.read_csv(os.path.join(data_dir, "population_2002_2022.csv"))
revenu = pd.read_csv(os.path.join(data_dir, "revenu_2002_2022.csv"))
logements = pd.read_csv(os.path.join(data_dir, "logements_sociaux_2002_2022.csv"))

# === Mapping nom_candidat → bord_politique ===
bord_map = {
    "MACRON EMMANUEL": "centre",
    "LE PEN MARINE": "extreme_droite",
    "LE PEN JEAN MARIE": "extreme_droite",
    "MELENCHON JEAN LUC": "gauche",
    "HOLLANDE FRANCOIS": "gauche",
    "SARKOZY NICOLAS": "droite",
    "ROYAL SEGOLENE": "gauche",
    "CHIRAC JACQUES": "droite",
    "BAYROU FRANCOIS": "centre",
    "JOSPIN LIONEL": "gauche",
    "FILLON FRANCOIS": "droite",
    "HAMON BENOIT": "gauche",
    "BESANCENOT OLIVIER": "gauche",
    "LAGUILLER ARLETTE": "gauche",
    "CHEVENEMENT JEAN-PIERRE": "gauche",
    "GLUCKSTEIN DANIEL": "gauche",
    "MEGRET BRUNO": "extreme_droite",
    "DE VILLIERS PHILIPPE": "droite",
    "BUFFET MARIE-GEORGE": "gauche",
    "POUTOU PHILIPPE": "gauche",
    "ARTHAUD NATHALIE": "gauche",
    "ASSELINEAU FRANCOIS": "extreme_droite",
    "DUPONT-AIGNAN NICOLAS": "droite",
    "LASSALLE JEAN": "centre"
}

# Ajout du bord politique
elections["bord_politique"] = elections["nom_candidat"].map(bord_map)
elections = elections.dropna(subset=["bord_politique"])

# Agrégation des scores par bord politique
scores = elections.groupby(["code_departement", "annee", "bord_politique"])["score"].sum().reset_index()

# Pour chaque département + année, garder le bord gagnant (max score)
gagnants = scores.sort_values("score", ascending=False).groupby(["code_departement", "annee"]).first().reset_index()
gagnants = gagnants.rename(columns={"score": "resultat"})

# Fusion avec les indicateurs
df = gagnants.merge(chomage, on=["code_departement", "annee"], how="left")
df = df.merge(criminalite, on=["code_departement", "annee"], how="left")
df = df.merge(pauvrete, on=["code_departement", "annee"], how="left")
df = df.merge(population, on=["code_departement", "annee"], how="left")
df = df.merge(revenu, on=["code_departement", "annee"], how="left")
df = df.merge(logements, on=["code_departement", "annee"], how="left")

# Colonnes finales strictement demandées
df = df[[
    "code_departement",
    "bord_politique",
    "resultat",
    "annee",
    "taux_chomage",
    "nombre_auteurs_poursuivables",
    "taux_pauvrete",
    "population",
    "revenu_median",
    "logements_sociaux"
]]

# Sauvegarde
output_path = os.path.join(output_dir, "final_dataset_clean.csv")
df.to_csv(output_path, index=False)

print(f"✅ Dataset nettoyé et réduit à 100 lignes → {output_path}")
