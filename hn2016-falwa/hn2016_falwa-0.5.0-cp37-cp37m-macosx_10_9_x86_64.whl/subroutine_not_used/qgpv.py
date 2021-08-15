from math import pi,exp
import numpy as np

def compute_qgpv_givenvort(omega,nlat,nlon,kmax,unih,ylat,avort,potential_temp,
                           t0_cn,t0_cs,stat_cn,stat_cs,scale_height=7000.):
    """
    The function "compute_qgpv_givenvort" computes the quasi-geostrophic potential
    vorticity based on the absolute vorticity, potential temperature and static
    stability given.

    Please make inquiries and report issues via Github: https://github.com/csyhuang/hn2016_falwa/issues


    Parameters
    ----------
    omega : float, optional
        Rotation rate of the planet.
    nlat : int
        Latitudinal dimension of the latitude grid.
    nlon : int
        Longitudinal dimension of the longitude grid.
    kmax : int
        Vertical dimension of the height grid.
    unih : sequence or array_like
        Numpy array of height in [meters]; dimension = (kmax)
    ylat : sequence or array_like
        Numpy array of latitudes in [degrees]; dimension = (nlat)
    avort : ndarray
        Three-dimension numpy array of absolute vorticity (i.e. relative vorticity
        + 2*Omega*sin(lat)) in [1/s]; dimension = (kmax x nlat x nlon)
    potential_temp : ndarray
        Three-dimension numpy array of potential temperature in [K];
        dimension = (kmax x nlat x nlon)
    t0_cn : sequence or array_like
        Area-weighted average of potential temperature (\tilde{\theta} in HN16)
        in the Northern hemispheric domain with dimension = (kmax)
    t0_cs : sequence or array_like
        Area-weighted average of potential temperature (\tilde{\theta} in HN16)
        in the Southern hemispheric domain with dimension = (kmax)
    stat_cn : sequence or array_like
        Static stability (d\tilde{\theta}/dz in HN16) in the Northern hemispheric
        domain with dimension = (kmax)
    stat_cs : sequence or array_like
        Static stability (d\tilde{\theta}/dz in HN16) in the Southern hemispheric
        domain with dimension = (kmax)
    scale_height : float
        Scale height of the atmosphere in [m] with default value 7000.


    Returns
    -------
    QGPV : ndarray
        Three-dimension numpy array of quasi-geostrophic potential vorticity;
        dimension = (kmax x nlat x nlon)
    dzdiv : ndarray
        Three-dimension numpy array of the stretching term in QGPV;
        dimension = (kmax x nlat x nlon)

    """

    clat = np.cos(ylat*pi/180.)
    clat = np.abs(clat) # Just to avoid the negative value at poles

    # --- Next, calculate PV ---
    av2 = np.empty_like(potential_temp) # dv/d(lon)
    av3 = np.empty_like(potential_temp) # du/d(lat)
    qgpv = np.empty_like(potential_temp) # av1+av2+av3+dzdiv

    av1 = np.ones((kmax,nlat,nlon)) * 2*omega*np.sin(ylat[np.newaxis,:,np.newaxis]*pi/180.)

    # Calculate the z-divergence term
    zdiv = np.empty_like(potential_temp)
    dzdiv = np.empty_like(potential_temp)
    for kk in range(kmax): # This is more efficient
        zdiv[kk,:60,:] = exp(-unih[kk]/scale_height)*(potential_temp[kk,:60,:]-t0_cs[kk])/stat_cs[kk]
        zdiv[kk,60:,:] = exp(-unih[kk]/scale_height)*(potential_temp[kk,60:,:]-t0_cn[kk])/stat_cn[kk]

    dzdiv[1:kmax-1,:,:] = np.exp(unih[1:kmax-1,np.newaxis,np.newaxis]/scale_height)* \
    (zdiv[2:kmax,:,:]-zdiv[0:kmax-2,:,:]) \
    /(unih[2:kmax,np.newaxis,np.newaxis]-unih[0:kmax-2,np.newaxis,np.newaxis])

    dzdiv[0,:,:] = exp(unih[0]/scale_height)*(zdiv[1,:,:]-zdiv[0,:,:])/ \
    (unih[1,np.newaxis,np.newaxis]-unih[0,np.newaxis,np.newaxis])
    dzdiv[kmax-1,:,:] = exp(unih[kmax-1]/scale_height)*(zdiv[kmax-1,:,:]-zdiv[kmax-2,:,:])/ \
    (unih[kmax-1,np.newaxis,np.newaxis]-unih[kmax-2,np.newaxis,np.newaxis])

    qgpv = avort+dzdiv * av1
    return qgpv, dzdiv
