import os
import requests
import pandas as pd

# URLs des fichiers .xlsx des élections
election_urls = {
    "elections_2002": "https://www.data.gouv.fr/fr/datasets/r/6a99f5eb-436a-4ebf-9924-479aca1fc178",
    "elections_2007": "https://www.data.gouv.fr/fr/datasets/r/23061ba7-39a6-464b-bd31-c6b1137b69ba",
    "elections_2012": "https://www.data.gouv.fr/fr/datasets/r/adac47aa-6436-47aa-b1c0-f35882187970",
    "elections_2017_T1": "https://www.data.gouv.fr/fr/datasets/r/449f02ce-e971-46a9-aa72-ca66858f16cf",
    "elections_2017_T2": "https://www.data.gouv.fr/fr/datasets/r/0e50ba6a-8175-4455-9e4a-09a7783dc547",
    "elections_2022_T1": "https://www.data.gouv.fr/fr/datasets/r/98eb9dab-f328-4dee-ac08-ac17211357a8",
    "elections_2022_T2": "https://www.data.gouv.fr/fr/datasets/r/92fcc5b6-df2a-4a33-ab28-555803511206",
}

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
