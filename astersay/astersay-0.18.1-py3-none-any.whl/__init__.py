#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import gettext
import os
from astersay import version

VERSION = (0, 18, 1, 'final', 0)


def get_path(*sub):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if sub:
        return os.path.join(base_dir, *sub)
    return base_dir


def get_version():
    return version.get_version(VERSION, get_path())


__version__ = get_version()

gettext.bindtextdomain(__name__, get_path('locale'))
gettext.textdomain(__name__)
