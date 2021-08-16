import pandas as pd


def match_kronos_propositions_and_shipments(
    kronos_propositions_df: pd.DataFrame, shipments_all_propositions_df: pd.DataFrame
):
    kronos_propositions_df = kronos_propositions_df.rename(columns={"id": "kronos_proposition_id"})
    kronos_propositions_df = kronos_propositions_df.dropna(subset=["shipment_id"])

    # Merge on kronos_proposition_id to get kronos_action (new system: table propositions has kronos_proposition_id)
    kronos_propositions_df = pd.merge(
        kronos_propositions_df,
        shipments_all_propositions_df[
            ["kronos_proposition_id", "proposition_id", "kronos_action", "foresea_name"]
        ].dropna(subset=["kronos_proposition_id"]),
        how="left",
        on="kronos_proposition_id",
    )

    kronos_propositions_df_with_foresea_name = (
        kronos_propositions_df[~kronos_propositions_df["foresea_name"].isnull()]
        .drop(["proposition_id_x"], axis=1)
        .rename(columns={"proposition_id_y": "proposition_id"})
    )
    kronos_propositions_df_without_foresea_name = (
        kronos_propositions_df[kronos_propositions_df["foresea_name"].isnull()]
        .drop(["foresea_name", "proposition_id_y", "kronos_action"], axis=1)
        .rename(columns={"proposition_id_x": "proposition_id"})
    )

    # Merge on proposition_id for remaining kronos_propositions (old system: table kronos_proposition_id has proposition_id)
    kronos_propositions_df_without_foresea_name = pd.merge(
        kronos_propositions_df_without_foresea_name,
        shipments_all_propositions_df[["proposition_id", "kronos_action"]].dropna(subset=["proposition_id"]),
        how="left",
        on="proposition_id",
    )

    # Concatenate
    kronos_propositions_df = pd.concat(
        [kronos_propositions_df_with_foresea_name, kronos_propositions_df_without_foresea_name], sort=False
    ).reset_index(drop=True)

    # Sort with shipment_id, then proposition_id to put most relevant Kronos propositions first
    kronos_propositions_df = kronos_propositions_df.sort_values(
        by=["shipment_id", "proposition_id", "created_at"], ascending=False,
    )
    kronos_propositions_df = kronos_propositions_df.drop_duplicates(subset=["shipment_id"])
    return kronos_propositions_df.drop(["foresea_name"], axis=1)
