from data_utils import get_raw_path, ensure_dir_exists
from token_manager import get_insee_token
import requests
import csv
import os
import xmltodict

# Constantes pour les séries INSEE
SERIES = {
    "chomage": {
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
    },
    "criminalite": {
        "01": "001688517",
        "02": "001688518",
        "06": "001688522",
        "13": "001688528",
        "17": "001688532",
        "21": "001688534",
        "29": "001688539",
        "31": "001688541",
        "33": "001688543",
        "34": "001688544",
        "38": "001688547",
        "44": "001688550",
        "54": "001688555",
        "59": "001688558",
        "60": "001688559",
        "62": "001688561",
        "69": "001688565",
        "75": "001688569",
        "83": "001688577",
        "974": "001688599"
    }
}

def fetch_chomage():
    """Récupère les données de chômage depuis l'API INSEE"""
    token = get_insee_token()
    output_dir = get_raw_path("chomage")
    ensure_dir_exists(output_dir)

    for code_dept, idbank in SERIES["chomage"].items():
        url = f"https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/{idbank}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/xml"
        }
        
        response = requests.get(url, headers=headers)
        
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

def fetch_criminalite():
    """Récupère les données de criminalité depuis l'API INSEE"""
    token = get_insee_token()
    output_dir = get_raw_path("criminalite")
    ensure_dir_exists(output_dir)

    for code_dept, idbank in SERIES["criminalite"].items():
        url = f"https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/{idbank}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/xml"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            xml_data = xmltodict.parse(response.text)
            series = xml_data['message:StructureSpecificData']['message:DataSet']['Series']
            observations = series['Obs']
            
            output_path = os.path.join(output_dir, f"criminalite_{code_dept}.csv")
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["année", "nombre_auteurs_poursuivables"])
                for obs in observations:
                    periode = obs['@TIME_PERIOD']
                    valeur = obs['@OBS_VALUE']
                    writer.writerow([periode, valeur])
            
            print(f"✅ {code_dept} → {output_path}")
        else:
            print(f"❌ Erreur {code_dept}: Status code {response.status_code}")

def run_all_fetch():
    """Exécute tous les processus de récupération"""
    print("Début de la récupération des données...")
    fetch_chomage()
    fetch_criminalite()
    print("✅ Toutes les récupérations sont terminées")

if __name__ == "__main__":
    run_all_fetch()
