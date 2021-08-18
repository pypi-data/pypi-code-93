"""
Utility functions for validating RCMIP submissions
"""
import os.path

import pandas as pd
import pkg_resources

SUBMISSION_TEMPLATE = os.path.join(
    "..", "data", "rcmip-data-submission-template-v5-0-0.xlsx"
)


def load_submission_template_definitions(fp=None, component="variables"):
    """
    Load submission template definitions

    Parameters
    ----------
    fp : str
        Filepath from which to load the definitions. If ``None``, definitions
        will be loaded from
        ``pyrcmip/data/rcmip-data-submission-template-v4-0-0.xlsx``.

    component : {"variables", "regions", "scenarios"}
        Definitions section to load

    Returns
    -------
    :obj:`pd.DataFrame`
    """
    if fp is None:
        fp = pkg_resources.resource_stream(__name__, SUBMISSION_TEMPLATE)

    if component == "variables":
        component_kwargs = {
            "sheet_name": "variable_definitions",
            "usecols": range(1, 6),
        }

    elif component == "regions":
        component_kwargs = {
            "sheet_name": "region_definitions",
        }

    elif component == "scenarios":
        component_kwargs = {
            "sheet_name": "scenario_info",
            "skiprows": 2,
            "usecols": range(1, 5),
        }

    else:
        raise NotImplementedError("Unrecognised component: {}".format(component))

    out = pd.read_excel(fp, engine="openpyxl", **component_kwargs)
    out.columns = out.columns.str.lower()

    if component == "variables":
        out["tier"] = out["tier"].astype(int)

    elif component == "scenarios":
        out = out.dropna()
        column_map = {
            "# scenario id": "scenario_id",
            "# scenario description": "description",
            "#scenario specification": "specification",
            "# tier in rcmp": "tier",
        }
        out.columns = out.columns.map(column_map)
        out["tier"] = out["tier"].astype(int)

    unnamed_cols = [c for c in out if c.startswith("unnamed:")]
    if unnamed_cols:
        out = out.drop(unnamed_cols, axis="columns")

    return out
