import pandas as pd
from pathlib import Path
import numpy as np
from data_utils import DEPARTEMENT_MAP, clean_nom, normalize_departement_label
from data_utils import (
    extract_criterion_and_departement,
    is_value_file,
    predict_missing_years
)


BORD_MAP = {
    "MACRON EMMANUEL":           "centre",
    "BAYROU FRANCOIS":           "centre",
    "LASSALLE JEAN":             "centre",
    "JOLY EVA":                  "centre",
    "LEPAGE CORINNE":            "centre",
    "CHIRAC JACQUES":            "droite",
    "SARKOZY NICOLAS":           "droite",
    "FILLON FRANCOIS":           "droite",
    "DE VILLIERS PHILIPPE":      "droite",
    "DUPONT-AIGNAN NICOLAS":     "droite",
    "SAINT-JOSSE JEAN":          "droite",
    "MADELIN ALAIN":             "droite",
    "NIHOUS FREDERIC":           "droite",
    "BOUTIN CHRISTINE":          "droite",
    "JOSPIN LIONEL":             "gauche",
    "HOLLANDE FRANCOIS":         "gauche",
    "ROYAL SEGOLENE":            "gauche",
    "HAMON BENOIT":              "gauche",
    "MELENCHON JEAN LUC":        "gauche",
    "BUFFET MARIE-GEORGE":       "gauche",
    "CHEVENEMENT JEAN-PIERRE":   "gauche",
    "TAUBIRA CHRISTIANE":        "gauche",
    "HUE ROBERT":                "gauche",
    "BESANCENOT OLIVIER":        "extreme_gauche",
    "LAGUILLER ARLETTE":         "extreme_gauche",
    "POUTOU PHILIPPE":           "extreme_gauche",
    "ARTHAUD NATHALIE":          "extreme_gauche",
    "GLUCKSTEIN DANIEL":         "extreme_gauche",
    "SCHIVARDI GERARD":          "extreme_gauche",
    "LE PEN JEAN MARIE":         "extreme_droite",
    "LE PEN MARINE":             "extreme_droite",
    "MEGRET BRUNO":              "extreme_droite",
    "ASSELINEAU FRANCOIS":       "extreme_droite",
    "BOVE JOSE":                 "autre",
    "VOYNET DOMINIQUE":          "autre",
    "MAMERE NOEL":               "autre",
    "CHEMINADE JACQUES":         "autre"
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
    rows = []

    try:
        if tour == 2 and annee in {2017, 2022}:
            # Cas particulier du second tour : 2 candidats séparés
            for _, row in df.iterrows():
                try:
                    code = str(row[dept_col]).replace(".0", "").strip().zfill(2)
                    if code == "ZD":
                        code = "974"

                    exprim = float(str(row[exprim_col]).replace(",", ".").replace(" ", ""))
                    if exprim == 0:
                        continue

                    # Bloc candidat 1
                    nom1 = clean_nom(row["Nom"])
                    prenom1 = clean_nom(row["Prénom"])
                    full1 = f"{nom1} {prenom1}".strip()
                    voix1 = float(str(row["Voix"]).replace(",", ".").replace(" ", ""))
                    bord1 = BORD_MAP.get(full1)

                    if bord1:
                        rows.append({
                            "code_departement": code,
                            "bord":             bord1,
                            "voix":             voix1,
                            "exprim":           exprim,
                            "annee":            annee,
                            "tour":             tour
                        })

                    # Bloc candidat 2 (second bloc plus loin)
                    nom2 = clean_nom(row.get("Unnamed: 28", ""))
                    prenom2 = clean_nom(row.get("Unnamed: 29", ""))
                    full2 = f"{nom2} {prenom2}".strip()
                    voix2 = float(str(row.get("Unnamed: 30", "0")).replace(",", ".").replace(" ", ""))
                    bord2 = BORD_MAP.get(full2)

                    if bord2:
                        rows.append({
                            "code_departement": code,
                            "bord":             bord2,
                            "voix":             voix2,
                            "exprim":           exprim,
                            "annee":            annee,
                            "tour":             tour
                        })

                except Exception:
                    continue

        else:
            # Tours classiques (1er tour, ou anciens formats)
            base = df.columns.get_loc("Sexe")
            nb_cand = (len(df.columns) - base) // 6

            for i in range(nb_cand):
                off = base + i * 6
                nom_col = df.columns[off + 1]
                prenom_col = df.columns[off + 2]
                voix_col = df.columns[off + 3]

                for _, row in df.iterrows():
                    try:
                        code = str(row[dept_col]).replace(".0", "").strip().zfill(2)
                        if code == "ZD":
                            code = "974"

                        nom = clean_nom(row[nom_col])
                        prenom = clean_nom(row[prenom_col])
                        full = f"{nom} {prenom}".strip()

                        voix = float(str(row[voix_col]).replace(",", ".").replace(" ", ""))
                        expr = float(str(row[exprim_col]).replace(",", ".").replace(" ", ""))

                        bord = BORD_MAP.get(full)
                        if not bord:
                            continue

                        rows.append({
                            "code_departement": code,
                            "bord":             bord,
                            "voix":             voix,
                            "exprim":           expr,
                            "annee":            annee,
                            "tour":             tour
                        })
                    except Exception:
                        continue

    except Exception:
        pass

    if not rows:
        return pd.DataFrame(columns=[
            "code_departement", "bord", "score", "annee", "tour"
        ])

    tmp = pd.DataFrame(rows)
    agg = tmp.groupby(
        ["code_departement", "bord", "annee", "tour"],
        as_index=False
    ).sum()
    agg["score"] = (agg["voix"] / agg["exprim"] * 100).round(2)

    return agg[[
        "code_departement", "bord", "score", "annee", "tour"
    ]]

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
        print(f"❌ Erreur fichier {path.name}: {e}")

    return pd.DataFrame(columns=[
        "code_departement", "bord", "score", "annee", "tour"
    ])

def process_elections():
    RAW_ELEC = BASE_DIR / "data" / "raw" / "elections"
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    depts_cibles = set(DEPARTEMENT_MAP.values())
    normalized_dept_map = {
        normalize_departement_label(name): code
        for name, code in DEPARTEMENT_MAP.items()
    }

    rows = []
    for file in sorted(RAW_ELEC.glob("*.csv")):
        parts = file.stem.split("_")
        if parts[-1] in ("T1", "T2"):
            annee = int(parts[-2])
            tour = 2 if parts[-1] == "T2" else 1
        else:
            annee = int(parts[-1])
            tour = 1

        if annee in {2017, 2022} and tour != 2:
            continue

        df = parse_election_file(file, annee, tour)
        if df.empty:
            continue

        if "Libellé du département" in df.columns:
            df["code_departement"] = df.apply(
                lambda row: DEPARTEMENT_MAP.get(
                    normalize_departement_label(row["Libellé du département"]),
                    row["code_departement"]
                ),
                axis=1
            )

        rows.append(df)

    if not rows:
        print("⚠️ Aucun fichier valide")
        return

    all_data = pd.concat(rows)
    pivot = all_data.pivot_table(
        index=["code_departement", "annee"],
        columns="bord",
        values="score",
        aggfunc="sum"
    ).reset_index()

    pivot.columns.name = None
    pivot = pivot.fillna(0)

    pivot = pivot.rename(columns={
        "gauche": "resultat_gauche",
        "droite": "resultat_droite",
        "centre": "resultat_centre",
        "extreme_droite": "resultat_extreme_droite",
        "extreme_gauche": "resultat_extreme_gauche",
        "autre": "resultat_autre"
    })

    for col in [
        "resultat_gauche", "resultat_droite", "resultat_centre",
        "resultat_extreme_droite", "resultat_extreme_gauche", "resultat_autre"]:
        if col not in pivot.columns:
            pivot[col] = 0.0

    pivot = pivot[[
        "code_departement", "annee",
        "resultat_gauche", "resultat_droite", "resultat_centre",
        "resultat_extreme_droite", "resultat_extreme_gauche", "resultat_autre"
    ]]

    pivot = pivot[pivot["code_departement"].isin(DEPARTEMENT_MAP.values())]
    pivot.to_csv(CLEAN_DIR / "elections_clean.csv", index=False)
    print(f"✅ Fichier généré : {CLEAN_DIR / 'elections_clean.csv'}")

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
