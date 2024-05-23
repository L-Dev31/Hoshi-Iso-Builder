#------------------------------------------------------------------------------
# This file is part of Hoshi - Wii ISO Builder.
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

import sys
import subprocess
from enum import Enum

# get system information

# I wanted a C-like enum
(WINDOWS, LINUX) = range(0, 2)
SYSTEM_OS = WINDOWS
if (sys.platform == "linux"):
  SYSTEM_OS = LINUX
# ~ print(SYSTEM_OS)

# function to execute binaries
def exec_subprocess(str_list):
  return subprocess.run(str_list, capture_output = True, text = True)

# setup binary tools
geckoloader_path = None
wit_path = None
if (SYSTEM_OS == WINDOWS):
  geckoloader_path = ["py", "-3.8", "Elements/CCPatching/tools/geckoloader/GeckoLoader.py"]
  wit_path = "Elements/CCPatching/tools/wit/windows/wit.exe"
elif (SYSTEM_OS == LINUX):
  geckoloader_path = ["python3.8", "Elements/CCPatching/tools/geckoloader/GeckoLoader.py"]
  wit_path = "Elements/CCPatching/tools/wit/linux/wit"

# ~ exec_subprocess(wit_path) 
# ~ exec_subprocess(geckoloader_path) 
