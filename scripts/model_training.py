import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import joblib
from sklearn.utils.multiclass import unique_labels

# Charger les données
data_path = "../data/final/final_dataset_complet.csv"
df = pd.read_csv(data_path)

# Features sélectionnées
features = [
    "taux_chomage",
    "nombre_auteurs_poursuivables",
    "taux_pauvrete",
    "population",
    "revenu_median",
    "logements_sociaux"
]
target = "bord_politique"

# Nettoyage des données
df_clean = df.dropna(subset=features + [target])

if df_clean.empty:
    print("Erreur : aucune donnée exploitable même avec les nouvelles données complétées.")
    exit()

# Encodage du target
le = LabelEncoder()
df_clean["target_encoded"] = le.fit_transform(df_clean[target])

# Split des données
X = df_clean[features]
y = df_clean["target_encoded"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Entraînement du modèle
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Prédictions
y_pred = model.predict(X_test)

# Évaluation
print("Accuracy score :", round(accuracy_score(y_test, y_pred), 2))
print("\nRapport de classification :")
labels_present = unique_labels(y_test, y_pred)
target_names_present = le.inverse_transform(labels_present)
print(classification_report(y_test, y_pred, labels=labels_present, target_names=target_names_present))

# Importance des variables
importances = model.feature_importances_
plt.figure(figsize=(8, 5))
plt.barh(features, importances)
plt.title("Importance des variables")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()

# Sauvegarde du modèle
os.makedirs("../models", exist_ok=True)
joblib.dump(model, "../models/random_forest_model.pkl")
print("Modèle sauvegardé dans /models")
