import os
import sys
import configparser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from PIL import Image, ImageTk
import shutil
import threading
import argparse
from file_ops import *
import file_ops

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from riiv import get_riiv_patches_inf, apply_riiv_patches_wrapper
from localization import LocalizationManager, ThemeManager

class HoshiIsoBuilder:
    def __init__(self, root, iso_path=None, xml_path=None, mods_path=None):
        self.root = root
        self.root.title("Hoshi Iso Builder")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        self.style = ttk.Style()
        self.style.configure("TButton", relief="flat", borderwidth=0)
        self.style.configure("TLabel", relief="flat")
        self.style.configure("TEntry", relief="flat")
        self.style.configure("TFrame", relief="flat")
        self.style.configure("TCheckbutton", relief="flat")
        self.style.configure("TRadiobutton", relief="flat")

        self.config = self.load_config()
        
        self.localization = LocalizationManager()
        self.theme_manager = ThemeManager()
        
        self.iso_path = tk.StringVar(value=iso_path if iso_path else "")
        self.xml_path = tk.StringVar(value=xml_path if xml_path else "")
        self.mods_path = tk.StringVar(value=mods_path if mods_path else "")

        self.selected_choices = []
        self.current_theme = self.theme_manager.current_theme
        
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'icon.png')
        if os.path.exists(icon_path):
            icon = ImageTk.PhotoImage(Image.open(icon_path))
            self.root.iconphoto(True, icon)
        
        self.apply_theme(self.current_theme)
        
        self.create_widgets()
        
        self.center_window()

    def load_config(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        
        if os.path.exists(config_path):
            config.read(config_path)
        else:
            config['General'] = {
                'language': 'fr',
                'theme': 'dark'
            }
            config['Paths'] = {
                'tools_dir': 'tools',
                'temp_dir': 'tmp'
            }
            config['Credits'] = {
                'hoshi_iso_builder': 'L-DEV',
                'riiv_converter': 'Humming Owl',
                'wit': 'Wiimm',
                'gecko_loader': '[placeholder]'
            }
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as configfile:
                config.write(configfile)
        
        return config
    
    def save_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        with open(config_path, 'w') as configfile:
            self.config.write(configfile)
    
    def apply_theme(self, theme_name):
        self.style = ttk.Style()
        
        if theme_name == 'dark':
            self.style.theme_use('clam')
            self.style.configure('TFrame', background='#1B202D')
            self.style.configure('TLabel', background='#1B202D', foreground='#f0f0f0')
            self.style.configure('TButton', background='#4C74FD', foreground='white')
            self.style.map('TButton', background=[('active', '#b685ff')])
            self.style.configure('TEntry', fieldbackground='#2d2d2d', foreground='#f0f0f0')
            self.style.configure('TCombobox', fieldbackground='#2d2d2d', foreground='#f0f0f0')
            self.style.map('TCombobox', fieldbackground=[('readonly', '#2d2d2d')])
            self.style.configure('TCheckbutton', background='#1B202D', foreground='#f0f0f0')
            
            self.root.configure(bg='#1B202D')
        else:
            self.style.theme_use('clam')
            self.style.configure('TFrame', background='#f5f5f5')
            self.style.configure('TLabel', background='#f5f5f5', foreground='#333333')
            self.style.configure('TButton', background='#8a4fff', foreground='white')
            self.style.map('TButton', background=[('active', '#7a3fee')])
            self.style.configure('TEntry', fieldbackground='white', foreground='#333333')
            self.style.configure('TCombobox', fieldbackground='white', foreground='#333333')
            self.style.map('TCombobox', fieldbackground=[('readonly', 'white')])
            self.style.configure('TCheckbutton', background='#f5f5f5', foreground='#333333')
            
            self.root.configure(bg='#f5f5f5')
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'title.png')
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((int(logo_image.width * 0.8), int(logo_image.height * 0.8)), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(main_frame, image=logo_photo)
            logo_label.image = logo_photo
            logo_label.pack(pady=(0, 20))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text=self.localization.get_string('MainWindow', 'select_iso', 'Sélectionner ISO/WBFS')).grid(row=0, column=0, sticky=tk.W, pady=5)
        iso_entry = ttk.Entry(file_frame, textvariable=self.iso_path, width=50)
        iso_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(file_frame, text="...", width=3, command=self.select_iso).grid(row=0, column=2, pady=5)
        
        ttk.Label(file_frame, text=self.localization.get_string('MainWindow', 'select_xml', 'Sélectionner XML')).grid(row=1, column=0, sticky=tk.W, pady=5)
        xml_entry = ttk.Entry(file_frame, textvariable=self.xml_path, width=50)
        xml_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(file_frame, text="...", width=3, command=self.select_xml).grid(row=1, column=2, pady=5)
        
        ttk.Label(file_frame, text=self.localization.get_string('MainWindow', 'select_mods', 'Sélectionner dossier de mods')).grid(row=2, column=0, sticky=tk.W, pady=5)
        mods_entry = ttk.Entry(file_frame, textvariable=self.mods_path, width=50)
        mods_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(file_frame, text="...", width=3, command=self.select_mods).grid(row=2, column=2, pady=5)
        
        file_frame.columnconfigure(1, weight=1)
        
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(20, 10))
        
        self.style.configure("Flat.TButton", relief="flat", borderwidth=0)

        build_button = ttk.Button(action_frame, text=self.localization.get_string('MainWindow', 'build_button', 'Construire'),
                                command=self.build_iso, style="Flat.TButton")
        build_button.pack(side=tk.LEFT, padx=5)

        settings_button = ttk.Button(action_frame, text=self.localization.get_string('MainWindow', 'settings_button', 'Paramètres'),
                                    command=self.show_settings, style="Flat.TButton")
        settings_button.pack(side=tk.RIGHT, padx=5)

        about_button = ttk.Button(action_frame, text=self.localization.get_string('MainWindow', 'about_button', 'À propos'),
                                command=self.show_about, style="Flat.TButton")
        about_button.pack(side=tk.RIGHT, padx=5)
        action_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=600, mode="determinate")
        self.progress_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        self.style.configure("Custom.Horizontal.TProgressbar", background="#4C74FD", troughcolor="#1B202D")
        self.progress_bar.configure(style="Custom.Horizontal.TProgressbar")
        
        credits_text = "Hoshi Iso Builder by L-DEV | Riiv Converter by Humming Owl | WIT by Wiimm | GeckoLoader by [placeholder]"
        credits_label = ttk.Label(main_frame, text=credits_text, font=('Segoe UI', 8))
        credits_label.pack(side=tk.BOTTOM, pady=(10, 0))
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def select_iso(self):
        file_path = filedialog.askopenfilename(
            title=self.localization.get_string('MainWindow', 'select_iso', 'Sélectionner ISO/WBFS'),
            filetypes=[("Wii ISO/WBFS", "*.iso *.wbfs"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.iso_path.set(file_path)
            self.status_var.set(self.localization.get_string('Messages', 'iso_select_success', 'Fichier ISO/WBFS sélectionné avec succès'))
    
    def select_xml(self):
        file_path = filedialog.askopenfilename(
            title=self.localization.get_string('MainWindow', 'select_xml', 'Sélectionner XML'),
            filetypes=[("Fichiers XML", "*.xml"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.xml_path.set(file_path)
            self.status_var.set(self.localization.get_string('Messages', 'xml_select_success', 'Fichier XML sélectionné avec succès'))
    
    def select_mods(self):
        folder_path = filedialog.askdirectory(
            title=self.localization.get_string('MainWindow', 'select_mods', 'Sélectionner dossier de mods')
        )
        if folder_path:
            self.mods_path.set(folder_path)
            self.status_var.set(self.localization.get_string('Messages', 'mods_select_success', 'Dossier de mods sélectionné avec succès'))
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title(self.localization.get_string('Settings', 'title', 'Paramètres'))
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        if self.current_theme == 'dark':
            settings_window.configure(bg='#1B202D')
        else:
            settings_window.configure(bg='#f5f5f5')
        
        main_frame = ttk.Frame(settings_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=self.localization.get_string('Settings', 'language', 'Langue')).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        available_languages = self.localization.get_available_languages()
        language_display_names = [self.localization.get_language_display_name(lang) for lang in available_languages]
        
        language_var = tk.StringVar(value=self.localization.get_language_display_name(self.localization.current_language))
        language_combo = ttk.Combobox(main_frame, textvariable=language_var, state='readonly')
        language_combo['values'] = language_display_names
        
        language_combo.grid(row=0, column=1, sticky=tk.EW, pady=10, padx=5)
        
        ttk.Label(main_frame, text=self.localization.get_string('Settings', 'theme', 'Thème')).grid(row=1, column=0, sticky=tk.W, pady=10)
        
        theme_var = tk.StringVar(value=self.current_theme)
        theme_frame = ttk.Frame(main_frame)
        theme_frame.grid(row=1, column=1, sticky=tk.W, pady=10)
        
        ttk.Radiobutton(
            theme_frame, 
            text=self.localization.get_string('Settings', 'theme_dark', 'Sombre'), 
            variable=theme_var, 
            value='dark'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            theme_frame, 
            text=self.localization.get_string('Settings', 'theme_light', 'Clair'), 
            variable=theme_var, 
            value='light'
        ).pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(
            button_frame, 
            text=self.localization.get_string('Settings', 'save_button', 'Enregistrer'),
            command=lambda: self.save_settings(settings_window, language_var.get(), theme_var.get(), available_languages, language_display_names)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text=self.localization.get_string('Settings', 'cancel_button', 'Annuler'),
            command=settings_window.destroy
        ).pack(side=tk.LEFT)
        
        main_frame.columnconfigure(1, weight=1)
        
        settings_window.update_idletasks()
        width = settings_window.winfo_width()
        height = settings_window.winfo_height()
        x = (settings_window.winfo_screenwidth() // 2) - (width // 2)
        y = (settings_window.winfo_screenheight() // 2) - (height // 2)
        settings_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def save_settings(self, window, language_display, theme, available_languages, language_display_names):
        language_code = self.localization.current_language
        for i, display_name in enumerate(language_display_names):
            if display_name == language_display:
                language_code = available_languages[i]
                break
        
        self.config.set('General', 'language', language_code)
        self.config.set('General', 'theme', theme)
        self.save_config()
        
        self.localization.change_language(language_code)
        
        if theme != self.current_theme:
            self.current_theme = theme
            self.theme_manager.change_theme(theme)
            self.apply_theme(theme)
            
            for widget in self.root.winfo_children():
                widget.destroy()
            self.create_widgets()
        
        window.destroy()
        
        messagebox.showinfo("Hoshi Iso Builder", "Settings successfully saved! Restart the application to apply changes.")
    
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title(self.localization.get_string('About', 'title', 'À propos'))
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        if self.current_theme == 'dark':
            about_window.configure(bg='#1B202D')
        else:
            about_window.configure(bg='#f5f5f5')
        
        main_frame = ttk.Frame(about_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'icon.png')
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((64, 64), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(main_frame, image=logo_photo)
            logo_label.image = logo_photo
            logo_label.pack(pady=(0, 10))
        
        title_label = ttk.Label(main_frame, text="Hoshi Iso Builder", font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 5))
        
        version_label = ttk.Label(main_frame, text=self.localization.get_string('General', 'version', 'v2.0'))
        version_label.pack(pady=(0, 20))
        
        credits_label = ttk.Label(main_frame, text=self.localization.get_string('About', 'credits', 'Crédits'), font=('Segoe UI', 12, 'bold'))
        credits_label.pack(pady=(0, 10))
        
        credits_text = f"{self.localization.get_string('About', 'hoshi_iso_builder', 'Hoshi Iso Builder par L-DEV')}\n"
        credits_text += f"{self.localization.get_string('About', 'riiv_converter', 'Riiv Converter par Humming Owl')}\n"
        credits_text += f"{self.localization.get_string('About', 'wit', 'WIT par Wiimm')}\n"
        credits_text += f"{self.localization.get_string('About', 'gecko_loader', 'GeckoLoader par [placeholder]')}"
        
        credits_content = ttk.Label(main_frame, text=credits_text, justify=tk.CENTER)
        credits_content.pack(pady=(0, 20))
        
        ttk.Button(
            main_frame, 
            text=self.localization.get_string('About', 'close_button', 'Fermer'),
            command=about_window.destroy
        ).pack()
        
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def show_patch_selection(self, sections):
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Patch Selection")
        selection_window.geometry("600x400")
        selection_window.transient(self.root)
        selection_window.grab_set()

        main_frame = ttk.Frame(selection_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        scroll_frame = ttk.Frame(main_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = tk.Canvas(scroll_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=canvas.yview)

        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)

        choice_vars = {}

        for section in sections:
            section_frame = ttk.Frame(content_frame)
            section_frame.pack(fill=tk.X, pady=(10, 5))

            section_label = ttk.Label(section_frame, text=f"Section: {section.name}", font=('Segoe UI', 10, 'bold'))
            section_label.pack(anchor=tk.W)

            for option in section.options:
                option_frame = ttk.Frame(content_frame)
                option_frame.pack(fill=tk.X, padx=20, pady=2)

                option_label = ttk.Label(option_frame, text=f"Option: {option.name}", font=('Segoe UI', 9, 'italic'))
                option_label.pack(anchor=tk.W)

                for choice in option.choices:
                    choice_frame = ttk.Frame(content_frame)
                    choice_frame.pack(fill=tk.X, padx=40, pady=1)

                    choice_key = f"{option.name} - {choice.name}"
                    choice_vars[choice_key] = tk.BooleanVar(value=False)
                    choice_check = ttk.Checkbutton(choice_frame, text=choice_key, variable=choice_vars[choice_key])
                    choice_check.pack(anchor=tk.W)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Apply", command=lambda: self.apply_patch_selection(selection_window, choice_vars)).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=selection_window.destroy).pack(side=tk.RIGHT)

        selection_window.update_idletasks()
        width = selection_window.winfo_width()
        height = selection_window.winfo_height()
        x = (selection_window.winfo_screenwidth() // 2) - (width // 2)
        y = (selection_window.winfo_screenheight() // 2) - (height // 2)
        selection_window.geometry(f"{width}x{height}+{x}+{y}")

    def apply_patch_selection(self, window, choice_vars):
        self.selected_choices = []
        for choice_key, var in choice_vars.items():
            if var.get():
                option_name, choice_name = choice_key.split(" - ")
                self.selected_choices.append(choice_name)
                debug_log(f"Selected choice: {choice_name} from option: {option_name}")
        window.destroy()
        self.start_build_process()
    
    def build_iso(self):
        if not self.iso_path.get() or not self.xml_path.get() or not self.mods_path.get():
            messagebox.showerror(
                "Hoshi Iso Builder", 
                self.localization.get_string('Messages', 'select_all_files', 'Veuillez sélectionner tous les fichiers nécessaires')
            )
            return
        
        if not os.path.exists(self.iso_path.get()):
            messagebox.showerror(
                "Hoshi Iso Builder", 
                self.localization.get_string('Messages', 'invalid_iso', 'Fichier ISO/WBFS invalide')
            )
            return
        
        if not os.path.exists(self.xml_path.get()):
            messagebox.showerror(
                "Hoshi Iso Builder", 
                self.localization.get_string('Messages', 'invalid_xml', 'Fichier XML invalide')
            )
            return
        
        if not os.path.exists(self.mods_path.get()):
            messagebox.showerror(
                "Hoshi Iso Builder", 
                self.localization.get_string('Messages', 'invalid_mods', 'Dossier de mods invalide')
            )
            return
        
        try:
            sections = get_riiv_patches_inf(self.iso_path.get(), self.xml_path.get(), self.mods_path.get())
            
            if sections is None:
                messagebox.showerror("Hoshi Iso Builder", "Riivolution XML est défectueux")
                return
            
            self.show_patch_selection(sections)
            
        except Exception as e:
            messagebox.showerror("Hoshi Iso Builder", f"Erreur lors de l'analyse des patches: {str(e)}")
    
    def start_build_process(self):
        debug_log(f"Selected choices: {self.selected_choices}")
        result = apply_riiv_patches_wrapper(
            self.iso_path.get(),
            self.xml_path.get(),
            self.mods_path.get(),
            self.selected_choices
        )
        if result:
            debug_log("Patch application completed successfully.")
        else:
            debug_log("Patch application failed.")

    def update_progress(self, value):
        self.progress_bar["value"] = value
        self.root.update_idletasks() 
            
    def build_process(self):
        try:
            file_ops.rm_folder("tmp")
            file_ops.rm_file("tmp_wit.xml")
            file_ops.rm_file("tmp_gl.txt")
            file_ops.rm_file("result.wbfs")
            
            self.root.after(0, lambda: self.update_progress(10))
            
            result = apply_riiv_patches_wrapper(
                self.iso_path.get(),
                self.xml_path.get(),
                self.mods_path.get(),
                self.selected_choices
            )
            
            self.root.after(0, lambda: self.update_progress(100))
            
            if result:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Hoshi Iso Builder", 
                    self.localization.get_string('Messages', 'build_success', 'Construction terminée avec succès')
                ))
                self.root.after(0, lambda: self.status_var.set(self.localization.get_string('Messages', 'build_success', 'Construction terminée avec succès')))
            else:
                self.root.after(0, lambda: messagebox.showerror(
                    "Hoshi Iso Builder", 
                    self.localization.get_string('Messages', 'build_error', 'Erreur lors de la construction')
                ))
                self.root.after(0, lambda: self.status_var.set(self.localization.get_string('Messages', 'build_error', 'Erreur lors de la construction')))
        
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("Hoshi Iso Builder", f"Erreur: {str(e)}"))
            self.root.after(0, lambda e=e: self.status_var.set(f"Erreur: {str(e)}"))
            
def main():
    parser = argparse.ArgumentParser(description="Hoshi Iso Builder")
    parser.add_argument("--game", help="Chemin vers le fichier ISO/WBFS du jeu", default=None)
    parser.add_argument("--xml", help="Chemin vers le fichier XML", default=None)
    parser.add_argument("--mods", help="Chemin vers le dossier de mods", default=None)
    args = parser.parse_args()

    root = tk.Tk()
    app = HoshiIsoBuilder(root, iso_path=args.game, xml_path=args.xml, mods_path=args.mods)
    root.mainloop()

if __name__ == "__main__":
    main()