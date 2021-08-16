import numpy as np
import pandas as pd


def encode_distance(train_df: pd.DataFrame, feature: str):
    train_df.loc[:, feature] = train_df[feature].apply(lambda x: int(x / 100) * 100 if not pd.isna(x) else np.nan)
    # value_counts = train_df[feature].value_counts()
    # mapping = {key: key if value >= group_size_threshold else DEFAULT_ENCODING for key, value in value_counts.items()}
    # train_df.loc[:, feature] = train_df[feature].replace(mapping)


# def encode_feature(train_df: pd.DataFrame, group_size_threshold: int, feature: str):
#     value_counts = train_df[feature].value_counts()
#     mapping = {key: key if value >= group_size_threshold else DEFAULT_ENCODING for key, value in value_counts.items()}
#     train_df.loc[:, feature] = train_df[feature].replace(mapping)


def encode_features(train_df: pd.DataFrame):
    # qualitative_features = [
    #     "pickup_harbor_country",
    #     "pickup_harbor_locode",
    #     "delivery_harbor_country",
    #     "delivery_harbor_locode",
    #     "pickup_shipowner",
    #     "departure_shipowner",
    #     "arrival_shipowner",
    #     "delivery_shipowner",
    #     "freight_shipowner",
    # ]
    distance_features = ["pickup_distance", "delivery_distance"]
    train_df_copy = train_df.copy()
    # for feature in qualitative_features:
    #     encode_feature(train_df_copy, group_size_threshold, feature)
    for feature in distance_features:
        encode_distance(train_df_copy, feature)
    return train_df_copy
