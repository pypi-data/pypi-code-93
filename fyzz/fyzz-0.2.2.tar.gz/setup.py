#!/usr/bin/env python
# pylint: disable-msg=W0404,W0622,W0704,W0613,W0403,W0622
# Copyright (c) 2003-2013 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
""" Generic Setup script, takes package info from __pkginfo__.py file """

import os.path as osp

from io import open
from setuptools import setup, find_packages


here = osp.abspath(osp.dirname(__file__))

pkginfo = {}
with open(osp.join(here, "__pkginfo__.py")) as f:
    exec(f.read(), pkginfo)

# Get the long description from the relevant file
# with open(osp.join(here, "README.rst"), encoding="utf-8") as f:
#     long_description = f.read()

kwargs = {}
if "subpackage_of" in pkginfo:
    kwargs["namespace_packages"] = ([pkginfo["subpackage_of"]],)


setup(
    name=pkginfo.get("distname", pkginfo["modname"]),
    version=pkginfo["version"],
    description=pkginfo["description"],
    long_description=pkginfo["long_description"],
    url=pkginfo["web"],
    author=pkginfo["author"],
    author_email=pkginfo["author_email"],
    license=pkginfo["license"],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=pkginfo.get("classifiers", []),
    packages=find_packages(exclude=["contrib", "docs", "test*"]),
    python_requires=">=3.4",
    install_requires=pkginfo.get("install_requires"),
    tests_require=pkginfo.get("tests_require"),
    scripts=pkginfo.get("scripts", []),
    ext_modules=pkginfo.get("ext_modules"),
    **kwargs
)
