import pandas as pd


def is_import(shipment: pd.Series):
    if shipment["delivery_harbor_country"] in ["FR", "BE", "NL", "ES", "IT",] and not shipment[
        "pickup_harbor_country"
    ] in ["FR", "BE", "NL", "ES", "IT"]:
        return True
    return False


def is_abroad(shipment_is_import: bool, carriage_type: str):
    if shipment_is_import:
        if carriage_type == "precarriage":
            return True
        return False
    if carriage_type == "postcarriage":
        return True
    return False
