from ale_py.roms.utils import find_atari_py_roms, find_external_roms, find_internal_roms

# Precedence is as follows:
#  1. Internal ROMs
#  2. External ROMs
#  3. ROMs from atari-py.roms
#  4. ROMs from atari-py-roms.roms
all = {}
all.update(find_atari_py_roms("atari_py_roms"))
all.update(find_atari_py_roms("atari_py"))
all.update(find_external_roms(__package__))
all.update(find_internal_roms(__package__))

globals().update(all)
__all__ = list(all.keys())
