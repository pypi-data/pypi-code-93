#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 10:43:15 2021

@author: mike
"""
import requests
import orjson
import copy

##########################################
### Functions


def query_esri_mapserver(base_url, layer_id, out_fields=None, where=None):
    """
    Query an ESRI map server for a vector layer and return a geojson structured dict.

    Parameters
    ----------
    base_url : str
        The base url for the map server up to the layer_id.
    layer_id : str or int
        The layer id.
    out_fields : None or list of str
        The output fields to be returned. The geometry will always be returned. None will return all fields.
    where : None or str
        The SQL style 'where' clause to query the layer. None will have no filters.

    Returns
    -------
    Dict
        In GeoJSON structure
    """
    url = base_url + str(layer_id) + '/query'

    ## Set up filters
    params = {'returnGeometry': 'true', 'f': 'geojson'}

    if out_fields is None:
        params.update({'outFields': '*'})
    elif isinstance(out_fields, list):
        out_str = ', '.join(out_fields)
        params.update({'outFields': out_str})
    else:
        raise ValueError('out_fields must either be None or a list of strings')

    if where is None:
        params.update({'where': '1=1'})
    elif isinstance(where, str):
        params.update({'where': where})
    else:
        raise ValueError('where must either be None or a string')

    ## Run the queries
    resp = requests.get(url, params=params)

    if not resp.ok:
        raise ValueError(resp.raise_for_status())

    data = orjson.loads(resp.content)

    if 'exceededTransferLimit' in data:
        exceed = data.pop('exceededTransferLimit')
    else:
        exceed = False

    data_all = copy.deepcopy(data)

    while exceed:
        last_id = data['features'][-1]['id']

        if isinstance(where, str):
            params.update({'where': where + 'and objectid > ' + str(last_id)})
        else:
            params.update({'where': 'objectid > ' + str(last_id)})

        resp = requests.get(url, params=params)

        if not resp.ok:
            raise ValueError(resp.raise_for_status())

        data = orjson.loads(resp.content)

        data_all['features'].extend(data['features'])

        if 'exceededTransferLimit' in data:
            exceed = data.pop('exceededTransferLimit')
        else:
            exceed = False

    return data_all































