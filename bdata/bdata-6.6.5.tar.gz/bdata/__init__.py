from .bdata import bdata
from .life import life
from .bjoined import bjoined
from .bmerged import bmerged
from .exceptions import InputError, MinimizationError

import os

__all__ = ['bdata', 'bjoined', 'bmerged', 'life']
__version__ = '6.6.5'
__author__ = 'Derek Fujimoto'
_mud_data = os.path.join(os.environ['HOME'], '.bdata')
