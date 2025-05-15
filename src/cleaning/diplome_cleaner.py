import pandas as pd
from pathlib import Path
from src.cleaning.dataset_cleaner import DatasetCleaner
from src.utils.data_utils import (
    extract_criterion_and_departement,
    is_value_file,
    predict_missing_years
)
from src.utils.constantes import TARGET_YEARS, CLEAN_DIR


class DiplomeCleaner(DatasetCleaner):
    def run(self) -> None:
        self._log("Traitement des données de diplomes...")
        criteres_data = {}

        for file in self.input_dir.glob("*.csv"):
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
                critere, dep_code = extract_criterion_and_departement(raw_label)

                if not dep_code:
                    if "ville de paris" in raw_label.lower():
                        dep_code = "75"
                    else:
                        self._log(f"Département non reconnu pour {file.name} → {raw_label}")
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
                df = df[["code_departement", "annee", "valeur"]].rename(columns={"valeur": slug})

                if slug not in criteres_data:
                    criteres_data[slug] = []

                criteres_data[slug].append(df)

            except Exception as e:
                self._log(f"Erreur dans {file.name} : {type(e).__name__} - {e}")
                continue

        if not criteres_data:
            self._log("Aucun critère de diplôme exploitable.")
            return

        final_df = None
        for slug, list_df in criteres_data.items():
            merged = pd.concat(list_df, ignore_index=True)
            if final_df is None:
                final_df = merged
            else:
                final_df = pd.merge(final_df, merged, on=["code_departement", "annee"], how="outer")

        final_df = final_df.sort_values(by=["code_departement", "annee"])
        final_df.to_csv(self.output_file, index=False)
        self._log(f"diplome_clean.csv généré avec {len(final_df)} lignes et {len(final_df.columns)} colonnes")
