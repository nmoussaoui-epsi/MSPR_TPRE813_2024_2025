# MSPR TPRE813 – Big Data & Analyse de données

## Objectif du projet

Ce projet a pour but de réaliser une preuve de concept (POC) pour une start-up fictive spécialisée dans le conseil en campagnes électorales. L’objectif est de prédire les tendances électorales en analysant des indicateurs socio-économiques (emploi, sécurité, population, entreprises, etc.) à l’aide de techniques de data science.

## Installation et configuration

Pour travailler sur ce projet, suivez les étapes ci-dessous :

### 1. Cloner le dépôt

Clonez le projet sur votre machine locale à l'aide de la commande suivante :

```bash
git clone <URL_DU_DEPOT>
cd MSPR_TPRE813_2024_2025
```

### 2. Installer les dépendances

Assurez-vous d'avoir Python installé sur votre machine (version 3.8 ou supérieure). Ensuite, installez les dépendances nécessaires en exécutant :

```bash
pip install -r requirements.txt
```

### 3. Configurer le fichier `.env`

Créez un fichier `.env` à la racine du projet et ajoutez-y les informations suivantes :

```
INSEE_CLIENT_ID=<VOTRE_CLIENT_ID>
INSEE_CLIENT_SECRET=<VOTRE_CLIENT_SECRET>
```

Pour obtenir ces identifiants, créez un compte sur le site de l'INSEE ([https://api.insee.fr/](https://api.insee.fr/)) et générez vos clés d'API.

### 4. Lancer le projet

Une fois les étapes précédentes terminées, vous pouvez exécuter les scripts Python ou les notebooks associés au projet pour commencer à travailler sur les données.
