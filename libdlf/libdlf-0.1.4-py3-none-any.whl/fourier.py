import os
import numpy as np


__all__ = [
    'key_81_2009',
    'key_241_2009',
    'key_601_2009',
    'key_101_2012',
    'key_201_2012',
    'grayver_50_2021',
]

_LIBPATH = os.path.abspath(os.path.dirname(__file__))
_CACHE = {}


def key_81_2009():
    """81 point Fourier filter, Sine and Cosine


    Designed and tested for controlled-source electromagnetic data.


    > Key, K., 2009;
    > 1D inversion of multicomponent, multifrequency marine CSEM data:
    > Methodology and synthetic studies for resolving thin resistive layers;
    > Geophysics, 74(2), F9-F20;
    > DOI: 10.1190/1.3058434


    Copyright 2009 Kerry Key

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, sin, cos : ndarray
        Filter base and its values.

    """
    if 'key_81_2009' not in _CACHE.keys():
        fname = 'lib/Fourier/fourier_key_81_2009_sincos.txt'
        _CACHE['key_81_2009'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_81_2009']


def key_241_2009():
    """241 point Fourier filter, Sine and Cosine


    Designed and tested for controlled-source electromagnetic data.


    > Key, K., 2009;
    > 1D inversion of multicomponent, multifrequency marine CSEM data:
    > Methodology and synthetic studies for resolving thin resistive layers;
    > Geophysics, 74(2), F9-F20;
    > DOI: 10.1190/1.3058434


    Copyright 2009 Kerry Key

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, sin, cos : ndarray
        Filter base and its values.

    """
    if 'key_241_2009' not in _CACHE.keys():
        fname = 'lib/Fourier/fourier_key_241_2009_sincos.txt'
        _CACHE['key_241_2009'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_241_2009']


def key_601_2009():
    """601 point Fourier filter, Sine and Cosine


    Designed and tested for controlled-source electromagnetic data.


    > Key, K., 2009;
    > 1D inversion of multicomponent, multifrequency marine CSEM data:
    > Methodology and synthetic studies for resolving thin resistive layers;
    > Geophysics, 74(2), F9-F20;
    > DOI: 10.1190/1.3058434


    Copyright 2009 Kerry Key

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, sin, cos : ndarray
        Filter base and its values.

    """
    if 'key_601_2009' not in _CACHE.keys():
        fname = 'lib/Fourier/fourier_key_601_2009_sincos.txt'
        _CACHE['key_601_2009'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_601_2009']


def key_101_2012():
    """101 point Fourier filter, Sine and Cosine


    Designed and tested for controlled-source electromagnetic data.


    > Key, K., 2012;
    > Is the fast Hankel transform faster than quadrature?;
    > Geophysics, 77(3), F21-F30;
    > DOI: 10.1190/geo2011-0237.1


    Copyright 2012 Kerry Key

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, sin, cos : ndarray
        Filter base and its values.

    """
    if 'key_101_2012' not in _CACHE.keys():
        fname = 'lib/Fourier/fourier_key_101_2012_sincos.txt'
        _CACHE['key_101_2012'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_101_2012']


def key_201_2012():
    """201 point Fourier filter, Sine and Cosine


    Designed and tested for controlled-source electromagnetic data.


    > Key, K., 2012;
    > Is the fast Hankel transform faster than quadrature?;
    > Geophysics, 77(3), F21-F30;
    > DOI: 10.1190/geo2011-0237.1


    Copyright 2012 Kerry Key

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, sin, cos : ndarray
        Filter base and its values.

    """
    if 'key_201_2012' not in _CACHE.keys():
        fname = 'lib/Fourier/fourier_key_201_2012_sincos.txt'
        _CACHE['key_201_2012'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_201_2012']


def grayver_50_2021():
    """50 point Fourier filter, Sine


    Designed and tested for planetary electromagnetic induction.


    > Grayver, A. V., A. Kuvshinov, and D. Werthmüller, 2021;
    > Time-Domain Modeling of Three-Dimensional Earth's and Planetary
    > Electromagnetic Induction Effect in Ground and Satellite Observations;
    > Journal of Geophysical Research: Space Physics, 126(3), e2020JA028672;
    > DOI: 10.1029/2020JA028672


    Copyright 2021 Alexander V. Grayver

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, sin : ndarray
        Filter base and its values.

    """
    if 'grayver_50_2021' not in _CACHE.keys():
        fname = 'lib/Fourier/fourier_grayver_50_2021_sin.txt'
        _CACHE['grayver_50_2021'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['grayver_50_2021']
