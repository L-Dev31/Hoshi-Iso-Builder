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

# Standard library imports
import os
import xml.etree.ElementTree as ET
from textwrap import wrap

def generate_temp_txt(geckoloader_patches):
    """Generates temp.txt with GeckoLoader patches."""
    with open("temp.txt", "w") as f:
        for patch in geckoloader_patches:
            offset = int(patch[0], 16)
            valuelist = wrap(patch[1], width=8)
            while len(valuelist[-1]) != 8:
                valuelist[-1] += "0"
            if len(valuelist) % 2 != 0:
                valuelist.append("00000000")
            f.write(f"{offset - 0x80000000 + 0x06000000:08X} {len(patch[1]) // 2:08X}\n")
            for i in range(len(valuelist)):
                f.write(f"{valuelist[i]} " if i % 2 == 0 else f"{valuelist[i]}\n")

def generate_temp_xml(root, patch_elems, patches_id, game_reg):
    """Generates temp.xml based on the patches and game region."""
    for patch in root.findall("patch"):
        if patch.attrib["id"] not in patches_id:
            root.remove(patch)
    
    for patch in patch_elems:
        for mem in patch:
            if "target" in mem.attrib and mem.attrib["target"] != game_reg:
                patch.remove(mem)
    
    tree = ET.ElementTree(root)
    tree.write("temp.xml")
