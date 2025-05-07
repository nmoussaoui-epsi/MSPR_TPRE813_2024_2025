from typing import Optional, Tuple
import pandas as pd

DEPARTEMENT_MAP = {
    "ain": "01", "aisne": "02", "alpes-maritimes": "06", "bouches-du-rhône": "13",
    "charente-maritime": "17", "côte-d'or": "21", "finistère": "29", "haute-garonne": "31",
    "gironde": "33", "hérault": "34", "isère": "38", "loire-atlantique": "44",
    "meurthe-et-moselle": "54", "nord": "59", "oise": "60", "pas-de-calais": "62",
    "rhône": "69", "paris": "75", "var": "83", "la réunion": "974"
}

def extract_from_label(raw_label: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrait (libellé_simplifié, code_departement) à partir de 'Libellé'"""
    parts = raw_label.strip().lower().split(" - ")
    if len(parts) < 2:
        return None, None
    dep_name = parts[-1]
    libelle = " - ".join(parts[:-1])
    for nom_dep, code in DEPARTEMENT_MAP.items():
        if nom_dep == dep_name:
            return libelle.strip().capitalize(), code
    return libelle.strip().capitalize(), None

def is_value_file(filename: str) -> bool:
    return "valeurs" in filename.lower()

def is_trimestriel(annee: str) -> bool:
    return "-t" in annee.lower()

def interpolate_missing_years(df: pd.DataFrame, year_col: str, value_col: str, target_years: list) -> pd.DataFrame:
    """
    Remplit les années manquantes par interpolation linéaire ou extrapolation si nécessaire.
    """
    df = df.copy()
    df = df[[year_col, value_col]]
    df = df[df[year_col].notna()]
    df[year_col] = df[year_col].astype(int)
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

    df = df.set_index(year_col).sort_index()
    df = df.reindex(range(min(target_years), max(target_years) + 1))
    df[value_col] = df[value_col].interpolate(method="linear", limit_direction="both")
    df = df.loc[target_years]
    df = df.reset_index().rename(columns={"index": year_col})

    return df