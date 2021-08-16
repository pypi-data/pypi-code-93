import pandas as pd


def determine_import_status(shipment: pd.Series):
    if shipment["freight_method"] == "truck":
        return "inland"
    pickup_country_is_france = not pd.isna(shipment["pickup_country"]) and shipment["pickup_country"].lower() == "fr"
    delivery_country_is_france = (
        not pd.isna(shipment["delivery_country"]) and shipment["delivery_country"].lower() == "fr"
    )
    pickup_country_in_europe = not pd.isna(shipment["pickup_country"]) and shipment["pickup_country"].lower() in [
        "fr",
        "be",
        "es",
    ]
    pickup_harbor_in_europe = not pd.isna(shipment["pickup_harbor_country"]) and shipment[
        "pickup_harbor_country"
    ].lower() in ["fr", "be", "es", "nl", "it"]
    delivery_country_in_europe = not pd.isna(shipment["delivery_country"]) and shipment["delivery_country"].lower() in [
        "fr",
        "be",
        "es",
    ]
    delivery_harbor_in_europe = not pd.isna(shipment["delivery_harbor_country"]) and shipment[
        "delivery_harbor_country"
    ].lower() in ["fr", "be", "es", "nl", "it"]

    if (delivery_country_in_europe or delivery_harbor_in_europe) and not pickup_country_is_france:
        return "import"
    if (pickup_country_in_europe or pickup_harbor_in_europe) and not delivery_country_is_france:
        return "export"
    return "cross_trade"
