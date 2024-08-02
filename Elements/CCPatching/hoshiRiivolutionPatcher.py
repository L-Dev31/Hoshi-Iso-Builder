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
import tempfile
import xml.etree.ElementTree as ET
import subprocess
import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple
from Elements.CCPatching.hoshiPatchFilesGenerator import generate_temp_txt, generate_temp_xml

# Custom imports
exec(open("Elements/CCPatching/hoshiBinaryToolsSetup.py").read())

# Configuration
TEMP_FOLDER = "temp"
TEMP_FILES_FOLDER = os.path.join(TEMP_FOLDER, "files")
TEMP_DATA_FOLDER = os.path.join(TEMP_FOLDER, "DATA")
TEMP_XML_FILE = "temp.xml"
TEMP_TXT_FILE = "temp.txt"

def exec_subprocess(command: List[str]) -> subprocess.CompletedProcess:
    """Executes a subprocess command and returns the result."""
    return subprocess.run(command, capture_output=True, text=True)

def show_error_message(error_message: str) -> None:
    """Displays an error message in a message box."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", error_message)
    root.destroy()

def check_game_image(game_image_path: str) -> None:
    """Checks if the game image is valid."""
    if not os.path.exists(game_image_path):
        raise ValueError("Game image file does not exist.")
    result = exec_subprocess([wit_path, "verify", "--test", "--quiet", game_image_path])
    if result.returncode != 0:
        raise ValueError("Invalid ISO/WBFS.")

def check_game_xml_id(game_image_path: str, riiv_xml_id: str) -> None:
    """Checks if the game image ID matches the Riivolution XML ID."""
    game_id = exec_subprocess([wit_path, "ID6", game_image_path])
    game_id = game_id.stdout[:-4]
    if game_id != riiv_xml_id:
        raise ValueError("Riivolution XML is incompatible with game image.")

def get_xml_patches(riiv_xml_path: str) -> List[Tuple[str, List[Tuple[str, List[Tuple[str, List[str]]]]]]]:
    """Returns the patches that can be applied from the Riivolution XML."""
    if not os.path.exists(riiv_xml_path):
        raise FileNotFoundError("Riivolution XML file does not exist.")
    xml = ET.parse(riiv_xml_path)
    root = xml.getroot()
    sections = []
    
    options_elem = root.find("options")
    if options_elem is None:
        raise ValueError("Invalid Riivolution XML: No 'options' element found.")
    
    for section in options_elem.findall("section"):
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

def validate_mod_files(mod_files_path: str, file_elems: List[ET.Element], memory_elems: List[ET.Element], game_reg: str) -> bool:
    """Checks if the mod files path is valid."""
    if not os.path.isdir(mod_files_path):
        raise ValueError("Mod files path is not a valid directory.")
    for file in file_elems:
        if not os.path.exists(os.path.join(mod_files_path, file.attrib["external"])):
            return False
    for mem in memory_elems:
        if "valuefile" in mem.attrib:
            valuefile_path = mem.attrib["valuefile"].replace("{$__region}", game_reg)
            if not os.path.exists(os.path.join(mod_files_path, valuefile_path)):
                return False
    return True

def apply_patches(game_image_path: str, riiv_xml_path: str, mod_files_path: str, patches_id: List[str]) -> None:
    try: 
        # Verify inserted data
        print("Selected game file :", game_image_path)
        print("Selected Riivolution XML file:", riiv_xml_path)
        print("Selected mod files path:", mod_files_path)
        print("Selected patches :", patches_id)

        check_game_image(game_image_path)

        # Parse Riivolution XML
        xml = ET.parse(riiv_xml_path)
        root = xml.getroot()

        # Retrieve patch elements based on IDs
        id_elem = root.find("id")
        options_elem = root.find("options")
        patch_elems = [patch for patch in root.findall("patch") if patch.attrib["id"] in patches_id]

        # Determine game's region
        regions = []
        if id_elem is not None and len(id_elem) != 0:
            check_game_xml_id(game_image_path, id_elem.attrib["game"])
            regions = [child.attrib["type"] for child in id_elem]
        else:
            regions = ["E", "P", "J", "K", "W"]

        # Check if game's region is supported by the XML
        game_reg = exec_subprocess([wit_path, "ID6", game_image_path]).stdout[3:4]
        if game_reg not in regions:
            raise ValueError("Game region not supported by XML.")

        # Retrieve folder, file, and memory elements from patches
        folder_elems = [folder for patch in patch_elems for folder in patch.findall("folder")]
        file_elems = [file for patch in patch_elems for file in patch.findall("file")]
        memory_elems = [memory for patch in patch_elems for memory in patch.findall("memory")]

        # Validate mod files path
        if not validate_mod_files(mod_files_path, file_elems, memory_elems, game_reg):
            raise ValueError("Invalid Mod files path. Check the path and try again.")
        print("Mod files path is valid...")

        # Extract game files
        temp_folder_path = os.path.join(TEMP_FOLDER, "files")
        exec_subprocess([wit_path, "extract", game_image_path, TEMP_FOLDER])
        if os.path.exists(TEMP_DATA_FOLDER):
            temp_folder_path = os.path.join(TEMP_DATA_FOLDER, "files")

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

        # Determine system path
        sys_path = os.path.join(TEMP_DATA_FOLDER, "sys") if "DATA" in temp_folder_path else os.path.join(TEMP_FOLDER, "sys")
        main_dol_path = os.path.join(sys_path, "main.dol")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Apply GeckoLoader patch
            gecko_output = os.path.join(temp_dir, "gecko_output.dol")
            geckopatch = subprocess.run(["python", geckoloader_path, main_dol_path, TEMP_TXT_FILE, "--dest", gecko_output, "--txtcodes", "ALL"], capture_output=True, text=True)
            print("GeckoLoader.py output:", geckopatch.stdout)

            # Apply WIT patch
            wit_output = os.path.join(temp_dir, "wit_output.dol")
            witpatch = subprocess.run([wit_path, "dolpatch", gecko_output, f"XML={TEMP_XML_FILE}", "--source", mod_files_path, "--dest", wit_output], capture_output=True, text=True)
            print("wit.exe output:", witpatch.stdout)

            # Replace the original main.dol with the patched version
            shutil.move(wit_output, main_dol_path)

    except Exception as e:
        show_error_message(f"An error occurred: {str(e)}")

# Example usage:
# apply_patches(iso_file, xml_file, mod_folder, selected_patches)