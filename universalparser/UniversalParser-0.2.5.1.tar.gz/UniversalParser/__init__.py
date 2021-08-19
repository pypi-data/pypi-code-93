from ._parse import *
from ._ntype import *
from ._exception import *
from ._rely import *
from ._collections import *
from .manager import *
from .struct import *

# shotcut
from .micro import Excel as ExcelParser
from .micro import Word as WordParser
from .micro import PowerPoint as PowerPointParser

from .xml.odict import parse_odict
from .xml.unparser import unparse_dict

name = 'UniversalParser'
__version__ = '0.2.5.1'
__author__ = 'jiyang'
__license__ = 'MIT'
