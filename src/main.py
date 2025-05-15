from pathlib import Path
from src.cleaning.chomage_cleaner import ChomageCleaner
from src.cleaning.elections_cleaner import ElectionsCleaner
from src.cleaning.logementsocial_cleaner import LogementSocialCleaner
from src.cleaning.diplome_cleaner import DiplomeCleaner
from src.cleaning.minimum_vieillesse_cleaner import MinimumVieillesseCleaner
from src.cleaning.pauvrete_cleaner import PauvreteCleaner
from src.cleaning.population_cleaner import PopulationCleaner
from src.cleaning.criminalite_cleaner import CriminaliteCleaner
from src.cleaning.cmu_cleaner import CmuCleaner
from src.cleaning.rsa_cleaner import RsaCleaner
from src.merge.merge_cleaned_data import merge_all_cleaned_data
from src.fetch.fetch_data import DataFetcher
from src.utils.constantes import BASE_DIR

def should_fetch_data() -> bool:
    raw_base = BASE_DIR / "data" / "raw"
    return not any(raw_base.rglob("*.csv"))

def fetch_if_needed():
    if should_fetch_data():
        print("Aucune donnée trouvée, démarrage de la récupération...")
        config_path = BASE_DIR / "data_sources.json"
        output_dir = BASE_DIR / "data" / "raw"
        fetcher = DataFetcher(config_path, output_dir)
        fetcher.fetch()
    else:
        print("Données déjà présentes, pas de récupération nécessaire.")


def main():
    raw_base = Path("data/raw")
    clean_base = Path("data/clean")
    clean_base.mkdir(parents=True, exist_ok=True)

    cleaners = [
        PopulationCleaner(raw_base / "population", clean_base / "population_clean.csv"),
        CriminaliteCleaner(
            input_dir=Path("."), output_file=Path("data/clean/criminalite_clean.csv")
        ),
        CmuCleaner(
            input_dir=Path("."), output_file=Path("data/clean/cmu_clean.csv")
        ),
        DiplomeCleaner(
            input_dir=Path("data/raw/diplome"),
            output_file=Path("data/clean/diplome_clean.csv"),
        ),
        MinimumVieillesseCleaner(
            input_dir=Path("data/raw/minimum_vieillesse_beneficiaires"),
            output_file=Path("data/clean/minimum_vieillesse_clean.csv"),
        ),
        LogementSocialCleaner(
            input_dir=Path("data/raw/nb_logements_sociaux_pour_10000_habitants"),
            output_file=Path("data/clean/logements_sociaux_clean.csv"),
        ),
        RsaCleaner(
            input_dir=Path("data/raw/rsa"), output_file=Path("data/clean/rsa_clean.csv")
        ),
        ChomageCleaner(
            input_dir=Path("data/raw/taux_de_chomage"),
            output_file=Path("data/clean/chomage_clean.csv"),
        ),
        PauvreteCleaner(
            input_dir=Path("data/raw/taux_de_pauvrete"),
            output_file=Path("data/clean/pauvrete_clean.csv"),
        ),
        ElectionsCleaner(
            input_dir=Path("data/raw/elections"),
            output_file=Path("data/clean/elections_clean.csv"),
        ),
    ]

    for cleaner in cleaners:
        cleaner.run()


if __name__ == "__main__":
    fetch_if_needed()
    main()
    merge_all_cleaned_data()
