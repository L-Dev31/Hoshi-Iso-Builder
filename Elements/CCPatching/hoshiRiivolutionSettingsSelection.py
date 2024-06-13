import sys
import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from Elements.CCPatching import hoshiRiivolutionPatcher

def run_hrss(iso_file, xml_file, mod_folder):
    sections = hoshiRiivolutionPatcher.get_xml_patches(xml_file)

    def create_option_menu(parent, option):
        option_name = option[0]
        if option_name:
            label = tk.Label(parent, text=option_name, font=("Helvetica", 14), bg="#1e1e1e", fg="#ffffff")
            label.pack(pady=10)

            choices = option[1]
            choice_patches = {choice[0]: choice[1] for choice in choices}  # Dictionary of choice name to patch ids

            var = tk.StringVar(parent)

            default_choice = "" if option_name.lower() == "disabled" else "Disabled"
            var.set(default_choice)

            dropdown_values = list(choice_patches.keys()) + ["Disabled"]

            dropdown = ttk.Combobox(parent, textvariable=var, values=dropdown_values, state="readonly", font=("Helvetica", 12), style="Dark.TCombobox")
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
                label = tk.Label(parent, text=section_name, font=("Helvetica", 16), bg="#1e1e1e", fg="#7a7aff")
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
            
            if choice_var == "Disabled":
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
        root.title("Riivolution Settings Selector")
        root.configure(bg="#1e1e1e")

        window_height, all_patches, variables = create_section(root, sections)
        window_height += 150
        root.geometry(f"400x{window_height}+100+100")
        root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", relief="flat")

        confirm_button = tk.Button(root, text="Confirm", width=10, command=lambda: confirm_settings(sections, all_patches, variables), font=("Helvetica", 12), bg="#7a7aff", fg="#ffffff", relief="flat")
        confirm_button.pack(pady=10)

        root.mainloop()
