"""Nettoyage et fusion intelligent des données brutes"""
import pandas as pd
from pathlib import Path
from data_utils import extract_from_label, is_value_file, is_trimestriel, interpolate_missing_years


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

TARGET_YEARS = [2002, 2007, 2012, 2017, 2022]

def clean_dataset(dataset_name: str):
    dataset_path = RAW_DIR / dataset_name
    all_data = []
    column_name = None

    for file in dataset_path.glob("*.csv"):
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
            libelle, dep_code = extract_from_label(raw_label)

            if not dep_code:
                print(f"⚠️ Département non reconnu pour {file.name} → {raw_label}")
                continue

            if column_name is None:
                column_name = libelle.replace(" ", "_").replace("'", "").lower()

            df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
            df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: column_name})

            if is_trimestriel(str(df["annee"].iloc[0])):
                df["annee"] = df["annee"].str.slice(0, 4).astype(int)
                df = df.groupby("annee")[column_name].mean().reset_index()

            df = interpolate_missing_years(df, "annee", column_name, TARGET_YEARS)
            df["code_departement"] = dep_code
            df = df[["code_departement", "annee", column_name]]

            all_data.append(df)

        except Exception as e:
            print(f"❌ Erreur dans {file.name}: {e}")
            continue

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv(CLEAN_DIR / f"{dataset_name}_clean.csv", index=False)
        print(f"✅ {dataset_name}_clean.csv créé avec {len(final_df)} lignes")
    else:
        print(f"❌ Aucun fichier nettoyable pour {dataset_name}")

def main():
    datasets = ["rsa", "minimum_vieillesse", "taux_de_chomage", "population"]
    for ds in datasets:
        clean_dataset(ds)

if __name__ == "__main__":
    main()
