#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel detector simulation framework."""

# flake8: noqa
try:
    # Try to import library 'attr'
    import attr

    del attr
    WITH_ATTR = True

except ImportError:
    WITH_ATTR = False

from ._version import get_versions
from .show_versions import show_versions

__all__ = ["get_versions", "show_versions"]
__version__ = get_versions()["version"]
del get_versions


if WITH_ATTR:
    # Library 'attr' is installed therefore 'set_options' can be used.
    from .options import SetOptions as set_options

    __all__ += ["set_options"]
