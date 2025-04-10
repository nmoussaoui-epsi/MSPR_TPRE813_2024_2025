import os
import subprocess
import sys

def run_script(script_path):
    """Exécute un script Python et affiche sa sortie en temps réel"""
    print(f"🚀 Exécution de {os.path.basename(script_path)}...")
    
    try:
        # Exécuter le script avec le processus Python actuel
        process = subprocess.Popen([sys.executable, script_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True)
        
        # Afficher la sortie en temps réel
        for line in process.stdout:
            print(f"  {line.strip()}")
            
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ {os.path.basename(script_path)} terminé avec succès\n")
            return True
        else:
            print(f"❌ {os.path.basename(script_path)} a échoué (code {process.returncode})\n")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {script_path}: {e}\n")
        return False

def main():
    """Exécute tous les scripts de récupération de données dans le bon ordre"""
    print("🔍 Initialisation des données du projet...\n")
    
    # Chemin du dossier des scripts
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Liste des scripts à exécuter dans l'ordre
    scripts_to_run = [
        os.path.join(scripts_dir, "get_chomage.py"),
        os.path.join(scripts_dir, "get_crimininalite.py"),
        os.path.join(scripts_dir, "get_elections.py"),
        os.path.join(scripts_dir, "get_population.py"),
        os.path.join(scripts_dir, "get_pauvrete.py"),
        os.path.join(scripts_dir, "get_revenu.py"),
    ]
    
    success_count = 0
    
    for script in scripts_to_run:
        if os.path.exists(script):
            if run_script(script):
                success_count += 1
        else:
            print(f"⚠️ Script introuvable: {script}\n")
    
    # Résumé
    print(f"📊 Récapitulatif: {success_count}/{len(scripts_to_run)} scripts exécutés avec succès")
    
    if success_count == len(scripts_to_run):
        print("✨ Toutes les données ont été correctement initialisées!")
    else:
        print("⚠️ Certains scripts ont échoué. Consultez les messages ci-dessus pour plus de détails.")

if __name__ == "__main__":
    main()
