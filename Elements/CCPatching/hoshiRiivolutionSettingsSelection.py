import sys
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import json
import os
from Elements.CCPatching import hoshiRiivolutionPatcher

# Lire le fichier settings.ini en UTF-8
config = configparser.ConfigParser()
with open('settings.ini', 'r', encoding='utf-8') as f:
    config.read_file(f)

theme = config['settings']['theme']
language = config['settings']['language']

# Charger le fichier de traduction correspondant
translation_file = f'Elements/translations/{language}.json'
if not os.path.exists(translation_file):
    print(f"Translation file {translation_file} not found")
    sys.exit(1)

with open(translation_file, 'r', encoding='utf-8') as f:
    translations = json.load(f)

# Définir les couleurs et styles pour les thèmes
if theme == "Dark":
    bg_color = "#1e1e1e"
    fg_color = "#ffffff"
    button_bg_color = "#7a7aff"
    button_fg_color = "#ffffff"
    section_fg_color = "#7a7aff"
elif theme == "Light":
    bg_color = "#ffffff"
    fg_color = "#000000"
    button_bg_color = "#7a7aff"
    button_fg_color = "#ffffff"
    section_fg_color = "#7a7aff"
else:
    print(f"Unknown theme: {theme}")
    sys.exit(1)

def run_hrss(iso_file, xml_file, mod_folder):
    sections = hoshiRiivolutionPatcher.get_xml_patches(xml_file)

    def create_option_menu(parent, option):
        option_name = option[0]
        if option_name:
            label = tk.Label(parent, text=translations.get(option_name, option_name), font=("Helvetica", 14), bg=bg_color, fg=fg_color)
            label.pack(pady=10)

            choices = option[1]
            choice_patches = {translations.get(choice[0], choice[0]): choice[1] for choice in choices}  # Dictionary of choice name to patch ids

            var = tk.StringVar(parent)

            default_choice = translations.get("Disabled", "Disabled")
            var.set(default_choice)

            dropdown_values = list(choice_patches.keys()) + [translations.get("Disabled", "Disabled")]

            dropdown = ttk.Combobox(parent, textvariable=var, values=dropdown_values, state="readonly", font=("Helvetica", 12), style="TCombobox")
            dropdown.pack()

            return label.winfo_reqheight() + dropdown.winfo_reqheight() + 10, choice_patches, var
        else:
            print(f"Option does not contain a 'name' attribute: {option}")
            return 0, {}, None

    def create_section(parent, sections):
        total_height = 0
        all_patches = {}
        variables = {}
        for section in sections:
            section_name = section[0]
            if section_name:
                label = tk.Label(parent, text=translations.get(section_name, section_name), font=("Helvetica", 16), bg=bg_color, fg=section_fg_color)
                label.pack(pady=10)
                total_height += label.winfo_reqheight() + 10

                options = section[1]
                for option in options:
                    option_height, choice_patches, var = create_option_menu(parent, option)
                    total_height += option_height if option_height else 0
                    all_patches.update(choice_patches)
                    if var:
                        variables[(section_name, option[0])] = (var, choice_patches)  # Store the variable and choice patches

        return total_height, all_patches, variables

    def confirm_settings(sections, all_patches, variables):
        selected_patches = {}
        disable_count = 0
        
        for (section_name, option_name), (var, choice_patches) in variables.items():
            choice_var = var.get()
            
            if choice_var == translations.get("Disabled", "Disabled"):
                disable_count += 1
            else:
                selected_patches[(section_name, option_name)] = choice_patches[choice_var]
        
        if disable_count == len(variables):
            messagebox.showerror("Error", "You can't disable all settings.")
            return

        print("\nSelected options and choices with patch IDs: ")
        for (section_name, option_name), patch_ids in selected_patches.items():
            selected_choice = variables[(section_name, option_name)][0].get()
            print(f"For Option '{option_name}', selected choice: '{selected_choice}'")

        result = messagebox.askyesno("Confirmation", "Are you sure you want to apply these settings?")
        if result:
            print("Settings confirmed")
            flat_patch_ids = [patch_id for patch_list in selected_patches.values() for patch_id in patch_list]
            hoshiRiivolutionPatcher.apply_patches(iso_file, xml_file, mod_folder, flat_patch_ids)
            quit()
        else:
            print("Settings not confirmed")

    if len(sections) == 1 and len(sections[0][1]) == 1:
        single_option = sections[0][1][0]
        patch_ids = [patch_id for _, patches in single_option[1] for patch_id in patches]  # List of all patch IDs
        
        print("\nSelected patches: ")
        for patch_id in patch_ids:
            print(f"{patch_id}: {type(patch_id)}")

        print("Settings confirmed")
        hoshiRiivolutionPatcher.apply_patches(iso_file, xml_file, mod_folder, patch_ids)
    else:
        root = tk.Tk()
        root.title(translations.get("Riivolution Settings Selector", "Riivolution Settings Selector"))
        root.configure(bg=bg_color)

        window_height, all_patches, variables = create_section(root, sections)
        window_height += 150
        root.geometry(f"400x{window_height}+100+100")
        root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=bg_color, background="#ffffff", foreground="#000000", arrowcolor="black", arrowsize=15)
        style.configure("TButton", background=button_bg_color, foreground=button_fg_color)

        confirm_button = tk.Button(root, text=translations.get("Confirm", "Confirm"), width=10, command=lambda: confirm_settings(sections, all_patches, variables), font=("Helvetica", 12), bg=button_bg_color, fg=button_fg_color, relief="flat")
        confirm_button.pack(pady=10)

        root.mainloop()

# Exemple d'appel de la fonction (à ajuster en fonction de vos besoins)
# run_hrss("path/to/iso_file.iso", "path/to/xml_file.xml", "path/to/mod_folder")
