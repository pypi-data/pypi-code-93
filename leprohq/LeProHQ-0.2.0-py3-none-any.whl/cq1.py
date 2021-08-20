# -*- coding: utf-8 -*-
import numba as nb
import numpy as np

from .cg0 import cg0t
from .color import Kgph, Kqph
from .partonic_vars import build_eta, build_xi
from .utils import ln2, raw_c


@nb.njit("UniTuple(f8,2)(string,string)", cache=True)
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


@nb.njit("f8(string,string, f8,f8)", cache=True)
def cq1t(proj, cc, xi, eta):
    """Threshold limit of cq1"""
    rho, beta, chi = build_eta(eta)
    rho_q, _beta_q, _chi_q = build_xi(xi)
    a11, a10 = aq(proj, cc)
    return (
        cg0t(proj, cc, xi, eta)
        * beta ** 2
        / np.pi ** 2
        * (rho_q / (rho_q - 1.0))
        * (Kqph / 6.0 / Kgph)
        * (a11 * np.log(beta) + a10)
    )


def cq1(proj, cc, xi, eta, path=None):
    """NLO Bethe-Heitler Quark coefficient function"""
    return raw_c(proj, cc, xi, eta, path, "cq1", cq1t, np.log(1e0))
