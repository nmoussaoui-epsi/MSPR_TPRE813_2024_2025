import requests
import csv
import os
import xmltodict
from token_manager import get_insee_token

CRIMINALITE_SERIES = {
    "01": "001779257",  # Ain
    "02": "001779258",  # Aisne
    "06": "001779262",  # Alpes-Maritimes
    "13": "001779269",  # Bouches-du-Rhône
    "21": "001779278",  # Côte-d'Or
    "29": "001779286",  # Finistère
    "31": "001779288",  # Haute-Garonne
    "33": "001779290",  # Gironde
    "34": "001779323",  # Hérault
    "38": "001779327",  # Isère
    "44": "001779333",  # Loire-Atlantique
    "54": "001779343",  # Meurthe-et-Moselle
    "59": "001779348",  # Nord
    "75": "001779373",  # Paris
    "83": "001779381",  # Var
    "971": "001779395",  # Guadeloupe
    "972": "001779396",  # Martinique
    "973": "001779397",  # Guyane
    "974": "001779398",  # La Réunion
    "976": "001779399"   # Mayotte
}


# Créer le dossier de sortie
output_dir = "../data/raw/criminalite"
os.makedirs(output_dir, exist_ok=True)

# Récupération du token
token = get_insee_token()
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/xml"
}

# Boucle sur les départements
for code_dept, idbank in CRIMINALITE_SERIES.items():
    url = f"https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/{idbank}"
    response = requests.get(url, headers=headers)

    print(f"Status code for {code_dept}: {response.status_code}")

    try:
        if response.status_code == 200:
            xml_data = xmltodict.parse(response.text)
            series = xml_data['message:StructureSpecificData']['message:DataSet']['Series']
            observations = series['Obs']

            output_path = os.path.join(output_dir, f"criminalite_{code_dept}.csv")
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["année", "nombre_auteurs_poursuivables"])
                for obs in observations:
                    annee = obs['@TIME_PERIOD']
                    valeur = obs['@OBS_VALUE']
                    writer.writerow([annee, valeur])

            print(f"✅ {code_dept} → {output_path}")
        else:
            print(f"❌ Erreur {code_dept}: Status code {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Erreur pour {code_dept}: {str(e)}")
        print(f"Response content: {response.text[:200]}")
