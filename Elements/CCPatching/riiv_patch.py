import math, os, shutil, pathlib
import xml.etree.ElementTree as ET
from textwrap import wrap

# custom import (C-like include)
# geckoloader_path and wit_path will be defined there
exec(open("Elements/CCPatching/bin_tool_setup.py").read())

# function to check if the game image is valid
def check_game_image(game_image_path):
  result = exec_subprocess([wit_path, "verify", "--test", "--quiet", game_image_path])
  if (result.returncode != 0):
    print("Invalid ISO/WBFS.")
    exit(1)
    
# function to check if the game image is valid for the riivolution XML
def check_game_xml_id(game_image_path, riiv_xml_id):
  game_id = exec_subprocess([wit_path, "ID6", game_image_path])
  game_id = game_id.stdout[:-4]
  if (game_id != riiv_xml_id):
    print("Riivolution XML is incompatible with game image.")
    exit(1)
    
# function to return the patches that can be applied
def get_xml_patches(riiv_xml_path):
  xml = ET.parse(riiv_xml_path)
  root = xml.getroot()
  patches_id = root.findall("patch")
  # list sections, its options the patches that involve
  sections = root.find("options").findall("section")
  sec_info = []
  
  # fill sec_info with strings
  for sec in sections:
    sec_info.append([])
    sec_info[-1].append(sec.attrib["name"])
    sec_info[-1].append([])
    for opt in sec:
      sec_info[-1][-1].append(opt.attrib["name"])
      sec_info[-1][-1].append([])
      for choice in opt:
        sec_info[-1][-1][-1].append(choice.attrib["name"])
        sec_info[-1][-1][-1].append([])
        for patch in choice:
          sec_info[-1][-1][-1][-1].append(patch.attrib["id"])
    
  return sec_info

# Riivolution XML processing
def exec_riiv_patch(game_image_path, riiv_xml_path, mod_files_path, patches_id):

  # check the game file first
  check_game_image(game_image_path)
  
  # remove possible residual files
  if (os.path.exists("temp/")):
    shutil.rmtree("temp/")
  if (os.path.exists("temp.txt")):
    os.remove("temp.txt")
  if (os.path.exists("temp.xml")):
    os.remove("temp.xml")
  if (os.path.exists("result.wbfs")):
    os.remove("result.wbfs")
  tmp_path = pathlib.Path("")
  for tmp in tmp_path.glob("*.tmp"):
    os.remove(tmp)
  
  # read XML
  xml = ET.parse(riiv_xml_path)
  root = xml.getroot()

  # get id, options and specific patch elements
  id_elem = None
  options_elem = None
  patch_elems = []
  for child in root:
    if (child.tag == "id"):
      id_elem = child
    elif (child.tag == "options"):
      options_elem = child
    elif (child.tag == "patch"):
      if (child.attrib["id"] in patches_id):
        patch_elems.append(child)
    
  # check game id with xml id
  regions = []
  if (len(id_elem) != 0):
    check_game_xml_id(game_image_path, id_elem.attrib["game"])  
    # get the number of regions (if no region tags that means it is for all regions)
    for child in id_elem:
      regions.append(child.attrib["type"])
  else:
    regions = ["E", "P", "J", "K", "W"]
  
  # check if the game region is supported by the riivolution XML
  game_reg = exec_subprocess([wit_path, "ID6", game_image_path])
  game_reg = game_reg.stdout[3:-3]
  if ((game_reg in regions) == False):
    print("Game region not supported by XML.")
    exit(1)
  
  # ignore options a go right to the patches
  # ~ for patch in patch_elems:
    # ~ print(patch.attrib["id"])
    
  # check if the replacements are available (i.e. if the mod folder provided is actually valid for the XML)
  # also, one thing, I assume that all files to replace are in the mod_files_path
  
  # list folder, file and memory patches
  folder_elems = []
  file_elems = []
  memory_elems = []
  
  # get folders, files and memory replacements
  for patch in patch_elems:
    folder_elems = folder_elems + patch.findall("folder")
    file_elems = file_elems + patch.findall("file")
    memory_elems = memory_elems + patch.findall("memory")
    
  # ~ for folder in folder_elems:
    # ~ print(folder.attrib["external"])
  # ~ for file in file_elems:
    # ~ print(file.attrib["external"])
  # ~ for mem in memory_elems:
    # ~ print(mem.attrib["offset"])
  
  # check files (check memory if there is a valuefile attribute)
  # folders not present will just be ignored  
  mod_files_valid = True
  for file in file_elems:
    if (os.path.exists(mod_files_path + "/" + file.attrib["external"]) == False):
      mod_files_valid = False
  for mem in memory_elems:
    if ("valuefile" in mem.attrib):
      if (os.path.exists(mod_files_path + "/" + mem.attrib["valuefile"]) == False):
        mod_files_valid = False
  
  # extract the game image contents (real)
  temp_folder_path = "temp/files"
  exec_subprocess([wit_path, "extract", game_image_path, "temp/"])
  
  # check if inside there is a DATA folder (>:[)
  if (os.path.exists("temp/DATA")):
    temp_folder_path = "temp/DATA/files"
  
  # check if the file replacements are possible
  is_replacement_valid = True
  for file in file_elems:
    if (os.path.exists(temp_folder_path + file.attrib["disc"]) == False):
      mod_files_valid = False
  
  # do the folder/file replacements first  
  for folder in folder_elems:
    if (os.path.exists(mod_files_path + "/" + folder.attrib["external"])):
      shutil.copytree(mod_files_path + "/" + folder.attrib["external"], temp_folder_path + folder.attrib["disc"], dirs_exist_ok = True)
    else:
      os.makedirs(temp_folder_path + folder.attrib["disc"], exist_ok = True)
  for file in file_elems:
    shutil.copy(mod_files_path + "/" + file.attrib["external"], temp_folder_path + file.attrib["disc"])
  
  # start the memory patches (divide them, a pack for WIT a pack for GeckoLoader)
  
  # prepare GeckoLoader patches (patches <= 0x8000FFFF)
  geckoloader_patches = []
  for mem in memory_elems:
    if (int(mem.attrib["offset"][2:], 16) <= 0x8000FFFF):
      geckoloader_patches.append([])
      geckoloader_patches[-1].append(mem.attrib["offset"][2:])
      if ("value" in mem.attrib):
        geckoloader_patches[-1].append(mem.attrib["value"])
      elif("valuefile" in mem.attrib):
        geckoloader_patches[-1].append("")
        tmpf = mem.attrib["valuefile"].replace("{$__region}", game_reg)
        tmpf = open(mod_files_path + "/" + tmpf, "rb")
        tmp_byte = 0
        while (tmp_byte != b""):
          tmp_byte = tmpf.read(1)
          geckoloader_patches[-1][-1] = geckoloader_patches[-1][-1] + tmp_byte.hex().upper()
        tmpf.close()
        mem.set("valuefile", mem.attrib["valuefile"].replace("{$__region}", game_reg))
    else: # other memory patches
      if("valuefile" in mem.attrib):
        mem.set("valuefile", mem.attrib["valuefile"].replace("{$__region}", game_reg))      
  
  # eliminate the patches that aren't in patches_id from the XML
  for patch in root.findall("patch"):
    if (patch.attrib["id"] in patches_id):
      continue
    else:
      root.remove(patch)
  
  # eliminate target patches (Aurum)
  for patch in patch_elems:
    for mem in patch:
      if ("target" in mem.attrib):
        if (mem.attrib["target"] != game_reg):
          patch.remove(mem)
        else:
          mem.attrib.pop("target")
  
  # write temp.xml for wit
  xml.write("temp.xml")
  
  # write geckoloader patches into a Gecko Code List
  tmpf = open("temp.txt", "w")
  for patch in geckoloader_patches:
    offset = int(patch[0], 16)
    valuelist = wrap(patch[1], width = 8)
    # fill with zeroes the last valuelist[i] or append 
    # "00000000" so that the GCL format is correct
    while (len(valuelist[-1]) != 8):
      valuelist[-1] = valuelist[-1] + "0"
    if (len(valuelist) % 2 != 0):
      valuelist.append("00000000")
    # write offset and string length
    tmpf.write("%08X %08X\n" % (offset - 0x80000000 + 0x06000000, int(len(patch[1]) / 2)))
    # write hex string
    for i in range(len(valuelist)): 
      if (i % 2 == 0):
        tmpf.write("%s " % (valuelist[i]))
      else:
        tmpf.write("%s\n" % (valuelist[i])) 
  tmpf.close()
  
  # apply geckoloader and wit patches to main.dol
  if (len(geckoloader_patches) != 0):
    if (temp_folder_path.find("DATA")):
      print(exec_subprocess(geckoloader_path + ["temp/DATA/sys/main.dol", "temp.txt", "--dest", "temp/DATA/sys/main_1.dol", "--txtcodes", "ALL"]).stdout)
      print(exec_subprocess([wit_path, "dolpatch", "temp/DATA/sys/main_1.dol", "XML=temp.xml", "--source", mod_files_path, "--dest", "temp/DATA/sys/main_2.dol"]).stdout)
      shutil.move("temp/DATA/sys/main_2.dol", "temp/DATA/sys/main.dol")
      os.remove("temp/DATA/sys/main_1.dol")
    else:
      print(exec_subprocess(geckoloader_path + ["temp/sys/main.dol", "temp.txt", "--dest", "temp/sys/main_1.dol", "--txtcodes", "ALL"]).stdout)
      print(exec_subprocess([wit_path, "dolpatch", "temp/sys/main_1.dol", "XML=temp.xml", "--source", mod_files_path, "--dest", "temp/sys/main_2.dol"]).stdout)
      shutil.move("temp/sys/main_2.dol", "temp/sys/main.dol")
      os.remove("temp/sys/main_1.dol")
  
  # done! (hopefully)
