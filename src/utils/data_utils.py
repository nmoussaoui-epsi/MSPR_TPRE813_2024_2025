import re
import unicodedata
import pandas as pd
import numpy as np
from typing import Optional, Tuple
from sklearn.linear_model import LinearRegression
from pathlib import Path
from src.utils.constantes import BORD_MAP, DEPARTEMENT_MAP


def is_value_file(filename: str) -> bool:
    return "valeurs" in filename.lower()


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


def is_trimestriel(annee: str) -> bool:
    return "-t" in annee.lower()


def predict_missing_years(
    df: pd.DataFrame,
    year_col: str,
    value_col: str,
    target_years: list,
    force_clip_upper_100: bool = False
) -> pd.DataFrame:
    df2 = df[[year_col, value_col]].dropna().copy()
    df2[year_col] = df2[year_col].astype(int)
    df2[value_col] = pd.to_numeric(df2[value_col], errors="coerce")
    df2 = df2.sort_values(year_col)

    years = df2[year_col].to_numpy()
    vals = df2[value_col].to_numpy()

    if len(years) == 0:
        return pd.DataFrame({year_col: target_years, value_col: [None]*len(target_years)})
    if len(years) == 1:
        flat = int(vals[0])
        return pd.DataFrame({year_col: target_years, value_col: [flat]*len(target_years)})

    y0, v0 = years[0], vals[0]
    y1, v1 = years[1], vals[1]
    slope_left = (v1 - v0) / (y1 - y0)

    model = LinearRegression().fit(years.reshape(-1, 1), vals)

    out = []
    for y in target_years:
        if y in years:
            v = df2.loc[df2[year_col] == y, value_col].iloc[0]
        else:
            v_glob = model.predict(np.array([[y]]))[0]
            if y < y0 and v_glob <= 0:
                v = v0 + slope_left * (y - y0)
            else:
                v = v_glob

        v = max(v, 0)
        if force_clip_upper_100:
            v = min(v, 99)

        out.append(int(round(v)))

    return pd.DataFrame({year_col: target_years, value_col: out})


def clean_nom(nom: str) -> str:
    if not isinstance(nom, str):
        return ""
    # Nettoyage agressif
    nom = nom.strip()
    nom = nom.replace('"', '').replace("'", '').replace("’", '').replace("‘", '').replace("`", "")
    nom = unicodedata.normalize("NFD", nom)
    nom = nom.encode("ascii", "ignore").decode("utf-8")
    nom = nom.replace("-", " ")
    nom = re.sub(r"[^\w\s]", "", nom)
    nom = re.sub(r"\s+", " ", nom)  # espaces multiples → un seul espace
    return nom.strip().upper()

def normalize_departement_label(label: str) -> str:
    label = label.strip().lower()
    label = ''.join(
        c for c in unicodedata.normalize('NFD', label)
        if unicodedata.category(c) != 'Mn'
    )
    label = label.replace("'", "").replace("-", " ")
    return label

def parse_election_file(path: Path, annee: int, tour: int) -> pd.DataFrame:
    try:
        if annee in {2002, 2007, 2012}:
            df = pd.read_csv(path, encoding="utf-8", sep=",", dtype=str)
            dept_col = df.columns[1]
            return extract_data_from_voix(df, annee, tour, dept_col, "Exprimés")

        elif annee == 2017:
            df = pd.read_csv(path, encoding="utf-8", skiprows=3, dtype=str)
            dept_col = "Code du département"
            return extract_data_from_voix(df, annee, tour, dept_col, "Exprimés")

        elif annee == 2022:
            df = pd.read_csv(path, encoding="utf-8", dtype=str)
            dept_col = "Code du département"
            return extract_data_from_voix(df, annee, tour, dept_col, "Exprimés")

    except Exception as e:
        print(f"[ERREUR] Fichier {path.name} : {e}")

    return pd.DataFrame(columns=[
        "code_departement", "bord", "score", "annee", "tour"
    ])


def extract_data_from_voix(df: pd.DataFrame, annee: int, tour: int,
                           dept_col: str, exprim_col: str) -> pd.DataFrame:
    rows = []

    try:
        if tour == 2 and annee in {2017, 2022}:
            for _, row in df.iterrows():
                try:
                    code = str(row[dept_col]).replace(".0", "").strip().zfill(2)
                    if code == "ZD":
                        code = "974"

                    exprim = float(str(row[exprim_col]).replace(",", ".").replace(" ", ""))
                    if exprim == 0:
                        continue

                    nom1 = clean_nom(row["Nom"])
                    prenom1 = clean_nom(row["Prénom"])
                    full1 = f"{nom1} {prenom1}".strip()
                    voix1 = float(str(row["Voix"]).replace(",", ".").replace(" ", ""))
                    bord1 = BORD_MAP.get(full1)

                    if bord1:
                        rows.append({
                            "code_departement": code,
                            "bord": bord1,
                            "voix": voix1,
                            "exprim": exprim,
                            "annee": annee,
                            "tour": tour
                        })

                    nom2 = clean_nom(row.get("Unnamed: 28", ""))
                    prenom2 = clean_nom(row.get("Unnamed: 29", ""))
                    full2 = f"{nom2} {prenom2}".strip()
                    voix2 = float(str(row.get("Unnamed: 30", "0")).replace(",", ".").replace(" ", ""))
                    bord2 = BORD_MAP.get(full2)

                    if bord2:
                        rows.append({
                            "code_departement": code,
                            "bord": bord2,
                            "voix": voix2,
                            "exprim": exprim,
                            "annee": annee,
                            "tour": tour
                        })
                except Exception:
                    continue

        else:
            base = df.columns.get_loc("Sexe")
            nb_cand = (len(df.columns) - base) // 6

            for i in range(nb_cand):
                nom_col = df.columns[base + i * 6 + 1]
                prenom_col = df.columns[base + i * 6 + 2]
                voix_col = df.columns[base + i * 6 + 3]

                for _, row in df.iterrows():
                    try:
                        code = str(row[dept_col]).replace(".0", "").strip().zfill(2)
                        if code == "ZD":
                            code = "974"

                        nom = clean_nom(row[nom_col])
                        prenom = clean_nom(row[prenom_col])
                        full = f"{nom} {prenom}".strip()

                        voix = float(str(row[voix_col]).replace(",", ".").replace(" ", ""))
                        exprim = float(str(row[exprim_col]).replace(",", ".").replace(" ", ""))
                        bord = BORD_MAP.get(full)
                        if not bord:
                            continue

                        rows.append({
                            "code_departement": code,
                            "bord": bord,
                            "voix": voix,
                            "exprim": exprim,
                            "annee": annee,
                            "tour": tour
                        })
                    except Exception:
                        continue
    except Exception:
        pass

    if not rows:
        return pd.DataFrame(columns=["code_departement", "bord", "score", "annee", "tour"])

    df_rows = pd.DataFrame(rows)
    agg = df_rows.groupby(["code_departement", "bord", "annee", "tour"], as_index=False).sum()
    agg["score"] = (agg["voix"] / agg["exprim"] * 100).round(2)

    return agg[["code_departement", "bord", "score", "annee", "tour"]]
