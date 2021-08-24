"""This module contains a function to extract the profiles from
simbench grids.

"""
import os
import simbench as sb
import pandas as pd

from midas.tools import LOG


def build_simbench_data(path=None, simbench_code=None):
    """Load a simbench case and save the profiles in a hdf5 database."""
    if path is None:
        path = os.path.abspath(
            os.path.join(__file__, "..", "..", "..", "..", "data")
        )
    if simbench_code is None:
        simbench_code = "1-LV-rural3--0-sw"

    output_path = os.path.abspath(os.path.join(path, f"{simbench_code}.hdf5"))
    if os.path.exists(output_path):
        LOG.debug("Found existing datasets at %s.", output_path)
        return True

    LOG.debug(
        "No dataset found. Start loading %s profiles ...",
        simbench_code,
    )
    grid = sb.get_simbench_net(simbench_code)

    profiles = sb.get_absolute_values(grid, True)
    load_map = pd.DataFrame(columns=["idx", "bus", "name"])
    sgen_map = pd.DataFrame(columns=["idx", "bus", "name"])

    for idx in range(len(grid.load)):
        load = grid.load.loc[idx]
        load_map = load_map.append(
            {"idx": idx, "bus": int(load["bus"]), "name": load["name"]},
            ignore_index=True,
        )
    for idx in range(len(grid.sgen)):
        sgen = grid.sgen.loc[idx]
        sgen_map = sgen_map.append(
            {"idx": idx, "bus": int(sgen["bus"]), "name": sgen["name"]},
            ignore_index=True,
        )

    profiles[("load", "p_mw")].to_hdf(output_path, "load_pmw", "w")
    profiles[("load", "q_mvar")].to_hdf(output_path, "load_qmvar")
    profiles[("sgen", "p_mw")].to_hdf(output_path, "sgen_pmw")
    load_map.to_hdf(output_path, "load_default_mapping")
    sgen_map.to_hdf(output_path, "sgen_default_mapping")

    LOG.debug("Load complete.")
