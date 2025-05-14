import pandas as pd
from pathlib import Path
import numpy as np
from data_utils import DEPARTEMENT_MAP, clean_nom 
from data_utils import (
    extract_criterion_and_departement,
    is_value_file,
    predict_missing_years
)

BORD_MAP = {
    "MACRON EMMANUEL":           "centre",
    "LE PEN MARINE":             "extreme_droite",
    "LE PEN JEAN MARIE":         "extreme_droite",
    "MELENCHON JEAN LUC":        "gauche",
    "HOLLANDE FRANCOIS":         "gauche",
    "SARKOZY NICOLAS":           "droite",
    "ROYAL SEGOLENE":            "gauche",
    "CHIRAC JACQUES":            "droite",
    "BAYROU FRANCOIS":           "centre",
    "JOSPIN LIONEL":             "gauche",
    "FILLON FRANCOIS":           "droite",
    "HAMON BENOIT":              "gauche",
    "BESANCENOT OLIVIER":        "gauche",
    "LAGUILLER ARLETTE":         "gauche",
    "CHEVENEMENT JEAN-PIERRE":   "gauche",
    "GLUCKSTEIN DANIEL":         "gauche",
    "MEGRET BRUNO":              "extreme_droite",
    "DE VILLIERS PHILIPPE":      "droite",
    "BUFFET MARIE-GEORGE":       "gauche",
    "POUTOU PHILIPPE":           "gauche",
    "ARTHAUD NATHALIE":          "gauche",
    "ASSELINEAU FRANCOIS":       "extreme_droite",
    "DUPONT-AIGNAN NICOLAS":     "droite",
    "LASSALLE JEAN":             "centre",
}

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

TARGET_YEARS = [2002, 2007, 2012, 2017, 2022]


def process_population():
    print("📦 Traitement des données de population...")
    RAW_DIR = BASE_DIR / "data" / "raw" / "population"
    criteres_data = {}

    for file in RAW_DIR.glob("*.csv"):
        if not is_value_file(file.name):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            libelle_line = next((line for line in lines if "Libellé" in line), None)
            if not libelle_line:
                print(f"⚠️ Pas de libellé dans {file.name}")
                continue

            raw_label = libelle_line.split(";")[1].strip('" \n')
            critere, dep_code = extract_criterion_and_departement(raw_label)

            if not dep_code:
                if "ville de paris" in raw_label.lower():
                    dep_code = "75"
                else:
                    print(f"⚠️ Département non reconnu pour {file.name} → {raw_label}")
                    continue

            slug = critere.replace(" ", "_").replace("'", "").replace("-", "_").lower()

            df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
            df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
            df = df[df["annee"].astype(str).str.isnumeric()]
            df["annee"] = df["annee"].astype(int)

            df = predict_missing_years(df, "annee", "valeur", TARGET_YEARS)
            df["code_departement"] = dep_code
            df = df[["code_departement", "annee", "valeur"]]
            df = df.rename(columns={"valeur": slug})

            if slug not in criteres_data:
                criteres_data[slug] = []

            criteres_data[slug].append(df)

        except Exception as e:
            print(f"❌ Erreur dans {file.name}: {e}")
            continue

    final_df = None
    for slug, list_df in criteres_data.items():
        merged_df = pd.concat(list_df, ignore_index=True)
        if final_df is None:
            final_df = merged_df
        else:
            final_df = pd.merge(final_df, merged_df, on=["code_departement", "annee"], how="outer")

    final_df = final_df.sort_values(by=["code_departement", "annee"])
    final_df.to_csv(CLEAN_DIR / "population_clean.csv", index=False)
    print(f"✅ population_clean.csv généré avec {len(final_df)} lignes")


def process_criminalite():
    print("📦 Traitement des données de criminalité...")
    RAW_FOLDERS = {
        "auteurs_afr_penales": "auteurs_poursuivables",
        "pop_ecrouee_taux_occupation_carcerale": "taux_occupation_carcerale"
    }

    all_criteres = {}

    for folder_name, column_slug in RAW_FOLDERS.items():
        folder_path = BASE_DIR / "data" / "raw" / folder_name
        all_criteres[column_slug] = []

        for file in folder_path.glob("*.csv"):
            if not is_value_file(file.name):
                continue

            try:
                with open(file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                libelle_line = next((line for line in lines if "Libellé" in line), None)
                if not libelle_line:
                    print(f"⚠️ Pas de libellé dans {file.name}")
                    continue

                raw_label = libelle_line.split(";")[1].strip('" \n')
                _, dep_code = extract_criterion_and_departement(raw_label)

                if not dep_code:
                    if "ville de paris" in raw_label.lower():
                        dep_code = "75"
                    else:
                        print(f"⚠️ Département non reconnu dans {file.name} → {raw_label}")
                        continue

                df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
                df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
                df = df[df["annee"].astype(str).str.isnumeric()]
                df["annee"] = df["annee"].astype(int)

                df = predict_missing_years(df, "annee", "valeur", TARGET_YEARS)
                df["code_departement"] = dep_code
                df = df[["code_departement", "annee", "valeur"]]
                df = df.rename(columns={"valeur": column_slug})

                all_criteres[column_slug].append(df)

            except Exception as e:
                print(f"❌ Erreur dans {file.name}: {e}")
                continue

    final_df = None
    for critere, dfs in all_criteres.items():
        merged = pd.concat(dfs, ignore_index=True)
        if final_df is None:
            final_df = merged
        else:
            final_df = pd.merge(final_df, merged, on=["code_departement", "annee"], how="outer")

    final_df = final_df.sort_values(by=["code_departement", "annee"])
    final_df.to_csv(CLEAN_DIR / "criminalite_clean.csv", index=False)
    print(f"✅ criminalite_clean.csv généré avec {len(final_df)} lignes")

def process_cmu():
    print("📦 Traitement des données CMU...")

    RAW_FOLDERS = {
        "cmu_nb_allocataires": "cmu_c_nb_allocataires",
        "cmu_taux_couverture": "cmu_c_taux_de_couverture"
    }

    all_criteres = {}

    for folder_name, column_slug in RAW_FOLDERS.items():
        folder_path = BASE_DIR / "data" / "raw" / folder_name
        all_criteres[column_slug] = []

        for file in folder_path.glob("*.csv"):
            if not is_value_file(file.name):
                continue

            try:
                with open(file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                libelle_line = next((line for line in lines if "Libellé" in line), None)
                if not libelle_line:
                    print(f"⚠️ Pas de libellé dans {file.name}")
                    continue

                raw_label = libelle_line.split(";")[1].strip('" \n')
                _, dep_code = extract_criterion_and_departement(raw_label)

                if not dep_code:
                    if "ville de paris" in raw_label.lower():
                        dep_code = "75"
                    else:
                        print(f"⚠️ Département non reconnu dans {file.name} → {raw_label}")
                        continue

                df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
                df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
                df = df[df["annee"].astype(str).str.isnumeric()]
                df["annee"] = df["annee"].astype(int)

                df = predict_missing_years(df, "annee", "valeur", TARGET_YEARS)
                df["code_departement"] = dep_code
                df = df[["code_departement", "annee", "valeur"]]
                df = df.rename(columns={"valeur": column_slug})

                all_criteres[column_slug].append(df)

            except Exception as e:
                print(f"❌ Erreur dans {file.name}: {e}")
                continue

    final_df = None
    for critere, dfs in all_criteres.items():
        merged = pd.concat(dfs, ignore_index=True)
        if final_df is None:
            final_df = merged
        else:
            final_df = pd.merge(final_df, merged, on=["code_departement", "annee"], how="outer")

    final_df = final_df.sort_values(by=["code_departement", "annee"])
    final_df.to_csv(CLEAN_DIR / "cmu_clean.csv", index=False)
    print(f"✅ cmu_clean.csv généré avec {len(final_df)} lignes et {len(final_df.columns)} colonnes")

def process_diplome():
    print("📦 Traitement des données de diplomes...")

    RAW_DIR = BASE_DIR / "data" / "raw" / "diplome"
    TARGET_YEARS = [2002, 2007, 2012, 2017, 2022]
    criteres_data = {}

    for file in RAW_DIR.glob("*.csv"):
        if not is_value_file(file.name):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            libelle_line = next((line for line in lines if "Libellé" in line), None)
            if not libelle_line:
                print(f"⚠️ Pas de libellé dans {file.name}")
                continue

            raw_label = libelle_line.split(";")[1].strip('" \n')
            critere, dep_code = extract_criterion_and_departement(raw_label)

            if not dep_code:
                if "ville de paris" in raw_label.lower():
                    dep_code = "75"
                else:
                    print(f"⚠️ Département non reconnu pour {file.name} → {raw_label}")
                    continue

            slug = critere.replace(" ", "_") \
                          .replace("'", "") \
                          .replace("-", "_") \
                          .replace("(", "") \
                          .replace(")", "") \
                          .replace(",", "") \
                          .lower()

            df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
            df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
            df = df[df["annee"].astype(str).str.isnumeric()]
            df["annee"] = df["annee"].astype(int)

            df = predict_missing_years(df, "annee", "valeur", TARGET_YEARS, force_clip_upper_100=True)
            df["code_departement"] = dep_code
            df = df[["code_departement", "annee", "valeur"]]
            df = df.rename(columns={"valeur": slug})

            if slug not in criteres_data:
                criteres_data[slug] = []

            criteres_data[slug].append(df)

        except Exception as e:
            print(f"❌ Erreur dans {file.name} : {type(e).__name__} - {e}")
            continue

    if not criteres_data:
        print("❌ Aucun critère de diplôme exploitable.")
        return

    final_df = None
    for slug, list_df in criteres_data.items():
        merged = pd.concat(list_df, ignore_index=True)
        if final_df is None:
            final_df = merged
        else:
            final_df = pd.merge(final_df, merged, on=["code_departement", "annee"], how="outer")

    final_df = final_df.sort_values(by=["code_departement", "annee"])
    final_df.to_csv(CLEAN_DIR / "diplome_clean.csv", index=False)
    print(f"✅ diplome_clean.csv généré avec {len(final_df)} lignes et {len(final_df.columns)} colonnes")

def process_minimum_vieillesse():
    print("📦 Traitement des données de minimum vieillesse...")

    RAW_DIR = BASE_DIR / "data" / "raw" / "minimum_vieillesse_beneficiaires"
    criteres_data = {}

    for file in RAW_DIR.glob("*.csv"):
        if not is_value_file(file.name):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            libelle_line = next((line for line in lines if "Libellé" in line), None)
            if not libelle_line:
                print(f"⚠️ Pas de libellé dans {file.name}")
                continue

            raw_label = libelle_line.split(";")[1].strip('" \n')
            critere, dep_code = extract_criterion_and_departement(raw_label)

            if not dep_code:
                if "ville de paris" in raw_label.lower():
                    dep_code = "75"
                else:
                    print(f"⚠️ Département non reconnu pour {file.name} → {raw_label}")
                    continue

            slug = critere.replace(" ", "_").replace("'", "").replace("-", "_").replace("(", "").replace(")", "").replace(",", "").lower()

            df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
            df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
            df = df[df["annee"].astype(str).str.isnumeric()]
            df["annee"] = df["annee"].astype(int)

            df = predict_missing_years(df, "annee", "valeur", [2002, 2007, 2012, 2017, 2022])
            df["code_departement"] = dep_code
            df = df[["code_departement", "annee", "valeur"]]
            df = df.rename(columns={"valeur": slug})

            if slug not in criteres_data:
                criteres_data[slug] = []

            criteres_data[slug].append(df)

        except Exception as e:
            print(f"❌ Erreur dans {file.name} : {type(e).__name__} - {e}")
            continue

    if not criteres_data:
        print("❌ Aucun fichier exploitable pour minimum vieillesse.")
        return

    final_df = None
    for slug, list_df in criteres_data.items():
        merged = pd.concat(list_df, ignore_index=True)
        if final_df is None:
            final_df = merged
        else:
            final_df = pd.merge(final_df, merged, on=["code_departement", "annee"], how="outer")

    final_df = final_df.sort_values(by=["code_departement", "annee"])
    final_df.to_csv(CLEAN_DIR / "minimum_vieillesse_clean.csv", index=False)
    print(f"✅ minimum_vieillesse_clean.csv généré avec {len(final_df)} lignes et {len(final_df.columns)} colonnes")

def process_logements_sociaux():
    print("📦 Traitement des données de logements sociaux...")

    RAW_DIR = BASE_DIR / "data" / "raw" / "nb_logements_sociaux_pour_10000_habitants"
    TARGET_YEARS = [2002, 2007, 2012, 2017, 2022]
    slug = "nb_logements_sociaux_pour_10000_habitants"
    dfs = []

    for file in RAW_DIR.glob("*.csv"):
        if not is_value_file(file.name):
            continue

        # Lecture du libellé pour extraire le département
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        libelle_line = next((l for l in lines if "Libellé" in l), None)
        if not libelle_line:
            print(f"⚠️ Pas de libellé dans {file.name}")
            continue

        raw_label = libelle_line.split(";")[1].strip('" \n')
        _, dep_code = extract_criterion_and_departement(raw_label)
        if not dep_code:
            if "ville de paris" in raw_label.lower():
                dep_code = "75"
            else:
                print(f"⚠️ Département non reconnu pour {file.name} → {raw_label}")
                continue

        # Chargement et nettoyage
        df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
        df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
        df = df[df["annee"].astype(str).str.isnumeric()]
        df["annee"] = df["annee"].astype(int)

        # Remplissage des années cibles
        df_filled = predict_missing_years(df, "annee", "valeur", TARGET_YEARS)

        # Ajout du code département et renommage
        df_filled["code_departement"] = dep_code
        df_filled = df_filled[["code_departement", "annee", "valeur"]]
        df_filled = df_filled.rename(columns={"valeur": slug})

        dfs.append(df_filled)

    if not dfs:
        print("❌ Aucun fichier exploitable pour logements sociaux.")
        return

    # Fusion et sauvegarde
    final = pd.concat(dfs, ignore_index=True)
    final = final.sort_values(by=["code_departement", "annee"])
    final.to_csv(CLEAN_DIR / "logements_sociaux_clean.csv", index=False)
    print(f"✅ logements_sociaux_clean.csv généré avec {len(final)} lignes (départements × années).")

import pandas as pd
from pathlib import Path
from data_utils import extract_criterion_and_departement, is_value_file, predict_missing_years

def process_rsa():
    print("📦 Traitement des données RSA...")
    RAW_DIR = BASE_DIR / "data" / "raw" / "rsa"
    TARGET_YEARS = [2002, 2007, 2012, 2017, 2022]
    slug = "rsa_nb_allocataires"
    dfs = []

    for file in RAW_DIR.glob("*.csv"):
        if not is_value_file(file.name):
            continue

        # 1) On détermine le département
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        libelle_line = next((l for l in lines if "Libellé" in l), None)
        raw_label = libelle_line.split(";")[1].strip('" \n')
        _, dep_code = extract_criterion_and_departement(raw_label)
        if not dep_code:
            print(f"⚠️ Département non reconnu pour {file.name}")
            continue

        # 2) Lecture brute et nettoyage
        df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
        df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
        df = df[df["annee"].astype(str).str.isnumeric()]
        df["annee"] = df["annee"].astype(int)
        df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")

        # 3) On note l’année minimale existante
        min_known = df["annee"].min()

        # 4) On remplit par prédiction (pour les années manquantes)
        filled = predict_missing_years(df, "annee", "valeur", TARGET_YEARS)

        # 5) On remplace par NA tout y < min_known
        filled.loc[filled["annee"] < min_known, "valeur"] = pd.NA

        # 6) On ajoute le code département et on renomme la colonne
        filled["code_departement"] = dep_code
        filled = filled[["code_departement", "annee", "valeur"]]
        filled = filled.rename(columns={"valeur": slug})

        dfs.append(filled)

    # 7) Fusion et sauvegarde
    if not dfs:
        print("❌ Aucun fichier RSA exploitable.")
        return

    final = pd.concat(dfs, ignore_index=True)
    final = final.sort_values(["code_departement","annee"])
    final.to_csv(CLEAN_DIR / "rsa_clean.csv", index=False)
    print(f"✅ rsa_clean.csv généré avec {len(final)} lignes.")

def process_chomage():
    print("📦 Traitement des données de taux de chômage...")
    RAW_DIR = BASE_DIR / "data" / "raw" / "taux_de_chomage"
    TARGET_YEARS = [2002, 2007, 2012, 2017, 2022]
    dfs = []

    for file in RAW_DIR.glob("*.csv"):
        if not is_value_file(file.name):
            continue

        # 1) extraire le libellé et le code département
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        libelle_line = next((l for l in lines if "Libellé" in l), None)
        if not libelle_line:
            print(f"⚠️ Pas de libellé dans {file.name}")
            continue
        raw_label = libelle_line.split(";")[1].strip('" \n')
        critere, dep_code = extract_criterion_and_departement(raw_label)
        if not dep_code:
            if "ville de paris" in raw_label.lower():
                dep_code = "75"
            else:
                print(f"⚠️ Département non reconnu pour {file.name} → {raw_label}")
                continue

        # 2) chargement, conversion trimestre → année, moyennage
        df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
        # on renomme la 1ʳᵉ colonne "periode", la 2ᵉ "valeur"
        df = df.rename(columns={df.columns[0]: "periode", df.columns[1]: "valeur"})
        # filtrer les lignes où "periode" est du type "YYYY-Tn"
        df = df[df["periode"].astype(str).str.match(r"\d{4}-T\d")]
        # extraire l'année
        df["annee"] = df["periode"].str.slice(0, 4).astype(int)
        # convertir la valeur en numérique
        df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")
        # calculer la moyenne annuelle
        annual = df.groupby("annee", as_index=False)["valeur"].mean()

        # 3) remplissage vers les années cibles
        filled = predict_missing_years(annual, "annee", "valeur", TARGET_YEARS)

        # 4) ajout du code département et slug
        slug = critere \
            .replace(" ", "_") \
            .replace("'", "") \
            .replace("-", "_") \
            .replace("(", "") \
            .replace(")", "") \
            .replace(",", "") \
            .lower()
        filled["code_departement"] = dep_code
        filled = filled.rename(columns={"valeur": slug})
        filled = filled[["code_departement", "annee", slug]]

        dfs.append(filled)

    if not dfs:
        print("❌ Aucun fichier exploitable pour le chômage.")
        return

    final = pd.concat(dfs, ignore_index=True)
    final = final.sort_values(["code_departement", "annee"])
    final.to_csv(CLEAN_DIR / "chomage_clean.csv", index=False)
    print(f"✅ chomage_clean.csv généré avec {len(final)} lignes et {len(final.columns)} colonnes")


def process_pauvrete():
    print("📦 Traitement des données de pauvreté...")
    RAW_DIR = BASE_DIR / "data" / "raw" / "taux_de_pauvrete"
    TARGET_YEARS = [2002, 2007, 2012, 2017, 2022]
    criteres_data: dict[str, list[pd.DataFrame]] = {}

    for file in RAW_DIR.glob("*.csv"):
        if not is_value_file(file.name):
            continue

        # Extraction du libellé et du code département
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        libelle_line = next((l for l in lines if "Libellé" in l), None)
        if not libelle_line:
            print(f"⚠️ Pas de libellé dans {file.name}")
            continue

        raw_label = libelle_line.split(";")[1].strip('" \n')
        critere, dep_code = extract_criterion_and_departement(raw_label)
        if not dep_code:
            print(f"⚠️ Département non reconnu pour {file.name} → {raw_label}")
            continue

        # Construction du slug
        slug = (
            critere
            .replace(" ", "_")
            .replace("'", "")
            .replace("-", "_")
            .replace(":", "")
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .lower()
        )

        # Lecture et nettoyage
        df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
        df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
        df = df[df["annee"].astype(str).str.isnumeric()]
        df["annee"] = df["annee"].astype(int)
        df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")

        # Remplissage des années cibles
        df_filled = predict_missing_years(df, "annee", "valeur", TARGET_YEARS)

        # Ajout du code département et renommage
        df_filled["code_departement"] = dep_code
        df_filled = df_filled[["code_departement", "annee", "valeur"]]
        df_filled = df_filled.rename(columns={"valeur": slug})

        criteres_data.setdefault(slug, []).append(df_filled)

    if not criteres_data:
        print("❌ Aucun critère de pauvreté exploitable.")
        return

    # Fusion de toutes les colonnes de pauvreté
    final = None
    for slug, dfs in criteres_data.items():
        merged = pd.concat(dfs, ignore_index=True)
        if final is None:
            final = merged
        else:
            final = pd.merge(final, merged, on=["code_departement", "annee"], how="outer")

    final = final.sort_values(by=["code_departement", "annee"])
    final.to_csv(CLEAN_DIR / "pauvrete_clean.csv", index=False)
    print(f"✅ pauvrete_clean.csv généré avec {len(final)} lignes et {len(final.columns)} colonnes")


def extract_data_from_voix(df: pd.DataFrame, annee: int, tour: int,
                           dept_col: str, exprim_col: str) -> pd.DataFrame:
    """
    Extrait code_departement, nom_candidat, nuance, voix, exprim, annee, tour
    puis calcule score = voix / exprim * 100.
    """
    rows = []
    try:
        base = df.columns.get_loc("Sexe")
        nb_cand = (len(df.columns) - base) // 6
        for i in range(nb_cand):
            off = base + i*6
            nom_col    = df.columns[off+1]
            prenom_col = df.columns[off+2]
            voix_col   = df.columns[off+3]
            nuance_col = df.columns[off+4]
            exprim_col = exprim_col

            for _, row in df.iterrows():
                code = str(row[dept_col]).replace(".0","").zfill(2)
                nom    = clean_nom(row[nom_col])
                prenom = clean_nom(row[prenom_col])
                voix   = float(str(row[voix_col]).replace(",",".").replace(" ",""))
                expr   = float(str(row[exprim_col]).replace(",",".").replace(" ",""))
                nuance = str(row[nuance_col]).strip().upper()

                rows.append({
                    "code_departement": code,
                    "nom_candidat":     f"{nom} {prenom}".strip(),
                    "nuance":           nuance,
                    "voix":             voix,
                    "exprim":           expr,
                    "annee":            annee,
                    "tour":             tour
                })
    except Exception as e:
        # si le format n'est pas exactement celui attendu, on ignore
        pass

    if not rows:
        return pd.DataFrame(columns=[
            "code_departement","nom_candidat","nuance",
            "voix","exprim","score","annee","tour"
        ])

    tmp = pd.DataFrame(rows)
    agg = tmp.groupby(
        ["code_departement","nom_candidat","nuance","annee","tour"],
        as_index=False
    ).sum()
    agg["score"] = (agg["voix"] / agg["exprim"] * 100).round(2)
    return agg[[
        "code_departement","nom_candidat","nuance",
        "score","annee","tour"
    ]]

def parse_election_file(path: Path, annee: int, tour: int) -> pd.DataFrame:
    """
    Lit le CSV selon l'année, skiprows si besoin, et appelle extract_data_from_voix().
    """
    try:
        if annee in {2002, 2007, 2012}:
            df = pd.read_csv(path, encoding="utf-8", sep=",", dtype=str)
            return extract_data_from_voix(
                df, annee, tour,
                dept_col="Code du département",
                exprim_col="Exprimés"
            )
        if annee == 2017:
            df = pd.read_csv(path, encoding="utf-8", skiprows=3, dtype=str)
            return extract_data_from_voix(
                df, annee, tour,
                dept_col=df.columns[0],
                exprim_col="Exprimés"
            )
        if annee == 2022:
            df = pd.read_csv(path, encoding="utf-8", dtype=str)
            return extract_data_from_voix(
                df, annee, tour,
                dept_col="Code du département",
                exprim_col="Exprimés"
            )
    except Exception as e:
        print(f"❌ Erreur fichier {path.name}: {e}")
    # retour vide si problème
    return pd.DataFrame(columns=[
        "code_departement","nom_candidat","nuance",
        "score","annee","tour"
    ])

def process_elections():
    print("📦 Sélection des vainqueurs d'élection…")
    RAW_ELEC = BASE_DIR / "data" / "raw" / "elections"
    # on ne conserve que ces codes-départements
    depts_cibles = set(DEPARTEMENT_MAP.values())

    winners = []
    for file in sorted(RAW_ELEC.glob("*.csv")):
        stem = file.stem  # ex: "elections_2017_T2"
        parts = stem.split("_")
        # déterminer année et tour
        if parts[-1] in ("T1", "T2"):
            annee = int(parts[-2])
            tour  = 2 if parts[-1] == "T2" else 1
        else:
            annee = int(parts[-1])
            tour  = 1

        df = parse_election_file(file, annee, tour)
        if df.empty:
            continue

        # si on a les deux tours, privilégier le 2ᵉ
        if 2 in df["tour"].unique():
            df = df[df["tour"] == 2]

        # pour chaque département ciblé, prendre le candidat qui a max score
        for dept, sub in df.groupby("code_departement", as_index=False):
            if dept not in depts_cibles:
                continue
            win = sub.loc[sub["score"].idxmax()]
            cand = win["nom_candidat"].strip().upper()
            bord = BORD_MAP.get(cand, "Autre")
            winners.append({
                "code_departement": dept,
                "bord_gagnant":     bord,
                "score":            win["score"],
                "annee":            annee
            })

    df_win = pd.DataFrame(winners)
    # on s’attend à len(depts_cibles) × 5 (2002,2007,2012,2017,2022)
    df_win = df_win[["code_departement", "bord_gagnant", "score", "annee"]]
    df_win = df_win.sort_values(["code_departement", "annee"])
    df_win.to_csv(CLEAN_DIR / "elections_clean.csv", index=False)
    print(f"✅ elections_clean.csv généré avec {len(df_win)} lignes")


def main():
    process_population()
    process_criminalite()
    process_cmu()
    process_diplome()
    process_minimum_vieillesse()
    process_logements_sociaux()
    process_rsa()
    process_chomage()
    process_pauvrete()
    process_elections()


if __name__ == "__main__":
    main()
