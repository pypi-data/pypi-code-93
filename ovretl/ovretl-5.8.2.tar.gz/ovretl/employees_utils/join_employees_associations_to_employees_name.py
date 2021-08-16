import pandas as pd


def join_employees_associations_to_employees_name(
    employees_df: pd.DataFrame, employee_shipment_associations_df: pd.DataFrame
):
    return pd.merge(
        employees_df,
        employee_shipment_associations_df[["employee_id", "shipment_id", "role"]],
        left_on="id",
        right_on="employee_id",
    )
