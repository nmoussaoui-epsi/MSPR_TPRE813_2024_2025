import pandas as pd
from pathlib import Path
from src.cleaning.dataset_cleaner import DatasetCleaner
from src.utils.data_utils import parse_election_file, normalize_departement_label
from src.utils.constantes import BASE_DIR, CLEAN_DIR, DEPARTEMENT_MAP


class ElectionsCleaner(DatasetCleaner):
    def run(self) -> None:
        self._log("Traitement des données électorales")
        input_dir = BASE_DIR / "data" / "raw" / "elections"
        rows = []

        for file in sorted(input_dir.glob("*.csv")):
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
            self._log("Aucun fichier valide")
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
        pivot.to_csv(self.output_file, index=False)
        self._log(f"Fichier généré : {self.output_file}")
