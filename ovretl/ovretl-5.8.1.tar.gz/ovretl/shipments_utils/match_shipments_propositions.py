import pandas as pd


def select_column_of_most_recent_entity(df_entity) -> pd.Series:
    return df_entity.sort_values(by="created_at", ascending=False).iloc[0:1]


def select_best_proposition_id(shipment_propositions: pd.DataFrame):
    mask_accepted = shipment_propositions["proposition_status"] == "accepted"
    mask_accepted_or_accepted_old_version = shipment_propositions["proposition_status"].isin(
        ["accepted", "accepted_old_version"])
    mask_sent = shipment_propositions["proposition_status"] == "sent"
    mask_purchase_ready = shipment_propositions["proposition_status"] == "purchase_ready"
    accepted_propositions = shipment_propositions[mask_accepted]
    if len(accepted_propositions) > 0:
        return select_column_of_most_recent_entity(accepted_propositions)
    accepted_or_accepted_old_version_propositions = shipment_propositions[mask_accepted_or_accepted_old_version]
    if len(accepted_or_accepted_old_version_propositions) > 0:
        return select_column_of_most_recent_entity(accepted_or_accepted_old_version_propositions)
    sent_propositions = shipment_propositions[mask_sent]
    if len(sent_propositions) > 0:
        return select_column_of_most_recent_entity(sent_propositions)
    purchase_ready_propositions = shipment_propositions[mask_purchase_ready]
    if len(purchase_ready_propositions) > 0:
        return select_column_of_most_recent_entity(purchase_ready_propositions)
    if len(shipment_propositions) > 0:
        return select_column_of_most_recent_entity(shipment_propositions)


def match_shipments_propositions(shipments_df: pd.DataFrame, propositions_df: pd.DataFrame):
    propositions_df = propositions_df.rename(columns={"id": "proposition_id", "status": "proposition_status"})
    propositions_df = propositions_df.groupby("shipment_id").apply(select_best_proposition_id).reset_index(drop=True)
    shipments_df = shipments_df.rename(columns={"id": "shipment_id", "status": "shipment_status"})
    return pd.merge(
        shipments_df.drop(["transit_time", "kronos_action"], axis=1, errors="ignore"),
        propositions_df[
            [
                "proposition_id",
                "proposition_status",
                "purchase_ready_date",
                "sent_date",
                "accepted_date",
                "shipment_id",
                "transit_time",
                "transit_time_door_to_port",
                "transit_time_port_to_door",
                "kronos_action",
                "kronos_proposition_id",
            ]
        ],
        how="left",
        on="shipment_id",
    )
