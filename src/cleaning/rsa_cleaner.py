import pandas as pd
from pathlib import Path
from src.cleaning.dataset_cleaner import DatasetCleaner
from src.utils.data_utils import (
    extract_criterion_and_departement,
    is_value_file,
    predict_missing_years
)
from src.utils.constantes import TARGET_YEARS, CLEAN_DIR


class RsaCleaner(DatasetCleaner):
    def run(self) -> None:
        self._log("Traitement des données RSA...")
        slug = "rsa_nb_allocataires"
        dfs = []

        for file in self.input_dir.glob("*.csv"):
            if not is_value_file(file.name):
                continue

            try:
                with open(file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                libelle_line = next((l for l in lines if "Libellé" in l), None)
                raw_label = libelle_line.split(";")[1].strip('" \n')
                _, dep_code = extract_criterion_and_departement(raw_label)
                if not dep_code:
                    self._log(f"Département non reconnu pour {file.name}")
                    continue

                df = pd.read_csv(file, sep=";", skiprows=4, encoding="utf-8")
                df = df.rename(columns={df.columns[0]: "annee", df.columns[1]: "valeur"})
                df = df[df["annee"].astype(str).str.isnumeric()]
                df["annee"] = df["annee"].astype(int)
                df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")

                min_known = df["annee"].min()
                filled = predict_missing_years(df, "annee", "valeur", TARGET_YEARS)
                filled.loc[filled["annee"] < min_known, "valeur"] = pd.NA

                filled["code_departement"] = dep_code
                filled = filled[["code_departement", "annee", "valeur"]].rename(columns={"valeur": slug})
                dfs.append(filled)

            except Exception as e:
                self._log(f"Erreur dans {file.name} : {type(e).__name__} - {e}")
                continue

        if not dfs:
            self._log("Aucun fichier RSA exploitable.")
            return

        final = pd.concat(dfs, ignore_index=True)
        final = final.sort_values(["code_departement", "annee"])
        final.to_csv(self.output_file, index=False)
        self._log(f"rsa_clean.csv généré avec {len(final)} lignes.")
