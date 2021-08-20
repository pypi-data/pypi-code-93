# -*- coding: utf-8 -*-
import numba as nb

NC = 3.0
CA = NC
CF = (NC ** 2 - 1.0) / (2.0 * NC)

Kqph = 1.0 / NC
Kgph = 1.0 / (NC ** 2 - 1.0)


@nb.njit("f8(u1)", cache=True)
def beta0_lf(nlf):
    return (11.0 * CA - 2.0 * nlf) / 3.0
