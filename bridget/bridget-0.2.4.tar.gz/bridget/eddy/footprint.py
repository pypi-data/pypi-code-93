"""
The `footprint` submodule implements common methods to calculate the
footprint of the measurement from Eddy Covariance data.
In addition, several functions are defined to calculate the required
meteorological parameters.

Beside several methods that can calculate the timevariat footprint,
an aggregation method for defining a common footprint region is
given.

Examples
--------

.. note::

    More to come soon

"""

import numpy as np
from math import gamma

def u_star_calc(cov_uw, cov_vw):
    """
    Function to calculate the friction velocity u_star [m/s].

    Parameters
    ----------
    cov_uw : list, float
        Covariance between the wind components u (horizontal) and w (vertical) [m2/s2].
    cov_vw : list, float
        Covariance between the wind components v (horizontal) and w (vertical) [m2/s2].

    Returns
    ----------
    u_star : list, float
        friction velocity [m/s].

    References
    ----------
    http://glossary.ametsoc.org/wiki/Friction_velocity (primary source: Sutton, O. G. 1953. Micrometeorology. p. 76.)
    """

    u_star = (cov_uw**2 + cov_vw**2)**(1/4)
    return u_star


def sat_vapor_pressure_calc(p, t_air):
    """
    Function to calculate the saturation vapor pressure e_w [hPa] of water vapor in moist air.

    Parameters
    ----------
    t_air : list, float
        air temperature [°C].
    p : list, float
        air pressure [hPa].

    Returns
    ----------
    e_w : list, float
        saturation vapor pressure [hPa].

    References
    ----------
    https://library.wmo.int/doc_num.php?explnum_id=3151 (p. 163)
    """

    e_w = (1.0016 + 3.15 * 10**(-6) * p - 0.074 * p**(-1)) * (6.112 * np.exp((17.62 * t_air) / (243.12 + t_air)))
    return e_w


def relative_humidity_calc(a, t_air, e_w):
    """
    Function to calculate relative humidity [%] from absolute humidity, saturation vapor pressure and air temperature.

    Parameters
    ----------
    a : list, float
        absolute humidity [g/m3].
    t_air : list, float
        air temperature [°C].
    e_w : list, float
        saturation vapor pressure [hPa].

    Returns
    ----------
    rh : list, float
        relativ humidity [%].

    References
    ----------

    """
    R_v = 461.5     #specific gas constant for water vapor [J/(kg*K)]
    rh = 100 * (a * 10**(-3)) * R_v * (t_air + 273.15) * (e_w * 100)**(-1)
    return rh


def act_vapor_pressure_calc(rh, e_w):
    """
    Function to calculate the actual vapor pressure e_a [hPa].

    Parameters
    ----------
    rh : list, float
        relative humidity [%].
    e_w : list, float
        saturation vapor pressure [hPa].

    Returns
    ----------
    e_a : list, float
        actual vapor pressure [hPa].

    References
    ----------
    https://library.wmo.int/doc_num.php?explnum_id=3151 (p. 163)
    """
    e_a = rh * e_w / 100
    return e_a


def air_density_calc(p, e_a, t_air):
    """
    Function to calculate the air density rho [] of humid air.

    Parameters
    ----------
    p : list, float
        air pressure [hPa].
    e_a : list, float
        actual vapor pressure [hPa].
    t_air : list, float
        air temperature [°C].

    Returns
    ----------
    rho : list, float
        air density [kg/m3].

    References
    ----------
    deviation from the ideal gas law
    """
    R_v = 461.5     #specific gas constant for water vapor [J/(kg*K)]
    R_d = 287.1     #specific gas constant for dry air [J/(kg*K)]

    p_d = p - e_a   # calculate the pressure of dry air p_d [hPa]
    rho = (p_d * 100) / (R_d * (t_air + 273.15)) + (e_a * 100) / (R_v * (t_air + 273.15))
    return rho

    ##different formula for rho, results are nearly equal/very similar, first formula is more intuitive (from perfect gas law)
    #rho_1 = 1.201 * ((290 * ((p * 100) - 0.378 * (e_a * 100))) / (1000 * (t_air + 273.15))) / 100



def specific_heat_cap_calc(e_a, p):
    """
    Function to calculate the specific heat capacity of air [J/(kgK)].

    Parameters
    ----------
    e_a : list, float
        actual vapor pressure [hPa].
    p : list, float
        air pressure [hPa].

    Returns
    ----------
    c_p : list, float
        specific heat capacity [J/(kgK)].

    References
    ----------
    http://python.hydrology-amsterdam.nl/moduledoc/index.html (primary source: http://www.fao.org/3/x0490e/x0490e07.htm)
            can´t really find the formula in the primary source (must be derived in any way)
    """
    c_p = 0.24 * 4185.5 * (1 + 0.8 * 0.622 * (e_a * 100) / (p * 100 - e_a * 100))
    return c_p


def sensible_heat_calc(rho, c_p, cov_wt):
    """
    Function to calculate the sensible heat flux hts [W/m2].

    Parameters
    ----------
    rho : list, float
        air density [kg/m3].
    c_p : list, float
        specific heat capacity [J/(kgK)].
    cov_wt : list, float
        covariance between the vertical wind component w and temperature [(m*°C)/s].

    Returns
    ----------
    hts : list, float
        sensible heat flux [W/m2].

    References
    Soltani, M., Mauder, M., Laux, P. et al. Turbulent flux variability and energy balance closure in the TERENO prealpine observatory: a hydrometeorological data analysis. Theor Appl Climatol 133, 937–956 (2018). https://doi.org/10.1007/s00704-017-2235-1
    ----------

    """
    hts = rho * c_p * cov_wt    #easiest formula for hts, but there are others
    return hts


def obukhov_length_calc(rho, c_p, u_star, t_air, hts, k = 0.4):
    """
    Function to calculate the Obukhov length L [m] based on the actual air temperature.

    Parameters
    ----------
    rho : list, float
        air density [kg/m3].
    c_p : list, float
        specific heat capacity [J/(kgK)].
    t_air : list, float
        air temperature [°C].
    u_star : list, float
        friction velocity [m/s].
    hts : list, float
        sensible heat flux [W/m2].
    k : float
        von Karman constant [-]
    Returns
    ----------
    L : list, float
        Obukhov length [m].

    References
    ----------
    Foken 2017, Micrometeorology, p. 55

    """
    g = 9.81    # gravity
    L = - (rho * c_p * u_star**3 * (t_air + 273.15)) / (k * g * hts)
    return L



def footprint(dt_index, t_air, a, p, u, cov_uw, cov_vw, cov_wt, var_v, direction, tstamp, z = 2.0, fetch = 200, grid = 500, method = "Kormann"):
    """
    Top-level footprint function.

    The calculation method is selected with the method parameter.
    Currently implemented methods are:

    - ``'kormann'``: Kormann and Meixner (2001)

    Other methods will follow, with the highest priority for the Kljun model (2015)

    For further information about the methods check the References section.
    Leclerc and Foken (2014) are giving an overview of avaiable footprint models in chapter 1.3 and table 1.3 (p.12)

    Parameters
    ----------
    dt_index : list, datetime
        datetime list corresponding to the other variables, format: '%m.%d.%Y %H:%M'.
    t_air : list, float
        air temperature [°C].
    a : list, float
        absolute humidity [g/m3].
    p : list, float
        air pressure [hPa].
    u : list, float
        horizontal wind component for the direction in which the sonic is oriented [m/s].
    cov_uw : list, float
        Covariance between the wind components u and w [m2/s2].
    cov_vw : list, float
        Covariance between the wind components v and w [m2/s2].
    cov_wt : list, float
        Covariance between the wind component w and temperature [(m*°C)/s].
    var_v : list, float
        variance of v (horizontal wind component for the direction rectangular to the orientation of the sonic) [m/s].
    direction : list, float
        wind direction [°].
    tstamp : int
        index of the line/time at which the footprint is to be calculated.
    z : float
        measurement height [m].
    fetch : int
        upwind distance over which calculation domain to extends [m].
    grid : int
        total calculation grid.
    method : string
        pick a calculation method.

    References
    ----------
    Leclerc MY, Foken T (eds) (2014) Footprints in Micrometeorology and Ecology. Springer, Berlin
    Kormann & Meixner 2001, An Analytical Footprint Model For Non-Neutral Stratification

    """
    if method.lower() == 'kormann':
      return footprint_kormann(dt_index, t_air, a, p, u, cov_uw, cov_vw, cov_wt, var_v, direction, tstamp, z, fetch, grid)
    else:
      raise NotImplementedError('Hold tight, other methods are about to come')




def footprint_kormann(dt_index, t_air, a, p, u, cov_uw, cov_vw, cov_wt, var_v, direction, tstamp, z, fetch, grid):
    """
    Footprint function to calculate the footprint after Kormann & Meixner (2001).


    Parameters
    ----------
    dt_index : list, datetime
        datetime list corresponding to the other variables.
    t_air : list, float
        air temperature [°C].
    a : list, float
        absolute humidity [g/m3].
    p : list, float
        air pressure [hPa].
    u : list, float
        horizontal wind component for the direction in which the sonic is oriented [m/s].
    cov_uw : list, float
        Covariance between the wind components u and w [m2/s2].
    cov_vw : list, float
        Covariance between the wind components v and w [m2/s2].
    cov_wt : list, float
        Covariance between the wind component w and temperature [(m*°C)/s].
    var_v : list, float
        variance of v (horizontal wind component for the direction rectangular to the orientation of the sonic) [m/s].
    direction : list, float
        wind direction [°].
    tstamp : int
        index of the line/time at which the footprint is to be calculated.
    z : float
        measurement height [m].
    fetch : int
        upwind distance over which calculation domain to extends [m].
    grid : int
        total calculation grid.

    Returns
    ----------
    fp : ndarray, float
        2D array containing the footprint values [1/m2].
    FP_east : ndarray, float
        2D array containing the grid point distance east of the center point [m].
    FP_north : ndarray, float
        2D array containing the grid point distance north of the center point [m].
    fp_norm : ndarray, float
        2D array containing the normalized footprint values [-].


    References
    ----------
    Kormann & Meixner 2001, An Analytical Footprint Model For Non-Neutral Stratification
    """
    t = tstamp

    u_star = u_star_calc(cov_uw[t], cov_vw[t])

    e_w = sat_vapor_pressure_calc(p[t], t_air[t])

    rh = relative_humidity_calc(a[t], t_air[t], e_w)

    e_a = act_vapor_pressure_calc(rh, e_w)

    rho = air_density_calc(p[t], e_a, t_air[t])

    c_p = specific_heat_cap_calc(e_a, p[t])

    hts = sensible_heat_calc(rho, c_p, cov_wt[t])

    L = obukhov_length_calc(rho, c_p, u_star, t_air[t], hts)

    ### core-footprint-calculation starts here

    #set up a coordinate system and matrices for the storage of results
    grid = 2 * grid//2

    l_east = np.linspace(-fetch, fetch, grid)    #constructing an array in eastern direction from -fetch to fetch with the resolution of the grid
    l_north = np.linspace(fetch, -fetch, grid)   #constructing an array in northern direction from fetch to -fetch with the resolution of the grid

    FP_east = (np.ones((len(l_east),len(l_east)))*l_east) #distance to the midpoint in east direction
    FP_north = (np.ones((len(l_north),len(l_north)))*l_north).transpose() #distance to the midpoint in north direction

    FP_dist = np.sqrt(FP_north**2 + FP_east**2) #distance to the midpoint / center

    FP_angle = np.arctan2(FP_east, FP_north) * 180/np.pi #angle to the midpoint [°]

    FP_angle = FP_angle - direction[t] #"turning the footprint into the direction of the wind"

    FP_x = np.cos(FP_angle/57) * FP_dist
    FP_y = np.sin(FP_angle/57) * FP_dist

    idx = np.where(FP_x > 0)   #only use upwind coordinates

    fp = np.zeros((grid,grid))
    D_y = np.zeros((grid,grid))
    P_f = np.zeros((grid,grid))
    u_plume = np.ones((grid,grid)) #sigma calculation: division by u_plume -> can´t be zero, everything "ones" should also be wrong???
    sigma = np.zeros((grid,grid))

    #f.1) calculate phi_c and phi_m (stability functions) [-], Kormann_Meixner gives no calculation if L = 0
    if (L > 0):
        phi_c = 1 + 5 * z/L
        phi_m = 1 + 5 * z/L
    elif (L < 0):
        phi_c = (1 - 16 * z/L)**(-1/2)
        phi_m = (1 - 16 * z/L)**(-1/4)

    #f.2) calculate m (exponent of the wind velocity power law) and n (exponent of the eddy diffusivity power law) [-]
    k = 0.4    # von Karman constant

    m = (u_star * phi_m) / (k * u[t])

    if (L > 0):
        n = 1 / (1 + 5 * z/L)
    elif (L < 0):
        n = (1 - 24 * z/L) / (1- 16 * z/L)

    #f.3) calculate r (shape factor) [-]
    r = 2 + m - n

    #f.4) calculate eddy diffusivity K [m2/s]
    K = (k * u_star * z) / phi_c

    #f.5) calculate U (constant in power law profile of the wind velocity) [m^(1-m)/s] and kappa (constant in power law profile of the eddy diffusivity) [m^(2-n/m)] (dimensions not realy working here)
    U = u[t] / z**m
    kappa = K / z**n

    #f.6) calculate xi (flux length scale) [m]
    xi = (U * z**r) / (r**2 * kappa)

    #f.7) calculate mu (constant) [-]
    mu = (1 + m) / r

    #f.8) calculate u_plume (effective plume velocity) [m/s]
    u_plume[idx] = gamma(mu) / gamma(1/r) * (r**2 * kappa / U)**(m/r) * U * FP_x[idx]**(m/r)    #others use k instead of kappa and u instead of U

    #f.9) calculate sigma (crosswind dispersion) [m]
    sigma[idx] = np.sqrt(var_v[t]) * FP_x[idx] / u_plume[idx]

    #f.10) calculate D_y (crosswind distribution) [1/m]
    D_y[idx] = 1 / (np.sqrt(2 * np.pi) * sigma[idx]) * np.exp(-(FP_y[idx]**2 / 2 * sigma[idx]**2))

    #f.11) calculate P_f (crosswind integrated flux footprint)
    P_f[idx] = (1 / gamma(mu)) * ((xi**mu) / (FP_x[idx]**(1 + mu))) * np.exp(- xi / FP_x[idx])

    #f.12) calculate fp (flux footprint) [1/m2]
    fp[idx] = D_y[idx] * P_f[idx]

    #f.13) normalization of the footprint (sum = 1)
    fp_norm = fp/np.sum(fp)

    return fp, FP_east, FP_north, fp_norm
