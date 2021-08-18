import platform
if platform.uname().system not in {"Darwin","Windows"}:
    import libpython # Import shared libraries before doing anything, only on linux
    libpython.init_libpython()
from swimbundle_utils.rest import *
from swimbundle_utils.flattener import *