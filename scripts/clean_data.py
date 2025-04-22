from data_utils import (
    get_raw_path, get_clean_path,
    standardize_columns, filter_election_years,
    save_clean_data, ELECTION_YEARS
)
import pandas as pd
import os

def clean_chomage():
    """Nettoie les données de chômage"""
    input_dir = get_raw_path("chomage")
    all_data = []

    for file in os.listdir(input_dir):
        if file.endswith(".csv") and file.startswith("chomage_"):
            code_dept = file.replace("chomage_", "").replace(".csv", "")
            path = os.path.join(input_dir, file)

            df = pd.read_csv(path)
            df = standardize_columns(df)

            if "année" in df.columns and "taux_chomage" in df.columns:
                df = df[["année", "taux_chomage"]].copy()
                df["code_departement"] = code_dept

                # Extraire l'année depuis le format 2022-Q1
                df["annee"] = df["année"].str.extract(r"^(\d{4})")
                df = df.dropna(subset=["annee"])
                df["annee"] = df["annee"].astype(int)

                # Garder uniquement les années électorales
                df = df[df["annee"].isin(ELECTION_YEARS)]

                # Moyenne par département et année
                df["taux_chomage"] = pd.to_numeric(df["taux_chomage"], errors="coerce")
                df = df.dropna(subset=["taux_chomage"])
                df = df.groupby(["code_departement", "annee"], as_index=False)["taux_chomage"].mean()

                all_data.append(df)

    # Fusionner et sauvegarder
    final_df = pd.concat(all_data)
    final_df = final_df.sort_values(["code_departement", "annee"])
    save_clean_data(final_df, "chomage_2002_2022.csv")

def clean_criminalite():
    """Nettoie les données de criminalité"""
    input_dir = get_raw_path("criminalite")
    all_data = []

    for file in os.listdir(input_dir):
        if file.endswith(".csv") and file.startswith("criminalite_"):
            code_dept = file.replace("criminalite_", "").replace(".csv", "")
            path = os.path.join(input_dir, file)

            df = pd.read_csv(path)
            df = standardize_columns(df)

            if "année" in df.columns and "nombre_auteurs_poursuivables" in df.columns:
                df = df[["année", "nombre_auteurs_poursuivables"]].copy()
                df["code_departement"] = code_dept
                df = filter_election_years(df)
                all_data.append(df)

    # Fusionner tous les départements
    final_df = pd.concat(all_data, ignore_index=True)

    # Créer la grille complète (20 départements x 5 années)
    departements = final_df["code_departement"].unique()
    grille_complete = pd.MultiIndex.from_product(
        [departements, ELECTION_YEARS],
        names=["code_departement", "annee"]
    ).to_frame(index=False)

    # Fusion avec les vraies données
    final_df = pd.merge(
        grille_complete, 
        final_df, 
        how="left", 
        left_on=["code_departement", "annee"],
        right_on=["code_departement", "année"]
    )

    # Nettoyer les colonnes
    if "année" in final_df.columns:
        final_df.drop(columns=["année"], inplace=True)
    
    if "annee_x" in final_df.columns and "annee_y" in final_df.columns:
        final_df["annee"] = final_df["annee_x"].combine_first(final_df["annee_y"])
        final_df.drop(columns=["annee_x", "annee_y"], inplace=True)

    # Sélectionner les colonnes finales
    final_df = final_df[["code_departement", "annee", "nombre_auteurs_poursuivables"]]
    save_clean_data(final_df, "criminalite_2002_2022.csv")

def clean_elections():
    """Nettoie les données d'élections"""
    input_dir = get_raw_path("elections")
    all_data = []

    for file in os.listdir(input_dir):
        if file.endswith(".csv") and file.startswith("elections_"):
            code_dept = file.replace("elections_", "").replace(".csv", "")
            path = os.path.join(input_dir, file)

            df = pd.read_csv(path)
            df = standardize_columns(df)

            if "année" in df.columns and "taux_abstention" in df.columns:
                df = df[["année", "taux_abstention"]].copy()
                df["code_departement"] = code_dept
                df = filter_election_years(df)
                all_data.append(df)

    final_df = pd.concat(all_data)
    save_clean_data(final_df, "elections_2002_2022.csv")

def clean_logements():
    """Nettoie les données de logements sociaux"""
    input_dir = get_raw_path("logements")
    all_data = []

    for file in os.listdir(input_dir):
        if file.endswith(".csv") and file.startswith("logements_"):
            code_dept = file.replace("logements_", "").replace(".csv", "")
            path = os.path.join(input_dir, file)

            df = pd.read_csv(path)
            df = standardize_columns(df)

            if "année" in df.columns and "nombre_logements_sociaux" in df.columns:
                df = df[["année", "nombre_logements_sociaux"]].copy()
                df["code_departement"] = code_dept
                df = filter_election_years(df)
                all_data.append(df)

    final_df = pd.concat(all_data)
    save_clean_data(final_df, "logements_sociaux_2002_2022.csv")

def run_all_cleaning():
    """Exécute tous les processus de nettoyage"""
    print("Début du nettoyage des données...")
    clean_chomage()
    clean_criminalite()
    clean_elections()
    clean_logements()
    print("✅ Tous les nettoyages sont terminés")

if __name__ == "__main__":
    run_all_cleaning()
