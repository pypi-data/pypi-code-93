# -*- coding: utf-8 -*-
'''Common libraries for proman.'''

import logging
from typing import List

logging.getLogger(__name__).addHandler(logging.NullHandler())

# package metadata
__author__ = 'Jesse P. Johnson'
__title__ = 'proman_common'
__version__ = '0.1.1-a1'
__license__ = 'MPL-2.0'
__all__: List[str] = ['GlobalDirs', 'AppDirs', 'SystemDirs', 'UserDirs']
