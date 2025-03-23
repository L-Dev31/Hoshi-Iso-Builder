#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import HoshiIsoBuilder

def check_tools():
    """Vérifie la présence des outils externes (GeckoLoader et wit)."""
    tools_missing = []

    # Vérifier GeckoLoader
    geckoloader_path = os.path.join("tools", "geckoloader", "GeckoLoader.py")
    if not os.path.exists(geckoloader_path):
        tools_missing.append("GeckoLoader (tools/geckoloader/GeckoLoader.py)")

    # Vérifier wit
    wit_path = os.path.join("tools", "wit", "windows", "wit.exe")
    if not os.path.exists(wit_path):
        tools_missing.append("wit (tools/wit/windows/wit.exe)")

    # Afficher un message d'erreur si des outils manquent
    if tools_missing:
        messagebox.showerror(
            "Outils manquants",
            "Les outils suivants sont manquants :\n\n" + "\n".join(tools_missing) + "\n\nVeuillez les installer avant de continuer."
        )
        return False

    return True

if __name__ == "__main__":
    root = tk.Tk()
    
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'icon.png')
    if os.path.exists(icon_path):
        icon = ImageTk.PhotoImage(Image.open(icon_path))
        root.iconphoto(True, icon)
    
    # Vérifier les outils avant de lancer l'application
    if check_tools():
        app = HoshiIsoBuilder(root)
        root.mainloop()