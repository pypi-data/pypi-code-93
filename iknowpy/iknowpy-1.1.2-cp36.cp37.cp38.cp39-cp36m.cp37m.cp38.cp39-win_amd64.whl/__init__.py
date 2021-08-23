"""Natural Language Processing Engine"""


""""""  # start delvewheel patch
def _delvewheel_init_patch_0_0_14():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'iknowpy.libs'))
    if sys.version_info[:2] >= (3, 8):
        if os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')):
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE']='1'
        os.add_dll_directory(libs_dir)
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-iknowpy-1.1.2')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_14()
del _delvewheel_init_patch_0_0_14
# end delvewheel patch



# provide useful error message when accidentally imported from source directory
import os
import inspect
file_directory = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda: 0)))
if os.path.isfile(os.path.join(file_directory, 'SOURCE')):
    raise ImportError(
        f'You have imported the source package {file_directory} instead of the '
        'installed package, which is not allowed. This occurred because the '
        '`iknowpy\' package source is in the directory where the import '
        'occurred and took precedence over the installed package. If you tried '
        'importing `iknowpy\' from the Python interactive console, change your '
        'working directory and try again. If you tried importing `iknowpy\' '
        'within a Python script, move the script to a different directory.'
    )
del os, inspect, file_directory

# export public variables and classes
from .version import __version__
from .labels import Labels
from .engine import iKnowEngine, UserDictionary