import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from pytz import utc


def get_week_number_from_jesus(date):
    return date.isocalendar()[1] + date.year * 52


def check_shipment_active_at_date(date, shipment: pd.Series):
    if shipment["cancelled"] == True:
        return False
    if shipment["shipment_status"] in [
        "new",
        "not_answered",
        "propositions_sent",
        "purchase_ready",
        "to_be_requoted",
        "not_answered_declined",
    ]:
        return False
    if pd.isna(shipment["operations_owner_id"]):
        return False
    if (pd.to_datetime(shipment["created_at"]) - date).days > 7:
        return False
    if pd.to_datetime(shipment["finished_date"]) < date:
        return False
    last_date = shipment["delivery_date"] if not pd.isna(shipment["delivery_date"]) else shipment["arrival_date"]
    if date > last_date:
        return False
    if (
        pd.isna(shipment["pickup_date"])
        and pd.isna(shipment["departure_date"])
        and pd.isna(shipment["arrival_date"])
        and pd.isna(shipment["delivery_date"])
    ):
        return True
    if not pd.isna(shipment["departure_date"]) and get_week_number_from_jesus(date) <= get_week_number_from_jesus(
        pd.to_datetime(shipment["departure_date"]) + relativedelta(days=2)
    ):
        return True

    if not pd.isna(shipment["arrival_date"]) and get_week_number_from_jesus(date) >= get_week_number_from_jesus(
        pd.to_datetime(shipment["arrival_date"]) + relativedelta(days=-10)
    ):
        return True
    return False


def determine_active_shipments_at_date(date, shipments_df: pd.DataFrame):
    shipments_df.loc[:, "active"] = shipments_df.apply(lambda s: check_shipment_active_at_date(date, s), axis=1)
    active_shipments = shipments_df[shipments_df["active"]]
    active_shipments.loc[:, "active_date"] = date
    return active_shipments


def determine_active_shipments(shipments_df: pd.DataFrame, date_end=datetime.datetime.now()):
    dates = pd.date_range(start="2020-01-01", end=date_end, freq="W-MON", tz=utc).to_series()
    df_list = []
    for date in dates:
        df_list.append(determine_active_shipments_at_date(date, shipments_df))
    active_shipments_data_df = pd.concat(df_list, sort=False)
    active_shipments_data_df = active_shipments_data_df[["active_date", "foresea_name", "operations",]]
    return active_shipments_data_df
