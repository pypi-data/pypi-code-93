import pandas as pd

from ovretl.performances_utils.calculate_business_days_delta import calculate_business_days_delta
from ovretl.performances_utils.calculate_business_hours_delta import calculate_business_hours_delta

QUOTATION_ASKED = "quotation_asked"
QUOTATION_CONSIDERED = "request_considered"
QUOTATION_PURCHASE_READY = "quotation_purchase_ready"
QUOTATION_SENT = "propositions_received"
QUOTATION_ACCEPTED = "quotation_accepted"
SHIPMENT_BOOKED = "shipment_booked"
SHIPMENT_ARRIVED = "shipment_arrived"
SHIPMENT_FINISHED = "shipment_finished"
BILLING_AVAILABLE = "billing_available"
BILLING_PAID = "billing_paid"


def drop_not_arrived_shipment_groups(shipment_events_df: pd.DataFrame):
    shipment_events_df = shipment_events_df.sort_values(by=["date"], ascending=False).reset_index(drop=True)
    if shipment_events_df.loc[0, "date_type"] == "estimated":
        return False
    return True


def extract_arrived_date_from_events(events_shipment_df: pd.DataFrame):
    events_shipment_df = events_shipment_df.dropna(subset=["shipment_id", "date"], how="any").drop(
        ["created_at"], axis=1
    )
    events_shipment_df = events_shipment_df.groupby("shipment_id").filter(drop_not_arrived_shipment_groups)
    events_shipment_df = events_shipment_df.sort_values(by=["shipment_id", "date"], ascending=False)
    events_shipment_df = events_shipment_df.drop_duplicates(subset=["shipment_id"])
    events_shipment_df.loc[:, "header"] = "shipment_arrived"
    events_shipment_df = events_shipment_df.rename(columns={"date": "created_at"})
    return events_shipment_df[["created_at", "header", "shipment_id"]]


def extract_finished_date_from_shipments(shipments_df: pd.DataFrame):
    shipments_df = shipments_df.dropna(subset=["finished_date"]).drop(["created_at"], axis=1)
    shipments_df.loc[:, "header"] = "shipment_finished"
    shipments_df = shipments_df.rename(columns={"finished_date": "created_at", "id": "shipment_id"})
    return shipments_df[["created_at", "header", "shipment_id"]]


def concatenate_activities(
    events_shipment_df: pd.DataFrame, activities_clean_df: pd.DataFrame, shipments_df: pd.DataFrame,
):
    activities_clean_df = pd.concat([activities_clean_df, events_shipment_df, shipments_df], sort=False)
    activities_clean_df.loc[:, "created_at"] = pd.to_datetime(activities_clean_df["created_at"]).apply(
        lambda t: t.replace(tzinfo=None)
    )
    activities_clean_df = activities_clean_df.sort_values(by=["shipment_id", "header", "created_at"], ascending=True)
    activities_clean_df = activities_clean_df.drop_duplicates(subset=["shipment_id", "header"])

    activities_clean_df = activities_clean_df[
        activities_clean_df["header"].isin(
            [
                QUOTATION_ASKED,
                QUOTATION_CONSIDERED,
                QUOTATION_PURCHASE_READY,
                QUOTATION_SENT,
                QUOTATION_ACCEPTED,
                SHIPMENT_BOOKED,
                SHIPMENT_ARRIVED,
                SHIPMENT_FINISHED,
                BILLING_AVAILABLE,
                BILLING_PAID,
            ]
        )
    ]
    activities_clean_df = pd.pivot_table(
        activities_clean_df, values="created_at", index=["shipment_id"], columns=["header"], aggfunc="first",
    )
    return activities_clean_df.reset_index()


def calculate_steps_time(activities_df: pd.DataFrame):
    activities_df.loc[:, "quotation_asked_considered_hours"] = activities_df.apply(
        lambda s: calculate_business_hours_delta(s[QUOTATION_ASKED], s[QUOTATION_CONSIDERED]), axis=1,
    )
    activities_df.loc[:, "quotation_considered_purchase_ready_hours"] = activities_df.apply(
        lambda s: calculate_business_hours_delta(s[QUOTATION_CONSIDERED], s[QUOTATION_PURCHASE_READY]), axis=1,
    )
    activities_df.loc[:, "quotation_purchase_ready_sent_hours"] = activities_df.apply(
        lambda s: calculate_business_hours_delta(s[QUOTATION_PURCHASE_READY], s[QUOTATION_SENT]), axis=1,
    )
    activities_df.loc[:, "quotation_asked_sent_hours"] = activities_df.apply(
        lambda s: calculate_business_hours_delta(s[QUOTATION_ASKED], s[QUOTATION_SENT]), axis=1,
    )
    activities_df.loc[:, "quotation_accepted_shipment_booked_days"] = activities_df.apply(
        lambda s: calculate_business_days_delta(s[QUOTATION_ACCEPTED], s[SHIPMENT_BOOKED]), axis=1,
    )
    activities_df.loc[:, "shipment_arrived_shipment_finished_days"] = activities_df.apply(
        lambda s: calculate_business_days_delta(s[SHIPMENT_ARRIVED], s[SHIPMENT_FINISHED]), axis=1,
    )
    activities_df.loc[:, "shipment_arrived_billing_available_days"] = activities_df.apply(
        lambda s: calculate_business_days_delta(s[SHIPMENT_ARRIVED], s[BILLING_AVAILABLE]), axis=1,
    )
    activities_df.loc[:, "billing_available_paid_days"] = activities_df.apply(
        lambda s: calculate_business_days_delta(s[BILLING_AVAILABLE], s[BILLING_PAID]), axis=1,
    )
    return activities_df


def calculate_shipments_treatment_steps_time(
    events_shipment_df: pd.DataFrame, activities_clean_df: pd.DataFrame, shipments_df: pd.DataFrame,
):
    events_shipment_df = extract_arrived_date_from_events(events_shipment_df=events_shipment_df)
    activities_clean_df = activities_clean_df.dropna(subset=["shipment_id"])[
        ["created_at", "header", "shipment_id", "employee_id"]
    ]
    shipments_df = extract_finished_date_from_shipments(shipments_df=shipments_df)

    activities_clean_df = concatenate_activities(
        events_shipment_df=events_shipment_df, activities_clean_df=activities_clean_df, shipments_df=shipments_df,
    )
    return calculate_steps_time(activities_df=activities_clean_df).drop(["employee_id"], axis=1, errors="ignore")
