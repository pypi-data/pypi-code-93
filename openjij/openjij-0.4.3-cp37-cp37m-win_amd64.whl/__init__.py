

""""""  # start delvewheel patch
def _delvewheel_init_patch_0_0_14():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))
    if sys.version_info[:2] >= (3, 8):
        if os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')):
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE']='1'
        os.add_dll_directory(libs_dir)
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-openjij-0.4.3')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_14()
del _delvewheel_init_patch_0_0_14
# end delvewheel patch

try:
    import typing 
except ImportError:
    from typing_extensions import * 
import cxxjij
import openjij.model
import openjij.sampler 
import openjij.sampler.chimera_gpu
import openjij.utils

from openjij.variable_type import SPIN, BINARY, Vartype, cast_vartype
from openjij.sampler import Response
from openjij.sampler import SASampler, SQASampler, CSQASampler
from openjij.model import BinaryQuadraticModel, BinaryPolynomialModel
from openjij.utils import solver_benchmark, convert_response
