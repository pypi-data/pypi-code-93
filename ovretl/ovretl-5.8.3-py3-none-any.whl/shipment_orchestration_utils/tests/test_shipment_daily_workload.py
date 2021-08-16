import pandas as pd

from ovretl.shipment_orchestration_utils.shipment_daily_workload import (
    total_tasks_weight,
    shipment_total_workflows_weight,
    shipments_remaining_estimation_days,
    shipments_timelines,
    estimated_remaining_daily_workload,
    daily_tasks_total_weight_on_shipment,
    shipments_daily_workload_timelines,
    shipment_workload_estimation_start_date,
)
from datetime import datetime, date
import time_machine


def test_total_task_weight():
    tasks_df = pd.DataFrame(data={"shipment_id": ["1", "2", "2", "1"], "weight": [1, 2, 3, 5]})
    result_should_be = pd.DataFrame(data={"shipment_id": ["1", "2"], "total_tasks_weight": [6, 5]}).set_index(
        "shipment_id"
    )
    result = total_tasks_weight(tasks_df)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_daily_tasks_total_weight_on_shipment():
    today_date = date(2020, 12, 28)
    other_date = date(2001, 1, 1)
    tasks_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "1", "2", "2", "1"],
            "status": ["done", "to_do", "to_do", "to_do", "to_do"],
            "due_date": [other_date, today_date, today_date, other_date, today_date],
            "weight": [1, 2, 3, 4, 5],
        }
    )
    result_should_be = 7
    result = daily_tasks_total_weight_on_shipment(tasks_df.loc[tasks_df["shipment_id"] == "1", :], today_date)
    assert result_should_be == result


def test_shipment_total_workflows_weight():
    sh_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2", "1", "2"],
            "total_workflow_weight": [1, 2, 3, 4],
            "workflow_associated_at": [
                datetime(2020, 11, 15),
                datetime(2020, 12, 28),
                datetime(2020, 12, 26),
                datetime(2020, 12, 26),
            ],
        }
    )
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": ["1", "2"],
            "total_workflows_weight": [4, 6],
            "workflow_associated_at": [datetime(2020, 11, 15), datetime(2020, 12, 26)],
        }
    )
    result = shipment_total_workflows_weight(sh_df)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_shipment_remaining_estimation_days():
    today = datetime(2020, 12, 28)
    today_date = today.date()
    day_before_1 = datetime(2020, 12, 27)
    day_before_2 = datetime(2020, 12, 26)
    sh_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2", "3"],
            "workflow_id": ["1", "2", "3"],
            "total_transit_time": [10, 10, 10],
            "workflow_associated_at": [today, day_before_1, day_before_2],
            "shipment_status": ["awaiting_booking", "booked", "booked"],
            "freight_method": ["air", "ocean", "ocean"],
            "freight_type": ["air", "ocean", "ocean"],
            "foresea_name": ["BATD", "BATE", "BATE"],
            "incoterm": ["fob", "ddp", "ddp"],
            "delivery_date": [None, None, None],
            "arrival_date": [None, None, None],
            "workload_estimation_start_date": [today_date, today_date, today_date],
        }
    )
    tasks_df = pd.DataFrame(data={"shipment_id": []})
    timelines = shipments_timelines(sh_df, tasks_df=tasks_df, today=today)
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": ["1", "2", "3"],
            "workflow_id": ["1", "2", "3"],
            "total_transit_time": [10, 10, 10],
            "workflow_associated_at": [today, day_before_1, day_before_2],
            "shipment_status": ["awaiting_booking", "booked", "booked"],
            "freight_method": ["air", "ocean", "ocean"],
            "freight_type": ["air", "ocean", "ocean"],
            "foresea_name": ["BATD", "BATE", "BATE"],
            "incoterm": ["fob", "ddp", "ddp"],
            "delivery_date": [None, None, None],
            "arrival_date": [None, None, None],
            "workload_estimation_start_date": [today_date, today_date, today_date],
            "remaining_days": [7, 6, 5],
        }
    )
    result = shipments_remaining_estimation_days(sh_df, timelines)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_shipments_timelines_with_transit_time():
    day_1 = datetime(2020, 12, 28)
    day_2 = datetime(2020, 12, 29)
    day_3 = datetime(2020, 12, 30)
    day_4 = datetime(2020, 12, 31)
    day_5 = datetime(2021, 1, 1)
    today = day_3
    sh_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2"],
            "total_transit_time": [4, 3],
            "workflow_associated_at": [day_1, day_3],
            "delivery_date": [None, None],
            "arrival_date": [None, None],
        }
    )
    tasks_df = pd.DataFrame(data={"shipment_id": []})
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": ["1", "1", "2", "2", "2"],
            "dates": [day_3, day_4, day_3, day_4, day_5],
            "date_weighting": 1,
        }
    )
    result_should_be.loc[:, ["dates"]] = result_should_be["dates"].dt.date
    result = shipments_timelines(active_shipments_data_df=sh_df, tasks_df=tasks_df, today=today)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_shipments_timelines_with_tracking_dates():
    day_1 = datetime(2020, 12, 28)
    day_2 = datetime(2020, 12, 29)
    day_3 = datetime(2020, 12, 30)
    day_4 = datetime(2020, 12, 31)
    day_5 = datetime(2021, 1, 1)
    today = day_1
    sh_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2"],
            "total_transit_time": [10, 10],
            "workflow_associated_at": [datetime(2020, 12, 27), datetime(2020, 12, 27)],
            "delivery_date": [day_1, None],
            "arrival_date": [day_1, day_4],
        }
    )
    tasks_df = pd.DataFrame(data={"shipment_id": []})
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": ["1", "1", "2", "2", "2", "2", "2"],
            "dates": [day_1, day_2, day_1, day_2, day_3, day_4, day_5],
            "date_weighting": 1,
        }
    )
    result_should_be.loc[:, ["dates"]] = result_should_be["dates"].dt.date
    result = shipments_timelines(active_shipments_data_df=sh_df, tasks_df=tasks_df, today=today)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_shipments_timelines_with_tracking_dates_and_tasks():
    day_1 = datetime(2020, 12, 28)
    day_2 = datetime(2020, 12, 29)
    day_3 = datetime(2020, 12, 30)
    day_4 = datetime(2020, 12, 31)
    day_5 = datetime(2021, 1, 1)
    sh_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2"],
            "total_transit_time": [10, 10],
            "workflow_associated_at": [day_2, day_4],
            "delivery_date": [day_1, None],
            "arrival_date": [day_1, day_4],
        }
    )
    tasks_df = pd.DataFrame(data={"shipment_id": ["1", "1", "2", "2"], "due_date": [day_1, day_2, day_3, day_4]})
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": ["1", "1", "2", "2", "2", "2", "2"],
            "dates": [day_1, day_2, day_1, day_2, day_3, day_4, day_5],
            "date_weighting": 1,
        }
    )
    result_should_be.loc[:, ["dates"]] = result_should_be["dates"].dt.date
    result = shipments_timelines(active_shipments_data_df=sh_df, tasks_df=tasks_df, today=day_1)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_shipments_timelines_with_tracking_dates_and_tasks_and_weekend():
    day_1 = datetime(2019, 12, 28)
    day_2 = datetime(2019, 12, 29)
    day_3 = datetime(2019, 12, 30)
    day_4 = datetime(2019, 12, 31)
    day_5 = datetime(2020, 1, 1)
    sh_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2"],
            "total_transit_time": [10, 10],
            "workflow_associated_at": [day_2, day_4],
            "delivery_date": [day_1, None],
            "arrival_date": [day_1, day_4],
        }
    )
    tasks_df = pd.DataFrame(data={"shipment_id": ["1", "1", "2", "2"], "due_date": [day_1, day_2, day_3, day_4]})
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": ["1", "1", "2", "2", "2", "2", "2"],
            "dates": [day_1, day_2, day_1, day_2, day_3, day_4, day_5],
            "date_weighting": [0, 0, 0, 0, 1, 1, 1],
        }
    )
    result_should_be.loc[:, ["dates"]] = result_should_be["dates"].dt.date
    result = shipments_timelines(active_shipments_data_df=sh_df, tasks_df=tasks_df, today=day_1)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_shipment_workload_estimation_start_date():
    sh_df = pd.DataFrame(data={"shipment_id": ["1", "2", "3"]})
    today = date.today()
    tasks_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2", "2", "2"],
            "status": ["done", "done", "to_do", "to_do"],
            "due_date": [
                datetime(2020, 12, 29),
                datetime(2020, 12, 26),
                datetime(2020, 12, 30),
                datetime(2020, 12, 29),
            ],
        }
    )
    result_should_be = pd.DataFrame(
        data={"shipment_id": ["1", "2", "3"], "workload_estimation_start_date": [today, date(2020, 12, 29), today],}
    )
    result = shipment_workload_estimation_start_date(sh_df, tasks_df, today)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_estimated_remaining_daily_workload():
    today = date(2020, 12, 26)
    sh_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2", "2"],
            "workflow_id": ["1", "2", "3"],
            "total_transit_time": [10, 12, 12],
            "workflow_associated_at": [datetime(2020, 11, 15), datetime(2020, 12, 28), datetime(2020, 12, 26)],
            "total_workflow_weight": [1, 10, 50],
            "shipment_status": ["awaiting_booking", "booked", "booked"],
            "freight_method": ["air", "ocean", "ocean"],
            "freight_type": ["air", "ocean", "ocean"],
            "foresea_name": ["BATD", "BATE", "BATE"],
            "incoterm": ["fob", "ddp", "ddp"],
            "delivery_date": [None, None, None],
            "arrival_date": [None, None, None],
        }
    )
    tasks_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2", "2", "2", "2"],
            "status": ["done", "to_do", "to_do", "done", "to_do"],
            "due_date": [
                datetime(2020, 11, 15),
                datetime(2020, 12, 26),
                datetime(2020, 12, 29),
                datetime(2020, 12, 28),
                datetime(2020, 12, 30),
            ],
            "weight": [1, 6, 4, 5, 5],
        }
    )
    timelines = shipments_timelines(sh_df, tasks_df, today)
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": ["1", "2"],
            "total_workflows_weight": [1, 60],
            "workflow_associated_at": [datetime(2020, 11, 15), datetime(2020, 12, 26)],
            "shipment_status": ["awaiting_booking", "booked"],
            "freight_method": ["air", "ocean"],
            "freight_type": ["air", "ocean"],
            "foresea_name": ["BATD", "BATE"],
            "incoterm": ["fob", "ddp"],
            "total_transit_time": [10, 12],
            "delivery_date": [None, None],
            "arrival_date": [None, None],
            "workload_estimation_start_date": [today, today],
            "remaining_days": [0, 8],
            "total_tasks_weight": [1, 20],
            "estimated_remaining_daily_workload": [0.0, 5.0],
        }
    )
    result = estimated_remaining_daily_workload(sh_df, tasks_df, timelines, today)
    pd.testing.assert_frame_equal(result, result_should_be)


def test_shipments_daily_workload_timelines():
    today = datetime(2020, 12, 27)
    """Traveller mocks all datetime functions using today, replacing current day info by
    a custom today date. Between traveller.start() and traveller.stop(), every
    call to today will return 27 December 2020. Thus shipments_daily_workload_timeline 
    is tested regardless of its dependency on current day"""
    traveller = time_machine.travel(today)
    traveller.start()
    sh_df = pd.DataFrame(
        data={
            "shipment_id": [1, 2, 2],
            "workflow_id": ["1", "2", "3"],
            "total_transit_time": [10, 12, 12],
            "workflow_associated_at": [
                datetime(2020, 11, 15).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                datetime(2020, 12, 28).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                datetime(2020, 12, 26).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            ],
            "total_workflow_weight": [1, 10, 50],
            "shipment_status": ["awaiting_booking", "booked", "booked"],
            "freight_method": ["air", "ocean", "ocean"],
            "freight_type": ["air", "ocean", "ocean"],
            "foresea_name": ["BATD", "BATE", "BATE"],
            "incoterm": ["fob", "ddp", "ddp"],
            "delivery_date": [None, None, None],
            "arrival_date": [None, None, None],
        }
    )
    tasks_df = pd.DataFrame(
        data={
            "shipment_id": [1, 2, 2, 2, 2, 2, 2],
            "status": ["to_do", "to_do", "to_do", "done", "to_do", "to_do", "done"],
            "due_date": [
                datetime(2020, 11, 15),
                datetime(2020, 12, 28),
                datetime(2020, 12, 29),
                datetime(2020, 12, 27),
                datetime(2020, 12, 30),
                datetime(2020, 12, 30),
                datetime(2020, 12, 27),
            ],
            "updated_at": [
                datetime(2020, 11, 15),
                datetime(2020, 12, 28),
                datetime(2020, 12, 29),
                datetime(2020, 12, 27),
                datetime(2020, 12, 30),
                datetime(2020, 12, 30),
                datetime(2020, 12, 27),
            ],
            "weight": [1, 1, 3, 3, 3, 10, 10],
        }
    )
    dates_sh_2 = pd.date_range(start=date(2020, 12, 27), periods=12)
    shipment_2_workload = [0.0, 1.0, 6.75, 16.75, 3.75, 3.75, 0.0, 0.0, 3.75, 3.75, 3.75, 3.75]
    result_should_be = pd.DataFrame(
        data={"shipment_id": 2, "dates": dates_sh_2, "daily_workload": shipment_2_workload,}
    )
    result_should_be["dates"] = result_should_be["dates"].dt.date
    result = shipments_daily_workload_timelines(active_shipments_data_df=sh_df, tasks_df=tasks_df)
    pd.testing.assert_frame_equal(result, result_should_be)
    traveller.stop()


def test_shipments_daily_workload_timelines_with_tracking_dates():
    today = datetime(2020, 12, 27)
    traveller = time_machine.travel(today)
    traveller.start()
    sh_df = pd.DataFrame(
        data={
            "shipment_id": [1, 2, 2],
            "workflow_id": ["1", "2", "3"],
            "total_transit_time": [2, 3, 3],
            "workflow_associated_at": [
                datetime(2020, 11, 15).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                datetime(2020, 12, 28).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                datetime(2020, 12, 26).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            ],
            "total_workflow_weight": [1, 10, 50],
            "shipment_status": ["awaiting_booking", "booked", "booked"],
            "freight_method": ["air", "ocean", "ocean"],
            "freight_type": ["air", "ocean", "ocean"],
            "foresea_name": ["BATD", "BATE", "BATE"],
            "incoterm": ["fob", "ddp", "ddp"],
            "delivery_date": [datetime(2020, 11, 23), None, None],
            "arrival_date": [None, datetime(2021, 1, 6), datetime(2021, 1, 6)],
        }
    )
    tasks_df = pd.DataFrame(
        data={
            "shipment_id": [1, 2, 2, 2, 2, 2, 2],
            "status": ["to_do", "to_do", "to_do", "done", "to_do", "to_do", "done"],
            "due_date": [
                datetime(2020, 11, 15),
                datetime(2020, 12, 28),
                datetime(2020, 12, 29),
                datetime(2020, 12, 27),
                datetime(2020, 12, 30),
                datetime(2020, 12, 30),
                datetime(2020, 12, 27),
            ],
            "updated_at": [
                datetime(2020, 11, 15),
                datetime(2020, 12, 28),
                datetime(2020, 12, 29),
                datetime(2020, 12, 27),
                datetime(2020, 12, 30),
                datetime(2020, 12, 30),
                datetime(2020, 12, 27),
            ],
            "weight": [1, 1, 3, 3, 3, 10, 10],
        }
    )
    dates_sh_2 = pd.date_range(start=date(2020, 12, 27), end=date(2021, 1, 7))
    shipment_2_workload = [0.0, 1.0, 6.75, 16.75, 3.75, 3.75, 0.0, 0.0, 3.75, 3.75, 3.75, 3.75]
    result_should_be = pd.DataFrame(
        data={"shipment_id": 2, "dates": dates_sh_2, "daily_workload": shipment_2_workload,}
    )
    result_should_be["dates"] = result_should_be["dates"].dt.date
    result = shipments_daily_workload_timelines(active_shipments_data_df=sh_df, tasks_df=tasks_df)
    pd.testing.assert_frame_equal(result, result_should_be)
    traveller.stop()
