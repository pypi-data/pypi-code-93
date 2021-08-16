import pandas as pd

from ovretl import determine_import_status


def test_determine_import_status():
    shipment_truck = pd.Series(data={"freight_method": "truck"})
    shipment_import = pd.Series(
        data={
            "freight_method": "ocean",
            "pickup_country": "CN",
            "pickup_harbor_country": "CN",
            "delivery_country": "FR",
            "delivery_harbor_country": "BE",
        }
    )
    shipment_export = pd.Series(
        data={
            "freight_method": "ocean",
            "pickup_country": "BE",
            "pickup_harbor_country": "FR",
            "delivery_country": "US",
            "delivery_harbor_country": "US",
        }
    )
    shipment_cross_trade = pd.Series(
        data={
            "freight_method": "ocean",
            "pickup_country": "HK",
            "pickup_harbor_country": "HK",
            "delivery_country": "US",
            "delivery_harbor_country": "US",
        }
    )
    assert determine_import_status(shipment_truck) == "inland"
    assert determine_import_status(shipment_import) == "import"
    assert determine_import_status(shipment_export) == "export"
    assert determine_import_status(shipment_cross_trade) == "cross_trade"
