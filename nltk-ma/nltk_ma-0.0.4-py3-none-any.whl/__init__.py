# Natural Language Toolkit (NLTK)
#
# Copyright (C) 2001-2021 NLTK Project
# Authors: Steven Bird <stevenbird1@gmail.com>
#          Edward Loper <edloper@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
The Natural Language Toolkit (NLTK) is an open source Python library
for Natural Language Processing.  A free online book is available.
(If you use the library for academic research, please cite the book.)

Steven Bird, Ewan Klein, and Edward Loper (2009).
Natural Language Processing with Python.  O'Reilly Media Inc.
http://nltk.org/book
"""

import os

# //////////////////////////////////////////////////////
# Metadata
# //////////////////////////////////////////////////////

# Version.  For each new release, the version number should be updated
# in the file VERSION.
try:
    # If a VERSION file exists, use it!
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    with open(version_file, "r") as infile:
        __version__ = infile.read().strip()
except NameError:
    __version__ = "unknown (running code interactively?)"
except IOError as ex:
    __version__ = "unknown (%s)" % ex

if __doc__ is not None:  # fix for the ``python -OO``
    __doc__ += "\n@version: " + __version__


# Copyright notice
__copyright__ = """\
Copyright (C) 2001-2021 NLTK Project.

Distributed and Licensed under the Apache License, Version 2.0,
which is included by reference.
"""

__license__ = "Apache License, Version 2.0"
# Description of the toolkit, keywords, and the project's primary URL.
__longdescr__ = """\
The Natural Language Toolkit (NLTK) is a Python package for
natural language processing.  NLTK requires Python 2.6 or higher."""
__keywords__ = [
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
]
__url__ = "http://nltk.org/"

# Maintainer, contributors, etc.
__maintainer__ = "Steven Bird, Edward Loper, Ewan Klein"
__maintainer_email__ = "stevenbird1@gmail.com"
__author__ = __maintainer__
__author_email__ = __maintainer_email__

# "Trove" classifiers for Python Package Index.
__classifiers__ = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Scientific/Engineering :: Human Machine Interfaces",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Text Processing",
    "Topic :: Text Processing :: Filters",
    "Topic :: Text Processing :: General",
    "Topic :: Text Processing :: Indexing",
    "Topic :: Text Processing :: Linguistic",
]

from nltkma.internals import config_java

# support numpy from pypy
try:
    import numpypy
except ImportError:
    pass

# Override missing methods on environments where it cannot be used like GAE.
import subprocess

if not hasattr(subprocess, "PIPE"):

    def _fake_PIPE(*args, **kwargs):
        raise NotImplementedError("subprocess.PIPE is not supported.")

    subprocess.PIPE = _fake_PIPE
if not hasattr(subprocess, "Popen"):

    def _fake_Popen(*args, **kwargs):
        raise NotImplementedError("subprocess.Popen is not supported.")

    subprocess.Popen = _fake_Popen

###########################################################
# TOP-LEVEL MODULES
###########################################################

# Import top-level functionality into top-level namespace

from nltkma.collocations import *
from nltkma.decorators import decorator, memoize
from nltkma.featstruct import *
from nltkma.grammar import *
from nltkma.probability import *
from nltkma.text import *
from nltkma.tree import *
from nltkma.util import *
from nltkma.jsontags import *

###########################################################
# PACKAGES
###########################################################

from nltkma.chunk import *
from nltkma.classify import *
from nltkma.inference import *
from nltkma.metrics import *
from nltkma.parse import *
from nltkma.tag import *
from nltkma.tokenize import *
from nltkma.translate import *
from nltkma.sem import *
from nltkma.stem import *

# Packages which can be lazily imported
# (a) we don't import *
# (b) they're slow to import or have run-time dependencies
#     that can safely fail at run time

from nltkma import lazyimport

app = lazyimport.LazyModule("nltk.app", locals(), globals())
chat = lazyimport.LazyModule("nltk.chat", locals(), globals())
corpus = lazyimport.LazyModule("nltk.corpus", locals(), globals())
draw = lazyimport.LazyModule("nltk.draw", locals(), globals())
toolbox = lazyimport.LazyModule("nltk.toolbox", locals(), globals())

# Optional loading

try:
    import numpy
except ImportError:
    pass
else:
    from nltkma import cluster

from nltkma.downloader import download, download_shell

try:
    import tkinter
except ImportError:
    pass
else:
    try:
        from nltkma.downloader import download_gui
    except RuntimeError as e:
        import warnings

        warnings.warn(
            "Corpus downloader GUI not loaded "
            "(RuntimeError during import: %s)" % str(e)
        )

# explicitly import all top-level modules (ensuring
# they override the same names inadvertently imported
# from a subpackage)

from nltkma import  chunk, classify, collocations
from nltkma import data, featstruct, grammar, help, inference, metrics
from nltkma import parse, probability, sem, stem, wsd
from nltkma import tag, tbl, text, tokenize, translate, tree, treetransforms, util


# FIXME:  override any accidentally imported demo, see https://github.com/nltk/nltk/issues/2116
def demo():
    print("To run the demo code for a module, type nltk.module.demo()")
