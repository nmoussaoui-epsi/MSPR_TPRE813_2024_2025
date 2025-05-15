import pandas as pd
from pathlib import Path

def merge_all_cleaned_data():
    print("Fusion des fichiers cleaned...")
    clean_dir = Path("data/clean")
    output_file = clean_dir / "merged_dataset.csv"

    clean_files = sorted(clean_dir.glob("*_clean.csv"))
    merged_df = None

    for file in clean_files:
        df = pd.read_csv(file)
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(
                merged_df, df, on=["code_departement", "annee"], how="outer"
            )

    merged_df = merged_df.sort_values(["code_departement", "annee"])
    merged_df.to_csv(output_file, index=False)
    print(f"Fusion terminée : {output_file} ({len(merged_df)} lignes)")
