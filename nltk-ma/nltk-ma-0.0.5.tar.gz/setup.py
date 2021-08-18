#!/usr/bin/env python
#
# Setup script for the Natural Language Toolkit
#
# Copyright (C) 2001-2021 NLTK Project
# Author: Steven Bird <stevenbird1@gmail.com>
#         Edward Loper <edloper@gmail.com>
#         Ewan Klein <ewan@inf.ed.ac.uk>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs

try:
    codecs.lookup("mbcs")
except LookupError:
    ascii = codecs.lookup("ascii")
    func = lambda name, enc=ascii: {True: enc}.get(name == "mbcs")
    codecs.register(func)

import os

# Use the VERSION file to get NLTK version
# version_file = os.path.join(os.path.dirname(__file__), "nltkma", "VERSION")
# with open(version_file) as fh:
#     nltkma_version = fh.read().strip()
nltkma_version = '0.0.5'

# setuptools
from setuptools import setup, find_packages

# Specify groups of optional dependencies
extras_require = {
    "machine_learning": ["gensim<4.0.0", "numpy", "python-crfsuite", "scikit-learn", "scipy"],
    "plot": ["matplotlib"],
    "tgrep": ["pyparsing"],
    "twitter": ["twython"],
    "corenlp": ["requests"],
}

# Add a group made up of all optional dependencies
extras_require["all"] = set(
    package for group in extras_require.values() for package in group
)

# Adds CLI commands
console_scripts = """
[console_scripts]
nltk=nltk.cli:cli
"""

_project_homepage = "http://nltk.org/"

setup(
    name="nltk-ma",
    version=nltkma_version,
    url=_project_homepage,
    project_urls={
        "Documentation": _project_homepage,
        "Source Code": "https://github.com/aydtmiri/nltk-ma"
    },
    long_description="""\
This implementation of NLTK (http://nltk.org/) extends the collocation and concordance line functions.""",
    license="Apache License, Version 2.0",
    keywords=[
        "NLP",
        "CL",
        "natural language processing",
        "computational linguistics",
        "parsing",
        "tagging",
        "tokenizing",
        "syntax",
        "linguistics",
        "language",
        "natural language",
        "text analytics",
    ],
    maintainer="Miriam Aydt",
    author="Steven Bird, Miriam Aydt",
    package_data={"nltk-ma": ["test/*.doctest", "VERSION"]},
    python_requires='>=3.6',
    install_requires=[
        "click",
        "joblib",
        "regex",
        "tqdm",
    ],
    extras_require=extras_require,
    packages=find_packages(),
    zip_safe=False,  # since normal files will be present too?
    entry_points=console_scripts,
)
