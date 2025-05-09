import pandas as pd
from pathlib import Path
from data_utils import (
    extract_criterion_and_departement,
    is_value_file,
    predict_missing_years
)

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


def main():
    process_population()
    process_criminalite()
    process_cmu()
    process_diplome()
    process_minimum_vieillesse()


if __name__ == "__main__":
    main()
