import pandas as pd
import os

# Départements à analyser
departements_cibles = {
    "01", "02", "06", "13", "17", "21", "29", "31", "33", "34",
    "38", "44", "54", "59", "60", "62", "69", "75", "83", "974"
}

# Répertoires
input_dir = "../data/raw/elections"
output_dir = "../data/clean"
os.makedirs(output_dir, exist_ok=True)

# Fichiers à traiter
elections_files = {
    "2002": "elections_2002.csv",
    "2007": "elections_2007.csv",
    "2012": "elections_2012.csv",
    "2017_T1": "elections_2017_T1.csv",
    "2017_T2": "elections_2017_T2.csv",
    "2022_T1": "elections_2022_T1.csv",
    "2022_T2": "elections_2022_T2.csv",
}

# Nettoyage des noms
def clean_nom(nom):
    return str(nom).replace('"', '').strip().upper()

# Extraction des données avec calcul de % voix/exprimés
def extract_data_from_voix(df, annee, tour, dept_col, exprim_col):
    rows = []

    try:
        nb_candidats = (len(df.columns) - df.columns.get_loc("Sexe")) // 6
        for i in range(nb_candidats):
            offset = df.columns.get_loc("Sexe") + i * 6
            nom_col = df.columns[offset + 1]
            prenom_col = df.columns[offset + 2]
            voix_col = df.columns[offset + 3]

            for _, row in df.iterrows():
                try:
                    code_dept = str(row[dept_col]).replace(".0", "").zfill(2)
                    if code_dept not in departements_cibles:
                        continue

                    nom = clean_nom(row[nom_col])
                    prenom = clean_nom(row[prenom_col])
                    candidat = f"{nom} {prenom}".strip()

                    voix = float(str(row[voix_col]).replace(",", ".").replace(" ", ""))
                    exprim = float(str(row[exprim_col]).replace(",", ".").replace(" ", ""))
                    rows.append([code_dept, candidat, voix, exprim, annee, tour])
                except:
                    continue
    except:
        pass

    df_temp = pd.DataFrame(rows, columns=["code_departement", "nom_candidat", "voix", "exprim", "annee", "tour"])
    # Regrouper par candidat/département et recalculer le % de voix exprimées
    df_agg = df_temp.groupby(["code_departement", "nom_candidat", "annee", "tour"], as_index=False).sum()
    df_agg["score"] = (df_agg["voix"] / df_agg["exprim"]) * 100
    df_agg["score"] = df_agg["score"].round(2)
    return df_agg[["code_departement", "nom_candidat", "score", "annee", "tour"]].to_dict("records")


# Parsing selon format
def parse_file(path, annee, tour):
    try:
        if annee in [2002, 2007, 2012]:
            df = pd.read_csv(path, encoding="utf-8", sep=",", dtype=str)
            return extract_data_from_voix(df, annee, tour, "Code du département", "Exprimés")
        elif annee == 2017:
            df = pd.read_csv(path, skiprows=3, dtype=str)
            return extract_data_from_voix(df, annee, tour, df.columns[0], "Exprimés")
        elif annee == 2022:
            df = pd.read_csv(path, dtype=str)
            return extract_data_from_voix(df, annee, tour, "Code du département", "Exprimés")
    except Exception as e:
        print(f"❌ Erreur fichier {path}: {e}")
    return []

# Traitement principal
all_data = []
for label, filename in elections_files.items():
    path = os.path.join(input_dir, filename)
    print(f"🔍 Traitement : {filename}")
    if not os.path.exists(path):
        print(f"⚠️ Fichier non trouvé : {path}")
        continue
    year = int(label.split("_")[0])
    tour = 2 if "_T2" in label else 1
    data = parse_file(path, year, tour)
    all_data.extend(data)
    print(f"✅ {len(data)} lignes extraites pour {filename}")

# Nettoyage final
if all_data:
    df_final = pd.DataFrame(all_data).drop_duplicates()

    # Nettoyage des noms de candidats
    candidats_map = {
        "MACRON": "MACRON EMMANUEL",
        "LE PEN": "LE PEN MARINE",
        "MÉLENCHON": "MELENCHON JEAN LUC",
        "MLENCHON": "MELENCHON JEAN LUC",
        "MELENCHON": "MELENCHON JEAN LUC",
        "HOLLANDE": "HOLLANDE FRANCOIS",
        "SARKOZY": "SARKOZY NICOLAS",
        "ROYAL": "ROYAL SEGOLENE",
        "CHIRAC": "CHIRAC JACQUES",
        "BAYROU": "BAYROU FRANCOIS",
        "JOSPIN": "JOSPIN LIONEL",
        "FILLON": "FILLON FRANCOIS",
        "HAMON": "HAMON BENOIT",
    }
    for pattern, replacement in candidats_map.items():
        df_final.loc[df_final["nom_candidat"].str.contains(pattern, na=False), "nom_candidat"] = replacement

    # Garder seulement les scores valides
    df_final = df_final[(df_final["score"] >= 0) & (df_final["score"] <= 100)]

    # Enregistrement
    output_path = os.path.join(output_dir, "elections_2002_2022.csv")
    df_final.to_csv(output_path, index=False)
    print(f"✅ Fichier final enregistré → {output_path}")
    print(f"📊 {len(df_final)} lignes de données traitées.")
else:
    print("⚠️ Aucune donnée extraite.")
