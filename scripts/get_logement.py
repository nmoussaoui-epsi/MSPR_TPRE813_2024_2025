import requests
import os

# URL directe du fichier CSV sur data.gouv.fr
url = "https://www.data.gouv.fr/fr/datasets/r/bf82e99f-cb74-48e6-b49f-9a0da726d5dc"

# Chemin de sauvegarde local
output_dir = "../data/raw/logements"
output_path = os.path.join(output_dir, "logements_sociaux.csv")

# Créer le dossier s’il n’existe pas
os.makedirs(output_dir, exist_ok=True)

# Télécharger le fichier
response = requests.get(url)

# Sauvegarde locale
if response.status_code == 200:
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Fichier téléchargé : {output_path}")
else:
    print(f"❌ Erreur {response.status_code} lors du téléchargement.")
