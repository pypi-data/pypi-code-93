# -*- coding: utf-8 -*-
from .raw import dq1 as raw_dq1


def dq1(proj, cc, xi, eta):
    """NLO Coulomb quark scaling coefficient functions"""
    return raw_dq1.__getattribute__(f"dq1_{proj}_{cc}")(  # pylint: disable=no-member
        xi, eta
    )
