import pandas as pd
import os
import glob

# Répertoires
input_dir = "../data/raw/population"
output_dir = "../data/clean"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "population_2002_2022.csv")

# Années électorales à cibler
annees_cibles = [2002, 2007, 2012, 2017, 2022]

# Liste des départements à inclure (comme dans clean_elections.py)
departements_cibles = [
    "01", "02", "06", "13", "21", "29", "31", "33", "34", 
    "38", "44", "54", "59","69", "75", "83", "971", "972", "973", "974"
]

# Vérifier l'existence du dossier
if not os.path.exists(input_dir):
    print(f"❌ Le répertoire '{input_dir}' n'existe pas.")
    os.makedirs(input_dir, exist_ok=True)
    print(f"✅ Répertoire '{input_dir}' créé.")
    print("⚠️ Veuillez y placer vos fichiers population_XX.csv avant de relancer ce script.")
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
        dept_code = file_name.replace("population_", "").replace(".csv", "")
        processed_depts.add(dept_code)
        
        # Chargement manuel du fichier pour ignorer les commentaires avec //
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line for line in f if not line.strip().startswith('//')]
        
        # Utiliser StringIO pour lire le contenu sans les commentaires
        from io import StringIO
        content = StringIO('\n'.join(lines))
        
        # Charger le CSV depuis le contenu filtré
        df = pd.read_csv(content)
        df.columns = df.columns.str.lower().str.strip()
        
        # Vérifier que les colonnes requises existent
        if "année" in df.columns and "population" in df.columns:
            # Garder uniquement les colonnes nécessaires
            df = df[["année", "population"]].copy()
            
            # Ajouter le code du département
            df["code_departement"] = dept_code
            
            # Convertir l'année en entier
            df["annee"] = pd.to_numeric(df["année"], errors="coerce")
            df = df.dropna(subset=["annee"])
            df["annee"] = df["annee"].astype(int)
            
            # Garder uniquement les années électorales
            df = df[df["annee"].isin(annees_cibles)]
            
            # Convertir la population en nombre
            df["population"] = pd.to_numeric(df["population"], errors="coerce")
            df = df.dropna(subset=["population"])
            
            # Arrondir la population à un nombre entier
            df["population"] = df["population"].round(0).astype(int)
            
            # Agréger par département et année (au cas où il y aurait plusieurs valeurs)
            df = df.groupby(["code_departement", "annee"], as_index=False)["population"].mean()
            
            all_data.append(df)
            print(f"✅ Ajouté {len(df)} lignes de {file_name}")
        else:
            print(f"⚠️ Fichier {file_name} ignoré: colonnes requises non trouvées")
            
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {file_name}: {e}")

# Fusion des dataframes (même si vide, on crée le squelette quand même)
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

# Sauvegarde (même si certaines données sont manquantes)
final_df.to_csv(output_file, index=False)
print(f"✅ Fichier sauvegardé : {output_file}")

