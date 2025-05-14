import json
import requests
import zipfile, io
from time import sleep
from pathlib import Path

BASE_DIR      = Path(__file__).resolve().parent.parent
RAW_DATA_DIR  = BASE_DIR / "data" / "raw"
JSON_PATH     = BASE_DIR / "data_sources.json"

def create_folder(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def load_config(json_path: Path) -> dict:
    return json.loads(json_path.read_text(encoding="utf-8"))

def extract_csv_from_zip(content: bytes, output_dir: Path, base_filename: str):
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for info in zf.infolist():
            if info.filename.lower().endswith(".csv") and "caractéristiques" not in info.filename.lower():
                with zf.open(info) as src, open(output_dir / f"{base_filename}_{Path(info.filename).stem}.csv", "wb") as dst:
                    dst.write(src.read())

def download_generic(url: str) -> bytes:
    r = requests.get(url)
    r.raise_for_status()
    return r.content

def fetch_all_data():
    config  = load_config(JSON_PATH)
    base_url = config.get("base_url", "")

    print("📥 Téléchargement en cours…")
    for ds in config["datasets"]:
        name = ds["name"]
        folder = RAW_DATA_DIR / name
        create_folder(folder)

        # 1) séries INSEE (zip ou csv direct)
        for series_id in ds.get("series", []):
            try:
                url = f"{base_url}{series_id}"
                content = download_generic(url)
                if content.startswith(b"PK\x03\x04"):
                    extract_csv_from_zip(content, folder, f"{name}_{series_id}")
                else:
                    (folder / f"{name}_{series_id}.csv").write_bytes(content)
                print(f"✅ {name}/{series_id}")
            except Exception as e:
                print(f"❌ Erreur {series_id} ({name}) : {e}")
            sleep(0.5)

        # 2) élections (URLs complètes)
        for label, url in ds.get("election_urls", {}).items():
            try:
                content = download_generic(url)
                # l’API retourne du CSV pur
                (folder / f"{name}_{label}.csv").write_bytes(content)
                print(f"✅ {name}/{label}")
            except Exception as e:
                print(f"❌ Erreur {label} ({name}) : {e}")
            sleep(0.5)

    print("✅ Tous les jeux de données ont été téléchargés.")

fetch_all_data()