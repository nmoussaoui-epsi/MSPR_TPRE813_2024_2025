import pandas as pd
import numpy as np
import joblib
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from src.db.db_config import conn, Engine

# Créer les dossiers figures et models s'ils n'existent pas
figures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "figures")
models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models")

os.makedirs(figures_dir, exist_ok=True)
os.makedirs(models_dir, exist_ok=True)

# Afficher les informations de départ
print("Chargement des données depuis la base PostgreSQL...")

# Requête pour récupérer les données utiles
df = pd.read_sql("""
SELECT 
    s.code_departement, s.annee,
    s.taux_chomage,
    s.cmu_taux_couverture,
    s.rsa_nb_allocataires,
    s.beneficiaires_minimum_vieillesse,
    s.taux_de_pauvrete_30_39,
    s.taux_de_pauvrete_40_49,
    s.taux_de_pauvrete_50_59,
    s.taux_de_pauvrete_60_74,
    s.taux_de_pauvrete_75_plus,
    s.taux_de_pauvrete_ensemble,
    s.taux_de_pauvrete_moins_30,
    r.resultat_gauche,
    r.resultat_droite,
    r.resultat_centre,
    r.resultat_extreme_droite,
    r.resultat_extreme_gauche
FROM indicateurs_sociaux s
JOIN resultats_elections r
ON s.code_departement = r.code_departement AND s.annee = r.annee
""", Engine)

# Vérifier les valeurs manquantes
print("\nValeurs manquantes par colonne:")
print(df.isna().sum())
print(f"Total de valeurs manquantes: {df.isna().sum().sum()}")

# Créer le label : bord politique majoritaire
def get_majority(row):
    scores = {
        'gauche': row['resultat_gauche'],
        'droite': row['resultat_droite'],
        'centre': row['resultat_centre'],
        'extreme_droite': row['resultat_extreme_droite'],
        'extreme_gauche': row['resultat_extreme_gauche']
    }
    return max(scores, key=scores.get)

df["label"] = df.apply(get_majority, axis=1)

# Afficher la distribution des classes
print("\nDistribution des classes:")
print(df["label"].value_counts())

# Définir X (features) et y (target)
X = df.drop(columns=[
    'code_departement', 'annee',
    'resultat_gauche', 'resultat_droite', 'resultat_centre',
    'resultat_extreme_droite', 'resultat_extreme_gauche',
    'label'
])
y = df["label"]

# Split train/test (avant imputation pour éviter des fuites de données)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nDimensions du jeu d'entraînement: {X_train.shape}")
print(f"Dimensions du jeu de test: {X_test.shape}")

# Créer un pipeline pour prétraiter les données et entraîner le modèle
print("\nCréation et entraînement du modèle avec pipeline...")
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),  # Remplacer les valeurs manquantes par la médiane
    ('scaler', StandardScaler()),                  # Normaliser les données
    ('classifier', RandomForestClassifier(         # Classifier avec RandomForest
        n_estimators=100,                         # Nombre d'arbres
        max_depth=10,                             # Profondeur max des arbres
        min_samples_split=5,                      # Nombre min d'échantillons pour diviser un nœud
        min_samples_leaf=2,                       # Nombre min d'échantillons dans une feuille
        random_state=42                           # Pour reproductibilité
    ))
])

# Entraîner le pipeline
pipeline.fit(X_train, y_train)

# Évaluer le modèle
y_pred = pipeline.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Matrice de confusion
print("\nMatrice de confusion:")
conf_matrix = confusion_matrix(y_test, y_pred)
print(conf_matrix)

# Créer la visualisation de la matrice de confusion et la sauvegarder
plt.figure(figsize=(10, 8))
class_names = sorted(df["label"].unique())
disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=class_names)
disp.plot(cmap=plt.cm.Blues, values_format='d')
plt.title('Matrice de confusion - Prédiction de tendances politiques')
plt.tight_layout()

# Sauvegarder la matrice de confusion dans le dossier figures
confusion_matrix_path = os.path.join(figures_dir, "confusion_matrix.png")
plt.savefig(confusion_matrix_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"\nMatrice de confusion sauvegardée dans: {confusion_matrix_path}")

# Créer un graphique pour l'importance des features
feature_importances = pipeline.named_steps['classifier'].feature_importances_
feature_names = X.columns
importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': feature_importances})
importance_df = importance_df.sort_values('Importance', ascending=False)

print("\nImportance des features:")
print(importance_df)

# Visualiser l'importance des features et sauvegarder
plt.figure(figsize=(12, 8))
sns.barplot(x='Importance', y='Feature', data=importance_df)
plt.title('Importance des indicateurs sociaux pour la prédiction politique')
plt.tight_layout()

# Sauvegarder le graphique d'importance des features
feature_importance_path = os.path.join(figures_dir, "feature_importance.png")
plt.savefig(feature_importance_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Graphique d'importance des features sauvegardé dans: {feature_importance_path}")

# Sauvegarder le pipeline complet (prétraitements + modèle) dans le dossier models
pipeline_path = os.path.join(models_dir, "model_pipeline.pkl")
joblib.dump(pipeline, pipeline_path)
print(f"\nPipeline complet (prétraitements + modèle) sauvegardé dans: {pipeline_path}")

# Sauvegarder séparément le modèle seul pour compatibilité
model_path = os.path.join(models_dir, "model_rf.pkl")
joblib.dump(pipeline.named_steps['classifier'], model_path)
print(f"Modèle entraîné (sans prétraitements) sauvegardé dans: {model_path}")

print("\nProcessus d'entraînement terminé avec succès!")