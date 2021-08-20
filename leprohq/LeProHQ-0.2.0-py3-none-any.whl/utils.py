# -*- coding: utf-8 -*-
import pathlib

import numba as nb
import numpy as np
import scipy.interpolate as ip

datadir = pathlib.Path(__file__).absolute().parent / "data"

ln2 = np.log(2)


@nb.njit("f8(f8)", cache=True)
def Li2(X):
    """
    Reimplementation of DDILOG (C332) from CERNlib :cite:`cernlib`.

    Note
    ----
    This is the dilog (:math:`Li_2(x)`) and *not* the Spence's function
    (:data:`scipy.special.spence`).

    Parameters
    ----------
    X : float
        argument of :math:`Li_2(x)`

    Returns
    -------
    float
        :math:`Li_2(x)`

    """
    # fmt: off
    Z1 = 1
    HF = Z1/2
    PI = 3.14159265358979324
    PI3 = PI**2/3
    PI6 = PI**2/6
    PI12 = PI**2/12

    C = np.array([
        +0.42996693560813697,
        +0.40975987533077105,
        -0.01858843665014592,
        +0.00145751084062268,
        -0.00014304184442340,
        +0.00001588415541880,
        -0.00000190784959387,
        +0.00000024195180854,
        -0.00000003193341274,
        +0.00000000434545063,
        -0.00000000060578480,
        +0.00000000008612098,
        -0.00000000001244332,
        +0.00000000000182256,
        -0.00000000000027007,
        +0.00000000000004042,
        -0.00000000000000610,
        +0.00000000000000093,
        -0.00000000000000014,
        +0.00000000000000002,
    ])

    if X == 1:
       H=PI6
    elif X == -1:
       H=-PI12
    else:
        T=-X
        if T <= -2:
            Y=-1/(1+T)
            S=1
            A=-PI3+HF*(np.log(-T)**2-np.log(1+1/T)**2)
        elif T < -1:
            Y=-1-T
            S=-1
            A=np.log(-T)
            A=-PI6+A*(A+np.log(1+1/T))
        elif T <= -HF:
            Y=-(1+T)/T
            S=1
            A=np.log(-T)
            A=-PI6+A*(-HF*A+np.log(1+T))
        elif T < 0:
            Y=-T/(1+T)
            S=-1
            A=HF*np.log(1+T)**2
        elif T <= 1:
            Y=T
            S=1
            A=0
        else:
            Y=1/T
            S=-1
            A=PI6+HF*np.log(T)**2

        H=Y+Y-1
        ALFA=H+H
        B1=0
        B2=0
        for I in range(19, 0-1, -1):
            B0=C[I]+ALFA*B1-B2
            B2=B1
            B1=B0

        H=-(S*(B0-H*B2)+A)

    DDILOG=H
    # fmt: on

    return DDILOG


class LeProHQError(ValueError):
    def __init__(self, *args, proj=None, cc=None, xi=None, eta=None):
        super().__init__(*args)
        self.proj = proj
        self.cc = cc
        self.xi = xi
        self.eta = eta


interpolator_1d = {}


def load_1d_interpolation(path):
    """Load 1D interpolator"""
    # already present?
    if path in interpolator_1d:
        return interpolator_1d[path]
    cnt = np.loadtxt(path)
    interpolator = ip.UnivariateSpline(cnt[0], cnt[1])
    interpolator_1d[path] = (cnt, interpolator)
    return interpolator_1d[path]


interpolator_2d = {}


def load_2d_interpolation(path):
    """Load 2D interpolator"""
    # already present?
    if path in interpolator_2d:
        return interpolator_2d[path]
    cnt = np.loadtxt(path)
    interpolator = ip.RectBivariateSpline(cnt[1:, 0], cnt[0, 1:], cnt[1:, 1:])
    interpolator_2d[path] = (cnt, interpolator)
    return interpolator_2d[path]


def raw_ctp(proj, cc, xi, eta, grid_tp, a_int, ct):
    """Abstract improved threshold limit"""
    t = ct(proj, cc, xi, eta)
    lnxi = np.log(xi)
    if lnxi > grid_tp[0, -1]:
        raise LeProHQError(
            f"xi interpolation for threshold coeff out of grid: {xi} > {np.exp(grid_tp[0,-1])}",
            proj=proj,
            cc=cc,
            xi=xi,
            eta=eta,
        )
    a = a_int(lnxi)
    return t * (1.0 + a * eta)


def raw_cb(proj, cc, xi, eta, grid_bulk, bulk_int):
    """Abstract bulk contribution"""
    lnxi = np.log(xi)
    if lnxi > grid_bulk[0, -1]:
        raise LeProHQError(
            f"xi interpolation for threshold coeff out of grid: {xi} > {np.exp(grid_bulk[0,-1])}",
            proj=proj,
            cc=cc,
            xi=xi,
            eta=eta,
        )
    return bulk_int(np.log(eta), np.log(xi))[0, 0]


def raw_c(proj, cc, xi, eta, path, cf, ct, high):
    """Abstract full NLO coefficient function"""
    # PV coeff function?
    if proj in ["xF3", "g4", "gL"]:
        return 0.0
    if path is None:
        path = datadir
    # load grids
    grid_tp, a_int = load_1d_interpolation(
        str(path) + f"/{cf}/{cf}-{proj}_{cc}-thres-coeff.dat"
    )
    grid_bulk, bulk_int = load_2d_interpolation(
        str(path) + f"/{cf}/{cf}-{proj}_{cc}-bulk.dat"
    )
    low = grid_bulk[1, 0]
    lneta = np.log(eta)
    # threshold only?
    if lneta < low:
        return raw_ctp(proj, cc, xi, eta, grid_tp, a_int, ct)
    # bulk only?
    if lneta >= high:
        return raw_cb(proj, cc, xi, eta, grid_bulk, bulk_int)
    # otherwise apply linear interpolation between the two
    tp = raw_ctp(proj, cc, xi, eta, grid_tp, a_int, ct)
    b = raw_cb(proj, cc, xi, eta, grid_bulk, bulk_int)
    return (tp * (lneta - high) + b * (low - lneta)) / (low - high)
