# -*- coding: utf-8 -*-
import numba as nb
import numpy as np

from .partonic_vars import build_eta, build_xi
from .raw import cg0 as raw_cg0


@nb.njit("f8(string,string, f8,f8)", cache=True)
def cg0t(proj, cc, xi, eta):
    """LO threshold limit"""
    rho, beta, chi = build_eta(eta)
    rho_q, _beta_q, _chi_q = build_xi(xi)
    if proj == "FL":
        if cc == "VV":
            return 4.0 * np.pi * beta ** 3 * rho_q ** 2 / (3.0 * (1.0 - rho_q) ** 3)
        else:  # FL_AA
            return np.pi * beta * rho_q ** 2 / (1.0 - rho_q)
    if proj == "F2" and cc == "AA":  # F2_AA
        return np.pi * beta * (1.0 - 2.0 * rho_q) * rho_q / (2.0 * (rho_q - 1.0))
    return np.pi / 2.0 * rho_q / (rho_q - 1.0) * beta


def cg0(proj, cc, xi, eta):
    """LO"""
    if proj in ["xF3", "g4", "gL"]:
        return 0.0
    return raw_cg0.__getattribute__(f"cg0_{proj}_{cc}")(  # pylint: disable=no-member
        xi, eta
    )
