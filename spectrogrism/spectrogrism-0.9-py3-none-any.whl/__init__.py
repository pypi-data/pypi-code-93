# Time-stamp: <2021-05-10 19:10 ycopin@lyonovae03>

"""
spectrogrism
============

Available submodules
--------------------

* :mod:`spectrogrism.spectrogrism` - core functionalities
* :mod:`spectrogrism.distortion` - dirtortions
* :mod:`spectrogrism.snifs` - SNIFS specificities
* :mod:`spectrogrism.nisp` - NISP specificities
"""

__version__ = '0.9'

# What does "from spectrogrism import *" does?
__all__ = ['spectrogrism', 'distortion', 'snifs', 'nisp']

# Set to True if you want to import all previous modules directly
__importAll = True

if __importAll:
    for pkg in __all__:
        __import__(__name__ + '.' + pkg, fromlist=[None])

#
