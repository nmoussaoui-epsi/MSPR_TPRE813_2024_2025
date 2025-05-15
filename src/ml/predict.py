import os
import sys
import joblib
import pandas as pd

# Définir les chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "..", "models")
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "data", "hypothetical")
MODEL_PATH = os.path.join(MODELS_DIR, "model_pipeline.pkl")

# Liste réelle des 20 départements du projet (dans l’ordre du merged_dataset)
departements = [
    (1, "Ain"), (2, "Aisne"), (6, "Alpes-Maritimes"), (13, "Bouches-du-Rhône"), (17, "Charente-Maritime"),
    (21, "Côte-d'Or"), (29, "Finistère"), (31, "Haute-Garonne"), (33, "Gironde"), (34, "Hérault"),
    (38, "Isère"), (44, "Loire-Atlantique"), (54, "Meurthe-et-Moselle"), (59, "Nord"), (60, "Oise"),
    (62, "Pas-de-Calais"), (69, "Rhône"), (75, "Paris"), (83, "Var"), (974, "La Réunion")
]
# Charger le modèle
if not os.path.exists(MODEL_PATH):
    print(f"Erreur : modèle introuvable à {MODEL_PATH}")
    sys.exit(1)

pipeline = joblib.load(MODEL_PATH)
print("Modèle chargé avec succès.\n")

# Lister les fichiers CSV dans le dossier hypothetical
csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

if not csv_files:
    print(f"Aucun fichier .csv trouvé dans {DATA_DIR}")
    sys.exit(1)

# Afficher les options
print("Fichiers disponibles dans 'data/hypothetical/' :")
for i, fname in enumerate(csv_files, start=1):
    print(f"{i}. {fname}")

# Demander le choix
try:
    choix = int(input("\nQuel fichier voulez-vous utiliser ? (numéro) ")) - 1
    if choix < 0 or choix >= len(csv_files):
        raise ValueError
except ValueError:
    print("Entrée invalide. Fin du script.")
    sys.exit(1)

selected_file = csv_files[choix]
file_path = os.path.join(DATA_DIR, selected_file)
print(f"\nFichier sélectionné : {selected_file}")

# Charger les données
try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"Erreur lors de la lecture du fichier : {e}")
    sys.exit(1)

# Vérifier que le nombre de lignes correspond à 20 départements
if len(df) != len(departements):
    print(f"Le fichier doit contenir exactement {len(departements)} lignes (1 par département)")
    sys.exit(1)

# Prédictions
try:
    predictions = pipeline.predict(df)
except Exception as e:
    print(f"Erreur pendant la prédiction : {e}")
    sys.exit(1)

# Affichage des résultats
print("\nRésultats de la prédiction :")
for dep_code, prediction in zip(departements, predictions):
    print(f"Département {dep_code} → Bord politique prédit : {prediction}")
