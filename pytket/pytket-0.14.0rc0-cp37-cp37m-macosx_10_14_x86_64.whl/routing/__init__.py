# Copyright 2019-2021 Cambridge Quantum Computing
#
# You may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence in the LICENCE file accompanying
# these documents or at:
#
#     https://cqcl.github.io/pytket/build/html/licence.html

"""
The routing module provides access to the tket :py:class:`Architecture` structure and
methods for modifying circuits to satisfy the architectural constraints. It also
provides acess to the :py:class:`Placement` constructors for relabelling Circuit qubits
and has some methods for routing circuits. This module is provided in binary form during
the PyPI installation.
"""

from pytket._tket.routing import *  # type: ignore
