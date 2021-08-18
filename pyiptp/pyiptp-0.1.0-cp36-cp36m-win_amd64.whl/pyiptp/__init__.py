# -*- coding: utf-8 -*-
"""
pyIPTP - Iso-Parametric Trajectory Planning toolkit
===================================================

pyiptp is a Python 3 package that provides several tools to design trajectories
in the joint space, combining the OOP approach with the feature of imposing
arbitrary constraints on n-th derivatives or anti-derivatives using iterative
loops. The adopted approach uses univariate B-splines to parameterize
trajectory pieces, which are then concatenated to build a piecewise trajectory.
Working on a parametric data structure, the tool offers many functions of shape
modeling and symbolic calculation by actually describing a small CAD for
trajectories. These functions, combined appropriately, define macro-instructions
that can be reused in several application cases and with which the trajectory
is defined with I/O block logic, thus dividing the entire trajectory planning
into simpler problems. Additionally, it has the broader goal of becoming the
new standard in electric axis control in **the fields of robotic and industrial
automation.

Some good reasons to use this library are:

* trajectory planning in joints space for robotic applications
* synthesis and study of automatic machines, such as cam mechanisms or
  articulated systems
* dynamic simulation of the mechatronic systems
* teaching

"""

__version__ = "0.1.0"

# Let users know if they're missing any of our hard dependencies
hard_dependencies = ("numpy", "scipy", "lxml")
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append("{0}: {1}".format(dependency, str(e)))

if missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" +
        "\n".join(missing_dependencies)
    )
del hard_dependencies, dependency, missing_dependencies

from . import cython_ubsplclib
from .cython_ubsplclib import *
from . import defdatastruct
from .defdatastruct import *
from . import factoryfunc
from .factoryfunc import *
from . import basicfunc
from .basicfunc import *

__all__=[]
__all__.extend(cython_ubsplclib.__all__)
__all__.extend(defdatastruct.__all__)
__all__.extend(factoryfunc.__all__)
__all__.extend(basicfunc.__all__)