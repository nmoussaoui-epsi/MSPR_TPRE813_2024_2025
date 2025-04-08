import requests
import os
from base64 import b64encode
from dotenv import load_dotenv

def get_insee_token():
    load_dotenv()

    client_id = os.getenv("INSEE_CLIENT_ID")
    client_secret = os.getenv("INSEE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise Exception("❌ INSEE_CLIENT_ID ou INSEE_CLIENT_SECRET manquant dans le .env")

    # Encodage en base64
    credentials = f"{client_id}:{client_secret}"
    encoded = b64encode(credentials.encode()).decode()

    # Requête
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post("https://api.insee.fr/token", headers=headers, data=data)

    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Token INSEE récupéré avec succès.")
        return token
    else:
        raise Exception(f"❌ Erreur lors de la récupération du token : {response.status_code} - {response.text}")
