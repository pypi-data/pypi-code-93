import pandas as pd
from ovretl.transit_times.location_functions import is_import, is_abroad


def add_features(train_df):
    train_df_copy = train_df.copy()
    train_df_copy.loc[:, "is_import"] = train_df_copy.apply(is_import, axis=1)
    pickup_df = train_df_copy[
        [
            "shipment_created_at",
            "foresea_name",
            "freight_method",
            "load_type",
            "pickup_harbor_country",
            "pickup_harbor_locode",
            "pickup_shipowner",
            "pickup_distance",
            "pickup_time",
            "departure_shipowner",
            "freight_shipowner",
            "is_import",
        ]
    ]
    pickup_df = pickup_df.rename(
        columns={
            "pickup_harbor_country": "harbor_country",
            "pickup_harbor_locode": "harbor_locode",
            "pickup_shipowner": "carriage_shipowner",
            "pickup_distance": "distance",
            "pickup_time": "time",
            "departure_shipowner": "harbor_shipowner",
        }
    ).dropna(subset=["time"])
    pickup_df.loc[:, "carriage_type"] = "precarriage"
    delivery_df = train_df_copy[
        [
            "shipment_created_at",
            "foresea_name",
            "freight_method",
            "load_type",
            "freight_shipowner",
            "arrival_shipowner",
            "delivery_harbor_country",
            "delivery_harbor_locode",
            "delivery_shipowner",
            "delivery_distance",
            "delivery_time",
            "is_import",
        ]
    ]
    delivery_df = delivery_df.rename(
        columns={
            "arrival_shipowner": "harbor_shipowner",
            "delivery_harbor_country": "harbor_country",
            "delivery_harbor_locode": "harbor_locode",
            "delivery_shipowner": "carriage_shipowner",
            "delivery_distance": "distance",
            "delivery_time": "time",
        }
    ).dropna(subset=["time"])
    delivery_df.loc[:, "carriage_type"] = "postcarriage"
    train_df_copy = pd.concat([pickup_df, delivery_df], sort=False)
    train_df_copy.loc[:, "is_abroad"] = train_df_copy.apply(
        lambda s: is_abroad(s["is_import"], s["carriage_type"]), axis=1
    )
    return train_df_copy
