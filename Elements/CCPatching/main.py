import sys, riiv_patch

# NOTE: this tool works with python 3.8 and assumes
# python 3.8 is installed so use python 3.8 always

# modules needed (because of GeckoLoader): chardet bs4
# Install Windows: py -3.8 -m pip install chardet bs4
# Install Linux (Ubuntu): python3.8 -m pip install chardet bs4

# tool usage command (linux):
# python3.8 main.py [ISO/WBFS file] [Riivolution XML] [Mod files folder]

# this first function will retrieve the information about the XML patches
# a Riivolution XML file consists of Sections, Options, Choices and Patches
# a Section contains Options, which contains Choices, which contains patches
# this function returns a list (a bit clunky) of that relation.
# You can use it to get the user to choose the patches to apply to the game (patches id)

sections = riiv_patch.get_xml_patches(sys.argv[2])
print(sections)

# Argument 1 --> ISO/WBFS File path (string)
# Argument 2 --> Riivolution XML file path (string)
# Argument 3 --> Mod files path, basically the folder (string)
# Argument 4 --> List of strings of the patches ID to patch to the game (list of strings)

# example for SMG0 USA:
# Arg 1 --> "path/to/SB4E01.wbfs"
# Arg 2 --> "path/to/SMG0-USA.xml"
# Arg 3 --> "path/to/SMG0"
# Arg 4 --> ["smg0"]

# ~ riiv_patch.exec_riiv_patch(arg1, arg2, arg3, arg4)

# a command I used for SMG0 USA
# ~ riiv_patch.exec_riiv_patch(sys.argv[1], sys.argv[2], sys.argv[3], ["smg0"])

# The final result of this command is a "result.wbfs" that has the
# game patches needed (hopefully it works correctly on console)
