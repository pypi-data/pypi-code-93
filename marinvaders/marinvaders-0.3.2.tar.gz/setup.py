#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = "marinvaders"
DESCRIPTION = (
    "The marinvaders (Marine Invaders) is tool to process data on marine "
    "invasive species from existing databases"
)
URL = "https://gitlab.com/dlab-indecol/marinvaders"
EMAIL = "radek.lonka@ntnu.no"
AUTHOR = "Radek Lonka"
REQUIRES_PYTHON = ">=3.7.0"
VERSION = "0.3.2"

# What packages are required for this module to be executed?
REQUIRED = [
    "requests",
    "beautifulsoup4",
    "cached-property",
    "geopandas",
    "matplotlib",
    "numpy",
    "pandas",
    "requests",
    "shapely",
    "openpyxl",
    "xlrd",
    "tables",
    "descartes",
]

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    py_modules=[
        "marinvaders.main",
        "marinvaders.api_calls",
        "marinvaders.alien_observation",
        "marinvaders.readers",
    ],
    install_requires=REQUIRED,
    license="GNU GPLv3",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
)
