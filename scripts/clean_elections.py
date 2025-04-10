import pandas as pd
import os
import re

# Départements à garder
departements_cibles = {
    "01", "02", "06", "13", "17", "21", "29", "31", "33", "34",
    "38", "44", "54", "59", "60", "62", "69", "75", "83", "974"
}

# Dossiers
input_dir = "../data/raw/elections"
output_dir = "../data/clean"
os.makedirs(output_dir, exist_ok=True)

# Fichiers d'élections à traiter
elections_files = {
    "2002": "elections_2002.csv",
    "2007": "elections_2007.csv",
    "2012": "elections_2012.csv",
    "2017_T1": "elections_2017_T1.csv",
    "2017_T2": "elections_2017_T2.csv",
    "2022_T1": "elections_2022_T1.csv",
    "2022_T2": "elections_2022_T2.csv",
}

# Fonction pour extraire les données de candidats
def extract_candidate_data(df, annee, tour, format_type):
    result_data = []
    dept_col = "Code du département"
    
    # S'assurer que le code département est bien formaté (2 chiffres)
    df[dept_col] = df[dept_col].astype(str).str.replace('\.0$', '', regex=True).str.zfill(2)
    
    # Filtrer pour ne garder que les départements cibles
    df = df[df[dept_col].isin(departements_cibles)]
    
    if format_type == "2002-2012":
        # Format 2002-2012: colonnes Nom.X, Prénom.X, Voix.X
        for i in range(16):  # Nombre max de candidats
            suffix = "" if i == 0 else f".{i}"
            nom_col = f"Nom{suffix}"
            prenom_col = f"Prénom{suffix}"
            voix_col = f"Voix{suffix}"
            
            if all(col in df.columns for col in [nom_col, prenom_col, voix_col]):
                for _, row in df.iterrows():
                    try:
                        code_dept = str(row[dept_col]).replace(".0", "").zfill(2)
                        nom = str(row[nom_col]).strip().upper()
                        prenom = str(row[prenom_col]).strip().upper()
                        voix = row[voix_col]
                        
                        # Vérifier si la valeur des voix est valide
                        if pd.notna(voix) and str(voix).strip() != "":
                            try:
                                voix = float(str(voix).replace(",", "."))
                                if voix > 0:  # Ignorer les valeurs nulles ou négatives
                                    result_data.append({
                                        "code_departement": code_dept,
                                        "nom_candidat": f"{nom} {prenom}",
                                        "score": voix,
                                        "annee": annee,
                                        "tour": tour
                                    })
                            except ValueError:
                                print(f"⚠️ Valeur de voix non numérique ignorée: '{voix}' pour {nom} {prenom}")
                    except Exception as e:
                        print(f"⚠️ Erreur lors du traitement d'une ligne: {e}")
    
    elif format_type == "2017":
        # Format 2017: Utiliser les colonnes après la 3ème ligne
        try:
            # Les colonnes pour les candidats sont par groupe de 7 (N°Panneau, Sexe, Nom, Prénom, Voix, % Voix/Ins, % Voix/Exp)
            nb_candidats = (len(df.columns) - 18) // 7  # 18 colonnes avant les candidats
            
            for i in range(nb_candidats):
                base_idx = 18 + (i * 7)  # Index de début pour chaque candidat
                if base_idx + 4 < len(df.columns):  # S'assurer qu'on a assez de colonnes
                    nom_col = df.columns[base_idx + 2]  # Nom
                    prenom_col = df.columns[base_idx + 3]  # Prénom
                    voix_col = df.columns[base_idx + 4]  # Voix
                    
                    for _, row in df.iterrows():
                        try:
                            code_dept = str(row[df.columns[0]]).replace(".0", "").zfill(2)
                            nom = str(row[nom_col]).strip().upper()
                            prenom = str(row[prenom_col]).strip().upper()
                            voix = row[voix_col]
                            
                            # Vérifier si la valeur des voix est valide
                            if pd.notna(voix) and str(voix).strip() != "":
                                try:
                                    voix = float(str(voix).replace(",", ".").replace(".0", ""))
                                    if voix > 0:  # Ignorer les valeurs nulles ou négatives
                                        result_data.append({
                                            "code_departement": code_dept,
                                            "nom_candidat": f"{nom} {prenom}",
                                            "score": voix,
                                            "annee": annee,
                                            "tour": tour
                                        })
                                except ValueError:
                                    print(f"⚠️ Valeur de voix non numérique ignorée: '{voix}' pour {nom} {prenom}")
                        except Exception as e:
                            print(f"⚠️ Erreur lors du traitement d'une ligne 2017: {e}")
        except Exception as e:
            print(f"❌ Erreur lors du traitement du format 2017: {e}")
    
    elif format_type == "2022":
        # Format 2022: colonnes simples directes
        try:
            for _, row in df.iterrows():
                try:
                    code_dept = str(row[dept_col]).replace(".0", "").zfill(2)
                    nom = str(row["Nom"]).strip().upper()
                    prenom = str(row["Prénom"]).strip().upper()
                    
                    # Pour 2022, on utilise directement la colonne Voix
                    if "Voix" in df.columns:
                        voix = row["Voix"]
                        
                        # Vérifier si la valeur des voix est valide
                        if pd.notna(voix) and str(voix).strip() != "":
                            try:
                                voix = float(str(voix).replace(",", "."))
                                if voix > 0:  # Ignorer les valeurs nulles ou négatives
                                    result_data.append({
                                        "code_departement": code_dept,
                                        "nom_candidat": f"{nom} {prenom}",
                                        "score": voix,
                                        "annee": annee,
                                        "tour": tour
                                    })
                            except ValueError:
                                print(f"⚠️ Valeur de voix non numérique ignorée: '{voix}' pour {nom} {prenom}")
                except Exception as e:
                    print(f"⚠️ Erreur lors du traitement d'une ligne 2022: {e}")
        except Exception as e:
            print(f"❌ Erreur lors du traitement du format 2022: {e}")
    
    return result_data

# Liste pour stocker tous les résultats
all_data = []

for label, filename in elections_files.items():
    path = os.path.join(input_dir, filename)
    print(f"🔍 Traitement : {filename}")
    
    if not os.path.exists(path):
        print(f"⚠️ Fichier non trouvé : {path}")
        continue
    
    year_str = label.split("_")[0]
    annee = int(year_str)
    tour = 2 if "_T2" in label else 1
    
    try:
        # Détecter le format en fonction de l'année et du fichier
        if annee in [2002, 2007, 2012]:
            # Format standard pour 2002, 2007, 2012
            df = pd.read_csv(path, encoding="utf-8", sep=",", dtype=str, low_memory=False)
            candidate_data = extract_candidate_data(df, annee, tour, "2002-2012")
            all_data.extend(candidate_data)
            print(f"✅ Traité {len(candidate_data)} candidats pour {filename}")
            
        # Modification de la partie qui traite les fichiers 2017
        
        elif annee == 2017:
            # Format spécial pour 2017 avec lignes d'en-tête
            try:
                # D'abord essayer avec skiprows pour ignorer les lignes d'en-tête problématiques
                df = pd.read_csv(path, dtype=str, low_memory=False, skiprows=3)
                
                # Vérifier si nous avons trouvé l'en-tête correctement
                if "Code du département" in df.columns or any("Code du département" in str(col) for col in df.columns):
                    # Trouver la colonne qui contient "Code du département"
                    dept_col = next((col for col in df.columns if "Code du département" in str(col)), "Code du département")
                    
                    # Normaliser certains noms de colonnes si nécessaire
                    for old_col in df.columns:
                        if "Libellé du département" in str(old_col):
                            df.rename(columns={old_col: "Libellé du département"}, inplace=True)
                    
                    # Extraire les données de candidats avec le format 2017
                    candidate_data = []
                    
                    # Pour les tours 1 et 2, le traitement est un peu différent
                    if tour == 1:
                        # Tour 1: 11 candidats groupés par 7 colonnes
                        nb_candidats = 11
                        for i in range(nb_candidats):
                            base_idx = 19 + (i * 7)  # Index ajusté pour le format spécifique
                            if base_idx + 6 < len(df.columns):
                                sexe_col = df.columns[base_idx + 1]
                                nom_col = df.columns[base_idx + 2]
                                prenom_col = df.columns[base_idx + 3]
                                voix_col = df.columns[base_idx + 4]
                                
                                for _, row in df.iterrows():
                                    try:
                                        code_dept = str(row[dept_col]).replace(".0", "").zfill(2)
                                        if code_dept in departements_cibles:
                                            nom = str(row.get(nom_col, "")).strip().upper()
                                            prenom = str(row.get(prenom_col, "")).strip().upper()
                                            voix = row.get(voix_col, "")
                                            
                                            if pd.notna(voix) and str(voix).strip() != "":
                                                try:
                                                    voix = float(str(voix).replace(",", ".").replace(".0", ""))
                                                    if voix > 0:
                                                        candidate_data.append({
                                                            "code_departement": code_dept,
                                                            "nom_candidat": f"{nom} {prenom}",
                                                            "score": voix,
                                                            "annee": annee,
                                                            "tour": tour
                                                        })
                                                except ValueError:
                                                    continue
                                    except Exception:
                                        continue
                    else:
                        # Tour 2: seulement 2 candidats (Macron et Le Pen)
                        candidats_t2 = [
                            {"nom": "MACRON", "prenom": "Emmanuel", "col_idx": 19},
                            {"nom": "LE PEN", "prenom": "Marine", "col_idx": 26}
                        ]
                        
                        for candidat in candidats_t2:
                            voix_col = df.columns[candidat["col_idx"] + 4]
                            
                            for _, row in df.iterrows():
                                try:
                                    code_dept = str(row[dept_col]).replace(".0", "").zfill(2)
                                    if code_dept in departements_cibles:
                                        voix = row.get(voix_col, "")
                                        
                                        if pd.notna(voix) and str(voix).strip() != "":
                                            try:
                                                voix = float(str(voix).replace(",", ".").replace(".0", ""))
                                                if voix > 0:
                                                    candidate_data.append({
                                                        "code_departement": code_dept,
                                                        "nom_candidat": f"{candidat['nom']} {candidat['prenom']}".upper(),
                                                        "score": voix,
                                                        "annee": annee,
                                                        "tour": tour
                                                    })
                                            except ValueError:
                                                continue
                                except Exception:
                                    continue
                    
                    all_data.extend(candidate_data)
                    print(f"✅ Traité {len(candidate_data)} candidats pour {filename}")
                else:
                    print(f"❌ En-tête non valide dans {filename} après avoir ignoré les premières lignes")
            except Exception as e:
                print(f"❌ Erreur lors du traitement du format 2017 pour {filename}: {e}")
                
        elif annee == 2022:
            # Format pour 2022
            df = pd.read_csv(path, encoding="utf-8", dtype=str, low_memory=False)
            candidate_data = extract_candidate_data(df, annee, tour, "2022")
            all_data.extend(candidate_data)
            print(f"✅ Traité {len(candidate_data)} candidats pour {filename}")
            
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {filename}: {e}")

# Création du DataFrame final
if all_data:
    df_final = pd.DataFrame(all_data)
    
    # Nettoyage et normalisation des noms de candidats
    candidats_map = {
        "MACRON": "MACRON EMMANUEL",
        "LE PEN": "LE PEN MARINE",
        "MLENCHON": "MELENCHON JEAN-LUC",
        "MÉLENCHON": "MELENCHON JEAN-LUC",
        "MELENCHON": "MELENCHON JEAN-LUC",
        "HOLLANDE": "HOLLANDE FRANCOIS",
        "SARKOZY": "SARKOZY NICOLAS",
        "ROYAL": "ROYAL SEGOLENE",
        "CHIRAC": "CHIRAC JACQUES",
        "BAYROU": "BAYROU FRANCOIS",
        "JOSPIN": "JOSPIN LIONEL",
        "FILLON": "FILLON FRANCOIS",
        "HAMON": "HAMON BENOIT",
    }
    
    # Normaliser les noms des candidats connus
    for pattern, replacement in candidats_map.items():
        df_final.loc[df_final["nom_candidat"].str.contains(pattern, case=False, na=False), "nom_candidat"] = replacement
    
    # Convertir le score en numérique et éliminer les valeurs aberrantes
    df_final["score"] = pd.to_numeric(df_final["score"], errors="coerce")
    df_final = df_final[df_final["score"] > 0]
    df_final = df_final[df_final["score"] < 1000000]  # Limite supérieure généreuse
    
    # Nettoyage final et sauvegarde
    df_final = df_final.dropna(subset=["score"])
    df_final["annee"] = df_final["annee"].astype(int)
    df_final["tour"] = df_final["tour"].astype(int)
    
    # Sauvegarde du fichier final
    output_path = os.path.join(output_dir, "elections_2002_2022.csv")
    df_final.to_csv(output_path, index=False)
    print(f"✅ Fichier final enregistré → {output_path}")
    print(f"📊 {len(df_final)} lignes de données traitées.")
else:
    print("⚠️ Aucune donnée n'a été extraite des fichiers.")
