import pandas as pd
from pathlib import Path
from src.cleaning.dataset_cleaner import DatasetCleaner
from src.utils.data_utils import (
    extract_criterion_and_departement,
    is_value_file,
    predict_missing_years
)
from src.utils.constantes import TARGET_YEARS, CLEAN_DIR


class ChomageCleaner(DatasetCleaner):
    def run(self) -> None:
        self._log("Traitement des données de taux de chômage...")
        dfs = []

        for file in self.input_dir.glob("*.csv"):
            if not is_value_file(file.name):
                continue

            try:
                with open(file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                libelle_line = next((l for l in lines if "Libellé" in l), None)
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

                df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
                df = df.rename(columns={df.columns[0]: "periode", df.columns[1]: "valeur"})
                df = df[df["periode"].astype(str).str.match(r"\d{4}-T\d")]
                df["annee"] = df["periode"].str.slice(0, 4).astype(int)
                df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")

                annual = df.groupby("annee", as_index=False)["valeur"].mean()
                filled = predict_missing_years(annual, "annee", "valeur", TARGET_YEARS)

                slug = critere.replace(" ", "_")\
                               .replace("'", "")\
                               .replace("-", "_")\
                               .replace("(", "")\
                               .replace(")", "")\
                               .replace(",", "")\
                               .lower()

                filled["code_departement"] = dep_code
                filled = filled.rename(columns={"valeur": slug})
                filled = filled[["code_departement", "annee", slug]]

                dfs.append(filled)

            except Exception as e:
                self._log(f"Erreur dans {file.name} : {type(e).__name__} - {e}")
                continue

        if not dfs:
            self._log("Aucun fichier exploitable pour le chômage.")
            return

        final = pd.concat(dfs, ignore_index=True)
        final = final.sort_values(["code_departement", "annee"])
        final.to_csv(self.output_file, index=False)
        self._log(f"chomage_clean.csv généré avec {len(final)} lignes et {len(final.columns)} colonnes")
