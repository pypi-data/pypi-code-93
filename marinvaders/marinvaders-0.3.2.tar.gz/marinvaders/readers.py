"""
Utility module for reading different data sources.

Data sources are specified at README.md
"""


import os
from enum import Enum
from pathlib import Path
from typing import Union

import pandas as pd

import geopandas as gpd


def data_path() -> os.path:
    """
    Path to data source files.

    Returns
    -------
    os.path
        Data path
    """
    this_dir, _ = os.path.split(__file__)
    return os.path.join(this_dir, "data")


class ShapeFiles(Enum):
    """
    Enum of shape files directory.
    """

    MEOW_ECOS: os.path = os.path.join("meow_ecos", "meow_ecos.shp")
    EEZ: os.path = os.path.join("eez_low_res", "eez_lr.shp")
    EEZ_IHO_UNION: os.path = os.path.join("EEZ_IHO_union_v2", "EEZ_IHO_union_v2.shp")
    IHO_SEA_AREAS: os.path = os.path.join("IHO Sea Areas", "World_Seas_IHO_v3.shp")


def read_shapefile(shape_name: ShapeFiles) -> gpd.GeoDataFrame:
    """
    Read shapefiles.

    Parameters
    ----------
    shape_name
        name of the shapefile defined in ShapeFile class

    Returns
    -------
    GeoPandas
        Shapefile data
    """
    gdf = gpd.read_file(os.path.join(data_path(), shape_name.value))

    if shape_name == ShapeFiles.MEOW_ECOS:
        for colname in ["ECO_CODE", "PROV_CODE", "RLM_CODE", "ALT_CODE", "ECO_CODE_X"]:
            gdf[colname] = gdf[colname].astype("int")
    else:
        gdf["MRGID"] = gdf["MRGID"].astype("int")

    return gdf


def read_gisd_worms_link() -> pd.DataFrame:
    """
    Reads GISD and WoRMS qualitative distribution linked to MEOW.

    Returns
    -------
    pd.DataFrame
        Distribution links
    """
    df = pd.read_excel(
        os.path.join(
            data_path(),
            "GISD_and_WoRMS_qualitative_distributions_linked_to_MEOWs.xlsx",
        ),
        skiprows=5,
        engine="openpyxl",
    )
    df["ECO_CODE_X"] = df["ECO_CODE_X"].str.replace(".", ",", regex=False)

    return df


def read_natcon() -> pd.DataFrame:
    """
    Reads NatCon dataset.

    Returns
    -------
    pd.DataFrame
        Natcon data
    """
    df = pd.read_csv(
        os.path.join(data_path(), "NatConAddAphiaID_FV.csv"),
    )
    df = df.dropna(subset=["aphiaID"])
    return df


def read_gisd(gisd_file: Path) -> pd.DataFrame:
    """
    Reads GISD dataset.

    Parameters
    ----------
    gisd_file: pathlib.Path
        Location of the JSON file containing the gisd data

    Returns
    -------
    pd.DataFrame
        GISD data
    """
    try:
        df = pd.read_json(gisd_file)
    except ValueError as e:
        raise ValueError(f"Error reading the gisd data from {gisd_file} : {e}")

    df.rename(columns={"Species": "species"}, inplace=True)

    return df


def eco_mrgid_link() -> pd.DataFrame:
    """
    Reads ECO regions code from MEOW merged with other shapefiles.
    This file maps ECO regions code wit MRGID

    Returns
    -------
    pd.DataFrame
        eco-region code linked to MRGID
    """
    df = pd.read_hdf(os.path.join(data_path(), "eco_mrgid.h5"))
    df.loc[:, "MRGID"] = df["MRGID"].astype("int64")

    return df


def read_redlist(redlist_file: Union[str, Path]) -> pd.DataFrame:
    """
    Reads redlist data which describes species affected by invasive species.

    Note
    ----
    Depends on redlist data from IUCN which needs to be downloaded manually
    from https://www.iucnredlist.org/search .  See also the documentation
    at https://marinvaders.gitlab.io/marinvaders/iucn_data/


    Parameters
    -----------
    redlist_file: str or pathlib.Path
        Manually downloaded search results from IUCN (assessment.csv)

    Returns
    -------
    Pandas DataFrame
        Affected species
    """
    df = pd.read_csv(redlist_file, usecols=["scientificName"]).rename(
        columns={"scientificName": "species"}
    )

    return df
