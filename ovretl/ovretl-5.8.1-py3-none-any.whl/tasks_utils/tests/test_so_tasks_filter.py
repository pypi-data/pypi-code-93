import pandas as pd
import datetime

from ovretl.tasks_utils.so_tasks_filter import so_tasks_filter


def test_so_tasks_filter():
    now_datetime = datetime.datetime.now()
    now_date = now_datetime.date()
    tasks_df = pd.DataFrame(
        data={
            "id": ["1", "2"],
            "so_id": ["1", None],
            "created_at": now_datetime,
            "updated_at": now_datetime,
            "due_date": now_datetime,
            "done_date": now_datetime,
        }
    )
    result_should_be = pd.DataFrame(
        data={
            "id": ["1"],
            "so_id": ["1"],
            "created_at": now_datetime,
            "updated_at": now_datetime,
            "due_date": now_datetime,
            "done_date": now_datetime,
        }
    )
    result = so_tasks_filter(tasks_df)
    pd.testing.assert_frame_equal(result, result_should_be)
