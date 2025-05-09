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


def main():
    # process_population()
    # process_criminalite()
    # process_cmu()
    # process_diplome()
    # process_minimum_vieillesse()
    # process_logements_sociaux()
    # process_rsa()
    # process_chomage()
    process_pauvrete()


if __name__ == "__main__":
    main()
