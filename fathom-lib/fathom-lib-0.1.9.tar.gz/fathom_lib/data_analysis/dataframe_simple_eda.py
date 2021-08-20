import json

import pandas as pd
from pandas_profiling import ProfileReport


def minify_report(profile_report):
    """
    For bigger datasets some of the properties of variables are too big to be displayed
    :param profile_report:
    :return:
    """
    for var_name in profile_report["variables"]:
        variable = profile_report["variables"][var_name]
        if len(variable.get("value_counts", [])) > 100:
            del variable["value_counts"]
        if "histogram" in variable:
            del variable["histogram"]
        if len(variable.get("scatter_data", [])) > 100:
            del variable["scatter_data"]
    return profile_report


def generate_simple_eda(df: pd.DataFrame, remove_big_info=True):
    profile = ProfileReport(df, minimal=True)
    report = json.loads(profile.to_json())
    if remove_big_info:
        return minify_report(report)
    else:
        return report
