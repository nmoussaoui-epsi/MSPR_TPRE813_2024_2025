import os
import pandas as pd
from typing import Union, List

# Constantes communes
ELECTION_YEARS = [2002, 2007, 2012, 2017, 2022]
BASE_DATA_DIR = "../data"
DEPARTEMENTS = ["01", "02", "06", "13", "17", "21", "29", "31", "33", "34", 
               "38", "44", "54", "59", "60", "62", "69", "75", "83", "974"]

def ensure_dir_exists(dir_path: str) -> None:
    """Crée un répertoire s'il n'existe pas"""
    os.makedirs(dir_path, exist_ok=True)

def get_raw_path(data_type: str) -> str:
    """Retourne le chemin vers les données brutes pour un type donné"""
    return os.path.join(BASE_DATA_DIR, "raw", data_type)

def get_clean_path() -> str:
    """Retourne le chemin vers les données nettoyées"""
    return os.path.join(BASE_DATA_DIR, "clean")

def get_final_path() -> str:
    """Retourne le chemin vers les données finales"""
    return os.path.join(BASE_DATA_DIR, "final")

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise les noms de colonnes"""
    df.columns = df.columns.str.lower().str.strip()
    return df

def filter_election_years(df: pd.DataFrame, year_col: str = "année") -> pd.DataFrame:
    """Filtre les données pour ne garder que les années électorales"""
    if year_col in df.columns:
        df = df[df[year_col].isin(ELECTION_YEARS)]
    return df

def save_clean_data(df: pd.DataFrame, filename: str) -> str:
    """Sauvegarde les données nettoyées"""
    output_path = os.path.join(get_clean_path(), filename)
    df.to_csv(output_path, index=False)
    print(f"✅ Données sauvegardées : {output_path}")
    return output_path

def validate_departement(code: str) -> bool:
    """Vérifie si un code département est valide"""
    return code in DEPARTEMENTS

def get_data_types() -> List[str]:
    """Retourne la liste des types de données gérés"""
    return ["chomage", "criminalite", "elections", "logements", "pauvrete", "population", "revenu"]
