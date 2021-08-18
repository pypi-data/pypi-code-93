# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

from fibomat.sample import Sample
from fibomat.site import Site
from fibomat.pattern import Pattern
from fibomat.mill import Mill
from fibomat.linalg import Vector, DimVector
from fibomat.units import U_, Q_

import fibomat.default_backends

__version__ = '0.3.7'

# try:
#     # Change here if project is renamed and does not equal the package name
#     dist_name = __name__
#     __version__ = get_distribution(dist_name).version
#     """package version"""
# except DistributionNotFound:
#     __version__ = 'unknown'
# finally:
#     del get_distribution, DistributionNotFound

__all__ = ['__version__', 'Sample', 'Site', 'Pattern', 'Mill', 'Vector', 'U_', 'Q_']
