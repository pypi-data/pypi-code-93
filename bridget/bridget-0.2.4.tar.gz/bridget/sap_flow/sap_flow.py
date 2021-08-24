"""
Sap Flow package
----------------

These functions can be used to process sap flow measurements from different sensors 
and measurement methods in order to to calculate transpiration estimates for 
individual trees and scale up to stands. Method-specific differences exist in 
the calculations from the temperature measurements up to sap velocity or sap 
flux density, whereas subsequent calculations can be applied to all methods. 

"""
import numpy as np

from .util import GEBAUER_FACTORS


def heat_pulse_velocity(temperatures, m_c, rho_b, probe_spacing):
    """Calculate heat pulse velocity from temperature measurements of sensors
    using the heat pulse / heat ratio method.  

    This function calculates the velocity of the inserted heat pulse from 
    the measured temperatures. (or does it?)

    Parameters
    ----------
    temperatures : list, numpy.array
        Array of two coupled temperatures per measurement depth
    m_c : list, numpy.array
        Water content of the wood
    rho_b : list, numpy.array
        Sapwood density
    probe_spacing : int
        Spacing between the temperature probes and the heating 
    

    Returns
    -------
    vh : numpy.array
        Array of heat pulse velocity per measurement depth.  
    t_rise : numpy.array
        timing offset in maximum temperature rise. 
        Will only be returned if ``with_uncertainties=True``.
    var_mc : numpy.array
        variance in m_v
        Will only be returned if ``with_uncertainties=True``.
    var_rho : numpy.array
        variance in rho_b
        Will only be returned if ``with_uncertainties=True``.
    t_diffusivity : numpy.array
        temperature diffusivity
        Will only be returned if ``with_uncertainties=True``.
    
    """
    raise NotImplementedError



def sap_velocity(method='East30_3needle', **kwargs):
    """Sap velocity calculation
    
    Calculate sap velocity according to the specified method or sensor. At the 
    moment only the heat ratio method for a 3-needle sensor by East30 is 
    implemented as an example.     

    """
    raise NotImplementedError


def sap_velocity_heat_ratio(dTu, dTd, method='East30_3needle', **kwargs):
    """
    """
    if method.lower() == 'east30_3needle':
        return _sap_velocity_East30_3needle(dTu, dTd, **kwargs)
    else:
        raise NotImplementedError



def _sap_velocity_East30_3needle(dTu, dTd, ru=0.006, rd=0.006, **kwargs):
    """Sap velocity for East30 Sensor
    
    Calculate sap velocity for East30 3-needle sap flow sensors for two corresponding
    temperature measurements below and above the middle heater needle. 
    Sap velocity (equation (6) page 33 East30 3-needle sap flow sensor manual), last term omitted, in [m/s]

    Parameters
    ----------
    ru, rd : float
        distance from heater to sensor, upstream (ru) and downstream (rd), in [m]
        (upstream corresponds to the needle below the heater, downstream in above the heater, in an assumed upward water movement)
    dTu : list, numpy.array
        time series of temperature differences in [K] at the upstream thermistor (below the heater in an upward water movement), differences are between initial 
        temperature and 60 seconds after heating. 
    dTd : list, numpy.array
        time series of temperature differences in [K] at the downstream thermistor (above the heater in an upward water movement), differences are between initial 
        temperature and 60 seconds after heating.
    
    Keyword Arguments
    -----------------
    k_sapwood : float
        thermal conductivity of sapwood in [W m-1 K-1], 0.5 is a literature value
    Cw : float
        specific heat of water in [J m-3 K-1], 4.1796 J/(cm³ K) at 25°C is a literature value
    force_si : bool
        Defaults to `False`. 

    Returns
    -------
    vs : numpy.array
        Array of sap velocity, here converted to [cm h-1].
    
    """
    # check parameter
    if dTu is None or dTd is None:
        raise ValueError('dTu and dTd need to be a numpy.array.')
    
    # dTu and dTd need the same dimension
    if not len(dTu) == len(dTd):
        raise ValueError('dTu and dTd need to be of same length')
    
#    if len(kwargs.keys()) > 0:
#        print('Got unknown parameter: %s' % ','.join(kwargs.keys()))
    
    # get other parameters
    k_sapwood = kwargs.get('k_sapwood', 0.5)           
    Cw = kwargs.get('Cw', 4.1796 * 1000000)
    
    # calculation of sap velocity 
    vs = 2 * k_sapwood / (Cw * (ru + rd)) * np.log(dTu / dTd)
    
    if kwargs.get('force_si', False):
        # convert [m/s] to [cm/h]
        vs = vs * 100 * 3600

    return vs


def sapwood_area(dbh: float, species: str, sapwood_depth=None, bark_depth=None, **kwargs) -> float:
    """ Sapwood area calculation
    
    This function will calculate the sapwood area, either from measured sapwood
    depth or using the empirical equation from Gebauer et al. (2008). The bark
    depth will be needed for the calculation after Gebauer et al. (2008). This
    can be either a measured value or also empirically calculated. 
    
    Reference: 
    Gebauer, T., Horna, V., and Leuschner, C. (2008). Variability in radial
    sap flux density patterns and sapwood area among seven cooccurring
    temperate broad-leaved tree species, Tree Physiol., 28, 1821–1830.
    
    Parameters
    ----------
    dbh : float
            diameter at breast height in [cm]
    species : str
            species name, can bei either "quercus petraea" or "fagus sylvatica"
            at this point
    sapwood depth : ??
            ??        
    bark_depth : ?? 
            measured bark depth in [mm]
    
    
    
    """
    # get the bark depth parameter
    bark_depth = __estimate_bark_depth(dbh, species, bark_depth)
    
    # check if user has sapwood_depth measurements
    if sapwood_depth is None:
        As = _sapwood_area_gebauer(dbh, species, **kwargs)
    else:
        # As = A_without_bark - A_heartwood
        r_x = (dbh - bark_depth/10) / 2    #TODO: inserted the /10 here -> check!
        A_without_bark = r_x**2 * np.pi
        A_heartwood = (r_x - sapwood_depth)**2 * np.pi
        
        As = A_without_bark - A_heartwood
    
    return As


def _sapwood_area_gebauer(dbh: float, species: str, **kwargs) -> float:
    """
    """
    # TODO: a und b noch aus Literatur bestimmen
    a, b = GEBAUER_FACTORS.get(species)
    As = a * dbh**b
    return As


def __estimate_bark_depth(dbh: float, species: str, bark_depth=None) -> float:
    """Estimation of bark depth
    
    This function calculates double bark depth according to the empirical 
    relation in Rössler (2008), if bark depth was not measured. Currently 
    implemented are the empirical coefficients for Quercus petraea and 
    Fagus sylvatica. 
    
    Reference: 
    Rässler, 2008. Rindenabzug richtig bemessen, Forstzeitung, 4, p. 21.

    Parameters
    ----------
    dbh : float
            diameter at breast height in [cm]
    species : str
            species name, can bei either "quercus petraea" or "fagus sylvatica"
            at this point
    bark_depth : ?? 
            measured bark depth in [mm]

    Returns
    -------
    bark_depth : float
        double bark depth, measured or calculated, in [mm]
        
    """ 
    if bark_depth is None and species is None:
        raise ValueError('You need to specify either the species or the bark depth.')
        
    # check bark_depth
    if bark_depth is not None:
        # TODO ducoment why we do this
        return bark_depth * 2
    
    # translate to latin name
    sp_name = GEBAUER_FACTORS.name_mapping.get(species.lower())

    if sp_name == 'quercus petraea':
        return 9.88855 + 0.56734 * dbh
    
    elif sp_name == 'fagus sylvatica':
        return 2.61029 + 0.28522 * dbh
    
    else:
        print('[Warning]: %s is not supported. Using bark depth of 0.' % species)
        return 0.


def __sap_flow_profile(As, vs, depths, dbh: float, species: str, bark_depth=None, sapwood_depth=None):
    # sapwood area slices
    _As = []
    
    # get the area for each v and depth pair
    for i, (v, depth) in enumerate(zip(vs, depths)):
        _A = sapwood_area(dbh, species, bark_depth=bark_depth, sapwood_depth=depth)
        if i == 0:
            _As.append(_A)
        else:
            _As.append(max(_A - np.sum(_As), 0))

    # last element
    _As[-1] = __estimate_last_chunk(dbh, species, depths[-1], sapwood_depth=sapwood_depth, bark_depth=bark_depth)

    return np.sum(np.array(_As) * vs)


def __estimate_last_chunk(dbh: float, species: str, upper_depth, sapwood_depth=None, bark_depth=None) -> float:
    # get bark depth
    bark_depth = __estimate_bark_depth(dbh, species, bark_depth)
    # TODO: I inserted the /10 to bark depth on 12.8.2021 because we need bark depth in cm -> check!
    r_x = (dbh - bark_depth/10) / 2
    
    #  Use measured sapwood depth or estimate it
    if sapwood_depth is None:
        A_rx = np.pi * r_x**2
        As = _sapwood_area_gebauer(dbh, species)
        Ah = A_rx - As
        r_h = np.sqrt(Ah / np.pi)
    else:
        r_h = r_x - sapwood_depth
    
    # TODO: add a comment what we actually do and why (A4 Renner 2016)
    r = r_x - upper_depth
    A = np.pi * (r**2 - (1 / 3) * r**2 + r * r_h + r_h**2)
    return A


def sap_flow(vs, dbh: float, species: str, depths=None, bark_depth=None, sapwood_depth=None, **kwargs):
    """Calculate sap flow from sap velocity and sapwood area. 

    Calculation of sap flow from sap velocity (profiles) and sapwood area 
    (increments). 

    Parameters
    ----------
    vs : numpy.array, numpy.float64
        Array of (corrected) sap velocity/sap flux density
    dbh : float
        Diameter at breast height in [cm]
    species : str
        species name, can bei either "quercus petraea" or "fagus sylvatica"
        at this point
    bark_depth : float
        Bark depth in [mm]
        

    Returns
    -------
    Q : numpy.array
        sap flow per tree in [litres/h]

    """
    if isinstance(vs, (int, float)):
        vs = np.float64(vs)
    elif isinstance(vs, (list, tuple)):
        vs = np.array(vs)
        edges = kwargs.get('edges')
        # check that depths are there
        if depths is None and edges is None:
            raise ValueError('If more than one velocity is given, you need to specify their depths or the profile edges.')
        if edges is None:
            depths = np.array(depths)
            edges = depths[:-1] + (np.diff(depths) / 2)
        else:
            edges = np.array(edges)
    
    # calculate the area first
    As = sapwood_area(dbh, species, bark_depth=bark_depth, sapwood_depth=sapwood_depth, **kwargs)
    
    # check inpiut dimnesionality
    if vs.size == 1:
        return As * vs    
    else:
        return __sap_flow_profile(As, vs, edges, dbh, species, bark_depth=bark_depth, sapwood_depth=sapwood_depth)
