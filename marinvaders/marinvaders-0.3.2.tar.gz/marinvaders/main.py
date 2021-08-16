"""
MarINvaders: Full/alien species distributions for a single species or a whole ecoregion.

The is the entry point to the marINvaders code base providing the to top-level
classes:

- Species
- MarinLife

For both, the algorithm collects species data from OBIS and connect to
distribution of the species
using WoRMS, NatCon and (optional) IUCN data sources. It uses geo-spatial
regions
based on MEOW ECOS merged with MRGID (used by WoRMS source) from different
shape-files.

More about data processing can be found at README.md and documentation
(https://marinvaders.gitlab.io/marinvaders/)
"""


import logging
import warnings
from typing import List, Union
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import shapely.geometry as sh_geo
from matplotlib.patches import Polygon

import geopandas as gpd
import numpy as np
from marinvaders.api_calls import request_obis
from marinvaders.alien_observation import observations
from marinvaders.readers import ShapeFiles, read_shapefile, read_redlist

# ignoring UserWarnings when using str.contains in Species.gisd() method
warnings.filterwarnings("ignore", "This pattern has match groups")
warnings.filterwarnings("ignore", "Geometry column does not contain geometry")

log_filename = "marinvaders.log"
handlers = [logging.FileHandler(log_filename)]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)-8s " "[%(filename)s:%(lineno)d]  %(message)s",
    handlers=handlers,
)

PUBLIC_HEADERS = [
    "aphiaID",
    "species",
    "ECOREGION",
    "ECO_CODE",
    "establishmentMeans",
    "dataset",
    "geometry",
]


def marine_ecoregions(**kwargs) -> gpd.GeoDataFrame:
    """
    Filter meow eco-regions using keywords arguments selectors.

    Note
    ----
    The values of selectors are processed as regexp.

    Parameters
    ----------
    kwargs:
        Selectors to filter using regexp.
        The selectors as a kwargs keys are:

            - ECO_CODE int or list of int
            - ECOREGION
            - PROVINCE
            - REALM

    Returns
    -------
    geoPandas
        Information on all selected eco-regions

    """

    meow_gpd = read_shapefile(ShapeFiles.MEOW_ECOS)

    for param in kwargs.items():
        # remove null
        colname = param[0].upper()
        if colname == "ECO_CODE":
            eco_codes = param[1]
            if isinstance(eco_codes, int):
                eco_codes = (eco_codes,)
            meow_gpd = meow_gpd[meow_gpd[colname].isin(eco_codes)]
        else:
            meow_gpd = meow_gpd[meow_gpd[colname].notnull()]
            meow_gpd = meow_gpd[meow_gpd[colname].str.contains(param[1], regex=True)]
        meow_gpd = meow_gpd.reset_index(drop=True)

    return meow_gpd[
        ["ECO_CODE", "ECO_CODE_X", "ECOREGION", "PROVINCE", "REALM", "geometry"]
    ]


def _get_obis(eco_code: int = None, aphia_id: int = None) -> pd.DataFrame:
    """
    Get OBIS species either for the selected eco-code from MEOW  or Aphia ID.
    Using both is currently not implemented.

    Parameters
    ----------
    eco_code: int
        Eco code of MEOW eco-region
    aphia_id: int
        Aphia ID of species

    Returns
    -------
    pandas.DataFrame
        Species information from the obis database

    Raises
    ------
    NotImplementedError
        When both arguments eco_code and aphia_id are used
    ValueError
        when both arguments are none

    """
    if eco_code and aphia_id:
        raise NotImplementedError(
            "Currently either geometry or aphiaID can " "be specified. Not both"
        )

    if eco_code:
        df_obis = request_obis(eco_code=eco_code)
    elif aphia_id:
        df_obis = request_obis(aphia_id=aphia_id)
    else:
        raise ValueError("Either eco_code or aphiaID must be specified")

    df_obis["ECO_CODE"] = eco_code

    return df_obis


class Species:
    """
    Class representing a single species.

    Attributes
    ----------
    aphia_id: int
        Aphia ID of species (using WoRMS classification).
    reported_as_alien: pandas.DataFrame (property)
        Marine eco-regions where the species is reported as alien
        based on WoRMS, NatCon and GISD (optional) sources
    all_occurrences: pandas.DataFrame (property)
        All eco-regions which report presence of the species.
    _obis: pandas.DataFrame
        Result from OBIS API request for this species
    """

    def __init__(self, aphia_id: Union[int, str], gisd_file: Union[str, Path] = None):
        """
        Class init method

        Parameters
        ----------
        aphia_id: int or str
            Species AphiaID (from WoRMS or OBIS).
            This can either be the AphiaID integer or the whole URI string
            ('urn:lsid:marinespecies.org:taxname:XXXXXX'), in which case the
            integer XXXXXX will be extracted and used

        gisd_file: pathlib.Path or str, optional
            The path to the gisd data json file.

        Raises
        ------
        RuntimeError
            When no record found in OBIS for the aphia ID of species
        """

        if type(aphia_id) == str:
            aphia_id = int(aphia_id.split(":")[-1])
        self.aphia_id: int = aphia_id
        self._obis: pd.DataFrame = _get_obis(aphia_id=aphia_id)
        if self._obis.empty:
            raise RuntimeError(
                "No record found in OBIS for species with "
                "aphia ID: {}".format(aphia_id)
            )
        self.all_occurrences: pd.DataFrame = self._create_all_occurrences(
            gisd_file=gisd_file
        )[PUBLIC_HEADERS]

        self.reported_as_alien: pd.DataFrame = self.all_occurrences[
            self.all_occurrences.establishmentMeans == "Alien"
        ]

    def _create_all_occurrences(
        self, gisd_file: Union[str, Path] = None
    ) -> pd.DataFrame:
        """
        Private method which runs during instance init.
        Reports all occurrences of a given species.

        Returns
        -------
        pd.DataFrame
            table of all observations
        """

        df = pd.concat(
            [
                self._obis,
                observations(self._obis.iloc[0:1], gisd_file=gisd_file, species=True),
            ]
        )

        ecoregions = marine_ecoregions()

        def map_point_to_polygon(polygon, ecocode, ecoregion, lon, lat):
            """Check if a given point (lon, lat) within polygon"""
            p = sh_geo.Point(lon, lat)
            if p.within(polygon):
                return polygon, ecocode, ecoregion
            return None, None, None

        # Check for each ecoregion if a given observation is within that
        # ecoregion
        for _, row in ecoregions.iterrows():
            ra, rb, rc = zip(
                *df.apply(
                    lambda x: map_point_to_polygon(
                        row["geometry"],
                        row["ECO_CODE"],
                        row["ECOREGION"],
                        x["decimalLongitude"],
                        x["decimalLatitude"],
                    )
                    if "geometry" not in df.columns or pd.isna(x["geometry"])
                    else (x["geometry"], x["ECO_CODE"], x["ECOREGION"]),
                    axis=1,
                )
            )
            # need to assign to object type to avoid deprecation warning
            df["geometry"], df["ECO_CODE"], df["ECOREGION"] = (
                np.array(ra, dtype=object),
                np.array(rb, dtype=object),
                np.array(rc, dtype=object),
            )
        df = df[df["ECO_CODE"].notna()]
        df = df.sort_values(by=["establishmentMeans"], na_position="last")
        df.drop_duplicates("ECO_CODE", inplace=True, keep="first")
        df["ECO_CODE"] = df["ECO_CODE"].astype("int64")
        df = df.drop(["index"], axis=1)

        return df

    def plot(self, show: bool = True):
        """
        Plot species object.

        Parameters
        ----------
        show: boolean, optional
            If true, calls plt.show() to show the figure (default).

        Returns
        -------
        matplotlib plot figure
        """
        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        fig, _ = plt.subplots(1, 1, sharey=True, figsize=(20, 30))
        fig.suptitle(
            "Observations of {}".format(self._obis.species.iloc[0]), fontsize=24
        )

        ax1 = plt.subplot(3, 1, 1)
        ax1.set_aspect("equal")
        world.plot(ax=ax1, color="white", edgecolor="black")
        polys = []
        for item in self.all_occurrences.iterrows():
            try:
                if type(item[1]["geometry"]) == sh_geo.MultiPolygon:
                    polys.extend(list(sh_geo.MultiPolygon(item[1]["geometry"])))
                else:
                    polys.append(sh_geo.Polygon(item[1]["geometry"]))
            except Exception as e:
                logging.error(e)
        for poly in polys:
            coords = poly
            x, y = coords.exterior.coords.xy
            x = x.tolist()
            y = y.tolist()
            xym = list(zip(x, y))
            m_poly = Polygon(
                xym, facecolor="green", edgecolor="green", linewidth=1, alpha=0.3
            )
            plt.gca().add_patch(m_poly)
        ax1.set_title(
            "Distribution of {} (from OBIS database)".format(self._obis.species.iloc[0])
        )

        ax2 = plt.subplot(3, 1, 2)
        ax2.set_aspect("equal")
        world.plot(ax=ax2, color="white", edgecolor="black")
        polys = []
        for item in self.reported_as_alien.iterrows():
            try:
                if type(item[1]["geometry"]) == sh_geo.MultiPolygon:
                    polys.extend(list(sh_geo.MultiPolygon(item[1]["geometry"])))
                else:
                    polys.append(sh_geo.Polygon(item[1]["geometry"]))
            except Exception as e:
                logging.error(e)
        for poly in polys:
            coords = poly
            x, y = coords.exterior.coords.xy
            x = x.tolist()
            y = y.tolist()
            xym = list(zip(x, y))
            m_poly = Polygon(
                xym, facecolor="red", edgecolor="red", linewidth=1, alpha=0.7
            )
            plt.gca().add_patch(m_poly)
        ax2.set_title("Alien distribution of {}".format(self._obis.species.iloc[0]))

        if show:
            plt.show()

        return fig


class MarineLife(object):
    """
    Class representing the marine life in selected MEOW eco-region.

    It finds which species present, which are aliens, and find all
    observations of the alien species in other eco regions based on
    OBIS source.

    Attributes
    ----------
    eco_code: int
        MEOW eco code of the selected region
    aliens: pandas.DataFrame (property)
        All alien species in teh eco-region
    all_species: pandas.DataFrame (property)
        All species present in the eco-region
    _obis: pandas.DataFrame
        Obis reports of species for this region.
    _alien_observations: pandas.DataFrame
        Observations of all species reported as alien
    """

    def __init__(
        self,
        eco_code: int,
        gisd_file: Union[str, Path] = None,
        redlist_file: Union[str, Path] = None,
    ):
        """
        Class init method.

        Parameters
        ----------
        eco_code: int
            Eco code of MEOW eco region.

        gisd_file: pathlib.Path or str, optional
            The path to the gisd data json file.

        redlist_file: pathlib.Path or str, optional
            The path to the redlist assessments.csv file.

        """
        self.eco_code: int = eco_code
        # All species from obis which are present in the selected eco-region
        self._obis: pd.DataFrame = _get_obis(eco_code=eco_code)
        # All species in other db (WoRMs, GISD, NatCon)
        self._alien_observations: pd.DataFrame = observations(
            self._obis, gisd_file=gisd_file
        )
        self.specify_redlist_data(redlist_file=redlist_file)

    def specify_redlist_data(
        self,
        redlist_file: Union[str, Path],
        result_attribute_name: str = "affected_by_invasive",
    ):
        """Specify location of the red list data file (assessments.csv)

        The redlist data should contain a list of species affected by invasive
        species (see documentation on how to obtain this list from the IUCN
        webpage).

        The species data is then crossreferenced against the species found in
        the eco-region.
        A list of all species affected by invasive species in this eco-region
        is then available
        in the attribute specified in the parameter 'result_attribute_name'
        ('affected_by_invasive' by default).

        Parameters
        ----------
        redlist_file: pathlib.Path or str
            The path to the redlist assessments.csv file.
            If set to None, the previously read redlist data will be removed and the result attribute
            will no longer be available.

        result_attribute_name: str, optional
            Result attribute name

        """
        if not redlist_file:
            try:
                delattr(self, result_attribute_name)
            except AttributeError:
                pass
        else:
            affected = read_redlist(redlist_file)
            result = pd.merge(self.all_species, affected, on="species", how="inner")[
                ["species", "aphiaID"]
            ].drop_duplicates()
            self.__setattr__(result_attribute_name, result)

    @property
    def alien_species(self) -> pd.DataFrame:
        """
        Return aliens species in currently selected eco-region.

        Returns
        -------
        pd.DataFrame
            aliens species
        """
        return self._alien_observations[
            self._alien_observations["ECO_CODE"] == self.eco_code
        ].reset_index(drop=True)

    @property
    def all_species(self) -> List[str]:
        """
        List of all unique species.

        Returns
        -------
        list
            species names
        """
        df_alien_observations = self._alien_observations[
            self._alien_observations["ECO_CODE"] == self.eco_code
        ].reset_index(drop=True)
        df_obis = self._obis[self._obis["ECO_CODE"] == self.eco_code].reset_index(
            drop=True
        )

        df_merged = pd.concat([df_alien_observations, df_obis]).sort_values(
            by=["establishmentMeans"], na_position="last"
        )
        df_merged.drop_duplicates("aphiaID", inplace=True, keep="first")

        return df_merged[PUBLIC_HEADERS]


def plot(eco_code, show: bool = True):
    """
    Plot world map with selected MEOW eco region

    Parameters
    ----------
    eco_code: int or Species obj
        If int is set as eco_code the plot will try to get eco region from
        MEOW and plot it. If no eco region is found for the int eco_code
        the function will raise ValueError.

    show: boolean, optional
        If true, calls plt.show() to show the figure (default).


    Returns
    ---------
    matplotlib plot figure

    Raises:
    -------
    Value Error
        When eco-region for the eco_code was not found.
    """

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    fig, ax = plt.subplots(figsize=(20, 30))
    ax.set_aspect("equal")
    world.plot(ax=ax, color="white", edgecolor="black")

    gdf = marine_ecoregions(eco_code=eco_code)
    if gdf.empty:
        raise ValueError(
            "Seems like the eco region should be plotted but "
            "no eco region found for eco code: {}.".format(eco_code)
        )
    coords = gdf.iloc[0]["geometry"]
    if coords.geom_type == "MultiPolygon":
        for polygon in coords:
            x, y = polygon.exterior.coords.xy
            x = x.tolist()
            y = y.tolist()
            xym = list(zip(x, y))
            poly = Polygon(xym, facecolor="blue", edgecolor="blue", linewidth=2)
            plt.gca().add_patch(poly)
    else:
        x, y = coords.exterior.coords.xy
        x = x.tolist()
        y = y.tolist()
        xym = list(zip(x, y))
        poly = Polygon(xym, facecolor="blue", edgecolor="blue", linewidth=2)
        plt.gca().add_patch(poly)
    plt.title("{} / {}".format(gdf.iloc[0]["ECOREGION"], gdf.iloc[0]["REALM"]))
    if show:
        plt.show()

    return fig
