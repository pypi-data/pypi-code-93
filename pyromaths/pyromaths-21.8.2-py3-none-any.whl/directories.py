"""Chemin de quelques répertoires propres à Pyromaths."""

import os
import sys

import pkg_resources

DATADIR = pkg_resources.resource_filename("pyromaths", "data")
EXODIR = os.path.join(DATADIR, "exercices")
LOCALEDIR = os.path.join(DATADIR, "locale")
HOME = os.path.expanduser("~")

if os.name == 'nt': # Windows
    CONFIGDIR = os.path.join(os.environ['APPDATA'], "pyromaths")
elif sys.platform == "darwin":  # Mac OS X
    CONFIGDIR = os.path.join(HOME, "Library", "Application Support", "Pyromaths")
else: # Linux (et autres ?)
    CONFIGDIR = os.path.join(HOME, ".config", "pyromaths")

