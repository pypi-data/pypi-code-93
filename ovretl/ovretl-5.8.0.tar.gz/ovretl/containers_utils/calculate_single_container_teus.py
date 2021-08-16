import pandas as pd


def calculate_single_container_teus(single_container: pd.Series):
    if "twenty" in single_container["container_type"]:
        single_container["teus"] = 1
        return single_container
    single_container["teus"] = 2
    return single_container
