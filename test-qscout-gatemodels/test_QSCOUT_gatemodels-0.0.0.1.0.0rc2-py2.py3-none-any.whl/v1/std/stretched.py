# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
from numpy import abs, diag, pi, kron

import pygsti

from . import NATIVE_GATES
from jaqalpaq.core.stretch import stretched_gates

NATIVE_GATES = NATIVE_GATES.copy()
del NATIVE_GATES["prepare_all"]
del NATIVE_GATES["measure_all"]
NATIVE_GATES = stretched_gates(NATIVE_GATES, suffix="_stretched")
