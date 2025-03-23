from lxml import etree
import file_ops
import subprocess
import os
import shutil
import sys
import xml_utils
from file_ops import debug_log

WINDOWS, LINUX = range(0, 2)
SYSTEM_OS = WINDOWS
if sys.platform == "linux":
    SYSTEM_OS = LINUX

geckoloader_path = ["tools/geckoloader/GeckoLoader.py"]
wit_path = None
if SYSTEM_OS == WINDOWS:
    wit_path = os.path.abspath("tools/wit/windows/wit.exe")
elif SYSTEM_OS == LINUX:
    wit_path = os.path.abspath("tools/wit/linux/wit")

def exec_subprocess(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        debug_log("Executed command: " + " ".join(command))
        debug_log("STDOUT: " + result.stdout)
        debug_log("STDERR: " + result.stderr)
        return result
    except Exception as e:
        debug_log("Error executing " + " ".join(command) + ": " + str(e))
        raise

def rtn_def_param_str(string, params_list):
    try:
        s = string.replace("{$__gameid}", params_list[0]).replace("{$__region}", params_list[1]).replace("{$__maker}", params_list[2])
        return file_ops.get_path_str(s)
    except Exception as e:
        debug_log("Error in rtn_def_param_str: " + str(e))
        raise

def check_game_image(game_image_path):
    result = exec_subprocess([wit_path, "verify", "--test", game_image_path])
    valid = result.returncode == 0
    if not valid:
        debug_log("Game image failed verification with WIT.")
    return valid

def check_game_xml_id(game_image_path, riiv_xml_id):
    game_id = exec_subprocess([wit_path, "ID6", game_image_path]).stdout.strip()
    is_id_sec_valid = [False, False, False]
    if riiv_xml_id[0] == game_id[:-3] or riiv_xml_id[0] == "":
        is_id_sec_valid[0] = True
    if len(riiv_xml_id[1]) == 0:
        is_id_sec_valid[1] = True
    else:
        for reg in riiv_xml_id[1]:
            if reg == game_id[3:-2]:
                is_id_sec_valid[1] = True
    if riiv_xml_id[2] == game_id[4:] or riiv_xml_id[2] == "":
        is_id_sec_valid[2] = True
    if False in is_id_sec_valid:
        debug_log("XML IDs do not match game IDs.")
        return False
    return game_id

def check_riiv_xml(xml_path):
    try:
        valid = xml_utils.check_with_sch(xml_path, "MyRiivolution.xsd")
        if not valid:
            debug_log("XML file does not conform to Riivolution schema.")
        return valid
    except Exception as e:
        debug_log("Error checking XML schema: " + str(e))
        return False

def get_patch_elem_root_path(root_elem, patch_elem):
    try:
        root_path = ""
        if "root" in root_elem.attrib:
            root_path += root_elem.attrib["root"]
        if "root" in patch_elem.attrib:
            root_path += patch_elem.attrib["root"]
        return file_ops.get_path_str(root_path)
    except Exception as e:
        debug_log("Error in get_patch_elem_root_path: " + str(e))
        raise

def check_riiv_patches(game_path, xml_path, mod_files_folder):
    if not check_game_image(game_path):
        print("Invalid ISO/WBFS")
        return False
    if not check_riiv_xml(xml_path):
        print("Invalid Riivolution XML")
        return False
    try:
        xml_tree = etree.parse(xml_path, etree.XMLParser(remove_comments=True))
        root = xml_tree.getroot()
    except Exception as e:
        debug_log("Error parsing XML: " + str(e))
        return False
    riiv_game_id = ["", [], ""]
    id_elem = root.find("id")
    if id_elem is not None:
        if "game" in id_elem.attrib:
            riiv_game_id[0] = id_elem.attrib["game"]
            if len(riiv_game_id[0]) == 3:
                for reg in id_elem:
                    riiv_game_id[1].append(reg.attrib["type"])
            else:
                riiv_game_id[1].append(riiv_game_id[0][3:])
                riiv_game_id[0] = riiv_game_id[0][:-1]
        if "developer" in id_elem.attrib:
            riiv_game_id[2] = id_elem.attrib["developer"]
    game_id = check_game_xml_id(game_path, riiv_game_id)
    if not game_id:
        print("Riivolution XML is not compatible with the provided Wii game")
        return False
    game_id_parts = [game_id[:-3], game_id[3:-2], game_id[4:]]
    debug_log("Split Game ID: " + str(game_id_parts))
    opt_patches_id = []
    options_elem = root.find("options")
    if options_elem is not None:
        for sec in options_elem:
            for opt in sec:
                for choice in opt:
                    for patch in choice:
                        opt_patches_id.append(patch.attrib["id"])
    elems_patch_id = [patch.attrib["id"] for patch in root.findall("patch")]
    for patch_id in opt_patches_id:
        if patch_id not in elems_patch_id:
            print("Patch from options does not exist in the XML")
            return False
    game_files_result = exec_subprocess([wit_path, "files", game_path])
    game_files = [file_ops.get_path_str(f.replace("DATA/files", "").replace("./files", "")) for f in game_files_result.stdout.split("\n") if ("DATA/files" in f or "./files" in f)]
    debug_log("Game files found: " + str(game_files))
    for patch in root.findall("patch"):
        patch_root_path = rtn_def_param_str(file_ops.get_base_path(mod_files_folder, True) + "/" + get_patch_elem_root_path(root, patch), game_id_parts)
        for patch_type in patch:
            if patch_type.tag == "file":
                fpath = patch_root_path + "/" + rtn_def_param_str(patch_type.attrib["external"], game_id_parts)
                if not file_ops.f_exists(fpath):
                    print("[WARNING] Line " + str(patch_type.sourceline) + ": File " + fpath + " does not exist. Skipping...")
                    continue
                if patch_type.attrib["disc"] not in game_files and patch_type.attrib.get("create", "false") == "false":
                    print("Line " + str(patch_type.sourceline) + ": File patch creates non-existent disc file without create attribute")
                    return False
            elif patch_type.tag == "folder":
                fpath = patch_root_path + "/" + rtn_def_param_str(patch_type.attrib["external"], game_id_parts)
                if not file_ops.f_exists(fpath):
                    print("[WARNING] Line " + str(patch_type.sourceline) + ": Folder " + fpath + " does not exist. Skipping...")
                    continue
                if "disc" in patch_type.attrib and rtn_def_param_str(patch_type.attrib["disc"], game_id_parts) not in game_files:
                    if patch_type.attrib.get("create", "false") == "false":
                        print("Line " + str(patch_type.sourceline) + ": Folder patch creates non-existent disc folder with create = False")
                        return False
            elif patch_type.tag == "memory":
                if "valuefile" in patch_type.attrib:
                    fpath = patch_root_path + "/" + rtn_def_param_str(patch_type.attrib["valuefile"], game_id_parts)
                    if not file_ops.f_exists(fpath):
                        print("[WARNING] Line " + str(patch_type.sourceline) + ": Memory patch file " + fpath + " does not exist. Skipping...")
                        continue
                if "0x8" not in patch_type.attrib["offset"]:
                    print("Line " + str(patch_type.sourceline) + ": Memory patch tries patching outside the 0x80000000 memory area")
                    return False
                if "original" in patch_type.attrib:
                    ram_dump_path = f"ram_dumps/{game_id_parts[0]}{game_id_parts[1]}{game_id_parts[2]}.bin"
                    if (not file_ops.f_exists(ram_dump_path) or file_ops.get_file_size(ram_dump_path) != 0x1800000):
                        print("Line " + str(patch_type.sourceline) + ": Memory element has original condition. No/Invalid ram dump of \"" + game_id_parts[0] + game_id_parts[1] + game_id_parts[2] + "\" was found in ram_dumps/")
                        return False
    return True

def check_riiv_patches_wrapper(game_path, xml_path, mod_files_folder):
    result = check_riiv_patches(game_path, xml_path, mod_files_folder)
    file_ops.rm_folder("tmp")
    return result

def get_riiv_patches_inf(game_path, xml_path, mod_files_folder):
    if not check_riiv_patches_wrapper(game_path, xml_path, mod_files_folder):
        return None
    class Section:
        def __init__(self, name):
            self.name = name
            self.options = []
    class Option:
        def __init__(self, name):
            self.name = name
            self.choices = []
    class Choice:
        def __init__(self, name):
            self.name = name
            self.patches = []
    class Patch:
        def __init__(self, id):
            self.id = id
    sections = []
    try:
        xml_tree = etree.parse(xml_path, etree.XMLParser(remove_comments=True))
        options_elem = xml_tree.find("options")
        for sec in options_elem:
            section_obj = Section(sec.attrib["name"])
            for opt in sec:
                option_obj = Option(opt.attrib["name"])
                for cho in opt:
                    choice_obj = Choice(cho.attrib["name"])
                    for pat in cho:
                        choice_obj.patches.append(Patch(pat.attrib["id"]))
                    option_obj.choices.append(choice_obj)
                section_obj.options.append(option_obj)
            sections.append(section_obj)
    except Exception as e:
        debug_log("Error extracting patch info: " + str(e))
        return None
    return sections

def patch_memory_section(patch_elems, root, mod_files_folder, game_id, ram_dump):
    try:
        tmp_gl = open("tmp_gl.txt", "w")
        tmp_wit = open("tmp_wit.xml", "w")
    except Exception as e:
        debug_log("Error creating temporary files: " + str(e))
        return False
    for patch in patch_elems:
        patch_root_path = rtn_def_param_str(file_ops.get_base_path(mod_files_folder, True) + "/" + get_patch_elem_root_path(root, patch), game_id)
        for patch_type in patch:
            if patch_type.tag != "memory":
                continue
            try:
                offset_hex_str = patch_type.attrib["offset"][2:]
                offset_hex_int = int(offset_hex_str, 16)
                debug_log("Patching memory at offset " + patch_type.attrib["offset"] + " (converted to " + str(offset_hex_int) + ")")
            except Exception as e:
                debug_log("Error converting offset: " + str(e))
                continue
            if "original" in patch_type.attrib:
                expected_hex = patch_type.attrib["original"].upper().replace("0X", "")
                dump_offset = offset_hex_int - 0x80000000
                ram_dump.seek(dump_offset)
                expected_length = int(len(expected_hex) / 2)
                actual_hex = ram_dump.read(expected_length).hex().upper()
                if expected_hex != actual_hex:
                    debug_log("[ERROR] At offset " + patch_type.attrib["offset"] + ": expected " + expected_hex + " != read " + actual_hex + ".")
                    return False
                patch_type.attrib["original"] = expected_hex
            if "valuefile" in patch_type.attrib:
                val_file_path = patch_root_path + "/" + rtn_def_param_str(patch_type.attrib["valuefile"], game_id)
                try:
                    with open(val_file_path, "rb") as vf:
                        data = vf.read(file_ops.get_file_size(val_file_path))
                    patch_type.attrib.pop("valuefile", None)
                    patch_type.set("value", data.hex().upper())
                except Exception as e:
                    debug_log("Error reading valuefile: " + str(e))
                    continue
            else:
                patch_type.attrib["value"] = patch_type.attrib["value"].upper().replace("0X", "")
            try:
                if offset_hex_int > 0x8000FFFF:
                    tmp_str = etree.tostring(patch_type).decode("utf-8").strip()
                    tmp_wit.write(tmp_str + "\n")
                    debug_log("Memory patch (XML) applied for offset " + patch_type.attrib["offset"])
                else:
                    value_str = patch_type.attrib["value"]
                    last_offset = offset_hex_int
                    while len(value_str) >= 8:
                        part = value_str[:8]
                        line = "%08X %s\n" % (last_offset - 0x80000000 + 0x04000000, part)
                        tmp_gl.write(line)
                        debug_log("Memory patch GL written: " + line.strip())
                        last_offset += 4
                        value_str = value_str[8:]
                    if len(value_str) == 6:
                        line1 = "%08X 0000%s\n" % (last_offset - 0x80000000 + 0x02000000, value_str[:-2])
                        line2 = "%08X 000000%s\n" % (last_offset + 2 - 0x80000000, value_str[4:])
                        tmp_gl.write(line1)
                        tmp_gl.write(line2)
                        debug_log("Memory patch GL written: " + line1.strip() + " and " + line2.strip())
                    elif len(value_str) == 4:
                        line = "%08X 0000%s\n" % (last_offset - 0x80000000 + 0x02000000, value_str)
                        tmp_gl.write(line)
                        debug_log("Memory patch GL written: " + line.strip())
                    elif len(value_str) == 2:
                        line = "%08X 000000%s\n" % (last_offset - 0x80000000, value_str)
                        tmp_gl.write(line)
                        debug_log("Memory patch GL written: " + line.strip())
            except Exception as e:
                debug_log("Error writing memory patch for offset " + patch_type.attrib["offset"] + ": " + str(e))
                continue
    tmp_wit.close()
    tmp_gl.close()
    return True

def apply_riiv_patches(game_path, xml_path, mod_files_folder, choice_str_list):
    if not check_riiv_patches_wrapper(game_path, xml_path, mod_files_folder):
        return False
    try:
        xml_tree = etree.parse(xml_path, etree.XMLParser(remove_comments=True))
        root = xml_tree.getroot()
    except Exception as e:
        debug_log("Error parsing XML in apply_riiv_patches: " + str(e))
        return False
    choices_names = []
    for sec in root.find("options"):
        for opt in sec:
            for cho in opt:
                choices_names.append(cho.attrib["name"])
    for choice_str in choice_str_list:
        if choice_str not in choices_names:
            debug_log("Choice '" + choice_str + "' does not exist in xml_utils.")
            return False
    patches_ids = []
    for sec in root.find("options"):
        for opt in sec:
            for cho in opt:
                if cho.attrib["name"] in choice_str_list:
                    for patch in cho:
                        patches_ids.append(patch.attrib["id"])
    patch_elems = [patch for patch in root.findall("patch") if patch.attrib["id"] in patches_ids]
    game_id_full = exec_subprocess([wit_path, "ID6", game_path]).stdout.strip()
    game_id = [game_id_full[:-3], game_id_full[3:-2], game_id_full[4:]]
    debug_log("Game ID for patching: " + str(game_id))
    result = exec_subprocess([wit_path, "extract", game_path, "tmp/"]).returncode
    if result != 0:
        debug_log("Error extracting game with WIT.")
        return False
    ext_game_path = "tmp/files/"
    if file_ops.f_exists("tmp/DATA/"):
        ext_game_path = "tmp/DATA/files/"
    for patch in patch_elems:
        patch_root_path = rtn_def_param_str(file_ops.get_base_path(mod_files_folder, True) + "/" + get_patch_elem_root_path(root, patch), game_id)
        for patch_type in patch:
            if patch_type.tag == "file":
                fpath1 = patch_root_path + "/" + rtn_def_param_str(patch_type.attrib["external"], game_id)
                fpath2 = rtn_def_param_str(ext_game_path + patch_type.attrib["disc"], game_id)
                file_ops.cp_file(fpath1, fpath2)
            elif patch_type.tag == "folder":
                if "disc" in patch_type.attrib:
                    fpath1 = patch_root_path + "/" + rtn_def_param_str(patch_type.attrib["external"], game_id)
                    fpath2 = rtn_def_param_str(ext_game_path + patch_type.attrib["disc"], game_id)
                    file_ops.cp_folder(fpath1, fpath2, False)

    has_memory_patches = any(
        patch_type.tag == "memory"
        for patch in patch_elems
        for patch_type in patch
    )

    memory_needs_original = any(
        patch_type.tag == "memory" and "original" in patch_type.attrib
        for patch in patch_elems
        for patch_type in patch
    )

    ram_dump = None
    if memory_needs_original:
        ram_dump_path = "ram_dumps/" + game_id[0] + game_id[1] + game_id[2] + ".bin"
        if not file_ops.f_exists(ram_dump_path):
            debug_log("Missing ram dump for memory patch.")
            return False
        ram_dump = open(ram_dump_path, "rb")

    if has_memory_patches:
        if not patch_memory_section(patch_elems, root, mod_files_folder, game_id, ram_dump):
            if ram_dump:
                ram_dump.close()
            return False

    if ram_dump:
        ram_dump.close()

    dol_path = "tmp/sys/main.dol"
    dol_tmp_path = "tmp/sys/main_tmp.dol"
    if file_ops.f_exists("tmp_gl.txt") and file_ops.get_file_size("tmp_gl.txt") != 0:
        print("[INFO] Patching DOL file...")
        result = exec_subprocess(["python"] + geckoloader_path + [dol_path, "tmp_gl.txt", "--dest", dol_tmp_path, "--txtcodes", "ALL", "--optimize"])
        if result.returncode != 0:
            print("An error occurred during GL DOL patching...")
            return False
        file_ops.cp_file(dol_tmp_path, dol_path)
        file_ops.rm_file(dol_tmp_path)
        if file_ops.f_exists("tmp_wit.xml") and file_ops.get_file_size("tmp_wit.xml") != 0:
            result = exec_subprocess([wit_path, "dolpatch", dol_path, "XML=tmp_wit.xml", "--dest", dol_tmp_path])
            if result.returncode != 0:
                print("An error occurred during WIT DOL patching...")
                return False
            file_ops.cp_file(dol_tmp_path, dol_path)
            file_ops.rm_file(dol_tmp_path)
    result = exec_subprocess([wit_path, "copy", "tmp/", "result.wbfs"])
    print("STDOUT: " + result.stdout)
    print("STDERR: " + result.stderr)
    return True

def apply_riiv_patches_wrapper(game_path, xml_path, mod_files_folder, choice_str_list):
    debug_log("Starting patch application...")
    debug_log("Game path: " + game_path)
    debug_log("XML path: " + xml_path)
    debug_log("Mod files folder: " + mod_files_folder)
    debug_log("Selected choices: " + str(choice_str_list))
    try:
        result = apply_riiv_patches(game_path, xml_path, mod_files_folder, choice_str_list)
        if result:
            debug_log("Patch application completed successfully.")
        else:
            debug_log("Patch application failed.")
        return result
    except Exception as e:
        debug_log("Error during patch application: " + str(e))
        return False