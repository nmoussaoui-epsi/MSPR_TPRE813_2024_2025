import os
import requests
from urllib.parse import urlparse

# URLs vers les exports CSV des résultats électoraux (API Tabular Data.gouv.fr)
election_urls = {
    "elections_2002": "https://tabular-api.data.gouv.fr/api/resources/6a99f5eb-436a-4ebf-9924-479aca1fc178/data/csv/",
    "elections_2007": "https://tabular-api.data.gouv.fr/api/resources/23061ba7-39a6-464b-bd31-c6b1137b69ba/data/csv/",
    "elections_2012": "https://tabular-api.data.gouv.fr/api/resources/adac47aa-6436-47aa-b1c0-f35882187970/data/csv/",
    "elections_2017_T1": "https://tabular-api.data.gouv.fr/api/resources/2776519f-a940-46f0-99f4-1a3a1374193b/data/csv/",
    "elections_2017_T2": "https://tabular-api.data.gouv.fr/api/resources/0e50ba6a-8175-4455-9e4a-09a7783dc547/data/csv/",
    "elections_2022_T1": "https://tabular-api.data.gouv.fr/api/resources/8b4d68f6-4490-4afc-b632-6c259073a4b9/data/csv/",
    "elections_2022_T2": "https://tabular-api.data.gouv.fr/api/resources/8986f174-d47e-46e5-a499-5d352d9422b3/data/csv/",
}

# Dossier de sortie
output_dir = "../data/raw/elections"
os.makedirs(output_dir, exist_ok=True)

# Téléchargement et enregistrement des fichiers
for label, url in election_urls.items():
    print(f"🔄 Téléchargement : {label}")
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Forcer l’extension CSV car l’API retourne toujours du CSV ici
            extension = ".csv"
            output_path = os.path.join(output_dir, f"{label}{extension}")

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✅ Enregistré : {output_path}")
        else:
            print(f"❌ Erreur HTTP {response.status_code} pour {label}")
    except Exception as e:
        print(f"⚠️ Exception lors du téléchargement de {label} : {e}")
