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
    names=["code_departement", "annee"]  # "annee" sans accent
).to_frame(index=False)

# Fusion avec les vraies données
final_df = pd.merge(
    grille_complete, 
    final_df, 
    how="left", 
    left_on=["code_departement", "annee"],
    right_on=["code_departement", "année"]
)

# Nettoyer les colonnes pour n'avoir qu'une seule colonne annee
if "année" in final_df.columns:
    # Si la colonne année existe, l'utiliser pour remplir les valeurs manquantes dans annee
    if "annee" in final_df.columns:
        # Conserver les valeurs de annee et supprimer année
        final_df.drop(columns=["année"], inplace=True)
    else:
        # Renommer année en annee
        final_df.rename(columns={"année": "annee"}, inplace=True)
    
# Vérifier et corriger les colonnes doublées suite au merge
if "annee_x" in final_df.columns and "annee_y" in final_df.columns:
    # Combiner les deux colonnes en une seule
    final_df["annee"] = final_df["annee_x"].combine_first(final_df["annee_y"])
    final_df.drop(columns=["annee_x", "annee_y"], inplace=True)

# Sélectionner uniquement les 3 colonnes voulues dans le bon ordre
final_df = final_df[["code_departement", "annee", "nombre_auteurs_poursuivables"]]

# Sauvegarder
final_df.to_csv(os.path.join(output_dir, "criminalite_2002_2022.csv"), index=False)


print("✅ Nettoyage terminé : data/clean/criminalite_2002_2022.csv")
