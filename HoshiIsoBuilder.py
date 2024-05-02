import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import webbrowser
import json
import time
import shutil
import re
import configparser

def is_wit_installed():
    try:
        subprocess.run(['wit', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

class HoshiIsoBuilder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hoshi - Universal Wii Iso Builder")
        self.root.geometry("500x520")
        self.root.resizable(False, False)

        self.dark_theme = {"bg": "#1e1e1e", "fg": "#ffffff"}
        self.light_theme = {"bg": "#ffffff", "fg": "#000000"}
        self.light_grey = "#7a7aff"
        self.custom_font = ("Helvetica", 12)

        icon_image = Image.open("Elements/Images/icon.png").resize((32, 32), Image.BICUBIC)
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.root.iconphoto(True, icon_photo)

        title_image = Image.open("Elements/Images/title.png").resize((280, 70), Image.BICUBIC)
        self.title_texture = ImageTk.PhotoImage(title_image)

        self.file_types = ["Riivolution file (.xml)", "Riivolution patch folder", "Base Rom (.iso .wbfs)", "Destination Rom (.iso .wbfs)"]
        self.file_paths = {}
        self.file_type_buttons = []
        self.start_button = None

        self.selected_language = "English"
        self.translations = {}
        for lang in ["English", "Français", "Deutsch", "日本語"]:
            try:
                with open(f"Elements/translations/{lang}.json", 'r', encoding='utf-8') as file:
                    self.translations[lang] = json.load(file)
            except FileNotFoundError:
                print(f"Translation file for '{lang}' not found.")

        self.initialize_ui()

    def initialize_ui(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.title_label = tk.Label(self.root, image=self.title_texture, bg=self.dark_theme["bg"])
        self.title_label.image = self.title_texture 
        self.title_label.pack(pady=10)

        self.root.configure(bg=self.dark_theme["bg"])

        options_frame = tk.Frame(self.root, bg=self.dark_theme["bg"])
        options_frame.pack(pady=10)

        for file_type in self.file_types:
            option_button = tk.Button(options_frame, text=file_type, font=self.custom_font, bg=self.light_grey, fg="#ffffff", relief=tk.FLAT, command=lambda ft=file_type: self.open_file(ft))
            option_button.pack(pady=5, fill=tk.X)
            self.file_type_buttons.append(option_button)

            file_path_text = tk.Text(options_frame, height=1, width=40, wrap=tk.WORD, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"], font=self.custom_font)
            file_path_text.pack(pady=5, fill=tk.X)
            self.file_paths[file_type] = file_path_text

        footer_frame = tk.Frame(self.root, bg=self.dark_theme["bg"])
        footer_frame.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Building !", command=self.start_building, font=self.custom_font, bg=self.light_grey, fg="#ffffff", relief=tk.FLAT, bd=0, padx=20, pady=10, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
        self.start_button.pack(pady=20, fill=tk.X)
        self.update_ui_language()

    def start_building(self):
        is_wit_installed()
        messagebox.showinfo("Warning", "During the process, ensure not to touch any files, turn off your computer, load your ISO on an emulator (e.g., Dolphin Emulator), uninstall Python or any other component, or modify any system files. The ISO patching process may take some time depending on your computer, so please be patient.")
        self.start_button.config(text="Processing...")
        self.root.update()
        self.root.after(100, self.continue_building)

    def prompt_id_name_change(self):
        idCheck = subprocess.run(["wit", "ID6", self.file_paths["Base Rom (.iso .wbfs)"].get("1.0", tk.END).strip()], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if idCheck.returncode == 0:
            original_id = idCheck.stdout.strip() if idCheck.stdout else ""

        nameCheck = subprocess.run(["wit", "ANAID", original_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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
        original_id_text = tk.Label(dialog, text=original_id, bg=self.dark_theme["bg"], fg=self.light_grey, font=self.custom_font)
        original_id_text.grid(row=1, column=1, sticky="w")
        original_name_text = tk.Label(dialog, text=original_name, bg=self.dark_theme["bg"], fg=self.light_grey, font=self.custom_font)
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

        cancel_button = tk.Button(dialog, text="Cancel", command=on_cancel, bg=self.light_grey, fg="#ffffff", relief=tk.FLAT, bd=0, padx=10, pady=5, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
        cancel_button.grid(row=3, column=1, pady=10)        
        ok_button = tk.Button(dialog, text="OK", command=on_okay, bg=self.light_grey, fg="#ffffff", relief=tk.FLAT, bd=0, padx=10, pady=5, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
        ok_button.grid(row=3, column=3, pady=10)

        dialog.wait_window(dialog)
        return mod_id, mod_name

    def continue_building(self):
        try:
            if not is_wit_installed():
                messagebox.showerror("Error", "Please install WIT to continue.")
                self.start_button.config(text="Start Building !")
                return

            destination_path = self.file_paths["Destination Rom (.iso .wbfs)"].get("1.0", tk.END).strip()
            riivolution_file = self.file_paths["Riivolution file (.xml)"].get("1.0", tk.END).strip()
            riivolution_folder = self.file_paths["Riivolution patch folder"].get("1.0", tk.END).strip()
            base_rom_file = self.file_paths["Base Rom (.iso .wbfs)"].get("1.0", tk.END).strip()
            custom_code_folder =  riivolution_folder + "/CustomCode"

            if not destination_path or not riivolution_file or not base_rom_file:
                messagebox.showerror("Error", "Please fill in all required fields.")
                self.start_button.config(text="Start Building !")
                return

            elements_directory = "Elements"
            if not os.path.exists(elements_directory):
                os.makedirs(elements_directory)

            #Files cleaning
            print("Welcome to Hoshi! Let us clean your files before starting...")
            if os.path.exists('codelist.txt'):
                os.remove('codelist.txt')
                print("Custom Code Cheat file removed")
            else:
                print("Custom Code Cheat file not found. Skip")

            if os.path.exists('temp'):
                shutil.rmtree('temp')
                print("Temporary Game files removed")
            else:
                print("temp directory not found. Skip")
            time.sleep(3)
            subprocess.run(["cls"], shell=True)

            #Region Checking
            regionCheck = subprocess.run(["wit", "ID6", base_rom_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if regionCheck.returncode == 0:
                region_id = regionCheck.stdout.strip()[3] if regionCheck.stdout else ""
                region_name = ""

                if region_id == "E":
                    region_name = "USA"
                elif region_id == "P":
                    region_name = "PAL"
                elif region_id == "K":
                    region_name = "KOR"
                elif region_id == "J":
                    region_name = "JPN"
                elif region_id == "W":
                    region_name = "TWN"
                else:
                    region_name = ""
                
                print("Detected Region:", region_name)
                time.sleep(3)
                subprocess.run(["cls"], shell=True)
            else:
                print("Error executing command:", regionCheck.stderr)
                time.sleep(3)
                subprocess.run(["cls"], shell=True)

            #Base Rom Extracting
            print("Extracting ROM:")
            subprocess.run(["wit", "extract", base_rom_file, ".\\temp"], shell=True)
            print("Base Rom extracted successfully")
            time.sleep(3)
            subprocess.run(["cls"], shell=True)

            game_id = regionCheck.stdout[:3]

            #Custom Code Patching
            if game_id == "SMN":
                print("New Super Mario Bros. Wii Custom code patching:")
                print("The custom code patching process is not made yet :/")
                time.sleep(3)
                subprocess.run(["cls"], shell=True)

            elif game_id == "SB4":
                print("Building GCT Patch :")
                #Building Cheatcode patch file
                subprocess.run(["Elements/CustomCodePatching/start.exe", riivolution_file, region_id]) 
                time.sleep(3)
                subprocess.run(["cls"], shell=True)
                #Patching Custom Code
                print("Super Mario Galaxy 2 Custom code patching:")
                print("The custom code patching process is not made yet :/")
                time.sleep(3)
                subprocess.run(["cls"], shell=True)

            elif game_id == "R64":
                print("Wii Music Custom code patching:")
                print("The custom code patching process is not made yet :/")
                time.sleep(3)
                subprocess.run(["cls"], shell=True)
            
            elif game_id == "RMC":
                print("Mario Kart Wii Custom code patching:")
                print("The custom code patching process is not made yet :/")
                time.sleep(3)
                subprocess.run(["cls"], shell=True)

            elif game_id == "RSB":
                print("Super Smash Bros. Brawl Custom code patching:")
                print("The custom code patching process is not made yet :/")
                time.sleep(3)
                subprocess.run(["cls"], shell=True)

            print("Patching ROM:")
            destination_folder = ".\\temp\\files"
            for root, dirs, files in os.walk(riivolution_folder):
                for file in files:
                    src_path = os.path.join(root, file)
                    relative_path = os.path.relpath(src_path, riivolution_folder)
                    dest_path = os.path.join(destination_folder, relative_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    print(f"Copying and replacing: {relative_path}")
                    shutil.copy2(src_path, dest_path)
            print("All files copied and replaced.")
            time.sleep(3)
            subprocess.run(["cls"], shell=True)

            response = messagebox.askyesno("ID and Name Change", "Do you want to change the ID and name of the game ?")
            if response:
                mod_id, mod_name = self.prompt_id_name_change()

            print("Rom building:")
            if os.path.exists(destination_path):
                os.remove(destination_path)
            
            if not response:
                print("Mod's details unchanged")
                subprocess.run(["wit", "copy", ".\\temp", destination_path], shell=True)
            else:
                print("Mod's ID:", mod_id)
                print("Mod's Name:", mod_name)
                subprocess.run(["wit", "copy", ".\\temp", destination_path, "--id=" + mod_id, "--name=" + mod_name], shell=True)

            print("The Iso was successfully created")
            time.sleep(3)
            subprocess.run(["cls"], shell=True)
            
            print("Almost done there! Cleaning up the files one last time...")
            if os.path.exists('codelist.txt'):
                os.remove('codelist.txt')
                print("Custom Code Cheat file removed")
            else:
                print("Custom Code Cheat file not found. Skip")

            if os.path.exists('temp'):
                shutil.rmtree('temp')
                print("Temporary Game files removed")
            else:
                print("temp directory not found. Skip")

            messagebox.showinfo("Success", "ROM successfully patched!")

            self.start_button.config(text="Start Building !")
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            messagebox.showerror("Error", error_message)
            print(error_message)
            self.start_button.config(text="Start Building !")
        
    def open_file(self, file_type):
        if file_type == "Riivolution file (.xml)":
            file_path = filedialog.askopenfilename(filetypes=[("Riivolution XML files", "*.xml")])
        elif file_type == "Riivolution patch folder":
            file_path = filedialog.askdirectory()
        elif file_type == "Base Rom (.iso .wbfs)":
            file_path = filedialog.askopenfilename(filetypes=[("ISO files", "*.iso"), ("WBFS files", "*.wbfs")])
        elif file_type == "Destination Rom (.iso .wbfs)":
            file_path = filedialog.asksaveasfilename(defaultextension=".iso", filetypes=[("ISO files", "*.iso"), ("WBFS files", "*.wbfs")])

        if file_path:
            self.update_file_path(file_type, file_path)

    def update_file_path(self, file_type, file_path):
        self.file_paths[file_type].delete(1.0, tk.END)
        self.file_paths[file_type].insert(tk.END, file_path)

    def set_theme(self, theme):
        theme_colors = self.dark_theme if theme == "Dark" else self.light_theme

        self.root.config(bg=theme_colors["bg"])
        self.title_label.config(bg=theme_colors["bg"], fg=theme_colors["fg"])

        for file_type, button in zip(self.file_types, self.file_type_buttons):
            self.file_paths[file_type].config(bg=theme_colors["bg"], fg=theme_colors["fg"])
            button.config(bg=self.light_grey, fg="#fff")

        options_frame = self.root.nametowidget(self.root.winfo_children()[2]) 
        options_frame.config(bg=theme_colors["bg"])

    def open_github_io(self, url):
        webbrowser.open(url)

    def save_settings(self):
        config = configparser.ConfigParser()
        config["file_paths"] = {}

        for file_type in self.file_types:
            config["file_paths"][file_type] = self.file_paths[file_type].get("1.0", tk.END).strip()

        file_path = filedialog.asksaveasfilename(defaultextension=".hoshi", filetypes=[("Hoshi files", "*.hoshi")])

        if file_path:
            with open(file_path, "w") as configfile:
                config.write(configfile)

            print(f"Settings saved to: {file_path}")

    def import_settings(self):
        file_path = filedialog.askopenfilename(filetypes=[("Hoshi files", "*.hoshi")])

        if file_path:
            config = configparser.ConfigParser()
            config.read(file_path)

            for file_type in self.file_types:
                self.update_file_path(file_type, config["file_paths"].get(file_type, ""))

            print(f"Settings imported from: {file_path}")

    def set_language(self, language):
        self.selected_language = language
        self.update_ui_language()

    def update_ui_language(self):
        current_translations = self.translations.get(self.selected_language, self.translations["English"])

        self.start_button.config(text=current_translations["start_button"])

        for file_type, button in zip(self.file_types, self.file_type_buttons):
            button.config(text=current_translations["file_types"][file_type])

        self.menu_bar.delete(0, tk.END)

        save_menu = tk.Menu(self.menu_bar, tearoff=0)
        save_menu.add_command(label=current_translations["save_menu"]["save_as"], command=self.save_settings)
        save_menu.add_command(label=current_translations["save_menu"]["import"], command=self.import_settings)
        self.menu_bar.add_cascade(label=current_translations["menu_labels"]["file"], menu=save_menu)

        theme_menu = tk.Menu(self.menu_bar, tearoff=0)
        theme_menu.add_command(label=current_translations["theme_menu"]["dark"], command=lambda: self.set_theme("Dark"))
        theme_menu.add_command(label=current_translations["theme_menu"]["light"], command=lambda: self.set_theme("Light"))
        self.menu_bar.add_cascade(label=current_translations["menu_labels"]["theme"], menu=theme_menu)

        language_menu = tk.Menu(self.menu_bar, tearoff=0)
        for lang in ["English", "Français", "Deutsch", "日本語"]:
            language_menu.add_command(label=lang, command=lambda lang=lang: self.set_language(lang))
        self.menu_bar.add_cascade(label=current_translations["menu_labels"]["language"], menu=language_menu)

        about_menu = tk.Menu(self.menu_bar, tearoff=0)
        about_menu.add_command(label=current_translations["credits_menu"]["gui_by"], command=lambda: self.open_github_io("https://github.com/L-Dev31"))
        about_menu.add_command(label=current_translations["credits_menu"]["system_programming_by"], command=lambda: self.open_github_io("https://github.com/Humming-Owl/"))
        about_menu.add_command(label=current_translations["credits_menu"]["wit_by"], command=lambda: self.open_github_io("https://github.com/Wiimm"))
        about_menu.add_command(label=current_translations["credits_menu"]["gkl_by"], command=lambda: self.open_github_io("https://github.com/JoshuaMKW"))
        self.menu_bar.add_cascade(label=current_translations["menu_labels"]["credits"], menu=about_menu)

    def run(self):
        self.update_ui_language()
        self.root.mainloop()

if __name__ == "__main__":
    app = HoshiIsoBuilder()
    app.run()