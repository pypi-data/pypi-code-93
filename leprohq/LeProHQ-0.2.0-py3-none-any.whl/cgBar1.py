# -*- coding: utf-8 -*-
import numpy as np

from .cg0 import cg0
from .color import beta0_lf
from .raw import cgBar1 as raw_cgBar1


def cgBar1(proj, cc, xi, eta):
    """NLO gluon uniform scaling coefficient function"""
    # PV coeff function?
    if proj in ["xF3", "g4", "gL"]:
        return 0.0
    return raw_cgBar1.__getattribute__(  # pylint: disable=no-member
        f"cgBar1_{proj}_{cc}"
    )(xi, eta)


def cgBarR1(proj, cc, xi, eta, nlf):
    """NLO gluon renormalization scaling coefficient function"""
    return beta0_lf(nlf) / (16.0 * np.pi * np.pi) * cg0(proj, cc, xi, eta)


def cgBarF1(proj, cc, xi, eta, nlf):
    """NLO gluon factorization scaling coefficient function"""
    return cgBar1(proj, cc, xi, eta) - cgBarR1(proj, cc, xi, eta, nlf)
