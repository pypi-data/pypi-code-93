"""Fyzz packaging information.

:organization: Logilab
:copyright: 2009-2013 LOGILAB S.A. (Paris, FRANCE).
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

# pylint: disable-msg=W0622

# package name
modname = "fyzz"
distname = "fyzz"

# release version
numversion = (0, 2, 2)
version = ".".join(str(num) for num in numversion)

# license and copyright
license = "LGPL v2"
copyright = """Copyright (c) 2003-2013 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr"""

# short and long description
description = "SPARQL parser"
long_description = "SPARQL parser written in Python using yapps"

# author name and email
author = "Logilab"
author_email = "contact@logilab.fr"

# home page
web = "http://www.logilab.org/project/%s" % modname

# mailing list
mailinglist = "mailto://python-projects@lists.logilab.org"

# download place
ftp = "ftp://ftp.logilab.org/pub/%s" % modname

# is there some directories to include with the source installation
include_dirs = []

# executable

scripts = []

install_requires = [
    "logilab-common >= 1.6.0",
    "yapps2 >= 2.2.0",  # XXX to ensure we don't use the broken pypi version
    "setuptools",
]
