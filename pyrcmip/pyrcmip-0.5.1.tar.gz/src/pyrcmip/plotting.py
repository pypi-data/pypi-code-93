"""
Helpers and config for plotting
"""
import numpy as np

CLIMATE_MODEL_PALETTE = {
    "assessed range": "tab:blue",
    "MAGICC7": "tab:orange",
    "two_layer": "tab:pink",
    "Raw CMIP6 multi-model ensemble": "tab:green",
    "HadCRUT.5.0.0.0": "tab:gray",
    "HadCRUT.5.0.0.0 (GMST)": "tab:gray",
    "AR6 Prelim. FGD": "tab:gray",
    "von Shuckmann et al. 2020": "tab:purple",
}
"""dict: Colour palette used for plots coloured by climate model"""


SCENARIO_PALETTE = {
    k: np.array(v) / 256
    for k, v in {
        "ssp119": (30, 150, 132),
        "ssp126": (29, 51, 84),
        "ssp245": (234, 221, 61),
        "ssp370": (242, 17, 17),
        "ssp370-lowNTCF": (242, 17, 17),
        "ssp434": (99, 189, 229),
        "ssp460": (232, 236, 49),
        "ssp585": (132, 11, 34),
        "ssp534-over": (154, 109, 201),
    }.items()
}
"""dict: Colour palette used for plots coloured by scenario"""
SCENARIO_PALETTE["historical"] = "tab:gray"


CMIP6_NAME = "Raw CMIP6 multi-model ensemble"
"""str: String used to represent the CMIP6 multi-model ensemble in plots"""
