import requests
import csv
import os
import xmltodict
from token_manager import get_insee_token

PAUVRETE_SERIES = {
    "01": "001742263",  # Ain
    "02": "001742264",  # Aisne
    "06": "001742268",  # Alpes-Maritimes
    "13": "001742275",  # Bouches-du-Rhône
    "21": "001742284",  # Côte-d'Or
    "29": "001742292",  # Finistère
    "31": "001742294",  # Haute-Garonne
    "33": "001742296",  # Gironde
    "34": "001742297",  # Hérault
    "38": "001742301",  # Isère
    "44": "001742343",  # Loire-Atlantique
    "54": "001742353",  # Meurthe-et-Moselle
    "59": "001742358",  # Nord
    "75": "001742374",  # Paris
    "83": "001742419",  # Var
    "972": "010001949",  # Martinique
    "974": "010001956"   # La Réunion
}

# Préparer le dossier de sortie
output_dir = "../data/raw/pauvrete"
os.makedirs(output_dir, exist_ok=True)

# Récupérer le token INSEE
token = get_insee_token()
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/xml"
}

# Récupération des données
for code_dept, idbank in PAUVRETE_SERIES.items():
    url = f"https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/{idbank}"
    response = requests.get(url, headers=headers)

    print(f"Status code for {code_dept}: {response.status_code}")

    try:
        if response.status_code == 200:
            xml_data = xmltodict.parse(response.text)
            series = xml_data['message:StructureSpecificData']['message:DataSet']['Series']
            observations = series['Obs']

            output_path = os.path.join(output_dir, f"pauvrete_{code_dept}.csv")
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["année", "taux_pauvrete"])
                for obs in observations:
                    annee = obs['@TIME_PERIOD']
                    valeur = obs['@OBS_VALUE']
                    writer.writerow([annee, valeur])

            print(f"✅ {code_dept} → {output_path}")
        else:
            print(f"❌ Erreur {code_dept}: {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Erreur pour {code_dept}: {str(e)}")
        print(f"Response content: {response.text[:200]}")
