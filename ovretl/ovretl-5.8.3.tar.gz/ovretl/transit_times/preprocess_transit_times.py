import pandas as pd
from ovretl.transit_times.add_features import add_features
from ovretl.transit_times.constants import DEFAULT_ENCODING
from ovretl.transit_times.encode_features import encode_features


def preprocess_transit_times(transit_times_df: pd.DataFrame, outlier_threshold: int):
    transit_times_df = transit_times_df[transit_times_df["freight_method"].isin(["air", "ocean"])]
    transit_times_df = transit_times_df[
        ~(transit_times_df["pickup_time"].isnull()) | ~(transit_times_df["delivery_time"].isnull())
    ]
    transit_times_df = transit_times_df[
        (transit_times_df["pickup_time"].isnull())
        | (transit_times_df["pickup_time"].apply(lambda x: x < outlier_threshold))
    ]
    transit_times_df = transit_times_df[
        (transit_times_df["delivery_time"].isnull())
        | (transit_times_df["delivery_time"].apply(lambda x: x < outlier_threshold))
    ]
    transit_times_df = encode_features(transit_times_df)
    transit_times_df = add_features(transit_times_df)
    transit_times_df.loc[:, "distance"] = transit_times_df["distance"].fillna(0)
    transit_times_df = transit_times_df.fillna(DEFAULT_ENCODING)
    transit_times_df = transit_times_df.sort_values(by="shipment_created_at")
    return transit_times_df
