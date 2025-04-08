import requests
import csv
import os
from token_manager import get_insee_token
import xmltodict


CHOMAGE_SERIES = {
    "01": "001515866",  # Ain
    "02": "001515867",  # Aisne
    "06": "001515871",  # Alpes-Maritimes
    "13": "001515877",  # Bouches-du-Rhône
    "17": "001515881",  # Charente-Maritime
    "21": "001515883",  # Côte-d'Or
    "29": "001515888",  # Finistère
    "31": "001515890",  # Haute-Garonne
    "33": "001515892",  # Gironde
    "34": "001515893",  # Hérault
    "38": "001515896",  # Isère
    "44": "001515899",  # Loire-Atlantique
    "54": "001515904",  # Meurthe-et-Moselle
    "59": "001515907",  # Nord
    "60": "001515908",  # Oise
    "62": "001515910",  # Pas-de-Calais
    "69": "001515914",  # Rhône
    "75": "001515918",  # Paris
    "83": "001515926",  # Var
    "974": "001515948"  # La Réunion
}


# Prépare le dossier
output_dir = "../data/raw/chomage"
os.makedirs(output_dir, exist_ok=True)

# Récupère le token
token = get_insee_token()
headers = {
    "Authorization": f"Bearer {token}"
}

# Boucle sur les départements
for code_dept, idbank in CHOMAGE_SERIES.items():
    url = f"https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/{idbank}"
    
    # Ajouter l'en-tête Accept pour XML
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/xml"
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"Status code for {code_dept}: {response.status_code}")
    
    try:
        if response.status_code == 200:
            xml_data = xmltodict.parse(response.text)
            series = xml_data['message:StructureSpecificData']['message:DataSet']['Series']
            observations = series['Obs']
            
            output_path = os.path.join(output_dir, f"chomage_{code_dept}.csv")
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["année", "taux_chomage"])
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
