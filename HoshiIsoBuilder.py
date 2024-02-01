import tkinter as tk
from tkinter import filedialog
import os
import webbrowser
import json

def start_building():
    destination_path = file_paths["Destination Rom (.iso .wbfs)"].get("1.0", tk.END).strip()
    if not destination_path:
        print("Please select a destination ROM file.")
        return

    riivolution_file = file_paths["Riivolution file (.xml)"].get("1.0", tk.END).strip()
    riivolution_folder = file_paths["Riivolution patch folder"].get("1.0", tk.END).strip()
    custom_code_folder = file_paths["Custom code folder"].get("1.0", tk.END).strip()

    if not riivolution_file or not custom_code_folder:
        print("Please select Riivolution file and Custom code folder.")
        return

    elements_directory = "Elements"
    if not os.path.exists(elements_directory):
        os.makedirs(elements_directory)

    base_rom_file = file_paths["Base Rom (.iso .wbfs)"].get("1.0", tk.END).strip()

    if not base_rom_file:
        print("Please select a Base ROM file.")
        return

    # Create start.bat content
    bat_content = f'.\\start.exe "{riivolution_file}" "{custom_code_folder}" "{destination_path}" E\n'

    # Add dolpatch commands

    # Wit conversion
    bat_content += f'wit extract "{base_rom_file}" ".\\temp"\n'

    # Apply mod patch
    bat_content += f'xcopy /E /I "{riivolution_folder}" ".\\temp"\n'
    bat_content += f'xcopy /E /I ".\\temp" ".\\temp\\files"\n'

    # Rebuild ISO/WBFS
    bat_content += f'wit copy ".\\temp" "{destination_path}"\n'

    bat_file_path = os.path.join(elements_directory, "start.bat")

    with open(bat_file_path, "w") as bat_file:
        bat_file.write(bat_content)

    os.system(bat_file_path)
    print(f"Building to: {destination_path}")


def open_file(file_type):
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
        print(f"Selected {file_type} file/folder: {file_path}")
        update_file_path(file_type, file_path)

def update_file_path(file_type, file_path):
    file_paths[file_type].delete(1.0, tk.END)
    file_paths[file_type].insert(tk.END, file_path)

def set_theme(theme):
    theme_colors = dark_theme if theme == "Dark" else light_theme
    root.config(bg=theme_colors["bg"])
    title_label.config(bg=theme_colors["bg"], fg=theme_colors["fg"])
    options_frame.config(bg=theme_colors["bg"])
    for file_type in file_paths:
        file_paths[file_type].config(bg=theme_colors["bg"], fg=theme_colors["fg"])
    footer_frame.config(bg=theme_colors["bg"])
    print(f"Setting theme to {theme}")

def open_github_io(url):
    webbrowser.open(url)

def save_settings():
    settings = {
        "riivolution_file": file_paths["Riivolution file (.xml)"].get("1.0", tk.END).strip(),
        "riivolution_folder": file_paths["Riivolution patch folder"].get("1.0", tk.END).strip(),
        "custom_code_folder": file_paths["Custom code folder"].get("1.0", tk.END).strip(),
        "base_rom_file": file_paths["Base Rom (.iso .wbfs)"].get("1.0", tk.END).strip(),
        "destination_path": file_paths["Destination Rom (.iso .wbfs)"].get("1.0", tk.END).strip()

    }

    save_path = filedialog.asksaveasfilename(defaultextension=".hos", filetypes=[("HOS files", "*.hos")])
    if save_path:
        with open(save_path, "w") as save_file:
            json.dump(settings, save_file)
        print(f"Settings saved to: {save_path}")

def import_settings():
    import_path = filedialog.askopenfilename(filetypes=[("HOS files", "*.hos")])
    if import_path:
        with open(import_path, "r") as import_file:
            settings = json.load(import_file)

        # Update GUI with imported settings
        for param, value in settings.items():
            update_file_path(param, value)

        print(f"Settings imported from: {import_path}")

root = tk.Tk()
root.title("Hoshi Iso Builder")
root.geometry("500x550")
root.resizable(False, False)

icon_image = tk.PhotoImage(file="icon.png")
root.iconphoto(True, icon_image)

dark_theme = {"bg": "#1e1e1e", "fg": "#ffffff"}
light_theme = {"bg": "#ffffff", "fg": "#000000"}
light_grey = "#7a7aff"
custom_font = ("Helvetica", 12)

root.config(bg=dark_theme["bg"])

title_label = tk.Label(root, text="Hoshi Iso Builder v0.1", font=("Helvetica", 16), **dark_theme)
title_label.pack(pady=10)

options_frame = tk.Frame(root, bg=dark_theme["bg"])
options_frame.pack(pady=10)

file_types = ["Riivolution file (.xml)", "Riivolution patch folder", "Custom code folder", "Base Rom (.iso .wbfs)", "Destination Rom (.iso .wbfs)"]

file_paths = {}

for file_type in file_types:
    option_button = tk.Button(options_frame, text=file_type, font=custom_font, bg="#7a7aff", fg="#ffffff", relief=tk.FLAT, command=lambda ft=file_type: open_file(ft))
    option_button.pack(pady=5, fill=tk.X)

    file_path_text = tk.Text(options_frame, height=1, width=40, wrap=tk.WORD, bg=dark_theme["bg"], fg=dark_theme["fg"], font=custom_font)
    file_path_text.pack(pady=5, fill=tk.X)

    file_paths[file_type] = file_path_text

footer_frame = tk.Frame(root, bg=dark_theme["bg"])
footer_frame.pack(pady=10)

start_button = tk.Button(root, text="Start Building !", command=start_building, font=custom_font, bg=light_grey, fg="#ffffff", relief=tk.FLAT, bd=0, padx=20, pady=10, borderwidth=0, highlightthickness=0, overrelief="flat", activebackground="#5555ff", activeforeground="#ffffff")
start_button.pack(pady=20, fill=tk.X)

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

theme_menu = tk.Menu(menu_bar, tearoff=0)
theme_menu.add_command(label="Dark", command=lambda: set_theme("Dark"))
theme_menu.add_command(label="Light", command=lambda: set_theme("Light"))

language_menu = tk.Menu(menu_bar, tearoff=0)
language_options = ["English", "Français", "日本語", "Русский"]
for lang in language_options:
    language_menu.add_command(label=lang, command=lambda lang=lang: print(f"Language set to {lang}"))

save_menu = tk.Menu(menu_bar, tearoff=0)
save_menu.add_command(label="Save settings as..", command=save_settings)
save_menu.add_command(label="Import settings", command=import_settings)

about_menu = tk.Menu(menu_bar, tearoff=0)
about_menu.add_command(label="UI design by L-DEV (Léo TOSKU)", command=lambda: open_github_io("https://github.com/L-Dev31"))
about_menu.add_command(label="System programming by Humming Owl", command=lambda: open_github_io("https://system-programming.github.io"))
about_menu.add_command(label="Wit by Wimm (Dirk CLEMENS)", command=lambda: open_github_io("https://github.com/Wiimm"))

menu_bar.add_cascade(label="File", menu=save_menu)
menu_bar.add_cascade(label="Theme", menu=theme_menu)
menu_bar.add_cascade(label="Language", menu=language_menu)
menu_bar.add_cascade(label="Credits", menu=about_menu)


root.mainloop()
