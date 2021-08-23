

""""""  # start delvewheel patch
def _delvewheel_init_patch_0_0_14():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pygeos.libs'))
    if sys.version_info[:2] >= (3, 8):
        if os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')):
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE']='1'
        os.add_dll_directory(libs_dir)
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-pygeos-0.10.2')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_14()
del _delvewheel_init_patch_0_0_14
# end delvewheel patch

from .lib import GEOSException  # NOQA
from .lib import Geometry  # NOQA
from .lib import geos_version, geos_version_string  # NOQA
from .lib import geos_capi_version, geos_capi_version_string  # NOQA
from .decorators import UnsupportedGEOSOperation  # NOQA
from .geometry import *  # NOQA
from .creation import *  # NOQA
from .constructive import *  # NOQA
from .predicates import *  # NOQA
from .measurement import *  # NOQA
from .set_operations import *  # NOQA
from .linear import *  # NOQA
from .coordinates import *  # NOQA
from .strtree import *  # NOQA
from .io import *  # NOQA

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
