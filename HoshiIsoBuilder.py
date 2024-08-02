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

# Tkinter imports for GUI
import tkinter as tk
from tkinter import filedialog, messagebox

# PIL (Pillow) for image processing
from PIL import Image, ImageTk

# Standard library imports
import subprocess
import webbrowser
import json
import configparser
import os

# Local module import
from Elements.CCPatching.hoshiGeneralProcess import ROMBuilder

class HoshiIsoBuilder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hoshi - Universal Wii Iso Builder")
        self.root.geometry("500x520")
        self.root.resizable(False, False)

        # Load settings from settings.ini
        config = configparser.ConfigParser()
        config.read("settings.ini", encoding="utf-8")
        self.selected_theme = config.get("settings", "theme", fallback="Dark")
        self.selected_language = config.get("settings", "language", fallback="English")

        # Define theme and language dictionaries
        self.dark_theme = {"bg": "#1e1e1e", "fg": "#ffffff"}
        self.light_theme = {"bg": "#ffffff", "fg": "#000000"}
        self.purple = "#7a7aff"
        self.custom_font = ("Helvetica", 12)

        # Initialize title_label
        self.title_label = None

        # Load images
        icon_image = Image.open("Elements/Images/icon.png").resize((32, 32), Image.BICUBIC)
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.root.iconphoto(True, icon_photo)

        title_image = Image.open("Elements/Images/title.png").resize((280, 70), Image.BICUBIC)
        self.title_texture = ImageTk.PhotoImage(title_image)

        # Define file types
        self.file_types = ["Riivolution file (.xml)", "Riivolution patch folder", "Base Rom (.iso .wbfs)", "Destination Rom (.iso .wbfs)"]
        self.file_paths = {}
        self.file_type_buttons = []
        self.start_button = None
        self.translations = {}
        for lang in ["English", "Français", "Deutsch", "日本語"]:
            try:
                with open(f"Elements/translations/{lang}.json", 'r', encoding='utf-8') as file:
                    self.translations[lang] = json.load(file)
            except FileNotFoundError:
                print(f"Translation file for '{lang}' not found.")

        self.initialize_ui()
        self.rom_builder = ROMBuilder(self.root, self.file_paths, self.start_button)

        # Apply loaded settings as if the user changed them
        self.set_theme(self.selected_theme)
        self.set_language(self.selected_language)


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
            option_button = tk.Button(options_frame, text=file_type, font=self.custom_font, bg=self.purple, fg="#ffffff", relief=tk.FLAT, command=lambda ft=file_type: self.open_file(ft))
            option_button.pack(pady=5, fill=tk.X)
            self.file_type_buttons.append(option_button)

            file_path_text = tk.Text(options_frame, height=1, width=40, wrap=tk.WORD, bg=self.dark_theme["bg"], fg=self.dark_theme["fg"], font=self.custom_font)
            file_path_text.pack(pady=5, fill=tk.X)
            self.file_paths[file_type] = file_path_text

        footer_frame = tk.Frame(self.root, bg=self.dark_theme["bg"])
        footer_frame.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Building !", command=self.start_building, font=self.custom_font, bg=self.purple, fg="#ffffff", relief=tk.FLAT, bd=0, padx=20, pady=10, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
        self.start_button.pack(pady=20, fill=tk.X)
        self.update_ui_language()

    def start_building(self):

        messagebox.showinfo("Warning", "During the process, ensure not to touch any files, turn off your computer, load your ISO on an emulator (e.g., Dolphin Emulator), uninstall Python or any other component, or modify any system files. The ISO patching process may take some time depending on your computer, so please be patient.")
        
        self.start_button.config(text="Processing...")
        self.root.update()

        try:
            self.root.after(100, self.rom_builder.continue_building)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during the building process: {e}")
            self.start_button.config(text="Start Building")
            self.root.update()
        
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
            button.config(bg=self.purple, fg="#fff")

        options_frame = self.root.nametowidget(self.root.winfo_children()[2]) 
        options_frame.config(bg=theme_colors["bg"])

        # Save theme to settings.ini
        self.save_settings(theme=theme, language=self.selected_language)

    def open_github_io(self, url):
        webbrowser.open(url)

    def save_settings(self, theme=None, language=None):
        config = configparser.ConfigParser()
        config["settings"] = {}

        if theme:
            config["settings"]["theme"] = theme
        if language:
            config["settings"]["language"] = language

        with open("settings.ini", "w", encoding="utf-8") as configfile:
            config.write(configfile)

    def import_settings(self):
        file_path = filedialog.askopenfilename(filetypes=[("Hoshi files", "*.hoshi")])

        if file_path:
            config = configparser.ConfigParser()
            config.read(file_path)

            for file_type in self.file_types:
                file_path_value = config["file_paths"].get(file_type, "")
                self.update_file_path(file_type, file_path_value)

            print(f"Settings imported from: {file_path}")

    def save_settings_as(self):
        paths = {file_type: text_widget.get(1.0, tk.END).strip() for file_type, text_widget in self.file_paths.items()}

        file_path = filedialog.asksaveasfilename(defaultextension=".hoshi", filetypes=[("Hoshi files", "*.hoshi")])

        if file_path:
            config = configparser.ConfigParser()
            config["file_paths"] = paths

            with open(file_path, 'w') as configfile:
                config.write(configfile)

            print(f"Settings saved to: {file_path}")

    def set_language(self, language):
        self.selected_language = language
        self.update_ui_language()

        # Save language to settings.ini
        self.save_settings(theme=self.selected_theme, language=language)

    def update_ui_language(self):
        current_translations = self.translations.get(self.selected_language, self.translations["English"])

        self.start_button.config(text=current_translations["start_button"])

        for file_type, button in zip(self.file_types, self.file_type_buttons):
            button.config(text=current_translations["file_types"][file_type])

        self.menu_bar.delete(0, tk.END)

        save_menu = tk.Menu(self.menu_bar, tearoff=0)
        save_menu.add_command(label=current_translations["save_menu"]["save_as"], command=self.save_settings_as)
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