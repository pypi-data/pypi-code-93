# -*- coding: utf-8 -*-
# :copyright: (c) 2020 by Jesse Johnson.
# :license: Apache 2.0, see LICENSE for more details.
'''Inspection based parser based on argparse.'''

import logging
from typing import List

from .argument import Argument  # noqa
from .formatter import ArgufyHelpFormatter  # noqa
from .parser import Parser  # noqa

__author__ = 'Jesse P. Johnson'
__author_email__ = 'jpj6652@gmail.com'
__title__ = 'argufy'
__description__ = 'Inspection based parser built on argparse.'
__version__ = '0.1.2-a0'
__license__ = 'Apache-2.0'
__copyright__ = 'Copyright 2020 Jesse Johnson.'
__all__: List[str] = ['Parser', 'ArgufyHelpFormatter']

logging.getLogger(__name__).addHandler(logging.NullHandler())
