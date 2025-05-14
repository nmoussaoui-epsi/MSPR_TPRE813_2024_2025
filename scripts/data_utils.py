from typing import Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import unicodedata
import re

# Liste des départements gérés
DEPARTEMENT_MAP = {
    "ain": "01", "aisne": "02", "alpes-maritimes": "06", "bouches-du-rhône": "13",
    "charente-maritime": "17", "côte-d'or": "21", "finistère": "29", "haute-garonne": "31",
    "gironde": "33", "hérault": "34", "isère": "38", "loire-atlantique": "44",
    "meurthe-et-moselle": "54", "nord": "59", "oise": "60", "pas-de-calais": "62",
    "rhône": "69", "paris": "75", "var": "83", "la réunion": "974"
}

def extract_criterion_and_departement(raw_label: str) -> Tuple[Optional[str], Optional[str]]:
    parts = raw_label.strip().lower().split(" - ")
    if len(parts) < 2:
        return None, None

    dep_name = parts[-1].strip()
    criterion = " - ".join(parts[:-1]).strip().capitalize()

    for nom_dep, code in DEPARTEMENT_MAP.items():
        if nom_dep in dep_name:
            return criterion, code

    if "ville de paris" in dep_name:
        return criterion, "75"

    return criterion, None

def is_value_file(filename: str) -> bool:
    return "valeurs" in filename.lower()

def is_trimestriel(annee: str) -> bool:
    return "-t" in annee.lower()

def predict_missing_years(
    df: pd.DataFrame,
    year_col: str,
    value_col: str,
    target_years: list,
    force_clip_upper_100: bool = False
) -> pd.DataFrame:
    """
    Remplit target_years en :
      - vraie valeur si présente,
      - sinon prédiction par régression linéaire globale,
        avec fallback à l'extrapolation à partir des 2 premiers points
        si la prédiction globale devient <= 0 pour y < min_known_year,
      - clamp bas à 0 ; clamp haut à 99 si force_clip_upper_100.
    """
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LinearRegression

    # Prépare et trie les points connus
    df2 = df[[year_col, value_col]].dropna().copy()
    df2[year_col] = df2[year_col].astype(int)
    df2[value_col] = pd.to_numeric(df2[value_col], errors="coerce")
    df2 = df2.sort_values(year_col)

    years = df2[year_col].to_numpy()
    vals  = df2[value_col].to_numpy()

    # 0 ou 1 point connus ?
    if len(years) == 0:
        return pd.DataFrame({year_col: target_years,
                             value_col: [None]*len(target_years)})
    if len(years) == 1:
        flat = int(vals[0])
        return pd.DataFrame({year_col: target_years,
                             value_col: [flat]*len(target_years)})

    # Calcul des pentes pour fallback local_linear
    y0, v0 = years[0],   vals[0]
    y1, v1 = years[1],   vals[1]
    slope_left = (v1 - v0) / (y1 - y0)

    # Entraîne la régression linéaire globale
    model = LinearRegression().fit(years.reshape(-1,1), vals)

    out = []
    for y in target_years:
        if y in years:
            # vraie valeur
            v = df2.loc[df2[year_col] == y, value_col].iloc[0]
        else:
            # prédiction globale
            v_glob = model.predict(np.array([[y]]))[0]

            if y < y0 and v_glob <= 0:
                # fallback : extrapolation linéaire à gauche
                v = v0 + slope_left * (y - y0)
            else:
                v = v_glob

        # clamp bas 0
        v = max(v, 0)
        # clamp haut si demandé (taux)
        if force_clip_upper_100:
            v = min(v, 99)

        out.append(int(round(v)))

    return pd.DataFrame({year_col: target_years, value_col: out})

def clean_nom(nom: str) -> str:
    if not isinstance(nom, str):
        return ""
    
    nom = nom.replace('"', '').replace("'", '').replace("’", '')
    nom = unicodedata.normalize("NFD", nom)
    nom = nom.encode("ascii", "ignore").decode("utf-8")
    nom = nom.replace("-", " ")
    nom = re.sub(r"[^\w\s]", "", nom)

    return nom.strip().upper()


def normalize_departement_label(label: str) -> str:
    """
    Supprime les accents, met en minuscules, normalise les espaces et tirets.
    Exemple : 'La Réunion' → 'la reunion', 'Côte-d'Or' → 'cote dor'
    """
    label = label.strip().lower()
    label = ''.join(
        c for c in unicodedata.normalize('NFD', label)
        if unicodedata.category(c) != 'Mn'
    )
    label = label.replace("'", "").replace("-", " ")
    return label
