# -*- coding: utf-8 -*-
"""Management of the importable functions of pdfo.

Authors
-------
Tom M. RAGONNEAU (tom.ragonneau@connect.polyu.hk)
and Zaikun ZHANG (zaikun.zhang@polyu.edu.hk)
Department of Applied Mathematics,
The Hong Kong Polytechnic University.

Dedicated to late Professor M. J. D. Powell FRS (1936--2015).
"""
from __future__ import division, print_function, absolute_import



""""""  # start delvewheel patch
def _delvewheel_init_patch_0_0_14():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pdfo.libs'))
    if sys.version_info[:2] >= (3, 8):
        if os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')):
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE']='1'
        os.add_dll_directory(libs_dir)
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-pdfo-1.1')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_14()
del _delvewheel_init_patch_0_0_14
# end delvewheel patch


from datetime import datetime

from ._dependencies import OptimizeResult, Bounds, LinearConstraint, NonlinearConstraint

from ._bobyqa import bobyqa
from ._cobyla import cobyla
from ._lincoa import lincoa
from ._newuoa import newuoa
from ._uobyqa import uobyqa
from ._pdfo import pdfo
from . import tests
from .tests import test_pdfo as testpdfo

# Definition of the metadata of PDFO for Python. It is accessible via:
# >>> import pdfo
# >>> print(pdfo.__author__)
# >>> ...
__all__ = ['OptimizeResult', 'Bounds', 'LinearConstraint', 'NonlinearConstraint', 'bobyqa', 'cobyla', 'lincoa',
           'newuoa', 'uobyqa', 'pdfo', 'tests', 'testpdfo']
__author__ = 'Tom M. Ragonneau and Zaikun Zhang'
__copyright__ = 'Copyright 2020--{}, Tom M. Ragonneau and Zaikun Zhang'.format(datetime.now().year)
__credits__ = ['Tom M. Ragonneau', 'Zaikun Zhang', 'Antoine Dechaume']
__license__ = 'LGPLv3+'
__version__ = '1.1'
__date__ = 'August, 2021'
__maintainer__ = 'Tom M. Ragonneau and Zaikun Zhang'
__email__ = 'tom.ragonneau@connect.polyu.hk and zaikun.zhang@polyu.edu.hk'
__status__ = 'Production'
