import pandas as pd
import unicodedata
from sqlalchemy import text
from db.db_config import conn, Engine

def run():
    print("Initialisation de la base de données...")

    # 1. Créer les tables si elles n'existent pas
    schema_sql = """
    CREATE TABLE IF NOT EXISTS departement (
        code_departement INT PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS annee (
        annee INT PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS indicateurs_sociaux (
        id SERIAL PRIMARY KEY,
        code_departement INT,
        annee INT,
        taux_chomage FLOAT,
        cmu_nb_allocataires INT,
        cmu_taux_couverture FLOAT,
        rsa_nb_allocataires FLOAT,
        beneficiaires_minimum_vieillesse INT,
        taux_de_pauvrete_30_39 INT,
        taux_de_pauvrete_40_49 INT,
        taux_de_pauvrete_50_59 INT,
        taux_de_pauvrete_60_74 INT,
        taux_de_pauvrete_75_plus INT,
        taux_de_pauvrete_ensemble INT,
        taux_de_pauvrete_moins_30 INT,
        FOREIGN KEY (code_departement) REFERENCES departement(code_departement),
        FOREIGN KEY (annee) REFERENCES annee(annee)
    );

    CREATE TABLE IF NOT EXISTS indicateurs_population (
        id SERIAL PRIMARY KEY,
        code_departement INT,
        annee INT,
        part_0_24 INT,
        part_25_59 INT,
        part_60_plus INT,
        part_75_plus INT,
        hommes INT,
        femmes INT,
        total INT,
        FOREIGN KEY (code_departement) REFERENCES departement(code_departement),
        FOREIGN KEY (annee) REFERENCES annee(annee)
    );

    CREATE TABLE IF NOT EXISTS indicateurs_education (
        id SERIAL PRIMARY KEY,
        code_departement INT,
        annee INT,
        taux_reussite_brevet INT,
        taux_reussite_bac_general INT,
        taux_reussite_bac_techno INT,
        taux_reussite_bac_pro INT,
        taux_reussite_bac_ensemble INT,
        taux_reussite_bep INT,
        taux_reussite_bts INT,
        taux_reussite_cap INT,
        FOREIGN KEY (code_departement) REFERENCES departement(code_departement),
        FOREIGN KEY (annee) REFERENCES annee(annee)
    );

    CREATE TABLE IF NOT EXISTS indicateurs_logement (
        id SERIAL PRIMARY KEY,
        code_departement INT,
        annee INT,
        nb_logements_sociaux INT,
        FOREIGN KEY (code_departement) REFERENCES departement(code_departement),
        FOREIGN KEY (annee) REFERENCES annee(annee)
    );

    CREATE TABLE IF NOT EXISTS indicateurs_criminalite (
        id SERIAL PRIMARY KEY,
        code_departement INT,
        annee INT,
        taux_occupation_carcerale INT,
        auteurs_poursuivables INT,
        FOREIGN KEY (code_departement) REFERENCES departement(code_departement),
        FOREIGN KEY (annee) REFERENCES annee(annee)
    );

    CREATE TABLE IF NOT EXISTS resultats_elections (
        id SERIAL PRIMARY KEY,
        code_departement INT,
        annee INT,
        resultat_gauche FLOAT,
        resultat_droite FLOAT,
        resultat_centre FLOAT,
        resultat_extreme_droite FLOAT,
        resultat_extreme_gauche FLOAT,
        resultat_autre FLOAT,
        FOREIGN KEY (code_departement) REFERENCES departement(code_departement),
        FOREIGN KEY (annee) REFERENCES annee(annee)
    );
    """

    conn.execute(text(schema_sql))

    # 2. Charger le dataset
    print("Chargement des données fusionnées...")
    df = pd.read_csv("data/clean/merged_dataset.csv")
    df.columns = [
        unicodedata.normalize("NFKD", c)
        .encode("ascii", "ignore")
        .decode("utf-8")
        .lower()
        .replace(" ", "_")
        .replace("___", "__")
        .replace("__", "_")
        for c in df.columns
    ]

    # 3. Remplir departement et annee
    existing_deps = pd.read_sql("SELECT code_departement FROM departement", Engine)
    new_deps = df[["code_departement"]].drop_duplicates()
    new_deps = new_deps[~new_deps["code_departement"].isin(existing_deps["code_departement"])]
    if not new_deps.empty:
        new_deps.to_sql("departement", Engine, if_exists="append", index=False)
    existing_years = pd.read_sql("SELECT annee FROM annee", Engine)
    new_years = df[["annee"]].drop_duplicates()
    new_years = new_years[~new_years["annee"].isin(existing_years["annee"])]

    if not new_years.empty:
        new_years.to_sql("annee", Engine, if_exists="append", index=False)

    # 4. Fonction générique pour insérer dans les sous-tables
    def insert_subset(table_name, columns, column_mappings=None):
        subset = df[["code_departement", "annee"] + columns].copy()
        
        # Remplacer les noms de colonnes par ceux définis dans le schéma
        if column_mappings:
            subset.columns = ["code_departement", "annee"] + [column_mappings.get(col, col.split("__")[-1]) for col in columns]
        else:
            subset.columns = ["code_departement", "annee"] + [col.split("__")[-1] for col in columns]
        
        subset.to_sql(table_name, Engine, if_exists="append", index=False)
    
    insert_subset("indicateurs_sociaux", [
        "taux_de_chomage_localise_par_departement",
        "cmu_c_nb_allocataires", "cmu_c_taux_de_couverture",
        "rsa_nb_allocataires", "beneficiaires_du_minimum_vieillesse",
        "taux_de_pauvrete_30_a_39_ans", "taux_de_pauvrete_40_a_49_ans",
        "taux_de_pauvrete_50_a_59_ans", "taux_de_pauvrete_60_a_74_ans",
        "taux_de_pauvrete_75_ans_ou_plus", "taux_de_pauvrete_ensemble",
        "taux_de_pauvrete_moins_de_30_ans"
    ], {
        "taux_de_chomage_localise_par_departement": "taux_chomage",
        "cmu_c_nb_allocataires": "cmu_nb_allocataires",
        "cmu_c_taux_de_couverture": "cmu_taux_couverture",
        "rsa_nb_allocataires": "rsa_nb_allocataires",
        "beneficiaires_du_minimum_vieillesse": "beneficiaires_minimum_vieillesse",
        "taux_de_pauvrete_30_a_39_ans": "taux_de_pauvrete_30_39",
        "taux_de_pauvrete_40_a_49_ans": "taux_de_pauvrete_40_49",
        "taux_de_pauvrete_50_a_59_ans": "taux_de_pauvrete_50_59",
        "taux_de_pauvrete_60_a_74_ans": "taux_de_pauvrete_60_74",
        "taux_de_pauvrete_75_ans_ou_plus": "taux_de_pauvrete_75_plus",
        "taux_de_pauvrete_ensemble": "taux_de_pauvrete_ensemble",
        "taux_de_pauvrete_moins_de_30_ans": "taux_de_pauvrete_moins_30"
    })

    insert_subset("indicateurs_population", [
        "estimations_de_population_part_des_0_24_ans", 
        "estimations_de_population_part_des_25_59_ans",
        "estimations_de_population_part_des_60_ans_ou_plus", 
        "estimations_de_population_dont_part_des_75_ans_ou_plus",
        "estimations_de_population_hommes", 
        "estimations_de_population_femmes",
        "estimations_de_population_ensemble"
    ], {
        "estimations_de_population_part_des_0_24_ans": "part_0_24",
        "estimations_de_population_part_des_25_59_ans": "part_25_59",
        "estimations_de_population_part_des_60_ans_ou_plus": "part_60_plus",
        "estimations_de_population_dont_part_des_75_ans_ou_plus": "part_75_plus",
        "estimations_de_population_hommes": "hommes",
        "estimations_de_population_femmes": "femmes",
        "estimations_de_population_ensemble": "total"
    })

    insert_subset("indicateurs_education", [
    "diplome_national_du_brevet_taux_de_reussite", 
    "bac_general_taux_de_reussite",
    "bac_technologique_taux_de_reussite", 
    "bac_professionnel_taux_de_reussite",
    "tous_baccalaureats_taux_de_reussite",
    "brevet_detudes_professionnelles_bep_et_brevet_detudes_professionnelles_agricoles_bepa_taux_de_reussite",
    "brevet_de_technicien_superieur_bts_et_brevet_de_technicien_superieur_agricole_btsa_taux_de_reussite",
    "certificat_daptitude_professionnelle_cap_et_certificat_daptitude_professionnelle_agricole_capa_taux_de_reussite"
    ], {
        "diplome_national_du_brevet_taux_de_reussite": "taux_reussite_brevet",
        "bac_general_taux_de_reussite": "taux_reussite_bac_general",
        "bac_technologique_taux_de_reussite": "taux_reussite_bac_techno",
        "bac_professionnel_taux_de_reussite": "taux_reussite_bac_pro",
        "tous_baccalaureats_taux_de_reussite": "taux_reussite_bac_ensemble",
        "brevet_detudes_professionnelles_bep_et_brevet_detudes_professionnelles_agricoles_bepa_taux_de_reussite": "taux_reussite_bep",
        "brevet_de_technicien_superieur_bts_et_brevet_de_technicien_superieur_agricole_btsa_taux_de_reussite": "taux_reussite_bts",
        "certificat_daptitude_professionnelle_cap_et_certificat_daptitude_professionnelle_agricole_capa_taux_de_reussite": "taux_reussite_cap"
    })

    insert_subset("indicateurs_logement", ["nb_logements_sociaux_pour_10000_habitants"], {
        "nb_logements_sociaux_pour_10000_habitants": "nb_logements_sociaux"
    })    
    insert_subset("indicateurs_criminalite", ["taux_occupation_carcerale", "auteurs_poursuivables"])
    insert_subset("resultats_elections", [
        "resultat_gauche", "resultat_droite", "resultat_centre",
        "resultat_extreme_droite", "resultat_extreme_gauche", "resultat_autre"
    ])

    print("Données injectées avec succès dans PostgreSQL.")

