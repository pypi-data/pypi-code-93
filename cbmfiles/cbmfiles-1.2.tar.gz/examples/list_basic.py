import sys

try:
    import cbmcodecs
except ModuleNotFoundError:
    pass

from cbm_files import BASICFile


with open(sys.argv[1], 'rb') as fileh:
    prog = BASICFile(fileh)
for l in prog.to_text():
    print(l)
