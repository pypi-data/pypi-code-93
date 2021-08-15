import numpy as np


def eqvlat_hemispheric(ylat, vort, area, nlat_s=None, n_points=None,
                       planet_radius=6.378e+6):

    """
    Compute equivalent latitude in a hemispheric domain.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of vorticity values; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    q_part : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).

    """
    import basis

    nlat = vort.shape[0]
    qref = np.zeros(nlat)
    brac = np.zeros(nlat)

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    # --- Southern Hemisphere ---
    qref1, dummy = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s, :], area[:nlat_s, :],
                                n_points, planet_radius=planet_radius)
    qref[:nlat_s] = qref1

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected
    qref2, dummy = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                                n_points, planet_radius=planet_radius)

    qref[-nlat_s:] = qref2[::-1]

    return qref


def eqvlat_bracket_hemispheric(ylat, vort, area, nlat_s=None, n_points=None,
                               planet_radius=6.378e+6, vgrad=None):

    """
    Compute equivalent latitude and <...>_Q in Nakamura and Zhu (2010) in a hemispheric domain.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of vorticity values; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.
    vgrad: ndarray, optional
        2-d numpy array of laplacian (or higher-order laplacian) values; dimension = (nlat, nlon)

    Returns
    -------
    q_part : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    brac : ndarray or None
        1-d numpy array of averaged vgrad in the square bracket.
        If *vgrad* = None, *brac* = None.

    """
    import basis

    nlat = vort.shape[0]
    qref = np.zeros(nlat)
    brac = np.zeros(nlat)

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    # --- Southern Hemisphere ---
    qref1, brac1 = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s,:], area[:nlat_s,:],
                                n_points, planet_radius=planet_radius,vgrad=vgrad)
    qref[:nlat_s] = qref1

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected
    qref2, brac2 = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                                n_points, planet_radius=planet_radius, vgrad=vgrad)

    qref[-nlat_s:] = qref2[::-1]

    brac[:nlat_s] = brac1
    brac[-nlat_s:] = brac2[::-1]

    return qref, brac


def qgpv_eqlat_lwa(ylat, vort, area, dmu, nlat_s=None, n_points=None,
                   planet_radius=6.378e+6):

    """
    Compute equivalent latitutde *qref* and local wave activity *lwa_result* based
    on Quasi-geostrophic potential vorticity field *vort* at a pressure level as
    outlined in Huang and Nakamura (2017).

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of Quasi-geostrophic potential vorticity field; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    qref : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    lwa_result : ndarray
        2-d numpy array of local wave activity values;
                    dimension = [nlat_s x nlon]

    """

    import basis

    nlat = vort.shape[0]
    nlon = vort.shape[1]

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    qref = np.zeros(nlat)
    lwa_result = np.zeros((nlat, nlon))

    # --- Southern Hemisphere ---
    qref1 = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s, :], area[:nlat_s, :],
                         n_points, planet_radius=planet_radius)
    qref[:nlat_s] = qref1
    lwa_result[:nlat_s, :], dummy = basis.lwa(nlon, nlat_s,
                                              vort[:nlat_s, :],
                                              qref1, dmu[:nlat_s])

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected
    qref2 = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                         n_points, planet_radius=planet_radius)
    qref[-nlat_s:] = -qref2[::-1]
    lwa_result[-nlat_s:, :], dummy = basis.lwa(nlon, nlat_s,
                                               vort[-nlat_s:, :],
                                               qref[-nlat_s:],
                                               dmu[-nlat_s:])
    return qref, lwa_result


def qgpv_eqlat_lwa_ncforce(ylat, vort, ncforce, area, dmu, nlat_s=None,
                           n_points=None, planet_radius=6.378e+6):

    """
    Compute equivalent latitutde *qref*, local wave activity *lwa_result* and
    non-conservative force on wave activity *bigsigma_result* based on Quasi-
    geostrophic potential vorticity field *vort* at a pressure level as
    outlined in Huang and Nakamura (2017).

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    vort : ndarray
        2-d numpy array of Quasi-geostrophic potential vorticity field; dimension = (nlat, nlon).
    ncforce: ndarray
        2-d numpy array of non-conservative force field (i.e. theta in NZ10(a) in equation (23a) and (23b));
        dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    n_points : int, default None
        Analysis resolution to calculate equivalent latitude. If input as None, it will be initialized as *nlat_s*.
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    qref : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    lwa_result : ndarray
        2-d numpy array of local wave activity values; dimension = (nlat, nlon).
    bigsigma_result: ndarray
        2-d numpy array of non-conservative force contribution value; dimension = (nlat, nlon).

    """

    import basis

    nlat = vort.shape[0]
    nlon = vort.shape[1]

    if nlat_s is None:
        nlat_s = int(nlat/2)

    if n_points is None:
        n_points = nlat_s

    qref = np.zeros(nlat)
    lwa_result = np.zeros((nlat, nlon))
    bigsigma_result = np.zeros((nlat, nlon))

    # --- Southern Hemisphere ---
    qref1 = basis.eqvlat(ylat[:nlat_s], vort[:nlat_s, :], area[:nlat_s, :],
                         n_points, planet_radius=planet_radius)
    qref[:nlat_s] = qref1
    lwa_result[:nlat_s, :], bigsigma_result[:nlat_s, :] = basis.lwa(nlon, nlat_s,
                                                                    vort[:nlat_s, :],
                                                                    qref1, dmu[:nlat_s],
                                                                    ncforce=ncforce[:nlat_s, :])

    # --- Northern Hemisphere ---
    vort2 = -vort[::-1, :]  # Added the minus sign, but gotta see if NL_North is affected
    qref2 = basis.eqvlat(ylat[:nlat_s], vort2[:nlat_s, :], area[:nlat_s, :],
                         n_points, planet_radius=planet_radius)
    qref[-nlat_s:] = -qref2[::-1]
    lwa_result[-nlat_s:, :], bigsigma_result[-nlat_s:, :] = basis.lwa(nlon, nlat_s,
                                                                      vort[-nlat_s:, :],
                                                                      qref[-nlat_s:],
                                                                      dmu[-nlat_s:],
                                                                      ncforce=ncforce[-nlat_s:, :])
    return qref, lwa_result, bigsigma_result


def qgpv_input_qref_to_compute_lwa(ylat, qref, vort, area, dmu, nlat_s=None,
                                   planet_radius=6.378e+6):
    """
    Compute equivalent latitutde *qref* and local wave activity *lwa_result* based
    on Quasi-geostrophic potential vorticity field *vort* at a pressure level as
    outlined in Huang and Nakamura (2017). This function computes lwa based on a
    prescribed *qref* instead of *qref* obtained from the QGPV field.

    Parameters
    ----------
    ylat : sequence or array_like
        1-d numpy array of latitude (in degree) with equal spacing in ascending order; dimension = nlat.
    qref : ndarray
        1-d numpy array of value Q(y) where latitude y is given by ylat; dimension = (nlat).
    vort : ndarray
        2-d numpy array of Quasi-geostrophic potential vorticity field; dimension = (nlat, nlon).
    area : ndarray
        2-d numpy array specifying differential areal element of each grid point; dimension = (nlat, nlon).
    dmu: sequence or array_like
        1-d numpy array of latitudinal differential length element (e.g. dmu = cos(lat) d(lat)). Size = nlat.
    nlat_s : int, default None
        The index of grid point that defines the extent of hemispheric domain from the pole. If input as None, it will be initialize as int(nlat/2).
    planet_radius : float, default 6.378e+6
        radius of spherical planet of interest consistent with input 'area'.

    Returns
    -------
    lwa_result : ndarray
        2-d numpy array of local wave activity values; dimension = (nlat, nlon).
    """
    import basis

    nlat = vort.shape[0]
    nlon = vort.shape[1]
    if nlat_s is None:
        nlat_s = nlat/2

    lwa_result = np.zeros((nlat, nlon))

    # --- Southern Hemisphere ---
    lwa_result[:nlat_s, :], dummy = basis.lwa(nlon, nlat_s, vort[:nlat_s, :],
                                              qref[:nlat_s], dmu[:nlat_s])

    # --- Northern Hemisphere ---
    lwa_result[-nlat_s:, :], dummy = basis.lwa(nlon, nlat_s, vort[-nlat_s:, :],
                                               qref[-nlat_s:], dmu[-nlat_s:])

    return lwa_result
