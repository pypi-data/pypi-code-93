# This file is placed in the Public Domain

__version__ = 55

import os
import sys

def ver(event):
    event.reply("%s %s" % (sys.argv[0].split(os.sep)[-1].upper(), __version__))
