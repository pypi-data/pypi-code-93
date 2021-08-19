# -*- coding: utf-8 -*-
from .raw import cqBarF1 as raw_cqBarF1


def cqBarF1(proj, cc, xi, eta):
    """NLO Bethe-Heitler quark scaling coefficient functions"""
    # PV coeff function?
    if proj in ["xF3", "g4", "gL"]:
        return 0.0
    return raw_cqBarF1.__getattribute__(  # pylint: disable=no-member
        f"cqBarF1_{proj}_{cc}"
    )(xi, eta)
