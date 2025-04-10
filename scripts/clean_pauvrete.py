import pandas as pd
import os
import glob

# Répertoires
input_dir = "../data/raw/pauvrete"
output_dir = "../data/clean"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "pauvrete_2002_2022.csv")

# Années électorales à cibler
annees_cibles = [2002, 2007, 2012, 2017, 2022]

# Liste des départements à inclure (comme dans clean_elections.py)
departements_cibles = [
    "01", "02", "06", "13", "17", "21", "29", "31", "33", "34",
    "38", "44", "54", "59", "60", "62", "69", "75", "83", "974"
]

# Vérifier l'existence du dossier
if not os.path.exists(input_dir):
    print(f"❌ Le répertoire '{input_dir}' n'existe pas.")
    os.makedirs(input_dir, exist_ok=True)
    print(f"✅ Répertoire '{input_dir}' créé.")
    print("⚠️ Veuillez y placer vos fichiers pauvrete_XX.csv avant de relancer ce script.")
    exit()

# Rechercher tous les fichiers CSV dans le répertoire
csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
print(f"📂 {len(csv_files)} fichiers CSV trouvés dans {input_dir}")

if not csv_files:
    print("⚠️ Aucun fichier CSV trouvé. Veuillez ajouter des fichiers dans le répertoire.")
    exit()

# Liste pour stocker les dataframes
all_data = []
processed_depts = set()

# Chargement et traitement de chaque fichier
for file_path in csv_files:
    file_name = os.path.basename(file_path)
    print(f"🔍 Traitement de {file_name}")
    
    try:
        # Extraire le code du département depuis le nom du fichier
        dept_code = file_name.replace("pauvrete_", "").replace(".csv", "")
        processed_depts.add(dept_code)
        
        # Charger le fichier
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower().str.strip()
        
        # Vérifier que les colonnes requises existent
        if "année" in df.columns and "taux_pauvrete" in df.columns:
            # Garder uniquement les colonnes nécessaires
            df = df[["année", "taux_pauvrete"]].copy()
            
            # Ajouter le code du département
            df["code_departement"] = dept_code
            
            # Convertir l'année en entier
            df["annee"] = pd.to_numeric(df["année"], errors="coerce")
            df = df.dropna(subset=["annee"])
            df["annee"] = df["annee"].astype(int)
            
            # Garder uniquement les années électorales
            df = df[df["annee"].isin(annees_cibles)]
            
            # Convertir le taux de pauvreté en nombre
            df["taux_pauvrete"] = pd.to_numeric(df["taux_pauvrete"], errors="coerce")
            df = df.dropna(subset=["taux_pauvrete"])
            
            # Agréger par département et année (au cas où il y aurait plusieurs valeurs)
            df = df.groupby(["code_departement", "annee"], as_index=False)["taux_pauvrete"].mean()
            
            all_data.append(df)
            print(f"✅ Ajouté {len(df)} lignes de {file_name}")
        else:
            print(f"⚠️ Fichier {file_name} ignoré: colonnes requises non trouvées")
            
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {file_name}: {e}")

# Fusionner tous les dataframes si nous en avons
if not all_data:
    print("❌ Aucune donnée valide n'a été trouvée dans les fichiers.")
    exit()

# Fusion des dataframes et tri
data_df = pd.concat(all_data) if all_data else pd.DataFrame()
print(f"✅ {len(data_df)} lignes de données valides extraites")

# Création du squelette complet pour tous les départements et toutes les années
skeleton = []
for dept in departements_cibles:
    for year in annees_cibles:
        skeleton.append({
            "code_departement": dept,
            "annee": year
        })

# Conversion du squelette en DataFrame
skeleton_df = pd.DataFrame(skeleton)

# Fusion avec les données existantes
final_df = pd.merge(
    skeleton_df, 
    data_df, 
    on=["code_departement", "annee"], 
    how="left"  # Garde toutes les combinaisons dept/année du squelette
)

# Suppression de la colonne "année" (issue des données brutes) si elle existe
if "année" in final_df.columns:
    final_df = final_df.drop(columns=["année"])

# Tri des données
final_df = final_df.sort_values(["code_departement", "annee"])

# Sauvegarde
final_df.to_csv(output_file, index=False)
print(f"✅ Fichier sauvegardé : {output_file}")


