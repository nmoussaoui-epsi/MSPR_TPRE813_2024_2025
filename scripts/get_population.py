import requests
import csv
import os
import xmltodict
from token_manager import get_insee_token

# Dictionnaire des séries de population par département
POPULATION_SERIES = {
    "01": "001760080",
    "02": "001760081",
    "06": "001760085",
    "13": "001760092",
    "21": "001760102",
    "29": "001760110",
    "31": "001760097",
    "33": "001760113",
    "34": "001760114",
    "38": "001760118",
    "44": "001760124",
    "54": "001760134",
    "59": "001760139",
    "69": "001760149",
    "75": "001760155",
    "83": "001760163",
    "971": "001760176",
    "972": "001760177",
    "973": "001760178",
    "974": "001760179"
}


# Prépare le dossier de sortie
output_dir = "../data/raw/population"
os.makedirs(output_dir, exist_ok=True)

# Récupère le token
token = get_insee_token()
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/xml"
}

# Boucle sur les départements
for code_dept, idbank in POPULATION_SERIES.items():
    url = f"https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/{idbank}"
    response = requests.get(url, headers=headers)

    print(f"Status code for {code_dept}: {response.status_code}")

    try:
        if response.status_code == 200:
            xml_data = xmltodict.parse(response.text)
            series = xml_data['message:StructureSpecificData']['message:DataSet']['Series']
            observations = series['Obs']

            output_path = os.path.join(output_dir, f"population_{code_dept}.csv")
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["année", "population"])
                for obs in observations:
                    periode = obs['@TIME_PERIOD']
                    valeur = obs['@OBS_VALUE']
                    writer.writerow([periode, valeur])

            print(f"✅ {code_dept} → {output_path}")
        else:
            print(f"❌ Erreur {code_dept}: Status code {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Erreur pour {code_dept}: {str(e)}")
        print(f"Response content: {response.text[:200]}")
