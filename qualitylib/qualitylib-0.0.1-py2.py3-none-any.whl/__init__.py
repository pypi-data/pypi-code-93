"""Top-level package for qualitylib."""

__author__ = """Pradeep Reddy Raamana"""
__email__ = 'raamana@gmail.com'

from sys import version_info

if version_info.major >= 3:
    pass
else:
    raise NotImplementedError('qualitylib requires Python 3 or higher! ')

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
