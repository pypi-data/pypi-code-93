"""
Formalisms published in Saxton and Rawls (2006)
"""
# {# pkglts, src
# FYEO
# #}
# {# pkglts, version, after src
from . import version

__version__ = version.__version__
# #}
# {# pkglts, glabdata, after version
from .info import pth_clean, pth_raw
# #}
