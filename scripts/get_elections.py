import os
import requests
import pandas as pd

# URLs des fichiers .xlsx des élections
# election_urls = {
#     "elections_2002": "https://www.data.gouv.fr/fr/datasets/r/c5e0f812-48a6-437b-b5c2-1dbcc0c69c5d",
#     "elections_2007": "https://www.data.gouv.fr/fr/datasets/r/835a83c4-f24c-4f71-947b-5e0939db7d1e",
#     "elections_2012": "https://www.data.gouv.fr/fr/datasets/r/073e9a44-52a2-4032-84a8-4ce02eb2f7ad",
#     "elections_2017": "https://www.data.gouv.fr/fr/datasets/r/f010ab8f-3255-4f75-a9d4-27c21d3e44a3",
#     "elections_2022": "https://www.data.gouv.fr/fr/datasets/r/42a88f46-5893-4a47-b3a9-364b1d80e9cc"
# }

# Dossier de sortie
output_dir = "../data/raw/elections"
os.makedirs(output_dir, exist_ok=True)

# Télécharger et convertir chaque fichier
for filename, url in election_urls.items():
    print(f"🔄 Téléchargement : {filename}")
    xlsx_path = os.path.join(output_dir, f"{filename}.xlsx")
    csv_path = os.path.join(output_dir, f"{filename}.csv")

    # Télécharger le fichier xlsx
    response = requests.get(url)
    if response.status_code == 200:
        with open(xlsx_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Téléchargé : {xlsx_path}")

        # Essayer d’ouvrir et convertir en CSV
        try:
            df = pd.read_excel(xlsx_path)
            df.to_csv(csv_path, index=False)
            print(f"📁 Converti : {csv_path}")
        except Exception as e:
            print(f"⚠️ Erreur de conversion {filename}: {e}")
    else:
        print(f"❌ Échec du téléchargement : {filename}")
