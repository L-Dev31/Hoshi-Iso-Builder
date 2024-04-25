import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import webbrowser
import json
import time
import shutil

class HoshiIsoBuilder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hoshi v0.2")
        self.root.geometry("500x520")
        self.root.resizable(False, False)

        self.menu_bar = None
        self.dark_theme = {"bg": "#1e1e1e", "fg": "#ffffff"}
        self.light_theme = {"bg": "#ffffff", "fg": "#000000"}
        self.light_grey = "#7a7aff"
        self.custom_font = ("Helvetica", 12)

        icon_image = Image.open("Elements/icon.png")
        icon_image = icon_image.resize((32, 32), Image.BICUBIC)  
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.root.iconphoto(True, icon_photo)

        title_image = Image.open("Elements/title.png")
        title_image = title_image.resize((280, 70), Image.BICUBIC)
        self.title_texture = ImageTk.PhotoImage(title_image)

        self.file_types = ["Riivolution file (.xml)", "Riivolution patch folder", "Base Rom (.iso .wbfs)", "Destination Rom (.iso .wbfs)"]
        self.file_paths = {}
        self.file_type_buttons = []
        self.start_button = None

        self.selected_language = "English"

        self.translations = {
            "English": {
                "start_button": "Start Building !",
                "file_types": {
                    "Riivolution file (.xml)": "Riivolution file (.xml)",
                    "Riivolution patch folder": "Riivolution patch folder",
                    "Base Rom (.iso .wbfs)": "Base Rom (.iso .wbfs)",
                    "Destination Rom (.iso .wbfs)": "Destination Rom (.iso .wbfs)",
                },
                "menu_labels": {
                    "file": "📁 File",
                    "theme": "🎨 Theme",
                    "language": "🌎 Language",
                    "credits": "⭐ Credits",
                },
                "save_menu": {
                    "save_as": "Save as..",
                    "import": "Import",
                },
                "theme_menu": {
                    "dark": "Dark",
                    "light": "Light",
                },
                "credits_menu": {
                    "gui_by": "GUI by L-DEV (Léo TOSKU)",
                    "system_programming_by": "System programming by Humming Owl",
                    "wit_by": "Wit by Wimm",
                    "gkl_by": "Gecko Loader by JoshuaMKW",
                },
            },
            "Français": {
                "start_button": "Démarrer le processus !",
                "file_types": {
                    "Riivolution file (.xml)": "Fichier Riivolution (.xml))",
                    "Riivolution patch folder": "Dossier du patch Riivolution",
                    "Base Rom (.iso .wbfs)": "Fichier ROM de base (.iso .wbfs)",
                    "Destination Rom (.iso .wbfs)": "Fichier ROM de destination (.iso .wbfs)",
                },
                "menu_labels": {
                    "file": "📁 Fichier",
                    "theme": "🎨 Thème",
                    "language": "🌍 Langue",
                    "credits": "⭐ Crédits",
                },
                "save_menu": {
                    "save_as": "Enregistrer sous..",
                    "import": "Importer",
                },
                "theme_menu": {
                    "dark": "Sombre",
                    "light": "Clair",
                },
                "credits_menu": {
                    "gui_by": "Interface graphique par L-DEV (Léo TOSKU)",
                    "system_programming_by": "Système par Humming Owl",
                    "wit_by": "Wit par Wiimm",
                    "gkl_by": "Gecko Loader par JoshuaMKW",
                },
            },
            "Deutsch": {
                "start_button": "Start!",
                "file_types": {
                    "Riivolution file (.xml)": "Riivolution-Datei (.xml)",
                    "Riivolution patch folder": "Riivolution Patch-Ordner",
                    "Base Rom (.iso .wbfs)": "Originale ROM (.iso .wbfs)",
                    "Destination Rom (.iso .wbfs)": "Neue ROM (.iso .wbfs)",
                },
                "menu_labels": {
                    "file": "📁 Datei",
                    "theme": "🎨 Design",
                    "language": "🌍 Sprache",
                    "credits": "⭐ Credits",
                },
                "save_menu": {
                    "save_as": "Speichern unter..",
                    "import": "Importieren",
                },
                "theme_menu": {
                    "dark": "Dunkel",
                    "light": "Hell",
                },
                "credits_menu": {
                    "gui_by": "GUI von L-DEV (Léo TOSKU)",
                    "system_programming_by": "Systemprogrammierung von Humming Owl",
                    "wit_by": "Wit von Wiimm",
                    "gkl_by": "Gecko Loader von JoshuaMKW",
                },
            },
            "日本語": {
                "start_button": "始める!",
                "file_types": {
                    "Riivolution file (.xml)" : "Riivolution ファイルを指定 (.xml)",
                    "Riivolution patch folder" : "Riivolution パッチフォルダーを指定",
                    "Base Rom (.iso .wbfs)" : "ベースRomを指定 (.iso .wbfs)",
                    "Destination Rom (.iso .wbfs)" : "カスタムRomの保存先 (.iso .wbfs)",
                },
                "menu_labels": {
                    "file": " ファイル",
                    "theme": " テーマ",
                    "language": " 言語",
                    "credits": " クレジット",
                },
                "save_menu": {
                    "save_as": "上書き保存..",
                    "import": "インポート",
                },
                "theme_menu": {
                    "dark": "ダーク",
                    "light": "ライト",
                },
                "credits_menu": {
                    "gui_by": "GUI設計,デザイン L-DEV (Léo TOSKU)",
                    "system_programming_by": "システムプログラミング Humming Owl",
                    "wit_by": "Wit by Wimm",
                    "gkl_by": "Gecko Loader by JoshuaMKW",
                },
            },
        }

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
        
        original_name_id = original_id[:3]
        if original_name_id.startswith("RMG"):
            original_name = "SUPER MARIO GALAXY"
        elif original_name_id == "SB4":
            original_name = "SUPER MARIO GALAXY MORE"
        else:
            original_name = "Unknown or not SMG/SMG2"

        mod_id = ""
        mod_name = ""
        
        # Create dialog for user input
        dialog = tk.Toplevel(self.root)
        dialog.title("Modify ID and Name")
        dialog.configure(bg=self.dark_theme["bg"])

        # Original ID and Name (display only)
        tk.Label(dialog, text="Original", font=self.custom_font, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(dialog, text="ID :", bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=1, column=0, sticky="w")
        tk.Label(dialog, text="Name :", bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=2, column=0, sticky="w")
        original_id_text = tk.Label(dialog, text=original_id, bg=self.dark_theme["bg"], fg=self.light_grey, font=self.custom_font)
        original_id_text.grid(row=1, column=1, sticky="w")
        original_name_text = tk.Label(dialog, text=original_name, bg=self.dark_theme["bg"], fg=self.light_grey, font=self.custom_font)
        original_name_text.grid(row=2, column=1, sticky="w")

        # New ID and Name
        tk.Label(dialog, text="New", font=self.custom_font, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=0, column=2, columnspan=2)
        tk.Label(dialog, text="ID :", bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=1, column=2)
        tk.Label(dialog, text="Name :", bg=self.dark_theme["bg"], fg=self.dark_theme["fg"]).grid(row=2, column=2)
        new_id_text = tk.Text(dialog, height=1, width=20, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"], font=self.custom_font)
        new_id_text.grid(row=1, column=3)
        new_name_text = tk.Text(dialog, height=1, width=20, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"], font=self.custom_font)
        new_name_text.grid(row=2, column=3)

        # OK and Cancel buttons
        ok_button = tk.Button(dialog, text="OK", command=dialog.destroy, bg=self.light_grey, fg="#ffffff", relief=tk.FLAT, bd=0, padx=10, pady=5, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
        ok_button.grid(row=3, column=1, pady=10)
        cancel_button = tk.Button(dialog, text="Cancel", command=lambda: self.cancel_modification(dialog), bg=self.light_grey, fg="#ffffff", relief=tk.FLAT, bd=0, padx=10, pady=5, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
        cancel_button.grid(row=3, column=3, pady=10)

        # Wait for dialog to close
        dialog.wait_window(dialog)

        # Retrieve user input
        new_id = new_id_text.get("1.0", tk.END).strip()
        new_name = new_name_text.get("1.0", tk.END).strip()

        # Update the UI accordingly
        new_id_text.insert(tk.END, new_id)
        new_name_text.insert(tk.END, new_name)

        return new_id, new_name

    def cancel_modification(self, dialog):
        dialog.destroy()
        self.start_button.config(text="Start Building !")

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

            # Check if any required file paths are empty
            if not destination_path or not riivolution_file or not base_rom_file:
                messagebox.showerror("Error", "Please fill in all required fields.")
                self.start_button.config(text="Start Building !")
                return

            elements_directory = "Elements"
            if not os.path.exists(elements_directory):
                os.makedirs(elements_directory)

            # Region checker
            regionCheck = subprocess.run(["wit", "ID6", base_rom_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if regionCheck.returncode == 0:
                region_id = regionCheck.stdout.strip()[3] if regionCheck.stdout else ""
                region_name = ""

                if region_id == "E":
                    region_name = "North America"
                elif region_id == "P":
                    region_name = "Europe"
                elif region_id == "K":
                    region_name = "South Korea"
                elif region_id == "J":
                    region_name = "Japan"
                else:
                    region_name = "Unknown"
                
                print("Detected Region:", region_name)
                time.sleep(3)
                subprocess.run(["cls"], shell=True)
            else:
                print("Error executing command:", regionCheck.stderr)
                time.sleep(3)
                subprocess.run(["cls"], shell=True)

            # GCT Builder
            custom_code_folder =  riivolution_folder + "/CustomCode"
            print("Building GCT Patch :")
            subprocess.run([".\\Elements\\start.exe", riivolution_file, custom_code_folder, region_id], shell=True)
            time.sleep(3)
            subprocess.run(["cls"], shell=True)

            # Rom Extraction
            print("Extracting ROM:")
            subprocess.run(["wit", "extract", base_rom_file, ".\\temp"], shell=True)
            print("Base Rom extracted successfully")
            time.sleep(3)
            subprocess.run(["cls"], shell=True)

            # Patching Dol
            print("Patching DOL:")
            subprocess.run(["Elements/GeckoLoader.exe", "temp/sys/main.dol", "codelist.txt"])
            shutil.copy2("geckoloader-build/main.dol", "temp/sys/")
            print("The main.dol file was successfully patched")
            time.sleep(3)
            subprocess.run(["cls"], shell=True)

            # Patching Rom
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

            # Prompt for ID and Name change
            new_id, new_name = self.prompt_id_name_change()

            # Iso Rebuilding
            print("Rom building:")
            if os.path.exists(destination_path):
                os.remove(destination_path)
            subprocess.run(["wit", "copy", ".\\temp", destination_path], shell=True)
            print("The Iso was successfully created")
            time.sleep(3)
            subprocess.run(["cls"], shell=True)
            
            # Cleaning Files
            print("Cleaning Temp files:")
            shutil.rmtree('geckoloader-build')
            os.remove('codelist.txt')
            print("Custom Code patch files removed")
            shutil.rmtree('temp')
            print("Temporary Game files removed")
            time.sleep(3)
            subprocess.run(["cls"], shell=True)

            #Success
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
        settings = {
            "file_paths": {file_type: self.file_paths[file_type].get("1.0", tk.END).strip() for file_type in self.file_types},
        }

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])

        if file_path:
            with open(file_path, "w") as json_file:
                json.dump(settings, json_file, indent=4)

            print(f"Settings saved to: {file_path}")

    def import_settings(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])

        if file_path:
            with open(file_path, "r") as json_file:
                settings = json.load(json_file)

            for file_type in self.file_types:
                self.update_file_path(file_type, settings["file_paths"].get(file_type, ""))

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

def is_wit_installed():
    try:
        subprocess.run(['wit', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    app = HoshiIsoBuilder()
    app.run()

