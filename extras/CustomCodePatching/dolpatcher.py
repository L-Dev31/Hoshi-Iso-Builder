from zipfile import ZipFile
from pathlib import Path
from platform import system
from tkinter import filedialog
from sys import argv
import os
import subprocess
import shutil

SYATI = os.path.join(os.path.dirname(__file__), "Syati-main")
#SYATISETUP = os.path.join(os.path.dirname(__file__), "syatisetup.exe")
PATCHES = Path('Elements\\CustomCodePatching\\patches.xml').absolute()
HOME_DIR = Path(__file__).parent.absolute()
SYSTEM = system().lower()

if __name__ == '__main__':
    if len(argv) < 3:
        raise Exception("Did not specify a target region and DOL file path.")
    region = argv[1]
    dol_file_path = argv[2]
    if SYSTEM != 'windows':
        raise Exception("Non-Windows systems are not supported ATM.")

    os.chdir(SYATI)

    if not os.path.exists("deps"):
        os.mkdir('deps')

    if not os.path.exists('dols'):
        os.mkdir('dols')

    os.chdir('deps')

    os.chdir('../')

    #subprocess.run(SYATISETUP)

    shutil.copyfile(dol_file_path, f'dols\\{region}.dol')

    subprocess.run(f'python buildloader.py {region}', shell=True)

    subprocess.run(f'wit dolpatch dols\\{region}.dol xml={PATCHES}')

    loader_file = os.path.join(SYATI, "dols", f"{region}.dol")
    shutil.copyfile(loader_file, dol_file_path)

    print(f"Patched DOL saved to: {dol_file_path}")

    print("Finished!")
