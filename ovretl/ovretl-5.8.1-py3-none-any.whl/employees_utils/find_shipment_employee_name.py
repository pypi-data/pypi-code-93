import pandas as pd


def find_shipment_employee_name(employees_associated_df: pd.DataFrame, role: str):
    if len(employees_associated_df) == 0:
        return None
    mask_employees = employees_associated_df["role"] == role
    employees_associated_df_filtered = employees_associated_df[mask_employees].reset_index(drop=True)
    if len(employees_associated_df_filtered) > 0:
        return employees_associated_df_filtered.loc[0, "name"]
    return None


def add_employees_to_shipments(shipments_df: pd.Series, employees_df: pd.DataFrame):
    shipments_df = (
        pd.merge(
            left=shipments_df, right=employees_df[["id", "name"]], left_on="sales_owner_id", right_on="id", how="left",
        )
        .drop(["id", "sales_owner_id"], axis=1)
        .rename(columns={"name": "sales"})
    )
    shipments_df = (
        pd.merge(
            left=shipments_df,
            right=employees_df[["id", "name"]],
            left_on="operations_owner_id",
            right_on="id",
            how="left",
        )
        .drop(["id", "operations_owner_id"], axis=1)
        .rename(columns={"name": "operations"})
    )
    shipments_df = (
        pd.merge(
            left=shipments_df,
            right=employees_df[["id", "name"]],
            left_on="pricing_owner_id",
            right_on="id",
            how="left",
        )
        .drop(["id", "pricing_owner_id"], axis=1)
        .rename(columns={"name": "pricing"})
    )
    return shipments_df
