#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Charge Distortion Model for CCDs.

============================
This is a function to run the upgraded CDM CTI model developed by Alex Short (ESA).

:requires: NumPy

:author: Alex Short
:author: Sami-Matias Niemi
:author: David Lucsanyi
"""
import logging
import typing as t

import numba
import numpy as np

from pyxel.detectors import CCD

try:
    from matplotlib import pyplot as plt
except ImportError:
    # raise Warning('Matplotlib cannot be imported')
    pass


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# @pyxel.register(group='charge_transfer', name='cdm', detector='ccd')
# TODO: What is the type of 'tr_p', 'tr_s', 'nt_p', 'nt_s', 'sigma_p' and 'sigma_s' ?
#       Is it `t.Union[float, t.Iterable[float]]` ???
def cdm(
    detector: CCD,
    parallel_cti: bool,
    serial_cti: bool,
    beta_p: float,
    beta_s: float,
    tr_p: t.Sequence[float],
    tr_s: t.Sequence[float],
    nt_p: t.Sequence[float],
    nt_s: t.Sequence[float],
    sigma_p: t.Sequence[float],
    sigma_s: t.Sequence[float],
    charge_injection: bool,
) -> None:
    """Charge Distortion Model (CDM) model wrapper.

    :param detector: Pyxel CCD detector object
    :param parallel_cti: switch on CTI in parallel direction (along column)
    :param serial_cti: switch on CTI in serial direction (along rows)
    :param charge_injection: set this true in case of charge injection,
        charge packets goes through all pixels in parallel direction
    :param beta_p: electron cloud expansion coefficient, parallel
    :param beta_s: electron cloud expansion coefficient, serial
    :param tr_p: trap release time constants (τ_r), parallel
    :param tr_s: trap release time constants (τ_r), serial
    :param nt_p: absolute trap densities (n_t), parallel
    :param nt_s: absolute trap densities (n_t), serial
    :param sigma_p: trap capture cross-sections (σ), parallel
    :param sigma_s: trap capture cross-sections (σ), serial
    """
    # Ne - number of electrons in a pixel
    # ne - electron density in the vicinity of the trap
    # Vc - volume of the charge cloud
    # Pr - the probability that the trap will release the electron into the sample
    # tau_c - capture time constant
    # Pc - capture probability (per vacant trap) as a function of the number of sample electrons Ne
    # NT - number of traps in the column,
    # NT = 2*nt*Vg*x  where x is the number of TDI transfers or the column length in pixels.
    # Nc - number of electrons captured by a given trap species during the transit of an integrating signal packet
    # N0 - initial trap occupancy
    # Nr - number of electrons released into the sample during a transit along the column
    # vg: assumed maximum geometrical volume electrons can occupy within a pixel (parallel)
    # svg: assumed maximum geometrical volume electrons can occupy within a pixel (serial)
    # t: constant TDI period (parallel)
    # st: constant TDI period (serial)

    logging.info("")
    char = detector.characteristics

    detector.pixel.array = run_cdm(
        s=detector.pixel.array,
        vg=char.vg,
        svg=char.svg,
        t=char.t,
        st=char.st,
        fwc=char.fwc,
        sfwc=char.fwc_serial,
        vth=detector.e_thermal_velocity,
        parallel_cti=parallel_cti,
        serial_cti=serial_cti,
        charge_injection=charge_injection,
        chg_inj_parallel_transfers=detector.geometry.row,
        beta_p=beta_p,
        beta_s=beta_s,
        tr_p=np.array(tr_p),
        tr_s=np.array(tr_s),
        nt_p=np.array(nt_p),
        nt_s=np.array(nt_s),
        sigma_p=np.array(sigma_p),
        sigma_s=np.array(sigma_s),
    )


@numba.jit(nopython=True, nogil=True, parallel=False)
def run_cdm(
    s: np.ndarray,
    beta_p: float,
    beta_s: float,
    vg: float,
    svg: float,
    t: float,
    st: float,
    fwc: float,
    sfwc: float,
    vth: float,
    tr_p: np.ndarray,
    tr_s: np.ndarray,
    nt_p: np.ndarray,
    nt_s: np.ndarray,
    sigma_p: np.ndarray,
    sigma_s: np.ndarray,
    charge_injection: bool = False,
    chg_inj_parallel_transfers: int = 0,
    parallel_cti: bool = True,
    serial_cti: bool = True,
) -> np.ndarray:
    """CDM model.

    :param s: np.ndarray
    :param dob:
    :param beta_p: electron cloud expansion coefficient (parallel)
    :param beta_s: electron cloud expansion coefficient (serial)
    :param vg: assumed maximum geometrical volume electrons can occupy within a pixel (parallel)
    :param svg: assumed maximum geometrical volume electrons can occupy within a pixel (serial)
    :param t: constant TDI period (parallel)
    :param st: constant TDI period (serial)
    :param fwc:
    :param sfwc:
    :param vth:
    :param charge_injection:
    :param chg_inj_parallel_transfers:
    :param sigma_p:
    :param sigma_s:
    :param tr_p:
    :param tr_s:
    :param nt_p: number of traps per electron cloud (and not pixel!) in parallel direction
    :param nt_s: number of traps per electron cloud (and not pixel!) in serial direction
    :param parallel_cti:
    :param serial_cti:
    :return:
    """
    ydim, xdim = s.shape  # full signal array we want to apply cdm for

    kdim_p = len(nt_p)
    kdim_s = len(nt_s)

    # np.clip(s, 0., fwc, s)      # full well capacity

    nt_p = nt_p / vg  # parallel trap density (traps / cm**3)
    nt_s = nt_s / svg  # serial trap density (traps / cm**3)

    # nt_p *= rdose             # absolute trap density [per cm**3]
    # nt_s *= rdose             # absolute trap density [per cm**3]

    # IMAGING (non-TDI) MODE
    # Parallel direction
    if parallel_cti:
        no = np.zeros((xdim, kdim_p))
        alpha_p = t * sigma_p * vth * fwc ** beta_p / (2.0 * vg)  # type: np.ndarray
        g_p = 2.0 * nt_p * vg / fwc ** beta_p  # type: np.ndarray
        for i in range(0, ydim):
            if charge_injection:
                gamma_p = (
                    g_p * chg_inj_parallel_transfers
                )  # number of all transfers in parallel dir.
            else:
                gamma_p = g_p * i  # TODO: (i+1) ?????????????
            for k in range(kdim_p):
                for j in numba.prange(0, xdim):
                    nc = 0.0
                    if s[i, j] > 0.01:
                        nc = max(
                            (gamma_p[k] * s[i, j] ** beta_p - no[j, k])
                            / (gamma_p[k] * s[i, j] ** (beta_p - 1.0) + 1.0)
                            * (
                                1.0
                                - np.exp(-1 * alpha_p[k] * s[i, j] ** (1.0 - beta_p))
                            ),
                            0.0,
                        )
                        no[j, k] += nc
                    nr = no[j, k] * (1.0 - np.exp(-t / tr_p[k]))
                    s[i, j] += -1 * nc + nr
                    no[j, k] -= nr
                    if s[i, j] < 0.01:
                        s[i, j] = 0.0

    # IMAGING (non-TDI) MODE
    # Serial direction
    if serial_cti:
        sno = np.zeros((ydim, kdim_s))
        alpha_s = st * sigma_s * vth * sfwc ** beta_s / (2.0 * svg)  # type: np.ndarray
        g_s = 2.0 * nt_s * svg / sfwc ** beta_s
        for j in range(0, xdim):
            gamma_s = g_s * j  # TODO: (j+1) ?????????????
            for k in range(kdim_s):
                for i in numba.prange(0, ydim):
                    nc = 0.0
                    if s[i, j] > 0.01:
                        nc = max(
                            (gamma_s[k] * s[i, j] ** beta_s - sno[i, k])
                            / (gamma_s[k] * s[i, j] ** (beta_s - 1.0) + 1.0)
                            * (
                                1.0
                                - np.exp(-1 * alpha_s[k] * s[i, j] ** (1.0 - beta_s))
                            ),
                            0.0,
                        )
                        sno[i, k] += nc
                    nr = sno[i, k] * (1.0 - np.exp(-st / tr_s[k]))
                    s[i, j] += -1 * nc + nr
                    sno[i, k] -= nr
                    if s[i, j] < 0.01:
                        s[i, j] = 0.0

    return s


def plot_serial_profile(
    data: np.ndarray, row: int, data2: t.Optional[np.ndarray] = None
) -> None:
    """TBW.

    :param data:
    :param row:
    :param data2:
    """
    ydim, xdim = data.shape
    profile_x = list(range(ydim))
    profile_y = data[row, :]
    plt.title("Serial profile")
    plt.plot(profile_x, profile_y, color="blue")
    if data2 is not None:
        profile_y_2 = data2[row, :]
        plt.plot(profile_x, profile_y_2, color="red")


def plot_parallel_profile(
    data: np.ndarray, col: int, data2: t.Optional[np.ndarray] = None
) -> None:
    """TBW.

    :param data:
    :param col:
    :param data2:
    """
    ydim, xdim = data.shape
    profile_x = list(range(xdim))
    profile_y = data[:, col]
    plt.title("Parallel profile")
    plt.plot(profile_x, profile_y, color="blue")
    if data2 is not None:
        profile_y_2 = data2[:, col]
        plt.plot(profile_x, profile_y_2, color="red")


def plot_1d_profile(
    array: np.ndarray, offset: int = 0, label: str = "", m: str = "-"
) -> None:
    """Plot profile on log scale.

    :param array:
    :param offset:
    :param label:
    :param m:
    """
    x = list(range(offset, offset + len(array)))
    # plt.title('Parallel profile, charge injection')
    plt.semilogy(x, array, m, label=label)
    if label:
        plt.legend()


def plot_1d_profile_lin(
    array: np.ndarray,
    offset: int = 0,
    label: str = "",
    m: str = "-",
    col: t.Optional[str] = None,
) -> None:
    """TBW.

    :param array:
    :param offset:
    :param label:
    :param m:
    :param col:
    """
    x = list(range(offset, offset + len(array)))
    # plt.title('Parallel profile, charge injection')
    plt.plot(x, array, m, label=label, color=col)
    if label:
        plt.legend()


def plot_1d_profile_with_err(
    array: np.ndarray, error: np.ndarray, offset: int = 0, label: str = ""
) -> None:
    """TBW.

    :param array:
    :param error:
    :param offset:
    :param label:
    """
    x = list(range(offset, offset + len(array)))
    plt.title("Parallel profile with error, charge injection")
    plt.errorbar(x, array, error, label=label, linestyle="None", marker=".")
    if label:
        plt.legend()


def plot_residuals(
    data: np.ndarray, data2: np.ndarray, label: str = ""
) -> None:  # col='magenta',
    """TBW.

    :param data:
    :param data2:
    # :param col:
    :param label:
    """
    x = list(range(len(data)))
    # plt.title('Residuals of fitted and target parallel CTI profiles')
    residuals = np.around(data - data2, decimals=5)
    # residuals = data-data2
    # plt.plot(x, residuals, '.', color=col, label=label)
    plt.plot(x, residuals, ".", label=label)
    plt.legend()


def plot_image(data: np.ndarray) -> None:
    """TBW.

    :param data:
    """
    plt.imshow(data, cmap=plt.gray())  # , interpolation='nearest')
    plt.xlabel("x - serial direction")
    plt.ylabel("y - parallel direction")
    plt.title("CCD image with CTI")
    plt.colorbar()


# @numba.jit(nopython=True, nogil=True, parallel=True)
def optimized_cdm(
    s: np.ndarray,
    beta_p: float,
    beta_s: float,
    vg: float,
    svg: float,
    t: float,
    st: float,
    fwc: float,
    sfwc: float,
    vth: float,
    tr_p: np.ndarray,
    tr_s: np.ndarray,
    nt_p: np.ndarray,
    nt_s: np.ndarray,
    sigma_p: np.ndarray,
    sigma_s: np.ndarray,
    charge_injection: bool = False,
    chg_inj_parallel_transfers: int = 0,
    parallel_cti: bool = True,
    serial_cti: bool = True,
) -> np.ndarray:
    """CDM model.

    Done by Patricia Liebing. Not yet test or compared to the original 'run_cdm' function.

    :param s: np.ndarray
    :param dob:
    :param beta_p: electron cloud expansion coefficient (parallel)
    :param beta_s: electron cloud expansion coefficient (serial)
    :param vg: assumed maximum geometrical volume electrons can occupy within
               a pixel (parallel)
    :param svg: assumed maximum geometrical volume electrons can occupy within
                a pixel (serial)
    :param t: constant TDI period (parallel)
    :param st: constant TDI period (serial)
    :param fwc:
    :param sfwc:
    :param vth:
    :param charge_injection:
    :param chg_inj_parallel_transfers:
    :param sigma_p:
    :param sigma_s:
    :param tr_p:
    :param tr_s:
    :param nt_p: number of traps per electron cloud (and not pixel!)
                 in parallel direction
    :param nt_s: number of traps per electron cloud (and not pixel!)
                 in serial direction
    :param parallel_cti:
    :param serial_cti:
    :return:
    """
    ydim, xdim = s.shape  # full signal array we want to apply cdm for

    kdim_p = len(nt_p)
    kdim_s = len(nt_s)

    # np.clip(s, 0., fwc, s)      # full well capacity

    nt_p = nt_p / vg  # parallel trap density (traps / cm**3)
    nt_s = nt_s / svg  # serial trap density (traps / cm**3)

    # nt_p *= rdose             # absolute trap density [per cm**3]
    # nt_s *= rdose             # absolute trap density [per cm**3]

    # IMAGING (non-TDI) MODE
    # Parallel direction
    if parallel_cti:
        no = np.zeros((xdim, kdim_p))
        alpha_p = t * sigma_p * vth * fwc ** beta_p / (2.0 * vg)  # type: np.ndarray
        g_p = 2.0 * nt_p * vg / fwc ** beta_p  # type: np.ndarray
        for i in range(0, ydim):
            if charge_injection:
                gamma_p = (
                    g_p * chg_inj_parallel_transfers
                )  # number of all transfers in parallel dir.
            else:
                gamma_p = g_p * (i + 1)
            for k in range(kdim_p):
                nc = np.zeros(xdim)
                nctest = np.zeros(xdim)
                sclm = s[i, :]
                idx = np.where(sclm > 0.01)
                nok = no[:, k]
                nc[idx] += (
                    (gamma_p[k] * sclm[idx] ** beta_p - nok[idx])
                    / (gamma_p[k] * sclm[idx] ** (beta_p - 1.0) + 1.0)
                    * (1.0 - np.exp(-1 * alpha_p[k] * sclm[idx] ** (1.0 - beta_p)))
                )
                no[:, k] += np.fmax(nctest, nc)
                nr = no[:, k] * (1.0 - np.exp(-t / tr_p[k]))
                s[i, :] += -1 * nc + nr
                no[:, k] -= nr

    # IMAGING (non-TDI) MODE
    # Serial direction
    if serial_cti:
        sno = np.zeros((ydim, kdim_s))
        alpha_s = st * sigma_s * vth * sfwc ** beta_s / (2.0 * svg)  # type: np.ndarray
        g_s = 2.0 * nt_s * svg / sfwc ** beta_s  # type: np.ndarray
        for j in range(0, xdim):
            gamma_s = g_s * (j + 1)
            for k in range(kdim_s):
                ncs = np.zeros(ydim)
                ncstest = np.zeros(ydim)
                srow = s[:, j]
                idxs = np.where(srow > 0.01)
                snok = sno[:, k]
                ncs[idxs] += (
                    (gamma_s[k] * srow[idxs] ** beta_s - snok[idxs])
                    / (gamma_s[k] * srow[idxs] ** (beta_s - 1.0) + 1.0)
                    * (1.0 - np.exp(-1 * alpha_s[k] * srow[idxs] ** (1.0 - beta_s)))
                )
                sno[:, k] += np.fmax(ncstest, ncs)
                nrs = sno[:, k] * (1.0 - np.exp(-st / tr_s[k]))
                s[:, j] += -1 * ncs + nrs
                sno[:, k] -= nrs

    return s
