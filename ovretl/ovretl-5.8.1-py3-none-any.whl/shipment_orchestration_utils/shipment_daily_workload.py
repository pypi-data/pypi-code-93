import pandas as pd
from datetime import date, timedelta
import numpy as np
from typing import NamedTuple
from ovretl.shipment_orchestration_utils.utils import string_date_to_datetime


class ShipmentTimelineInfos(NamedTuple):
    shipment_id: str
    workflow_associated_at: date
    total_transit_time: int
    arrival_date: date or None
    delivery_date: date or None


def total_tasks_weight(tasks_df: pd.DataFrame) -> pd.DataFrame:
    tasks_df = tasks_df.loc[:, ["shipment_id", "weight"]].groupby("shipment_id").sum()
    return tasks_df.rename(columns={"weight": "total_tasks_weight"})


def daily_tasks_total_weight_on_shipment(tasks_df: pd.DataFrame, date: date) -> int:
    is_todo_task_due_date = (tasks_df["status"] == "to_do") & (tasks_df["due_date"] == date)
    tasks_todo_today_on_shipment_df = tasks_df[is_todo_task_due_date]
    if len(tasks_todo_today_on_shipment_df["shipment_id"]) == 0:
        return 0
    daily_tasks_todo_total_weight_df = (
        tasks_todo_today_on_shipment_df.loc[:, ["shipment_id", "weight"]].groupby("shipment_id").sum()
    )
    return daily_tasks_todo_total_weight_df.weight.iat[0]


def shipment_total_workflows_weight(active_shipments_data_df: pd.DataFrame,) -> pd.DataFrame:
    active_shipments_data_df = active_shipments_data_df.groupby("shipment_id", as_index=False).agg(
        {
            "total_workflow_weight": sum,
            "workflow_associated_at": min,
            **{
                col: "first"
                for col in active_shipments_data_df.columns
                if col not in ["shipment_id", "total_workflow_weight", "workflow_associated_at"]
            },
        }
    )
    active_shipments_data_df = active_shipments_data_df.rename(
        columns={"total_workflow_weight": "total_workflows_weight"}
    )
    return active_shipments_data_df


def shipments_remaining_estimation_days(
    active_shipments_data_df: pd.DataFrame, shipments_timelines_df: pd.DataFrame
) -> pd.DataFrame:
    total_remaining_days = []
    for shipment_tuple in active_shipments_data_df.itertuples():
        shipment_timeline = shipments_timelines_df.loc[
            shipments_timelines_df["shipment_id"] == shipment_tuple.shipment_id, :
        ]
        shipment_future_days = shipment_timeline.loc[
            shipment_timeline["dates"] > shipment_tuple.workload_estimation_start_date, :
        ]
        """counting in regard of date_weighting moves weekend days out of estimation"""
        total_remaining_days.append(sum(shipment_future_days["date_weighting"]))
    active_shipments_data_df.loc[:, "remaining_days"] = total_remaining_days
    return active_shipments_data_df


def get_shipment_start_date(shipment_tuple: ShipmentTimelineInfos, shipment_tasks: pd.Series) -> date:
    if len(shipment_tasks) == 0:
        return shipment_tuple.workflow_associated_at
    return shipment_tasks["due_date"].min().date()


def get_shipment_end_date(shipment_tuple: ShipmentTimelineInfos) -> date or None:
    if not pd.isnull(shipment_tuple.delivery_date):
        return shipment_tuple.delivery_date
    if not pd.isnull(shipment_tuple.arrival_date):
        return shipment_tuple.arrival_date
    return None


def shipment_date_range(
    shipment_tuple: ShipmentTimelineInfos, shipment_tasks: pd.Series, today: date
) -> pd.DatetimeIndex:
    shipment_start_date = get_shipment_start_date(shipment_tuple, shipment_tasks)
    shipment_end_date = get_shipment_end_date(shipment_tuple)
    if pd.isnull(shipment_end_date):
        remaining_shipment_days = shipment_tuple.total_transit_time - (today - shipment_start_date).days
        return pd.date_range(start=today, periods=max(0, remaining_shipment_days))
    return pd.date_range(start=today, end=shipment_end_date + timedelta(days=1))


def calculate_dates_weighting(date: date):
    """consider weekend as days off i.e. with 0 weighting"""
    if date.weekday() >= 5:
        return 0
    return 1


def shipments_timelines(active_shipments_data_df: pd.DataFrame, tasks_df: pd.DataFrame, today: date) -> pd.DataFrame:
    shipments_timeline_infos_grouped = (
        active_shipments_data_df.loc[
            :, ["shipment_id", "workflow_associated_at", "total_transit_time", "arrival_date", "delivery_date",],
        ]
        .groupby(["shipment_id", "total_transit_time"], as_index=False)
        .agg({"workflow_associated_at": min, **{col: "first" for col in ["delivery_date", "arrival_date"]}})
    )
    shipments_timelines_list = []
    for shipment_timeline_infos_tuple in shipments_timeline_infos_grouped.itertuples(True, "ShipmentTimelineInfos"):
        shipment_tasks = tasks_df[tasks_df["shipment_id"] == shipment_timeline_infos_tuple.shipment_id]
        shipment_timeline_df = pd.DataFrame(data={"shipment_id": [], "dates": []})
        dates = shipment_date_range(
            shipment_tuple=shipment_timeline_infos_tuple, shipment_tasks=shipment_tasks, today=today
        )
        shipment_timeline_df["dates"] = dates
        shipment_timeline_df["shipment_id"] = shipment_timeline_infos_tuple.shipment_id
        shipments_timelines_list.append(shipment_timeline_df)
    shipments_timelines_df = pd.concat(shipments_timelines_list)
    shipments_timelines_df.loc[:, "dates"] = shipments_timelines_df["dates"].dt.date
    shipments_timelines_df.loc[:, "date_weighting"] = shipments_timelines_df.loc[:, "dates"].apply(
        calculate_dates_weighting
    )
    return shipments_timelines_df.reset_index(drop=True)


def shipment_workload_estimation_start_date(
    active_shipments_data_df: pd.DataFrame, tasks_df: pd.DataFrame, today: date
):
    estimation_start_date = []
    todo_tasks_df = tasks_df[tasks_df["status"] == "to_do"]
    for shipment_id in active_shipments_data_df["shipment_id"]:
        shipment_todo_tasks = todo_tasks_df[tasks_df["shipment_id"] == shipment_id]
        if len(shipment_todo_tasks) == 0:
            estimation_start_date.append(today)
        else:
            estimation_start_date.append(shipment_todo_tasks["due_date"].min().date())
    active_shipments_data_df.loc[:, "workload_estimation_start_date"] = estimation_start_date
    return active_shipments_data_df


def estimated_remaining_daily_workload(
    active_shipments_data_df: pd.DataFrame, tasks_df: pd.DataFrame, shipments_timelines_df: pd.DataFrame, today: date
) -> pd.DataFrame:
    active_shipments_data_df = active_shipments_data_df[
        [
            "shipment_id",
            "shipment_status",
            "freight_method",
            "freight_type",
            "total_workflow_weight",
            "foresea_name",
            "incoterm",
            "total_transit_time",
            "workflow_associated_at",
            "delivery_date",
            "arrival_date",
        ]
    ]
    active_shipments_data_df = shipment_total_workflows_weight(active_shipments_data_df=active_shipments_data_df)
    active_shipments_data_df = shipment_workload_estimation_start_date(active_shipments_data_df, tasks_df, today)
    active_shipments_data_df = shipments_remaining_estimation_days(active_shipments_data_df, shipments_timelines_df)
    total_tasks_weight_df = total_tasks_weight(tasks_df=tasks_df)
    active_shipments_data_df = pd.merge(active_shipments_data_df, total_tasks_weight_df, on="shipment_id", how="left")
    active_shipments_data_df.loc[:, "estimated_remaining_daily_workload"] = (
        active_shipments_data_df["total_workflows_weight"] - active_shipments_data_df["total_tasks_weight"]
    ) / active_shipments_data_df["remaining_days"]
    active_shipments_data_df.loc[
        ~np.isfinite(active_shipments_data_df["estimated_remaining_daily_workload"]),
        "estimated_remaining_daily_workload",
    ] = 0
    return active_shipments_data_df


def daily_workload_calculation(shipments_timelines_df: pd.DataFrame, tasks_df: pd.DataFrame) -> pd.DataFrame:
    tasks_df.loc[:, "due_date"] = tasks_df["due_date"].dt.date
    shipments_timelines_df.loc[:, "created_tasks_weight"] = shipments_timelines_df.apply(
        lambda row: daily_tasks_total_weight_on_shipment(
            tasks_df=tasks_df.loc[tasks_df["shipment_id"] == row["shipment_id"], :], date=row["dates"],
        ),
        axis=1,
    )
    shipments_timelines_df.loc[:, "daily_workload"] = shipments_timelines_df["date_weighting"] * (
        shipments_timelines_df["created_tasks_weight"] + shipments_timelines_df["estimated_remaining_daily_workload"]
    )
    return shipments_timelines_df


def shipments_daily_workload_timelines(active_shipments_data_df: pd.DataFrame, tasks_df: pd.DataFrame) -> pd.DataFrame:
    today = date.today()
    tasks_df.loc[:, "weight"] = tasks_df["weight"].fillna(0)
    tasks_df = tasks_df.loc[:, ["shipment_id", "due_date", "status", "weight", "updated_at"]]
    active_shipments_data_df.loc[:, ["workflow_associated_at"]] = active_shipments_data_df.loc[
        :, ["workflow_associated_at"]
    ].applymap(string_date_to_datetime)
    shipments_timelines_df = shipments_timelines(active_shipments_data_df, tasks_df, today)
    active_shipments_data_df = estimated_remaining_daily_workload(
        active_shipments_data_df=active_shipments_data_df,
        tasks_df=tasks_df,
        shipments_timelines_df=shipments_timelines_df,
        today=today,
    )
    shipments_timelines_df = pd.merge(shipments_timelines_df, active_shipments_data_df, how="left", on="shipment_id")
    shipments_timelines_df.loc[
        shipments_timelines_df["dates"] <= shipments_timelines_df["workload_estimation_start_date"],
        "estimated_remaining_daily_workload",
    ] = 0
    shipments_timelines_df = daily_workload_calculation(
        shipments_timelines_df=shipments_timelines_df, tasks_df=tasks_df
    )
    return shipments_timelines_df[["shipment_id", "dates", "daily_workload"]]
