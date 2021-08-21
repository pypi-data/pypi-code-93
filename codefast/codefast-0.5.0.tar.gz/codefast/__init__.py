import builtins
import sys

import codefast.utils as utils
import codefast.reader
from codefast.logger import Logger
from codefast.ds import nstr, pair_sample, fplist
from codefast.utils import uuid, shell, cipher, decipher, retry
from codefast.utils import FileIO as io
from codefast.utils import json_io as js
from codefast.utils import FormatPrint as fp
from codefast.math import math

# Export methods and variables
file = utils.FileIO
csv = utils.CSVIO
net = utils.Network
os = utils._os()

logger = Logger()
info = logger.info
error = logger.error
warning = logger.warning

say = io.say

# Deprecated
builtins.io = utils.FileIO
builtins.read = utils.FileIO()
builtins.jsn = utils.JsonIO()
json = utils.JsonIO()
text = utils.FileIO
sys.modules[__name__] = utils.wrap_mod(sys.modules[__name__],
                                       deprecated=['text', 'json', 'file', 'read', 'say', 'jsn'])
