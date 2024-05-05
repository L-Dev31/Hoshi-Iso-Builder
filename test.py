import os
import subprocess

region_name = "USA"

dol_file = os.path.join(os.path.dirname(__file__), "temp", "sys", "main.dol")
subprocess.run(["python", "Elements/CustomCodePatching/dolpatcher.py", region_name, dol_file]) 