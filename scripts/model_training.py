import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import joblib

# Charger les données
data_path = "../data/final/final_dataset.csv"
df = pd.read_csv(data_path)

# Sélection minimale de features avec peu ou pas de valeurs manquantes
features = ["taux_chomage"]
target = "bord_politique"

# Nettoyage
df_clean = df.dropna(subset=features + [target])

if df_clean.empty:
    print("Erreur : aucune donnée exploitable même avec la sélection minimale.")
    exit()

# Encodage de la cible
le = LabelEncoder()
df_clean["target_encoded"] = le.fit_transform(df_clean[target])

# Séparation des données
X = df_clean[features]
y = df_clean["target_encoded"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modèle Random Forest
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Évaluation
y_pred = model.predict(X_test)
print("Accuracy score :", round(accuracy_score(y_test, y_pred), 2))
print("\nRapport de classification :")
from sklearn.utils.multiclass import unique_labels

# Identifier les classes réellement présentes dans y_test
labels_present = unique_labels(y_test, y_pred)
target_names_present = le.inverse_transform(labels_present)

print(classification_report(y_test, y_pred, labels=labels_present, target_names=target_names_present))


# Importance des features
importances = model.feature_importances_
plt.figure(figsize=(6, 4))
plt.barh(features, importances)
plt.title("Importance des variables")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()

# Sauvegarde
os.makedirs("../models", exist_ok=True)
joblib.dump(model, "../models/random_forest_model.pkl")
print("Modèle sauvegardé dans /models")
