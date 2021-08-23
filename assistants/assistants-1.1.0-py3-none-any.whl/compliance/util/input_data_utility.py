from typing import Optional

import pandas as pd

date_start_2017 = pd.Timestamp(2017, 1, 1)
date_end_sept_2018 = pd.Timestamp(2018, 9, 30)
date_end_sept_2017 = pd.Timestamp(2017, 9, 30)
date_start_2018 = pd.Timestamp(2018, 1, 1)
date_end_sept_2021 = pd.Timestamp(2021, 9, 30)


def completed_to_due_vector(completed: pd.Series, transition_process_1: Optional[pd.Series] = None) -> pd.Series:
    # https://cms.scouts.org.uk/media/7295/pre-launch-checks-training-requirements-por-updates-v3.pdf
    out = completed + pd.DateOffset(years=3)  # NoQA  # 3 years is base
    out[completed < date_start_2017] = completed + pd.DateOffset(years=5)  # NoQA
    out[(completed >= date_start_2017) & (completed <= date_end_sept_2018)] = date_end_sept_2021
    out[(completed > date_end_sept_2017) & (completed < date_start_2018)] = completed + pd.DateOffset(years=4)  # NoQA

    if transition_process_1 is not None:
        out[~transition_process_1 & (out < date_end_sept_2021)] = date_end_sept_2021

    return out
