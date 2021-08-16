import datetime

import numpy as np
import pandas as pd


def calculate_business_days_delta(date_1: datetime.datetime, date_2: datetime.datetime):
    if date_1 is None or date_2 is None or pd.isna(date_1) or pd.isna(date_2):
        return None
    return max(0, np.busday_count(date_1.strftime("%Y-%m-%d"), date_2.strftime("%Y-%m-%d")))
