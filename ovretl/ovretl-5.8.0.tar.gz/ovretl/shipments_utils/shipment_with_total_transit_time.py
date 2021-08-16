import pandas as pd


def shipments_with_total_transit_time(shipments_with_employees_df: pd.DataFrame) -> pd.DataFrame:
    active_shipments_df = shipments_with_employees_df[
        (shipments_with_employees_df["shipment_status"] != "finished") & (~shipments_with_employees_df["cancelled"])
    ]
    active_shipments_df.loc[
        :, ["transit_time_door_to_port", "transit_time_port_to_door", "transit_time"]
    ] = active_shipments_df[["transit_time_door_to_port", "transit_time_port_to_door", "transit_time"]].fillna(0)
    active_shipments_df.loc[:, "total_transit_time"] = (
        active_shipments_df["transit_time_door_to_port"]
        + active_shipments_df["transit_time"]
        + active_shipments_df["transit_time_port_to_door"]
    )
    return active_shipments_df
