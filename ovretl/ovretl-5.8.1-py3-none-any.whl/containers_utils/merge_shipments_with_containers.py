import pandas as pd


def merge_with_propositions_containers_then_with_shipments_containers(
    shipments_df: pd.DataFrame, propositions_containers_df: pd.DataFrame, shipments_containers_df: pd.DataFrame,
) -> pd.DataFrame:
    shipments_df = pd.merge(
        shipments_df,
        propositions_containers_df[["teus", "tc", "hazardous", "refrigerated", "proposition_id"]],
        how="left",
        on="proposition_id",
    )

    shipments_df_with_teus = shipments_df[~shipments_df["teus"].isnull()]
    shipments_df_without_teus = shipments_df[shipments_df["teus"].isnull()].drop(
        ["teus", "tc", "hazardous", "refrigerated"], axis=1
    )

    shipments_df_without_teus = pd.merge(
        shipments_df_without_teus,
        shipments_containers_df[["teus", "tc", "hazardous", "refrigerated", "shipment_id"]],
        how="left",
        on="shipment_id",
    )
    return (
        pd.concat([shipments_df_with_teus, shipments_df_without_teus], sort=False)
        .reset_index(drop=True)
        .rename(columns={"hazardous": "containers_hazardous", "refrigerated": "containers_refrigerated",})
    )


def split_propositions_shipments_containers(containers_df: pd.DataFrame):
    propositions_containers_df = containers_df[~containers_df["proposition_id"].isnull()]
    shipments_containers_df = containers_df[~containers_df["shipment_id"].isnull()]
    return propositions_containers_df, shipments_containers_df


def merge_shipments_with_containers(
    shipments_df: pd.DataFrame, containers_df: pd.DataFrame, drop_duplicate_key="shipment_id",
):
    (propositions_containers_df, shipments_containers_df,) = split_propositions_shipments_containers(containers_df)
    shipments_df = merge_with_propositions_containers_then_with_shipments_containers(
        shipments_df=shipments_df,
        propositions_containers_df=propositions_containers_df,
        shipments_containers_df=shipments_containers_df,
    )
    shipments_df = shipments_df.sort_values(by=["teus", "tc"], ascending=False)
    shipments_df = shipments_df[
        (~shipments_df.duplicated(subset=[drop_duplicate_key])) | (shipments_df[drop_duplicate_key].isnull())
    ]
    return shipments_df
