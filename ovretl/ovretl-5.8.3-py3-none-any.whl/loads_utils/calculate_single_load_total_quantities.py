import pandas as pd


def calculate_single_load_total_weight(single_load):
    return single_load["unit_weight"] * single_load["unit_number"]


def calculate_single_load_total_volume(single_load):
    return (
        single_load["unit_length"]
        * single_load["unit_width"]
        * single_load["unit_height"]
        * single_load["unit_number"]
        / 1000000
    )


def calculate_single_load_total_quantities(single_load: pd.Series) -> pd.Series:
    single_load["total_weight"] = (
        single_load["total_weight"]
        if not pd.isna(single_load["total_weight"]) and single_load["total_weight"] > 0
        else calculate_single_load_total_weight(single_load)
    )
    single_load["total_volume"] = (
        single_load["total_volume"]
        if not pd.isna(single_load["total_volume"]) and single_load["total_volume"] > 0
        else calculate_single_load_total_volume(single_load)
    )
    single_load["total_number"] = single_load["unit_number"]
    return single_load


def calculate_taxable_weight(total_weight: float, total_volume: float):
    return round(max(total_volume / 6, total_weight / 1000) * 1000, 3)


def calculate_weight_measurable(total_weight: float, total_volume: float):
    return round(max(total_weight / 1000, total_volume, 1), 3)
