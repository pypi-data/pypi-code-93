from collections import defaultdict
import time

import pandas as pd

from shapely.geometry import Point

import geopandas

def _get_throttle_time(provider):
    """
    Amount of time to wait between requests to a geocoding API, for providers
    that specify rate limits in their terms of service.
    """
    import geopy.geocoders

    # https://operations.osmfoundation.org/policies/nominatim/
    if provider == geopy.geocoders.Nominatim:
        return 1
    else:
        return 0

def geocode(strings,config, provider=None,**geocode_config):
    """
    Geocode a set of strings and get a GeoDataFrame of the resulting points.
    Parameters
    ----------
    strings : list or Series of addresses to geocode
    provider : str or geopy.geocoder
        Specifies geocoding service to use. If none is provided,
        will use 'photon' (see the Photon's terms of service at:
        https://photon.komoot.io).
        Either the string name used by geopy (as specified in
        geopy.geocoders.SERVICE_TO_GEOCODER) or a geopy Geocoder instance
        (e.g., geopy.geocoders.Photon) may be used.
        Some providers require additional arguments such as access keys
        See each geocoder's specific parameters in geopy.geocoders
    Notes
    -----
    Ensure proper use of the results by consulting the Terms of Service for
    your provider.
    Geocoding requires geopy. Install it using 'pip install geopy'. See also
    https://github.com/geopy/geopy
    """

    if provider is None:
        provider = "photon"
    throttle_time = _get_throttle_time(provider)

    return _query(strings, provider,config,throttle_time, **geocode_config)

def _query(data, provider, config,throttle_time, **geocode_config):
    # generic wrapper for calls over lists to geopy Geocoders
    from geopy.geocoders.base import GeocoderQueryError
    from geopy.geocoders import get_geocoder_for_service

    if not isinstance(data, pd.Series):
        data = pd.Series(data)

    if isinstance(provider, str):
        _provider = get_geocoder_for_service(provider)

    coder = _provider(**config)
    results = {}

    for i, s in data.items():
        try:
            results[i] = coder.geocode(s,**geocode_config)
        except (GeocoderQueryError, ValueError):
            results[i] = (None, None)
        time.sleep(throttle_time)

    df = _prepare_geocode_result(results,provider,data)
    return df

def _prepare_geocode_result(results,provider,data):
    """
    Helper function for the geocode function
    Takes a dict where keys are index entries, values are tuples containing:
    (address, (lat, lon))
    """
    # Prepare the data for the DataFrame as a dict of lists
    d = defaultdict(list)
    index = []

    for i, s in results.items():

        if s is None:
            p = Point()
            address = None

        else:
            address = s.address
            lat = s.latitude
            long = s.longitude
            raw = s.raw

            # loc is lat, lon and we want lon, lat
            if lat and long is None:
                p = Point()
            else:
                p = Point(long, lat)
        d['GeoAPI'].append(provider)
        d["geometry"].append(p)
        d["address"].append(address)
        index.append(i)

    df = geopandas.GeoDataFrame(d, index=index, crs="EPSG:4326")
    df = pd.concat([df,data],axis=1)
    return df


    