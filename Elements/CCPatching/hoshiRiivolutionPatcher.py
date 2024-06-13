#------------------------------------------------------------------------------
# This file is part of Hoshi - Wii ISO Builder.
# by Humming Owl (Isaac LIENDO) | rewritten by L-DEV (Léo TOSKU)
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
import shutil
import xml.etree.ElementTree as ET
import subprocess
import tkinter as tk
from tkinter import messagebox
from Elements.CCPatching.hoshiPatchFilesGenerator import generate_temp_txt, generate_temp_xml

# Custom imports
exec(open("Elements/CCPatching/hoshiBinaryToolsSetup.py").read())

def exec_subprocess(command):
    """Executes a subprocess command and returns the result."""
    return subprocess.run(command, capture_output=True, text=True)

def show_error_message(error_message):
    """Displays an error message in a message box."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", error_message)
    root.destroy()

def check_game_image(game_image_path):
    """Checks if the game image is valid."""
    result = exec_subprocess([wit_path, "verify", "--test", "--quiet", game_image_path])
    if result.returncode != 0:
        show_error_message("Invalid ISO/WBFS.")
        exit(1)

def check_game_xml_id(game_image_path, riiv_xml_id):
    """Checks if the game image ID matches the Riivolution XML ID."""
    game_id = exec_subprocess([wit_path, "ID6", game_image_path])
    game_id = game_id.stdout[:-4]
    if game_id != riiv_xml_id:
        show_error_message("Riivolution XML is incompatible with game image.")
        exit(1)

def get_xml_patches(riiv_xml_path):
    """Returns the patches that can be applied from the Riivolution XML."""
    xml = ET.parse(riiv_xml_path)
    root = xml.getroot()
    sections = []
    
    for section in root.find("options").findall("section"):
        section_name = section.get("name")
        options = []
        
        for option in section.findall("option"):
            option_name = option.get("name")
            choices = []
            
            for choice in option.findall("choice"):
                choice_name = choice.get("name")
                patches = [patch.get("id") for patch in choice.findall("patch")]
                choices.append((choice_name, patches))
                
            options.append((option_name, choices))
        
        sections.append((section_name, options))
    
    return sections

def validate_mod_files(mod_files_path, file_elems, memory_elems, game_reg):
    """Checks if the mod files path is valid."""
    for file in file_elems:
        if not os.path.exists(os.path.join(mod_files_path, file.attrib["external"])):
            return False
    for mem in memory_elems:
        if "valuefile" in mem.attrib:
            valuefile_path = mem.attrib["valuefile"].replace("{$__region}", game_reg)
            if not os.path.exists(os.path.join(mod_files_path, valuefile_path)):
                return False
    return True

def apply_patches(game_image_path, riiv_xml_path, mod_files_path, patches_id):
    try: 
        # Verify inserted datas
        print("Selected game file :", game_image_path)
        print("Selected Riivolution XML file:", riiv_xml_path)
        print("Selected mod files path:", mod_files_path)
        print("Selected patches :", patches_id)

        check_game_image(game_image_path)

        # Parse Riivolution XML
        xml = ET.parse(riiv_xml_path)
        root = xml.getroot()

        # Retrieve patch elements based on IDs
        id_elem = None
        options_elem = None
        patch_elems = []
        for child in root:
            if child.tag == "id":
                id_elem = child
            elif child.tag == "options":
                options_elem = child
            elif child.tag == "patch" and child.attrib["id"] in patches_id:
                patch_elems.append(child)

        # Determine game's region
        regions = []
        if len(id_elem) != 0:
            check_game_xml_id(game_image_path, id_elem.attrib["game"])
            for child in id_elem:
                regions.append(child.attrib["type"])
        else:
            regions = ["E", "P", "J", "K", "W"]

        # Check if game's region is supported by the XML
        game_reg = exec_subprocess([wit_path, "ID6", game_image_path]).stdout[3:4]
        if game_reg not in regions:
            show_error_message("Game region not supported by XML.")
            exit(1)

        # Retrieve folder, file, and memory elements from patches
        folder_elems = []
        file_elems = []
        memory_elems = []
        for patch in patch_elems:
            folder_elems += patch.findall("folder")
            file_elems += patch.findall("file")
            memory_elems += patch.findall("memory")

        # Validate mod files path
        if not validate_mod_files(mod_files_path, file_elems, memory_elems, game_reg):
            show_error_message("Invalid Mod files path. Check the path and try again.")
            exit(1)
        print("Mod files path is valid...")

        # Extract game files
        temp_folder_path = "temp/files"
        exec_subprocess([wit_path, "extract", game_image_path, "temp/"])
        if os.path.exists("temp/DATA"):
            temp_folder_path = "temp/DATA/files"

        # Generate geckoloader patches
        geckoloader_patches = []
        for mem in memory_elems:
            if int(mem.attrib["offset"][2:], 16) <= 0x8000FFFF:
                patch = [mem.attrib["offset"][2:], mem.attrib.get("value", "")]
                if "valuefile" in mem.attrib:
                    valuefile_path = mem.attrib["valuefile"].replace("{$__region}", game_reg)
                    with open(os.path.join(mod_files_path, valuefile_path), "rb") as vf:
                        patch[1] = vf.read().hex().upper()
                geckoloader_patches.append(patch)
            elif "valuefile" in mem.attrib:
                mem.set("valuefile", mem.attrib["valuefile"].replace("{$__region}", game_reg))

        # Generate temporary XML and TXT files
        generate_temp_xml(root, patch_elems, patches_id, game_reg)
        generate_temp_txt(geckoloader_patches)

        print("Patching main.dol...")

        #Determine system path
        sys_path = "temp/DATA/sys" if "DATA" in temp_folder_path else "temp/sys"

        # Apply GeckoLoader patch
        geckopatch = subprocess.run(["python", geckoloader_path, sys_path + "/main.dol", "temp.txt", "--dest", sys_path + "/main_1.dol", "--txtcodes", "ALL"], capture_output=True, text=True)
        print("GeckoLoader.py output:", geckopatch.stdout)

        #Apply WIT patch
        witpatch = subprocess.run([wit_path, "dolpatch", sys_path + "/main_1.dol", "XML=temp.xml", "--source", mod_files_path, "--dest", sys_path + "/main_2.dol"], capture_output=True, text=True)
        print("wit.exe output:", witpatch.stdout)

        # Move patched files
        shutil.move(f"{sys_path}/main_2.dol", f"{sys_path}/main.dol")
        os.remove(f"{sys_path}/main_1.dol")


    except Exception as e:
        show_error_message(f"An error occurred: {str(e)}")

# Example usage:
# apply_patches(iso_file, xml_file, mod_folder, selected_patches)

