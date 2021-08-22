import os
import numpy as np


__all__ = [
    'anderson_801_1982',
    'kong_61_2007b',
    'kong_121_2007',
    'kong_241_2007',
    'key_101_2009',
    'key_201_2009',
    'key_401_2009',
    'key_51_2012',
    'key_101_2012',
    'key_201_2012',
    'wer_201_2018',
    'wer_2001_2018',
]

_LIBPATH = os.path.abspath(os.path.dirname(__file__))
_CACHE = {}


def anderson_801_1982():
    """801 point Hankel filter, J0 and J1


    > Anderson, W. L., 1982;
    > Fast Hankel transforms using related and lagged convolutions;
    > ACM Trans. on Math. Softw. (TOMS), 8, 344-368;
    > DOI: 10.1145/356012.356014


    The original filter values are published in the appendix to above article:
    Algorithm 588, DOI: 10.1145/356012.356015

    The values provided here are taken from code that accompanies:
    Key 2012, Geophysics, DOI: 10.1190/geo2011-0237.1


    Copyright 1982 Walter L. Anderson

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'anderson_801_1982' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_anderson_801_1982_j0j1.txt'
        _CACHE['anderson_801_1982'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['anderson_801_1982']


def kong_61_2007b():
    """61 point Hankel filter, J0 and J1


    Designed and tested for dipole antenna radiation in a conductive medium.


    > Kong, F. N, 2007;
    > Hankel transform filters for dipole antenna radiation in a conductive
    > medium;
    > Geophysical Prospecting, 55(1), 83-89;
    > DOI: 10.1111/j.1365-2478.2006.00585.x


    These filter values are available from

      http://www.em-earth-consulting.no

    in the three files YBASE61NEW.dat, J0K61NEW.dat, and J1K61NEW.dat.
    Please consult the original source for more details.

    The appendix "b" after the year indicates that it corresponds to the NEW
    set of filter values.


    Copyright 2007 Fannian Kong

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'kong_61_2007b' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_kong_61_2007b_j0j1.txt'
        _CACHE['kong_61_2007b'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['kong_61_2007b']


def kong_121_2007():
    """121 point Hankel filter, J0 and J1


    Designed and tested for dipole antenna radiation in a conductive medium.


    > Kong, F. N, 2007;
    > Hankel transform filters for dipole antenna radiation in a conductive
    > medium;
    > Geophysical Prospecting, 55(1), 83-89;
    > DOI: 10.1111/j.1365-2478.2006.00585.x


    These filter values are available from

      http://www.em-earth-consulting.no

    in the three files YBASE121.dat, J0K121.dat, and J1K121.dat.
    Please consult the original source for more details.


    Copyright 2007 Fannian Kong

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'kong_121_2007' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_kong_121_2007_j0j1.txt'
        _CACHE['kong_121_2007'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['kong_121_2007']


def kong_241_2007():
    """241 point Hankel filter, J0 and J1


    Designed and tested for dipole antenna radiation in a conductive medium.


    > Kong, F. N, 2007;
    > Hankel transform filters for dipole antenna radiation in a conductive
    > medium;
    > Geophysical Prospecting, 55(1), 83-89;
    > DOI: 10.1111/j.1365-2478.2006.00585.x


    These filter values are available from

      http://www.em-earth-consulting.no

    in the three files YBASE241.dat, J0K241.dat, and J1K241.dat.
    Please consult the original source for more details.


    Copyright 2007 Fannian Kong

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'kong_241_2007' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_kong_241_2007_j0j1.txt'
        _CACHE['kong_241_2007'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['kong_241_2007']


def key_101_2009():
    """101 point Hankel filter, J0 and J1


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
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'key_101_2009' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_key_101_2009_j0j1.txt'
        _CACHE['key_101_2009'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_101_2009']


def key_201_2009():
    """201 point Hankel filter, J0 and J1


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
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'key_201_2009' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_key_201_2009_j0j1.txt'
        _CACHE['key_201_2009'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_201_2009']


def key_401_2009():
    """401 point Hankel filter, J0 and J1


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
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'key_401_2009' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_key_401_2009_j0j1.txt'
        _CACHE['key_401_2009'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_401_2009']


def key_51_2012():
    """51 point Hankel filter, J0 and J1


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
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'key_51_2012' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_key_51_2012_j0j1.txt'
        _CACHE['key_51_2012'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_51_2012']


def key_101_2012():
    """101 point Hankel filter, J0 and J1


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
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'key_101_2012' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_key_101_2012_j0j1.txt'
        _CACHE['key_101_2012'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_101_2012']


def key_201_2012():
    """201 point Hankel filter, J0 and J1


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
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'key_201_2012' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_key_201_2012_j0j1.txt'
        _CACHE['key_201_2012'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['key_201_2012']


def wer_201_2018():
    """201 point Hankel filter, J0 and J1


    Designed and tested for controlled-source electromagnetic data.

    See the notebook `Filter-wer201.ipynb` in the repo
    https://github.com/emsig/article-fdesign


    > Werthmüller, D., K. Key, and E. Slob, 2019;
    > A tool for designing digital filters for the Hankel and Fourier
    > transforms in potential, diffusive, and wavefield modeling;
    > Geophysics, 84(2), F47-F56;
    > DOI: 10.1190/geo2018-0069.1


    Copyright 2018 Dieter Werthmüller

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'wer_201_2018' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_wer_201_2018_j0j1.txt'
        _CACHE['wer_201_2018'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['wer_201_2018']


def wer_2001_2018():
    """2001 point Hankel filter, J0 and J1


    Designed and tested for ground-penetrating radar (GPR).

    See the notebook `Filter-wer2001.ipynb` in the repo
    https://github.com/emsig/article-fdesign


    > Werthmüller, D., K. Key, and E. Slob, 2019;
    > A tool for designing digital filters for the Hankel and Fourier
    > transforms in potential, diffusive, and wavefield modeling;
    > Geophysics, 84(2), F47-F56;
    > DOI: 10.1190/geo2018-0069.1


    Copyright 2018 Dieter Werthmüller

    This work is licensed under a CC BY 4.0 license.
    <http://creativecommons.org/licenses/by/4.0/>.


    Returns
    -------
    base, j0, j1 : ndarray
        Filter base and its values.

    """
    if 'wer_2001_2018' not in _CACHE.keys():
        fname = 'lib/Hankel/hankel_wer_2001_2018_j0j1.txt'
        _CACHE['wer_2001_2018'] = np.loadtxt(
            os.path.join(_LIBPATH, fname), unpack=True)
    return _CACHE['wer_2001_2018']
