"""Chemin de quelques répertoires propres à Pyromaths-QT."""

import os
import sys

import pkg_resources

DATADIR = pkg_resources.resource_filename("pyromaths.qt", "data")
IMGDIR = os.path.join(DATADIR, "images")
LOCALEDIR = os.path.join(DATADIR, "locale")
