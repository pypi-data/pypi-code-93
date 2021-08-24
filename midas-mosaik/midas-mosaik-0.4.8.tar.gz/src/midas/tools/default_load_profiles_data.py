"""This module contains utility functions to convert the publicly
available datasets into a hdf5 database file.

"""
import os
import platform
from zipfile import ZipFile

import h5py
import pandas as pd
import wget

from midas.tools import LOG

if platform.system() == "Windows" or platform.system() == "Darwin":
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context


BASE_URL = "https://www.bdew.de/media/documents/Profile.zip"


def build_dlp_data(path=None, filename=None):
    """Convert the default load profiles that can be downloaded
    from the BDEW (last visited on 2020-07-07):

    https://www.bdew.de/energie/standardlastprofile-strom/

    :params path: the path including the filename.

    """
    if path is None:
        path = os.path.abspath(
            os.path.join(__file__, "..", "..", "..", "..", "data")
        )
    if filename is None:
        filename = "Repräsentative Profile VDEW.xls"

    output_path = os.path.abspath(os.path.join(path, filename))
    if os.path.exists(output_path):
        LOG.debug("Found existing datasets at %s.", output_path)
        return True

    LOG.debug("No dataset found. Start downloading default load profiles ...")
    tmp = os.path.abspath(os.path.join(path, "tmp"))
    os.makedirs(tmp, exist_ok=True)
    fname = BASE_URL.rsplit("/", 1)[-1]

    if not os.path.exists(os.path.join(tmp, fname)):
        fname = wget.download(BASE_URL, out=tmp)

    target = os.path.join(tmp, "dlp")

    with ZipFile(os.path.join(tmp, fname), "r") as zip_ref:
        zip_ref.extractall(os.path.join(tmp, target))

    excel_path = os.path.join(
        target,
        "Repräsentative Profile VDEW.xls",
    )

    sheet_names = [
        "H0",
        "G0",
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6",
        "L0",
        "L1",
        "L2",
    ]
    data = pd.read_excel(
        io=excel_path, sheet_name=sheet_names, header=[1, 2], skipfooter=1
    )

    h5f = h5py.File(output_path, "w")
    seasons = [
        ("Winter", "winter"),
        ("Sommer", "summer"),
        ("Übergangszeit", "transition"),
    ]
    days = [
        ("Samstag", "saturday"),
        ("Sonntag", "sunday"),
        ("Werktag", "weekday"),
    ]
    for name in sheet_names:
        grp = h5f.create_group(name)
        for season in seasons:
            subgrp = grp.create_group(season[1])
            for day in days:
                subgrp.create_dataset(
                    day[1], data=data[name][(season[0], day[0])]
                )
    h5f.attrs["hint"] = (
        "Quarter-hourly power values for annual " "consumption."
    )
    h5f.attrs["ref_value"] = "1000 kWh/a"
    h5f.close()
    LOG.debug("Download complete.")
