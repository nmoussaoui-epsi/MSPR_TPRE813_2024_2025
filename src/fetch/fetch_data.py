# src/fetch/fetch_data.py
import json
import requests
import zipfile
import io
from pathlib import Path
from time import sleep


class DataFetcher:
    """
    Classe responsable du téléchargement et de l'extraction des jeux de données
    depuis des URLs fournies dans des fichiers de configuration JSON.
    """

    def __init__(self, config_path: Path, output_dir: Path, delay: float = 0.5):
        self.config = self._load_config(config_path)
        self.base_url = self.config.get("base_url", "")
        self.output_dir = output_dir
        self.delay = delay
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _download(self, url: str) -> bytes:
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def _extract_csv_from_zip(self, content: bytes, output_path: Path, base_name: str) -> None:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            for entry in archive.infolist():
                if entry.filename.lower().endswith(".csv") and "caractéristiques" not in entry.filename.lower():
                    with archive.open(entry) as src, open(
                        output_path / f"{base_name}_{Path(entry.filename).stem}.csv", "wb"
                    ) as dst:
                        dst.write(src.read())

    def fetch(self) -> None:
        for dataset in self.config.get("datasets", []):
            dataset_name = dataset["name"]
            dataset_dir = self.output_dir / dataset_name
            dataset_dir.mkdir(parents=True, exist_ok=True)

            for series_id in dataset.get("series", []):
                url = f"{self.base_url}{series_id}"
                try:
                    content = self._download(url)

                    if content.startswith(b"PK\x03\x04"):
                        self._extract_csv_from_zip(content, dataset_dir, f"{dataset_name}_{series_id}")
                    else:
                        (dataset_dir / f"{dataset_name}_{series_id}.csv").write_bytes(content)

                    print(f"[OK] {dataset_name}/{series_id}")
                except Exception as e:
                    print(f"[ERREUR] {dataset_name}/{series_id} : {e}")

                sleep(self.delay)

            for label, url in dataset.get("election_urls", {}).items():
                try:
                    content = self._download(url)
                    (dataset_dir / f"{dataset_name}_{label}.csv").write_bytes(content)
                    print(f"[OK] {dataset_name}/{label}")
                except Exception as e:
                    print(f"[ERREUR] {dataset_name}/{label} : {e}")

                sleep(self.delay)


if __name__ == "__main__":
    fetcher = DataFetcher(
        config_path=Path("data/data_sources.json"),
        output_dir=Path("data/raw")
    )
    fetcher.fetch()
