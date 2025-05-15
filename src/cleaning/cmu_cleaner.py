import pandas as pd
from pathlib import Path
from src.cleaning.dataset_cleaner import DatasetCleaner
from src.utils.data_utils import (
    extract_criterion_and_departement,
    is_value_file,
    predict_missing_years
)
from src.utils.constantes import TARGET_YEARS, CLEAN_DIR, BASE_DIR


class CmuCleaner(DatasetCleaner):
    FOLDER_MAP = {
        "cmu_nb_allocataires": "cmu_c_nb_allocataires",
        "cmu_taux_couverture": "cmu_c_taux_de_couverture"
    }

    def run(self) -> None:
        self._log("Traitement des données CMU...")
        all_criteres = {}

        for folder_name, column_slug in self.FOLDER_MAP.items():
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
                        self._log(f"Pas de libellé dans {file.name}")
                        continue

                    raw_label = libelle_line.split(";")[1].strip('" \n')
                    _, dep_code = extract_criterion_and_departement(raw_label)

                    if not dep_code:
                        if "ville de paris" in raw_label.lower():
                            dep_code = "75"
                        else:
                            self._log(f"Département non reconnu dans {file.name} → {raw_label}")
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
                    self._log(f"Erreur dans {file.name}: {e}")
                    continue

        final_df = None
        for critere, dfs in all_criteres.items():
            merged = pd.concat(dfs, ignore_index=True)
            if final_df is None:
                final_df = merged
            else:
                final_df = pd.merge(final_df, merged, on=["code_departement", "annee"], how="outer")

        final_df = final_df.sort_values(by=["code_departement", "annee"])
        output_path = CLEAN_DIR / "cmu_clean.csv"
        final_df.to_csv(output_path, index=False)
        self._log(f"cmu_clean.csv généré avec {len(final_df)} lignes et {len(final_df.columns)} colonnes")
