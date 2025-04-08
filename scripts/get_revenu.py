import requests
import csv
import os
import xmltodict
from token_manager import get_insee_token

REVENU_SERIES = {
    "01": "001741391",  # Ain
    "02": "001741392",  # Aisne
    "06": "001741396",  # Alpes-Maritimes
    "13": "001741403",  # Bouches-du-Rhône
    "21": "001741412",  # Côte-d'Or
    "29": "001741420",  # Finistère
    "31": "001741422",  # Haute-Garonne
    "33": "001741424",  # Gironde
    "34": "001741425",  # Hérault
    "38": "001741429",  # Isère
    "44": "001741435",  # Loire-Atlantique
    "54": "001741445",  # Meurthe-et-Moselle
    "59": "001741450",  # Nord
    "75": "001741466",  # Paris
    "83": "001741474",  # Var
    "972": "010001957",  # Martinique
    "974": "010001962",  # La Réunion
}


# Créer le dossier de sortie
output_dir = "../data/raw/revenu"
os.makedirs(output_dir, exist_ok=True)

# Récupérer le token INSEE
token = get_insee_token()
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/xml"
}

# Récupérer les données
for code_dept, idbank in REVENU_SERIES.items():
    url = f"https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/{idbank}"
    response = requests.get(url, headers=headers)

    print(f"Status code for {code_dept}: {response.status_code}")

    try:
        if response.status_code == 200:
            xml_data = xmltodict.parse(response.text)
            series = xml_data['message:StructureSpecificData']['message:DataSet']['Series']
            observations = series['Obs']

            output_path = os.path.join(output_dir, f"revenu_{code_dept}.csv")
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["année", "revenu_median"])
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
