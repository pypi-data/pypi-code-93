# -*- coding: utf-8 -*-
import numpy as np

from .partonic_vars import PartonicVars
from .cg0 import cg0t
from .color import Kgph, Kqph
from .utils import ln2, raw_c


def aq(proj, cc):
    """Quark NLO resummation coefficients"""
    a11 = 1.0
    a10 = -13.0 / 12.0 + 3.0 / 2.0 * ln2
    if proj == "FL" and cc == "VV":
        a11 -= 2.0 / 5.0
        a10 = -77.0 / 100.0 + 9.0 / 10.0 * ln2
    elif proj == "x2g1" and cc == "VV":
        a10 -= 1.0 / 4.0
    return a11, a10


def cq1t(proj, cc, xi, eta):
    """Threshold limit of cq1"""
    v = PartonicVars(xi, eta)
    a11, a10 = aq(proj, cc)
    return (
        cg0t(proj, cc, xi, eta)
        * v.beta ** 2
        / np.pi ** 2
        * (v.rho_q / (v.rho_q - 1.0))
        * (Kqph / 6.0 / Kgph)
        * (a11 * np.log(v.beta) + a10)
    )


def cq1(proj, cc, xi, eta, path=None):
    """NLO Bethe-Heitler Quark coefficient function"""
    return raw_c(proj, cc, xi, eta, path, "cq1", cq1t, np.log(1e0))
