# -*- coding: utf-8 -*-
import numpy as np

from .partonic_vars import PartonicVars
from .raw import cg0 as raw_cg0


def cg0t(proj, cc, xi, eta):
    """LO threshold limit"""
    v = PartonicVars(xi, eta)
    if proj == "FL":
        if cc == "VV":
            return (
                4.0 * np.pi * v.beta ** 3 * v.rho_q ** 2 / (3.0 * (1.0 - v.rho_q) ** 3)
            )
        else:  # FL_AA
            return np.pi * v.beta * v.rho_q ** 2 / (1.0 - v.rho_q)
    if proj == "F2" and cc == "AA":  # F2_AA
        return (
            np.pi * v.beta * (1.0 - 2.0 * v.rho_q) * v.rho_q / (2.0 * (v.rho_q - 1.0))
        )
    return np.pi / 2.0 * v.rho_q / (v.rho_q - 1.0) * v.beta


def cg0(proj, cc, xi, eta):
    """LO"""
    if proj in ["xF3", "g4", "gL"]:
        return 0.0
    return raw_cg0.__getattribute__(f"cg0_{proj}_{cc}")(  # pylint: disable=no-member
        xi, eta
    )
