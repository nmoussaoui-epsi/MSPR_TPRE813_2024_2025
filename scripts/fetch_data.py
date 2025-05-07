import json
import requests
import zipfile
import io
from time import sleep
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
JSON_PATH = BASE_DIR / "data_sources.json"

def create_folder(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def load_config(json_path: Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_download_url(base_url: str, series_id: str) -> str:
    return f"{base_url}{series_id}"

def extract_csv_from_zip(content: bytes, output_dir: Path, base_filename: str):
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            for zip_info in zf.infolist():
                if not zip_info.filename.lower().endswith(".csv"):
                    continue
                with zf.open(zip_info) as file:
                    stem = Path(zip_info.filename).stem
                    output_file = output_dir / f"{base_filename}_{stem}.csv"
                    with open(output_file, "wb") as out_f:
                        out_f.write(file.read())
    except zipfile.BadZipFile:
        raise Exception("ZIP invalide ou corrompu")

def download_file(url: str, output_dir: Path, dataset_name: str, series_id: str):
    response = requests.get(url)
    response.raise_for_status()

    content = response.content
    base_filename = f"{dataset_name}_{series_id}"

    if content[:4] == b"PK\x03\x04":
        extract_csv_from_zip(content, output_dir, base_filename)
    else:
        output_file = output_dir / f"{base_filename}.csv"
        with open(output_file, "wb") as f:
            f.write(content)

def fetch_all_data():
    config = load_config(JSON_PATH)
    base_url = config.get("base_url")

    print("📥 Téléchargement en cours...")

    for dataset in config["datasets"]:
        name = dataset["name"]
        series_list = dataset["series"]
        folder_path = RAW_DATA_DIR / name

        create_folder(folder_path)

        for series_id in series_list:
            url = build_download_url(base_url, series_id)
            try:
                download_file(url, folder_path, name, series_id)
            except Exception as e:
                print(f"❌ Erreur pour {series_id} ({name}) : {e}")
            sleep(0.5)

    print("✅ Tous les jeux de données ont été téléchargés.")

if __name__ == "__main__":
    fetch_all_data()
