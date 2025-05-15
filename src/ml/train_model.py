import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from src.db.db_config import Engine

# Créer les dossiers figures et models
figures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "figures")
models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")
os.makedirs(figures_dir, exist_ok=True)
os.makedirs(models_dir, exist_ok=True)

print("Chargement des données depuis PostgreSQL...")

# Requête SQL complète avec tous les JOIN
df = pd.read_sql("""
SELECT 
    s.code_departement, s.annee,
    s.taux_chomage, s.cmu_nb_allocataires, s.cmu_taux_couverture,
    s.rsa_nb_allocataires, s.beneficiaires_minimum_vieillesse,
    s.taux_de_pauvrete_30_39, s.taux_de_pauvrete_40_49, s.taux_de_pauvrete_50_59,
    s.taux_de_pauvrete_60_74, s.taux_de_pauvrete_75_plus,
    s.taux_de_pauvrete_ensemble, s.taux_de_pauvrete_moins_30,

    c.taux_occupation_carcerale, c.auteurs_poursuivables,

    e.taux_reussite_brevet, e.taux_reussite_bac_general, e.taux_reussite_bac_techno,
    e.taux_reussite_bac_pro, e.taux_reussite_bac_ensemble,
    e.taux_reussite_bep, e.taux_reussite_bts, e.taux_reussite_cap,

    p.part_0_24, p.part_25_59, p.part_60_plus, p.part_75_plus,
    p.hommes, p.femmes, p.total,

    l.nb_logements_sociaux,

    r.resultat_gauche, r.resultat_droite, r.resultat_centre,
    r.resultat_extreme_droite, r.resultat_extreme_gauche

FROM indicateurs_sociaux s
JOIN resultats_elections r ON s.code_departement = r.code_departement AND s.annee = r.annee
LEFT JOIN indicateurs_criminalite c ON s.code_departement = c.code_departement AND s.annee = c.annee
LEFT JOIN indicateurs_education e ON s.code_departement = e.code_departement AND s.annee = e.annee
LEFT JOIN indicateurs_population p ON s.code_departement = p.code_departement AND s.annee = p.annee
LEFT JOIN indicateurs_logement l ON s.code_departement = l.code_departement AND s.annee = l.annee
""", Engine)

# Gérer les valeurs manquantes
print("\nValeurs manquantes par colonne:")
print(df.isna().sum())
print(f"Total: {df.isna().sum().sum()}")

# Créer le label
def get_majority(row):
    return max({
        'gauche': row['resultat_gauche'],
        'droite': row['resultat_droite'],
        'centre': row['resultat_centre'],
        'extreme_droite': row['resultat_extreme_droite'],
        'extreme_gauche': row['resultat_extreme_gauche']
    }, key=lambda k: row[f'resultat_{k}'])

df["label"] = df.apply(get_majority, axis=1)

# Définir X et y
X = df.drop(columns=[
    "code_departement", "annee",
    "resultat_gauche", "resultat_droite", "resultat_centre",
    "resultat_extreme_droite", "resultat_extreme_gauche",
    "label"
])
y = df["label"]

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nDimensions X_train : {X_train.shape}")
print(f"Dimensions X_test : {X_test.shape}")

# Pipeline
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(
        n_estimators=100, max_depth=10, min_samples_split=5,
        min_samples_leaf=2, random_state=42
    ))
])

# Entraînement
pipeline.fit(X_train, y_train)

# Évaluation
y_pred = pipeline.predict(X_test)
print("\nClassification report :")
print(classification_report(y_test, y_pred))

# Matrice de confusion
conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 8))
disp = ConfusionMatrixDisplay(conf_matrix, display_labels=sorted(df["label"].unique()))
disp.plot(cmap=plt.cm.Blues, values_format='d')
plt.title("Matrice de confusion")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "confusion_matrix.png"), dpi=300)
plt.close()

# Importance des features
importances = pipeline.named_steps['classifier'].feature_importances_
feature_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": importances
}).sort_values("Importance", ascending=False)

print("\nImportance des variables :")
print(feature_df)

plt.figure(figsize=(12, 8))
sns.barplot(x="Importance", y="Feature", data=feature_df)
plt.title("Importance des variables dans la prédiction")
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "feature_importance.png"), dpi=300)
plt.close()

# Sauvegarde du modèle
joblib.dump(pipeline, os.path.join(models_dir, "model_pipeline.pkl"))
joblib.dump(pipeline.named_steps['classifier'], os.path.join(models_dir, "model_rf.pkl"))

print("\nModèle entraîné et sauvegardé avec succès.")
