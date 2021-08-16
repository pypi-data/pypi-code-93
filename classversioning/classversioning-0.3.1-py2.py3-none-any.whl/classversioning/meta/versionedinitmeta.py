#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" versionedinitmeta.py
Description:
"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2021, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "0.3.1"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Prototype"

# Default Libraries #

# Downloaded Libraries #
from baseobjects import InitMeta

# Local Libraries #
from .versionedmeta import VersionedMeta


# Definitions #
# Meta Classes #
class VersionedInitMeta(InitMeta, VersionedMeta):
    """A mixed class of the InitMeta and VersionMeta."""
    ...
