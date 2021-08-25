#!/usr/bin/env python

import numpy as np
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
import astropy.units as u


def parangle(ra, dec, utdate, uttime, site, verbose=False):
    """
    Compute the parallactic angle of a position at a given date-time.
    Based on parangle.pro by Tim Robishaw
    Bryan Miller

    Parameters
        ra:         RA of base position [sexigesimal string]
        dec:        Dec of base position [sexigesimal string]
        site:       Observation site, from EarthLocation.get_site_names()
        utdate:     UT date for parallactic angle calculations (YYYY-MM-DD)
        uttime:     UT time for parallactic angle calculations (HH:MM:SS)
        verbose:    Verbose output?
    Returns
        parang [deg]
    """
    # degrees per radian
    degrad = 180. * u.deg /(np.pi * u.rad)

    l_ra = ra.strip()
    l_dec = dec.strip()
    if '-' not in l_dec and l_dec[0] != '+':
        l_dec = '+' + l_dec

    # Coordinate object
    coord = SkyCoord(l_ra,l_dec,frame='icrs',unit = (u.hr, u.deg))

    # Observation time
    obs_time = Time(utdate + 'T' + uttime, format='isot', scale='utc')

    # Location
    location = EarthLocation.of_site(site)
    if verbose:
        print('Site: ', location)

    altaz = coord.transform_to(AltAz(obstime=obs_time, location=location))
    if verbose:
        print('Alt/Az: ', altaz.alt.deg, altaz.az.deg)

    # Hour angle
    ha = np.arcsin(-np.sin(altaz.az) * np.cos(altaz.alt) / np.cos(coord.dec))
    if verbose:
        print('HA: ', ha)

    # Parallactic angle
    parang = -degrad * np.arctan2(-np.sin(ha),
                                  np.cos(coord.dec) * np.tan(location.lat) - np.sin(coord.dec) * np.cos(ha))

    return parang
