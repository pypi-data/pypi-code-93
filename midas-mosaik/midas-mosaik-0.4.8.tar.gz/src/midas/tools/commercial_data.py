import os
from datetime import datetime
from zipfile import ZipFile

import pandas as pd
import wget

from midas.tools import LOG

BASE_URL = "https://openei.org/datasets/files/961/pub/"
LOC_URL = BASE_URL + (
    "COMMERCIAL_LOAD_DATA_E_PLUS_OUTPUT/USA_NY_Rochester-Greater.Rochester."
    "Intl.AP.725290_TMY3/RefBldg"
)
POST_FIX = "New2004_v1.3_7.1_5A_USA_IL_CHICAGO-OHARE.csv"
DATA_URLS = [
    ("FullServiceRestaurant", "FullServiceRestaurant"),
    ("Hospital", "Hospital"),
    ("LargeHotel", "LargeHotel"),
    ("LargeOffice", "LargeOffice"),
    ("MediumOffice", "MediumOffice"),
    ("MidriseApartment", "MidriseApartment"),
    ("OutPatient", "OutPatient"),
    ("PrimarySchool", "PrimarySchool"),
    ("QuickServiceRestaurant", "QuickServiceRestaurant"),
    ("SecondarySchool", "SecondarySchool"),
    ("SmallHotel", "SmallHotel"),
    ("SmallOffice", "SmallOffice"),
    ("Stand-aloneRetail", "StandaloneRetail"),
    ("StripMall", "StripMall"),
    ("SuperMarket", "SuperMarket"),
    ("Warehouse", "Warehouse"),
]

EL_COLS = [
    "Electricity:Facility [kW](Hourly)",
    "Fans:Electricity [kW](Hourly)",
    "Cooling:Electricity [kW](Hourly)",
    "Heating:Electricity [kW](Hourly)",
]


def build_commercial_data(path=None, filename=None):
    if path is None:
        path = os.path.abspath(
            os.path.join(__file__, "..", "..", "..", "..", "data")
        )
    if filename is None:
        filename = "CommercialsRefTMY3.hdf5"

    output_path = os.path.abspath(os.path.join(path, filename))
    if os.path.exists(output_path):
        LOG.debug("Found existing datasets at %s.", output_path)
        return True

    LOG.debug("No dataset found. Start downloading commercial profiles ...")
    tmp = os.path.abspath(os.path.join(path, "tmp"))
    os.makedirs(tmp, exist_ok=True)

    files = [(LOC_URL + f + POST_FIX).rsplit("/", 1)[1] for f, _ in DATA_URLS]

    for idx in range(len(files)):
        if not os.path.exists(os.path.join(tmp, files[idx])):
            files[idx] = wget.download(
                LOC_URL + DATA_URLS[idx][0] + POST_FIX, out=tmp
            )
        else:
            files[idx] = os.path.join(tmp, files[idx])

    date_range = pd.date_range(
        start="2004-01-01 00:00:00",
        end="2004-12-31 23:00:00",
        freq="H",
        tz="Europe/Berlin",
    )
    dr_pt1 = pd.date_range(
        start="2004-01-01 00:00:00",
        end="2004-02-28 23:00:00",
        freq="H",
        tz="Europe/Berlin",
    )
    dr_pt2 = pd.date_range(
        start="2004-02-29 00:00:00",
        end="2004-02-29 23:00:00",
        freq="H",
        tz="Europe/Berlin",
    )
    data = pd.DataFrame(index=date_range)

    for (src, tar), file_ in zip(DATA_URLS, files):
        fpath = os.path.join(tmp, file_)
        tsdat = pd.read_csv(fpath, sep=",")
        tsdat1 = tsdat.iloc[: len(dr_pt1)]
        tsdat1 = tsdat1.append(tsdat1.iloc[-24:])
        tsdat2 = tsdat.iloc[len(dr_pt1) :]
        tsdat = tsdat1.append(tsdat2)
        tsdat.index = date_range
        data[tar] = tsdat[EL_COLS].sum(axis=1) * 1e-3

    # print(data[:10])
    data.to_hdf(output_path, "load_pmw", "w")
    LOG.debug("Download complete.")


def unzip(path, fname, target):

    with ZipFile(os.path.join(path, fname), "r") as zip_ref:
        tar_path = os.path.join(path, target)
        os.makedirs(tar_path, exist_ok=True)
        zip_ref.extractall(tar_path)


if __name__ == "__main__":
    build_commercial_data()
