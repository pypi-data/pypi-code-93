import os
import h5py
import pandas as pd
import numpy as np
import subprocess
import shutil
import tarfile

from midas.tools import LOG

TOKEN = "fDaPqqSuMBhsXD8nQ_Nn"


def build_smartnord_data(path=None, filename=None):
    if path is None:
        path = os.path.abspath(
            os.path.join(__file__, "..", "..", "..", "..", "data")
        )
    if filename is None:
        filename = "SmartNordProfiles.hdf5"
    output_path = os.path.abspath(os.path.join(path, filename))
    if os.path.exists(output_path):
        LOG.debug("Found existing datasets at %s.", output_path)
        return

    print("Data not found at", output_path)

    tmp_path = os.path.abspath(os.path.join(path, "tmp"))

    zip_path = os.path.join(
        tmp_path, "smart_nord_data", "HouseholdProfiles.tar.gz"
    )
    if not os.path.exists(zip_path):
        subprocess.check_output(
            [
                "git",
                "clone",
                f"https://midas:{TOKEN}@gitlab.com/midas-mosaik/midas-data",
                os.path.join(tmp_path, "smart_nord_data"),
            ]
        )
    with tarfile.open(zip_path, "r:gz") as tar_ref:
        tar_ref.extractall(tmp_path)
    tmp_name = os.path.join(tmp_path, "HouseholdProfiles.hdf5")
    shutil.move(tmp_name, output_path)


def convert_smartnord_data(path_to_profiles):
    """Load the old-style Smard Nord database and convert the data."""

    path = os.path.abspath(
        os.path.join(__file__, "..", "..", "..", "..", "data")
    )
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, "SmartNordProfiles.hdf5")

    data = list()

    with h5py.File(path_to_profiles, "r") as data_file:
        num_lands = len(data_file)
        for land in data_file:
            load_ids = list(data_file[land])
            loads = np.zeros((len(load_ids), 35_040))

            for load_id in load_ids:
                idx = int(load_id)
                loads[idx] = np.array(data_file[land][load_id][()])
                loads[idx] *= -1e-6

            data.append(loads)

    load_p = pd.DataFrame()
    for land_id, land in enumerate(data):
        for load_id, load in enumerate(land):
            key = f"Load{land_id}p{load_id:03d}"
            load_p[key] = load

    load_p.to_hdf(path, "load_pmw", "w")


if __name__ == "__main__":
    build_smartnord_data(
        os.path.join(
            "/",
            "home",
            "stephan",
            "data",
            "projects",
            "midas",
            "src",
            "midas",
            "data",
            "house_profiles.hdf5",
        )
    )
