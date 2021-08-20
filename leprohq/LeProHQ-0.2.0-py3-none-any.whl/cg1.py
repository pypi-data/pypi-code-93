# -*- coding: utf-8 -*-
import numpy as np

from .cg0 import cg0t
from .color import CA, CF
from .partonic_vars import build_eta
from .raw import cg1_a10 as raw_cg1_a10
from .utils import ln2, raw_c


def ag(proj, cc, xi):
    """Gluon NLO resummation coefficients"""
    a12 = 1.0
    a11 = -5.0 / 2.0 + 3.0 * ln2
    if proj == "FL" and cc == "VV":
        a11 -= 2.0 / 3.0
    a10_OK = raw_cg1_a10.__getattribute__(  # pylint: disable=no-member
        f"cg1_a10_{proj}_{cc}_OK"
    )(xi)
    a10_QED = raw_cg1_a10.__getattribute__(  # pylint: disable=no-member
        f"cg1_a10_{proj}_{cc}_QED"
    )(xi)
    return a12, a11, a10_OK, a10_QED


def cg1t(proj, cc, xi, eta):
    """threshold limit of cg1"""
    rho, beta, chi = build_eta(eta)
    coulomb = np.pi ** 2 / (16.0 * beta) * (2.0 * CF - CA)
    a12, a11, a10_OK, a10_QED = ag(proj, cc, xi)
    res = (
        CA * (a12 * np.log(beta) ** 2 + a11 * np.log(beta) + a10_OK)
        + 2.0 * CF * a10_QED
    )
    return cg0t(proj, cc, xi, eta) / np.pi ** 2 * (coulomb + res)


def cg1(proj, cc, xi, eta, path=None):
    """NLO Gluon coefficient function"""
    return raw_c(proj, cc, xi, eta, path, "cg1", cg1t, np.log(1e-1))
