"""
Utiltiy module for finding observation for species.

The species reported by OBIS are used to search in WoRMS, GISD and NatCon
observations sources and are merged if record was found as a alien means.
"""

import logging
from typing import Union

import numpy as np
import pandas as pd


from pathlib import Path

from marinvaders.api_calls import request_worms
from marinvaders.readers import (
    ShapeFiles,
    eco_mrgid_link,
    read_gisd,
    read_gisd_worms_link,
    read_natcon,
    read_shapefile,
)


def observations(
    obis: pd.DataFrame, species: bool = False, gisd_file: Union[str, Path] = None
) -> pd.DataFrame:
    """
    Get the data from the available data sources.

    Currently this obtains data from worms, natcon and GISD (optional)

    Parameters
    ----------
    obis: pd.DataFrame
        DataFrame of species from obis to be searched for
    species: bool
        Flag used for NatCon source.
        If False then it returns all NatCon data and the obis parameter is omitted.
        If True the NatCon returns only subset specified in obis parameter.
    gisd_file: str or pathlib.Path, optional
        Location of the GISD data file (in json format)

    Returns
    -------
    pd.DataFrame
        DataFrame with all data but with dropped duplicates.

    """
    logging.info("Processing observations.")

    # When processing region (species==False) the NatCon can add few
    # more species to OBIS species. Even they are aliens the
    # GISD and Worms can add more regions then.
    # Therefor we need to run NatCon first, append species and run the rest.
    if species:
        natcon_obs = natcon(obis)
    else:
        natcon_obs = natcon()
        # sanity check, only one region allowed
        assert (
            obis["ECO_CODE"] == obis["ECO_CODE"].iloc[0]
        ).all(), "Multiple regions are not allowed here!"
        natcon_obs["ECO_CODE"] = obis["ECO_CODE"].iloc[0]
        obis = pd.concat([obis, natcon_obs[["aphiaID", "species", "ECO_CODE"]]])
        obis.loc[:, "ECO_CODE"] = obis["ECO_CODE"].astype("int64")

    worms_obs = worms(obis)

    if gisd_file:
        gisd_obs = gisd(obis, gisd_file=gisd_file)
    else:
        gisd_obs = pd.DataFrame()

    if all([worms_obs.empty, gisd_obs.empty, natcon_obs.empty]):
        return pd.DataFrame()
    result = pd.concat([worms_obs, gisd_obs, natcon_obs], sort=True).reset_index(
        drop=True
    )

    # add ECO_CODE column to result
    df_eco_mrgid = eco_mrgid_link()
    result.loc[:, "ECO_CODE"] = result["ECO_CODE_X"].apply(
        lambda x: df_eco_mrgid[df_eco_mrgid["ECO_CODE_X"] == x].iloc[0]["ECO_CODE"]
    )
    result.drop_duplicates(
        subset=["ECO_CODE_X", "aphiaID", "establishmentMeans", "dataset"], inplace=True
    )
    result.loc[:, "ECO_CODE"] = result["ECO_CODE"].astype("int64")

    result = result[result["establishmentMeans"] == "Alien"].reset_index(drop=True)
    datasets = result.groupby(
        ["ECO_CODE_X", "aphiaID", "establishmentMeans", "species", "ECO_CODE"],
        as_index=False,
    )["dataset"].agg({"dataset": lambda x: ",".join(x)})
    result = datasets.merge(
        result,
        how="left",
        on=["ECO_CODE_X", "aphiaID", "establishmentMeans", "species", "ECO_CODE"],
    )
    result = result.drop(["dataset_y"], axis=1)
    result = result.rename(columns={"dataset_x": "dataset"})
    result.loc[:, "ECO_CODE"] = result["ECO_CODE"].astype("int64")
    result.loc[:, "aphiaID"] = result["aphiaID"].astype("int64")

    result.drop_duplicates(subset=["ECO_CODE_X", "aphiaID", "dataset"], inplace=True)

    return result


def worms(obis: pd.DataFrame) -> pd.DataFrame:
    """
    Process WoRMS observations for the specified species.

    Returns
    -------
    pandas.DataFrame
        Worms data
    """
    logging.info("Processing WoRMS")
    df_worms = request_worms(obis["aphiaID"].unique())
    if df_worms.empty:
        return pd.DataFrame()

    df_worms.loc[:, "MRGID"] = df_worms["locationID"].apply(
        lambda x: int(x.split("/")[-1])
    )

    df_worms.drop(
        [
            "decimalLatitude",
            "decimalLongitude",
            "higherGeography",
            "higherGeographyID",
            "locality",
            "locationID",
            "qualityStatus",
            "recordStatus",
            "typeStatus",
        ],
        axis=1,
        inplace=True,
    )
    df_worms = pd.merge(df_worms, obis, on=["aphiaID"])
    df_worms.drop_duplicates(inplace=True)

    # link with mrgid using manual xlsx file
    link_df = read_gisd_worms_link()
    link_df.dropna(subset=["MRGID"], inplace=True)
    link_df.loc[:, "MRGID"] = link_df["MRGID"].astype("int64")

    link_df.loc[:, "ECO_CODE_X"] = link_df["ECO_CODE_X"].astype("str")
    df_split = pd.concat(
        [
            pd.Series(row["MRGID"], row["ECO_CODE_X"].split(","))
            for _, row in link_df.iterrows()
        ]
    ).reset_index()
    df_split.columns = ["ECO_CODE", "MRGID"]

    df_all = link_df.merge(df_split, on="MRGID")
    df_all.drop(["ECO_CODE_X"], axis=1, inplace=True)

    link_manfile = df_all[(df_all["Source"] == "WoRMS") & (df_all["Shapefile"] == 0)]
    link_manfile = link_manfile[["MRGID", "ECO_CODE"]]
    link_manfile.loc[:, "MRGID"] = link_manfile["MRGID"].astype(int)

    df_worms_link_man = df_worms.merge(link_manfile, on="MRGID")
    df_worms_link_man.drop("ECO_CODE_x", axis=1, inplace=True)
    df_worms_link_man.loc[:, "ECO_CODE"] = df_worms_link_man["ECO_CODE_y"]
    df_worms_link_man.drop("ECO_CODE_y", axis=1, inplace=True)
    df_worms_link_man.replace("nan", np.nan, inplace=True)
    df_worms_link_man["ECO_CODE"].replace("-", np.nan, inplace=True)
    df_worms_link_man.dropna(subset=["ECO_CODE"], inplace=True)
    df_worms_link_man.loc[:, "ECO_CODE"] = df_worms_link_man["ECO_CODE"].astype("int64")

    df_meow = pd.DataFrame(read_shapefile(ShapeFiles.MEOW_ECOS))
    df_meow = df_meow[["ECO_CODE_X", "ECOREGION", "geometry"]]
    df_meow.loc[:, "ECO_CODE"] = df_meow["ECO_CODE_X"]
    df_meow.drop("ECO_CODE_X", axis=1, inplace=True)
    df_meow.loc[:, "ECO_CODE"] = df_meow["ECO_CODE"].astype("int64")
    df_worms_link_man = df_worms_link_man.merge(df_meow, on="ECO_CODE")

    # link with mrgid using other shapefiles
    df_eco_mrgid = eco_mrgid_link()
    df_worms_link_aut = df_worms.merge(df_eco_mrgid, on="MRGID")
    df_worms_link_aut.drop("ECO_CODE_x", axis=1, inplace=True)
    df_worms_link_aut.loc[:, "ECO_CODE"] = df_worms_link_aut["ECO_CODE_y"].apply(
        lambda x: df_eco_mrgid[df_eco_mrgid["ECO_CODE"] == x].iloc[0]["ECO_CODE_X"]
    )
    df_worms_link_aut.drop("ECO_CODE_y", axis=1, inplace=True)
    df_worms_link_aut = df_worms_link_aut[
        [
            "MRGID",
            "ECO_CODE",
            "ECOREGION",
            "geometry",
            "establishmentMeans",
            "aphiaID",
            "species",
        ]
    ]

    df_res = pd.concat([df_worms_link_man, df_worms_link_aut], sort=True)
    df_res.drop_duplicates(subset=df_res.columns.difference(["geometry"]), inplace=True)

    df_res.loc[:, "ECO_CODE_X"] = df_res["ECO_CODE"]
    df_res.drop("ECO_CODE", axis=1, inplace=True)
    df_res.loc[:, "dataset"] = "WoRMS"

    assert df_res[
        df_res["establishmentMeans"].isin(["", "Alien"])
    ].all, "WoRMS result establishmentMeans can be only '' or 'Alien'"

    return df_res


def gisd(obis: pd.DataFrame, gisd_file: Path) -> pd.DataFrame:
    """
    Process observations from GISD source.

    Parameters
    ----------
    obis: pd.DataFrame

    gisd_file: Path
        JSON file containing the gisd data

    Returns
    -------
    pandas.DataFrame
        GISD data
    """
    logging.info("Processing GISD")
    gisd_df = read_gisd(gisd_file)
    merged = obis.drop_duplicates(["aphiaID"]).merge(gisd_df, on="species", how="inner")
    xls = read_gisd_worms_link()
    eco_mrgi = eco_mrgid_link()
    eco_mrgi["MarRegion"].fillna("", inplace=True)
    alien = []
    for row in merged.iterrows():
        alien_locations = row[1]["alien_range"]
        for alien_loc in alien_locations:
            distr = xls[xls["Distribution"].str.contains(alien_loc["name"], case=False)]
            auto_eez_iho = eco_mrgi[
                pd.notna(eco_mrgi["MarRegion"])
                & eco_mrgi["MarRegion"].str.contains(alien_loc["name"], case=False)
            ]
            auto_eez = eco_mrgi[
                pd.notna(eco_mrgi["Territory1"])
                & eco_mrgi["Territory1"].str.contains(alien_loc["name"], case=False)
            ]
            auto_iho = eco_mrgi[
                pd.notna(eco_mrgi["NAME"])
                & eco_mrgi["NAME"].str.contains(alien_loc["name"], case=False)
            ]
            res_tmp = pd.concat([distr, auto_iho, auto_eez, auto_eez_iho], sort=True)
            res_tmp["location"] = alien_loc["name"]
            res_tmp["aphiaID"] = row[1]["aphiaID"]
            res_tmp["ECO_CODE"] = row[1]["ECO_CODE"]
            res_tmp["species"] = row[1]["species"]
            if not res_tmp.empty:
                alien.append(res_tmp)

    if not len(alien):
        return pd.DataFrame()
    alien = pd.concat(alien)
    alien["establishmentMeans"] = "Alien"
    alien["dataset"] = "GISD"
    alien = alien[["aphiaID", "species", "establishmentMeans", "MRGID", "dataset"]]
    eco_mrgi = eco_mrgi[["ECOREGION", "ECO_CODE_X", "MRGID", "geometry"]]

    alien = alien.merge(eco_mrgi, on="MRGID", how="left")
    alien = alien.dropna(subset=["ECO_CODE_X"])

    return alien


def natcon(obis: pd.DataFrame = None) -> pd.DataFrame:
    """
    Process observations for alien range from NatCon source.

    Returns
    -------
    pandas.DataFrame
        Natcon data
    """
    logging.info("Processing NatCon")
    natcon = read_natcon()
    natcon.loc[:, "species"] = natcon["SPECIES_NAME"]
    natcon = natcon.loc[:, ["aphiaID", "species", "ECOREGION", "ECO_CODE_X"]]
    natcon.loc[:, "establishmentMeans"] = "Alien"
    natcon.loc[:, "dataset"] = "NatCon"

    if obis is not None:
        natcon = natcon[natcon["aphiaID"].isin(obis["aphiaID"])]

    map_eco_mrgid = eco_mrgid_link()
    map_eco_mrgid = map_eco_mrgid[["MRGID", "ECO_CODE_X", "geometry"]]

    result = natcon.merge(map_eco_mrgid, on="ECO_CODE_X")

    return result
