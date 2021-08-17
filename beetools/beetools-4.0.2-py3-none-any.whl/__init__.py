
'''Tools for Bright Edge eServices developments & projects

These tools was designed for the use in the Bright Edge eServices echo system.
It defines methods and functions for general use purposes and standardization
in the Bright Edge eServices echo system.

The modules define defaults for log levels, display on console, operating
system names and date formats.

The defaults are used in this module and across the Bright Edge eServices
echo system.
'''
from .archiver import *
from .msg import *
from .script import *
from .strext import *
from .tools import *
from .venv import *

_VERSION = '0.0.4'
