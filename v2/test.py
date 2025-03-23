import os
import sys
import subprocess

selected = "smgrav"

if selected == "smg0" :
    DEFAULT_GAME_PATH = "F:\\smg_modding\\FILE\\GAME\\SMG2.wbfs"
    DEFAULT_XML_PATH = "F:\\smg_modding\\FILE\\MOD\\Super Mario Galaxy Zero\\riivolution\\SMG0-USA.xml"
    DEFAULT_MODS_PATH = "F:\\smg_modding\\FILE\\MOD\\Super Mario Galaxy Zero\\SMG0"
elif selected == "smgrav":
    DEFAULT_GAME_PATH = r"F:\smg_modding\FILE\GAME\SMG2.wbfs"
    DEFAULT_XML_PATH = r"C:\Users\leoto\Downloads\SuperMarioGravity_NewDemo.xml"
    DEFAULT_MODS_PATH = r"F:\smg_modding\FILE\MOD\SuperMarioGravity New Demo\SuperMarioGravity_NewDemo"
elif selected == "nmg":
    DEFAULT_GAME_PATH = r"F:\smg_modding\FILE\GAME\SMG2.wbfs"
    DEFAULT_XML_PATH = r"F:\smg_modding\FILE\MOD\Neo Mario Galaxy\nmg"
    DEFAULT_MODS_PATH = r"F:\smg_modding\FILE\MOD\Neo Mario Galaxy\riivolution\nmg.xml"

WINDOWS, LINUX = range(2)
SYSTEM_OS = WINDOWS if sys.platform == "win32" else LINUX

GECKOLOADER_PATH = os.path.abspath("tools/geckoloader/GeckoLoader.py")
WIT_PATH = os.path.abspath("tools/wit/windows/wit.exe" if SYSTEM_OS == WINDOWS else "tools/wit/linux/wit")

def check_file_exists(path, name):
    if os.path.exists(path):
        print(f"✔ {name} trouvé : {path}")
        return True
    else:
        print(f"❌ Erreur : {name} introuvable ({path})")
        return False

def main():
    # Vérifiez l'existence des fichiers nécessaires
    all_paths_exist = all([
        check_file_exists(DEFAULT_GAME_PATH, "Fichier de jeu"),
        check_file_exists(DEFAULT_XML_PATH, "Fichier XML"),
        check_file_exists(DEFAULT_MODS_PATH, "Dossier de mods"),
        check_file_exists(GECKOLOADER_PATH, "GeckoLoader"),
        check_file_exists(WIT_PATH, "WIT")
    ])
    
    if not all_paths_exist:
        return

    print("\nTous les fichiers requis sont présents. Lancement de main.py...")
    
    subprocess.run([
        sys.executable, "main.py",
        "--game", DEFAULT_GAME_PATH,
        "--xml", DEFAULT_XML_PATH,
        "--mods", DEFAULT_MODS_PATH
    ])

if __name__ == "__main__":
    main()