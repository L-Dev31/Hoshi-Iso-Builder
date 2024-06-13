#------------------------------------------------------------------------------
# This file is part of Hoshi - Wii ISO Builder.
# by L-DEV (Léo TOSKU)
#
# Hoshi is free and open-source software released under the GNU General Public
# License version 3 or any later version. You are free to redistribute and/or
# modify Hoshi, but you must adhere to the following conditions:
#
# - Credit the original work ("Hoshi") and its creators: L-DEV (Léo TOSKU) and 
#   Humming Owl (Isaac LIENDO).
#
# See the LICENSE file for more details.
#------------------------------------------------------------------------------

# Standard library imports
import os
import re
import time
import shutil

# Tkinter imports for GUI
import tkinter as tk
from tkinter import messagebox

# Local module imports
from Elements.CCPatching.hoshiBinaryToolsSetup import exec_subprocess, wit_path
from Elements.CCPatching import hoshiRiivolutionSettingsSelection

class ROMBuilder:
    def __init__(self, root, file_paths, start_button):
        self.root = root
        self.file_paths = file_paths
        self.start_button = start_button

    def prompt_id_name_change(self):
        # Set window's colors and fonts
        self.dark_theme = {"bg": "#1e1e1e", "fg": "#ffffff"}
        self.light_theme = {"bg": "#ffffff", "fg": "#000000"}
        self.purple = "#7a7aff"
        self.custom_font = ("Helvetica", 12)

        # Check the ID of the Game
        idCheck = exec_subprocess([wit_path, "ID6", self.file_paths["Base Rom (.iso .wbfs)"].get("1.0", tk.END).strip()])
        if idCheck.returncode == 0:
            original_id = idCheck.stdout.strip() if idCheck.stdout else ""

        # Check the Name of the Game
        nameCheck = exec_subprocess([wit_path, "ANAID", original_id])

        if nameCheck.returncode == 0:
            match = re.search(r'Game Title\s+-+\s+(.*)', nameCheck.stdout)
            original_name = match.group(1)[16:].strip() if match else ""
        else:
            original_name = "Unknown Game"

        mod_id = ""
        mod_name = ""

        dialog = tk.Toplevel(self.root)
        dialog.title("Modify ID and Name")
        dialog.configure(bg=self.dark_theme["bg"])
        dialog.resizable(False, False)

        tk.Label(dialog, text="Original", font=self.custom_font, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(dialog, text="ID :", bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=1, column=0, sticky="w")
        tk.Label(dialog, text="Name :", bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=2, column=0, sticky="w")
        original_id_text = tk.Label(dialog, text=original_id, bg=self.dark_theme["bg"], fg=self.purple, font=self.custom_font)
        original_id_text.grid(row=1, column=1, sticky="w")
        original_name_text = tk.Label(dialog, text=original_name, bg=self.dark_theme["bg"], fg=self.purple, font=self.custom_font)
        original_name_text.grid(row=2, column=1, sticky="w")

        tk.Label(dialog, text="New", font=self.custom_font, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=0, column=2, columnspan=2)
        tk.Label(dialog, text="ID (6 characters):", bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=1, column=2)
        tk.Label(dialog, text="Name (Max 32 characters):", bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=2, column=2)
        mod_id_text = tk.Entry(dialog, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"], font=self.custom_font)
        mod_id_text.grid(row=1, column=3)
        mod_name_text = tk.Entry(dialog, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"], font=self.custom_font)
        mod_name_text.grid(row=2, column=3)

        def on_okay():
            nonlocal mod_id, mod_name
            mod_id = mod_id_text.get().upper()
            mod_name = mod_name_text.get().strip()
            if len(mod_id) < 6 or len(mod_name) == 0 or len(mod_name) > 32:
                messagebox.showerror("Error", "Mod ID must be at least 6 characters long, Mod Name cannot be empty, and must be at most 32 characters long.")
                return
            dialog.destroy()

        def on_cancel():
            nonlocal mod_id, mod_name
            mod_id = ""
            mod_name = ""
            dialog.destroy()

        cancel_button = tk.Button(dialog, text="Cancel", command=on_cancel, bg=self.purple, fg="#ffffff", relief=tk.FLAT, bd=0, padx=10, pady=5, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
        cancel_button.grid(row=3, column=1, pady=10)
        ok_button = tk.Button(dialog, text="OK", command=on_okay, bg=self.purple, fg="#ffffff", relief=tk.FLAT, bd=0, padx=10, pady=5, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
        ok_button.grid(row=3, column=3, pady=10)

        dialog.wait_window(dialog)
        return mod_id, mod_name
    
    def continue_building(self):
        try:
            destination_path = self.file_paths["Destination Rom (.iso .wbfs)"].get("1.0", tk.END).strip()
            riivolution_file = self.file_paths["Riivolution file (.xml)"].get("1.0", tk.END).strip()
            riivolution_folder = self.file_paths["Riivolution patch folder"].get("1.0", tk.END).strip()
            base_rom_file = self.file_paths["Base Rom (.iso .wbfs)"].get("1.0", tk.END).strip()

            if not destination_path or not riivolution_file or not base_rom_file:
                raise ValueError("Please fill in all required fields.")

            elements_directory = "Elements"
            os.makedirs(elements_directory, exist_ok=True)

            # Clean temporary files before starting
            self.clean_files()
            # Extract the base ROM
            self.extract_rom(base_rom_file)
            # Check the game ID
            game_id = self.check_id(base_rom_file)            
            # Patch the ROM with the selected patches
            self.patch_rom(riivolution_folder)
            # Run the Riivolution settings selection and apply patches
            self.custom_code_patching(game_id, base_rom_file, riivolution_file, riivolution_folder)
            # Build the final ROM
            self.build_rom(destination_path)
            # Clean temporary files after completion
            self.clean_files()
            # Success message
            messagebox.showinfo("Success", "ROM successfully patched!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.start_button.config(text="Start Building !")
            self.root.update()

    def clean_files(self):
        print("Cleaning Files...")

        # Patch Files
        if os.path.exists("temp.xml"):
            os.remove("temp.xml")
            print("Temporary Patch files 1 removed")
        if os.path.exists("temp.txt"):
            os.remove("temp.txt")
            print("Temporary Patch files 2 removed")

        # Game Files
        if os.path.exists('temp'):
            shutil.rmtree('temp')
            print("Temporary Game files removed")
        else:
            print("temp directory not found. Skip")
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')

    def extract_rom(self, base_rom_file):
        print("Extracting ROM:")
        exec_subprocess([wit_path, "extract", base_rom_file, ".\\temp"])
        print("Base Rom extracted successfully")
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_id(self, base_rom_file):
        id_check = exec_subprocess([wit_path, "ID6", base_rom_file])
        game_id = id_check.stdout[:3]
        return game_id

    def custom_code_patching(self, game_id, base_rom_file, riivolution_file, riivolution_folder):
        hoshiRiivolutionSettingsSelection.run_hrss(base_rom_file,riivolution_file,riivolution_folder)
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')

    def patch_rom(self, riivolution_folder):
        print("Patching ROM:")
        destination_folder = ".\\temp\\files"
        for root, _, files in os.walk(riivolution_folder):
            for file in files:
                src_path = os.path.join(root, file)
                relative_path = os.path.relpath(src_path, riivolution_folder)
                dest_path = os.path.join(destination_folder, relative_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                print(f"Copying and replacing: {relative_path}")
                shutil.copy2(src_path, dest_path)
        print("All files copied and replaced.")
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')

    def build_rom(self, destination_path):
        print("Rom building:")

        if os.path.exists(destination_path):
            os.remove(destination_path)

        response = messagebox.askyesno("ID and Name Change", "Do you want to change the ID and name of the game?")
        if response:
            mod_id, mod_name = self.prompt_id_name_change()
            exec_subprocess([wit_path, "copy", ".\\temp", destination_path, "--id=" + mod_id, "--name=" + mod_name])
        else:
            exec_subprocess([wit_path, "copy", ".\\temp", destination_path])
        print("The Iso was successfully created")
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')


