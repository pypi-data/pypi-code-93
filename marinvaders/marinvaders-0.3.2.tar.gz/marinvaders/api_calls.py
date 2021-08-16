"""
Requests to the web services APIs of OBIS and WORMS

OBIS:   https://api.obis.org/
WoRMS: http://marinespecies.org/rest/
"""

import concurrent.futures
import logging
from typing import List

import numpy as np
import pandas as pd
import requests
import shapely.geometry as sh_geo


def request_obis(eco_code: int = None, aphia_id: int = None) -> pd.DataFrame:
    """
    Query OBIS API either by marine ecoregion code or aphia_id.
    WhenTimeout error occurs the request is repeated 5 times.

    Parameters
    ----------
    eco_code: int
        Marine eco region code
    aphia_id: int
        Species Aphia ID based on WoRMS

    Returns
    -------
    pandas.DataFrame
        Obis data

    Raises
    -------
    NotImplementedError
        If both eco_code and AphiaID is used
    ValueError
        Neither eco_code or AphiaID is used
    RuntimeError
        Anything get wrong during using OBIS API calls

    """
    # Get OBIS species (selected fields) for the selected polygon
    # https://api.obis.org
    size = 10000  # maximum number of records returned per one request
    after = None
    # some areas are too big and the Polygons exceeds character limits
    # in OBIS API and we will get HTTP response code 400 (Bad Request).
    # To fix it we change this flag to True,
    # we make bounding box of the min an max of the area and make new request
    # in the end when we will filter out species which are not in Polygon
    area_too_big = False

    results_dfs = []
    retry_counter = 5  # max number of request retry when Timeout error
    if eco_code and aphia_id:
        logging.error("Either eco_code or aphiaID can be specified. Not both")
        raise NotImplementedError(
            "Either ecocode or aphiaID can be specified." "Not both"
        )

    if eco_code:
        # the import here is because of circular import - marine_life imports
        # this module too.
        # We need only this one method.
        # TODO find better way in order to remove circular import
        from marinvaders.main import marine_ecoregions

        gdf = marine_ecoregions(eco_code=eco_code)
        geometry = gdf.iloc[0]["geometry"]

        def _round_remove_duplicates(array):
            """
            First round the Point from 14 digits after comma to 2 digits to
            prevent long URI which cause error in OBIS API,
            then remove duplicated point which can happen after rounding.
            At lats close the polygon.
            """
            df = pd.DataFrame(np.array(array))
            # rounding to 2 digits after comma. When using 3 digits the URI
            # was still to big for multi-polygon regions.
            df = df.round(2).drop_duplicates()
            retval = list(zip(df.iloc[:, 0], df.iloc[:, 1]))
            # closing polygon
            retval.append(retval[0])
            return retval

        geosjson = sh_geo.mapping(geometry)
        if geosjson["type"] == "MultiPolygon":
            coordinates = []
            for coord in geosjson["coordinates"]:
                res = _round_remove_duplicates(coord[0])
                coordinates.append([res])
            geosjson["coordinates"] = coordinates
        elif geosjson["type"] == "Polygon":
            res = _round_remove_duplicates(geosjson["coordinates"][0])
            geosjson["coordinates"] = [res]
        else:
            raise ValueError(
                "Geometry must be either Polygon or MultiPolygon."
                "Current type is: {}".format(geosjson["type"])
            )
        geometry = sh_geo.shape(geosjson)

        if not geometry.is_valid:
            raise RuntimeError("The geometry is not valid shape object.")
        _val = ("geometry", geometry)
    elif aphia_id:
        _val = ("taxonid", aphia_id)
    else:
        raise ValueError("Either geometry or aphiaID must be specified")

    while True:
        try:
            r = requests.get(
                "https://api.obis.org/v3/occurrence?&{}={}&size={}&after={}".format(
                    _val[0], _val[1], size, after
                )
            )
        except requests.exceptions.HTTPError as e:
            logging.error("HTTPSError: {}".format(e))
            break
        except requests.exceptions.Timeout as e:
            logging.error("Timeout Exception: {}".format(e))
            if retry_counter == 0:
                logging.warning("Tried already 5 times. Quiting")
                break
            logging.info("Retrying obis request")
            retry_counter -= 1
        except Exception as e:
            logging.error(
                "Something went wrong. error: {}, "
                "response code: {}, response text: {}".format(e, r.status_code, r.text)
            )
            break
        else:
            if r.status_code == 200:
                res_json = r.json()
                if not len(res_json["results"]):
                    break
                _data = res_json["results"]
                after = _data[-1]["id"]
                _data = [
                    dict(
                        id=item["id"],
                        aphiaID=item["aphiaID"],
                        species=item["species"],
                        decimalLatitude=item["decimalLatitude"],
                        decimalLongitude=item["decimalLongitude"],
                    )
                    for item in _data
                    if "aphiaID" in item and "species" in item
                ]
                # process only if not empty record is returned from request
                if _data:
                    df = pd.DataFrame.from_dict(_data)
                    df = df.dropna(subset=["species"])
                    df = df[
                        ["aphiaID", "species", "decimalLatitude", "decimalLongitude"]
                    ]
                    results_dfs.append(df)
            elif r.status_code == 400:
                # the geometry of selected area is huge (with a lot fo points)
                # and we need some tricks to deal with it.
                # So first we select bounding box and then we filter out
                # species outside of the origin geometry.
                area_too_big = True
                minx, miny, maxx, maxy = geometry.bounds
                geometry = sh_geo.Polygon(
                    [
                        (minx, miny),
                        (maxx, miny),
                        (maxx, maxy),
                        (minx, maxy),
                        (minx, miny),
                    ]
                )
                _val = ("geometry", geometry)
            else:
                str_val = (
                    "eco_code {}".format(eco_code)
                    if eco_code
                    else "aphiaID: {}".format(aphia_id)
                )
                _msg = "OBIS API for {} returned code: {} - {}".format(
                    str_val, r.status_code, r.text
                )
                raise RuntimeError(_msg)

    if len(results_dfs) == 0:
        raise RuntimeError(
            "No record found in OBIS for species with " "aphia ID: {}".format(aphia_id)
        )

    df_obis = pd.concat(results_dfs, sort=True)
    df_obis["aphiaID"] = df_obis["aphiaID"].fillna(-1)
    df_obis["aphiaID"] = df_obis["aphiaID"].astype("int64")

    df_obis.drop_duplicates(inplace=True)

    if area_too_big:
        geometry = gdf.iloc[0]["geometry"]
        df_obis["is_within_polygon"] = df_obis.apply(
            lambda x: sh_geo.Point(x["decimalLongitude"], x["decimalLatitude"]).within(
                geometry
            ),
            axis=1,
        )
        df_obis = df_obis[df_obis["is_within_polygon"]]
        df_obis = df_obis[["aphiaID", "species", "decimalLatitude", "decimalLongitude"]]

    return df_obis.reset_index()


def _fetch_worms(aphia_id: int) -> pd.DataFrame:
    """
    Helper function to fetch data from WoRMS per one Aphia ID species

    NOTE
    ----
    Exceptions are logged to log file and they do not raise
    Exception because not all species are observed in WoRMS so the program can
    continue without exit.

    Parameters
    ----------
    aphia_id: int
        aphia ID of species

    Returns
    -------
    pandas DataFrame
        Data on the specific species
    """
    r = None
    try:
        r = requests.get(
            "http://marinespecies.org/rest/AphiaDistributionsByAphiaID/{}".format(
                int(aphia_id)
            )
        )
    except Exception as e:
        # no record found for this AphiaID
        if r and r.status_code == 204:
            logging.warning(
                "WoRMS request for AphiaID: {} returned response_"
                "code 204 - "
                "No Content. Exception: {}".format(aphia_id, e)
            )
        else:
            logging.error(
                "WoRMS request Error: AphaID: {}. Exception: {}".format(aphia_id, e)
            )
        return pd.DataFrame()
    else:
        if r and r.status_code == 200:
            logging.info("WoRMS API call SUCCESS for aphia ID: {}".format(aphia_id))
            x = r.json()
            df = pd.DataFrame(x)
            df["aphiaID"] = aphia_id
            return df
        else:
            logging.warning("WoRMS API call failed for AphiID: {}, ".format(aphia_id))
            # returning empty DataFrame will fix error when
            # concatenating them later
            return pd.DataFrame()


def request_worms(aphia_ids: List[int]) -> pd.DataFrame:
    """
    Request call to WoRMS API web service

    NOTE: Exception are logged to log file - marine_invaders.log and passed

    Parameters
    ----------
    aphia_ids: list of int
        aphia IDs of species

    Returns
    -------
    pandas DataFrame
        Worms data
    """
    results_dfs = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {
            executor.submit(_fetch_worms, aphia_id): aphia_id for aphia_id in aphia_ids
        }
        for future in concurrent.futures.as_completed(future_to_url):
            aphia_id = future_to_url[future]
            try:
                data = future.result()
                results_dfs.append(data)
            except Exception as e:
                logging.error("{} generated an exception: {}".format(aphia_id, e))

    try:
        df_worms = pd.concat(results_dfs)
    except Exception as e:
        logging.info("No data found in WoRMS. Exception: {}".format(e))
        return pd.DataFrame()
    else:
        return df_worms
