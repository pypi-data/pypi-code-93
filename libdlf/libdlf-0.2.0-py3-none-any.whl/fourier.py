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
    if getattr(key_81_2009, 'cache', None) is None:
        fname = 'lib/Fourier/fourier_key_81_2009_sincos.npz'
        key_81_2009.cache = np.load(
            os.path.join(_LIBPATH, fname))['dlf']
    return key_81_2009.cache


key_81_2009.values = ['sin', 'cos']


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
    if getattr(key_241_2009, 'cache', None) is None:
        fname = 'lib/Fourier/fourier_key_241_2009_sincos.npz'
        key_241_2009.cache = np.load(
            os.path.join(_LIBPATH, fname))['dlf']
    return key_241_2009.cache


key_241_2009.values = ['sin', 'cos']


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
    if getattr(key_601_2009, 'cache', None) is None:
        fname = 'lib/Fourier/fourier_key_601_2009_sincos.npz'
        key_601_2009.cache = np.load(
            os.path.join(_LIBPATH, fname))['dlf']
    return key_601_2009.cache


key_601_2009.values = ['sin', 'cos']


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
    if getattr(key_101_2012, 'cache', None) is None:
        fname = 'lib/Fourier/fourier_key_101_2012_sincos.npz'
        key_101_2012.cache = np.load(
            os.path.join(_LIBPATH, fname))['dlf']
    return key_101_2012.cache


key_101_2012.values = ['sin', 'cos']


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
    if getattr(key_201_2012, 'cache', None) is None:
        fname = 'lib/Fourier/fourier_key_201_2012_sincos.npz'
        key_201_2012.cache = np.load(
            os.path.join(_LIBPATH, fname))['dlf']
    return key_201_2012.cache


key_201_2012.values = ['sin', 'cos']


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
    if getattr(grayver_50_2021, 'cache', None) is None:
        fname = 'lib/Fourier/fourier_grayver_50_2021_sin.npz'
        grayver_50_2021.cache = np.load(
            os.path.join(_LIBPATH, fname))['dlf']
    return grayver_50_2021.cache


grayver_50_2021.values = ['sin']
