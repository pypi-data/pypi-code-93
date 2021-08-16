import pandas as pd
from ovretl.containers_utils.calculate_single_container_teus import calculate_single_container_teus


def aggregate_containers(containers: pd.DataFrame):
    aggregated_containers = {}
    aggregated_containers["teus"] = containers["teus"].sum()
    aggregated_containers["tc"] = len(containers)
    aggregated_containers["hazardous"] = containers["hazardous"].any()
    aggregated_containers["refrigerated"] = (
        containers["container_type"]
        .isin(["twenty_standard_reefer", "forty_standard_reefer", "forty_highcube_reefer"])
        .any()
    )
    return pd.Series(aggregated_containers, index=["teus", "tc", "hazardous", "refrigerated"])


def calculate_entity_containers(containers_df: pd.DataFrame, key: str):
    entity_containers = containers_df[~containers_df[key].isnull()]
    return entity_containers.groupby(key).apply(aggregate_containers).reset_index().drop_duplicates(subset=[key])


def calculate_shipments_propositions_containers(containers_df: pd.DataFrame):
    containers_df = containers_df.apply(calculate_single_container_teus, axis=1)
    containers_df = containers_df.dropna(subset=["teus"])
    propositions_containers = calculate_entity_containers(containers_df=containers_df, key="proposition_id")
    shipments_containers = calculate_entity_containers(containers_df=containers_df, key="shipment_id")
    return pd.concat([propositions_containers, shipments_containers], sort=False)
