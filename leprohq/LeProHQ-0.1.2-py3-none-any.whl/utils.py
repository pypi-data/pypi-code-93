# -*- coding: utf-8 -*-
import pathlib

import numpy as np
import scipy.special as sf
import scipy.interpolate as ip

datadir = pathlib.Path(__file__).absolute().parent / "data"

ln2 = np.log(2)


def Li2(z):
    """
    Remap dilogarithm.

    Parameters
    ----------
        z : float
            argument

    Returns
    -------
        float :
            Li2(z)
    """
    return sf.spence(1.0 - z)


grids = {}
"""Grids cache"""


def load_grid(path):
    """
    Read a grid from file.

    Uses a caching bases on the path.

    Parameters
    ----------
        path : str
            file path

    Returns
    -------
        np.array :
            grid
    """
    # already present?
    if path in grids:
        return grids[path]
    cnt = np.loadtxt(path)
    grids[path] = cnt
    return cnt


def raw_ctp(proj, cc, xi, eta, cnt, ct):
    """Abstract improved threshold limit"""
    t = ct(proj, cc, xi, eta)
    a_int = ip.UnivariateSpline(cnt[0], cnt[1])
    a = a_int(np.log(xi))
    return t * (1.0 + a * eta)


def raw_cb(xi, eta, cnt):
    """Abstract bulk contribution"""
    bulk_int = ip.RectBivariateSpline(cnt[1:, 0], cnt[0, 1:], cnt[1:, 1:])
    return bulk_int(np.log(eta), np.log(xi))[0, 0]


def raw_c(proj, cc, xi, eta, path, cf, ct, high):
    """Abstract full NLO coefficient function"""
    # PV coeff function?
    if proj in ["xF3", "g4", "gL"]:
        return 0.0
    if path is None:
        path = datadir
    elif isinstance(path, str):
        path = pathlib.Path(path)
    # load grids
    grid_tp = load_grid(path / f"{cf}" / f"{cf}-{proj}_{cc}-thres-coeff.dat")
    grid_bulk = load_grid(path / f"{cf}" / f"{cf}-{proj}_{cc}-bulk.dat")
    low = grid_bulk[1, 0]
    lneta = np.log(eta)
    # threshold only?
    if lneta < low:
        return raw_ctp(proj, cc, xi, eta, grid_tp, ct)
    # bulk only?
    if lneta >= high:
        return raw_cb(xi, eta, grid_bulk)
    # otherwise apply linear interpolation between the two
    tp = raw_ctp(proj, cc, xi, eta, grid_tp, ct)
    b = raw_cb(xi, eta, grid_bulk)
    return (tp * (lneta - high) + b * (low - lneta)) / (low - high)
