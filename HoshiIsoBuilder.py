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
        self.root.geometry("500x550")
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

        self.file_types = ["Riivolution file (.xml)", "Riivolution patch folder", "Custom code folder", "Base Rom (.iso .wbfs)", "Destination Rom (.iso .wbfs)"]
        self.file_paths = {}
        self.file_type_buttons = []
        self.start_button = None

        self.selected_language = "English"

        self.translations = {
            "English": {
                "title": "Hoshi v0.2",
                "start_button": "Start Building !",
                "title_label": "Hoshi Iso Builder v0.2",
                "file_types": {
                    "Riivolution file (.xml)": "Riivolution file (.xml)",
                    "Riivolution patch folder": "Riivolution patch folder",
                    "Custom code folder": "Custom code folder",
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
                },
            },
            "Français": {
                "title": "Hoshi v0.2",
                "start_button": "Démarrer le processus !",
                "title_label": "Compilateur d'Iso, Hoshi v0.2",
                "file_types": {
                    "Riivolution file (.xml)": "Fichier Riivolution (.xml))",
                    "Riivolution patch folder": "Dossier du patch Riivolution",
                    "Custom code folder": "Dossier Custom Code",
                    "Base Rom (.iso .wbfs)": "Fichier ROM de base (.iso .wbfs)",
                    "Destination Rom (.iso .wbfs)": "Fichier ROM de destination (.iso .wbfs)",
                },
                "menu_labels": {
                    "file": "📁 Fichier",
                    "theme": "🎨 Thème",
                    "language": "🌎 Langue",
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
                },
            },
            "Deutsch": {
                "title": "Hoshi v0.2",
                "start_button": "Start !",
                "title_label": "Hoshi Iso Builder v0.2",
                "file_types": {
                    "Riivolution file (.xml)": "Riivolution-Datei (.xml)",
                    "Riivolution patch folder": "Riivolution Patch-Ordner",
                    "Custom code folder": "Custom Code Ordner",
                    "Base Rom (.iso .wbfs)": "Originale ROM (.iso .wbfs)",
                    "Destination Rom (.iso .wbfs)": "Neue ROM (.iso .wbfs)",
                },
                "menu_labels": {
                    "file": "📁 Datei",
                    "theme": "🎨 Design",
                    "language": "🌎 Sprache",
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
                },
            },
            "日本語": {
                "title": "星 v0.2",
                "start_button": "ビルドを開始する！",
                "title_label": "ISOコンパイラ、星 v0.2",
                "file_types": {
                    "Riivolution file (.xml)": "Riivolution XML ファイル",
                    "Riivolution patch folder": "Riivolution パッチフォルダー",
                    "Custom code folder": "カスタムコードフォルダー",
                    "Base Rom (.iso .wbfs)": "ベース ROM ファイル",
                    "Destination Rom (.iso .wbfs)": "目的の ROM ファイル",
                },
                "menu_labels": {
                    "file": "📁 ファイル",
                    "theme": "🎨 テーマ",
                    "language": "🌎 言語",
                    "credits": "⭐ クレジット",
                },
                "save_menu": {
                    "save_as": "名前を付けて保存..",
                    "import": "インポート",
                },
                "theme_menu": {
                    "dark": "ダーク",
                    "light": "ライト",
                },
                "credits_menu": {
                    "gui_by": "L-DEVによるグラフィカルインターフェース",
                    "system_programming_by": "システムプログラミング by Humming Owl",
                    "wit_by": "Wiimmの「Wit」",
                },
            },
            "Русский": {
                "title": "Hoshi v0.2",
                "start_button": "Начать строительство !",
                "title_label": "Компилятор ISO, Hoshi v0.2",
                "file_types": {
                    "Riivolution file (.xml)": "Файл Riivolution XML",
                    "Riivolution patch folder": "Папка патча Riivolution",
                    "Custom code folder": "Папка пользовательского кода",
                    "Base Rom (.iso .wbfs)": "Файл базовой ROM",
                    "Destination Rom (.iso .wbfs)": "Файл целевой ROM",
                },
                "menu_labels": {
                    "file": "📁 Файл",
                    "theme": "🎨 Тема",
                    "language": "🌎 Язык",
                    "credits": "⭐ Заслуги",
                },
                "save_menu": {
                    "save_as": "Сохранить как..",
                    "import": "Импорт",
                },
                "theme_menu": {
                    "dark": "Тёмная тема",
                    "light": "Светлая тема",
                },
                "credits_menu": {
                    "gui_by": "Интерфейс от L-DEV (Léo TOSKU)",
                    "system_programming_by": "Системное программирование от Humming Owl",
                    "wit_by": "Wit от Wiimm",
                },
            },
        }

        self.initialize_ui()

    def initialize_ui(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.title_label = tk.Label(self.root, text="Hoshi Iso Builder v0.2", font=("Helvetica", 16), bg=self.dark_theme["bg"], fg=self.dark_theme["fg"])
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
        self.start_button.config(text="Processing...")
        self.root.update()
        self.root.after(100, self.continue_building)

    def continue_building(self):
        try:
            if not is_wit_installed():
                messagebox.showerror("Error", "Please install WIT to continue.")
                self.start_button.config(text="Start Building !")
                return

            destination_path = self.file_paths["Destination Rom (.iso .wbfs)"].get("1.0", tk.END).strip()
            if not destination_path:
                messagebox.showerror("Error", "Please fill in all cells")
                self.start_button.config(text="Start Building !")
                return

            riivolution_file = self.file_paths["Riivolution file (.xml)"].get("1.0", tk.END).strip()
            riivolution_folder = self.file_paths["Riivolution patch folder"].get("1.0", tk.END).strip()
            custom_code_folder = self.file_paths["Custom code folder"].get("1.0", tk.END).strip()

            if not riivolution_file or not custom_code_folder:
                return

            elements_directory = "Elements"
            if not os.path.exists(elements_directory):
                os.makedirs(elements_directory)

            base_rom_file = self.file_paths["Base Rom (.iso .wbfs)"].get("1.0", tk.END).strip()

            if not base_rom_file:
                return

            # GCT Builder
            bat_content = f'".\\Elements\\start.exe" "{riivolution_file}" "{custom_code_folder}" E\n'
            # Rom Extraction
            bat_content += f'wit extract "{base_rom_file}" ".\\temp"\n'
            # Game Patching
            bat_content += f'xcopy /E /I "{riivolution_folder}" ".\\temp\\files"\n'
            # Dol Patching
            # Iso Rebuilding
            bat_content += f'wit copy ".\\temp" "{destination_path}"\n'

            bat_file_path = os.path.join(elements_directory, "start.bat")

            with open(bat_file_path, "w") as bat_file:
                bat_file.write(bat_content)

            os.system(bat_file_path)
            os.remove('codelist.txt')
            shutil.rmtree('temp')
            time.sleep(3)
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
        elif file_type == "Custom code folder":
            file_path = filedialog.askdirectory()
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

        self.title_label.config(text=current_translations["title_label"])

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
        for lang in ["English", "Français", "Deutsch", "日本語", "Русский"]:
            language_menu.add_command(label=lang, command=lambda lang=lang: self.set_language(lang))
        self.menu_bar.add_cascade(label=current_translations["menu_labels"]["language"], menu=language_menu)

        about_menu = tk.Menu(self.menu_bar, tearoff=0)
        about_menu.add_command(label=current_translations["credits_menu"]["gui_by"], command=lambda: self.open_github_io("https://github.com/L-Dev31"))
        about_menu.add_command(label=current_translations["credits_menu"]["system_programming_by"], command=lambda: self.open_github_io("https://github.com/Humming-Owl/"))
        about_menu.add_command(label=current_translations["credits_menu"]["wit_by"], command=lambda: self.open_github_io("https://github.com/Wiimm"))
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

