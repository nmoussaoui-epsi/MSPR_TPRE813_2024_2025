import os
import pandas as pd

# Constantes communes
ELECTION_YEARS = [2002, 2007, 2012, 2017, 2022]
BASE_DATA_DIR = "../data"

def ensure_dir_exists(dir_path):
    """Crée un répertoire s'il n'existe pas"""
    os.makedirs(dir_path, exist_ok=True)

def get_raw_path(data_type):
    """Retourne le chemin vers les données brutes pour un type donné"""
    return os.path.join(BASE_DATA_DIR, "raw", data_type)

def get_clean_path():
    """Retourne le chemin vers les données nettoyées"""
    return os.path.join(BASE_DATA_DIR, "clean")

def standardize_columns(df):
    """Standardise les noms de colonnes"""
    df.columns = df.columns.str.lower().str.strip()
    return df

def filter_election_years(df, year_col="année"):
    """Filtre les données pour ne garder que les années électorales"""
    if year_col in df.columns:
        df = df[df[year_col].isin(ELECTION_YEARS)]
    return df

def save_clean_data(df, filename):
    """Sauvegarde les données nettoyées"""
    output_path = os.path.join(get_clean_path(), filename)
    df.to_csv(output_path, index=False)
    print(f"✅ Données sauvegardées : {output_path}")
    return output_path
