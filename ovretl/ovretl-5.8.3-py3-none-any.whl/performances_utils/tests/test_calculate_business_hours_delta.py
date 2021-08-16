import datetime

from ovretl.performances_utils.calculate_business_hours_delta import calculate_business_hours_delta


def test_calculate_business_hours_delta():
    # 2h + 3h
    date_1 = datetime.datetime(2020, 6, 26, 17, 45)
    date_2 = datetime.datetime(2020, 6, 29, 11, 30)
    assert calculate_business_hours_delta(date_1, date_2) == 4.75

    # 2h + 3h
    date_3 = datetime.datetime(2020, 6, 25, 17, 30)
    date_4 = datetime.datetime(2020, 6, 26, 11, 30)
    assert calculate_business_hours_delta(date_3, date_4) == 5

    # 11h + 6h
    date_5 = datetime.datetime(2020, 6, 25, 11, 30)
    date_6 = datetime.datetime(2020, 6, 26, 17, 30)
    assert calculate_business_hours_delta(date_5, date_6) == 17

    # 6h
    date_7 = datetime.datetime(2020, 6, 25, 11, 45)
    date_8 = datetime.datetime(2020, 6, 25, 17, 30)
    assert calculate_business_hours_delta(date_7, date_8) == 5.75

    # 11h + 2h + 0h
    date_9 = datetime.datetime(2020, 6, 25, 17, 30)
    date_10 = datetime.datetime(2020, 6, 27, 11, 30)
    assert calculate_business_hours_delta(date_9, date_10) == 13

    # 11h + 5h
    date_11 = datetime.datetime(2020, 6, 26, 17, 30)
    date_12 = datetime.datetime(2020, 6, 30, 11, 30)
    assert calculate_business_hours_delta(date_11, date_12) == 16

    # 0h + 4h
    date_13 = datetime.datetime(2020, 6, 28, 22, 30)
    date_14 = datetime.datetime(2020, 6, 29, 12, 30)
    assert calculate_business_hours_delta(date_13, date_14) == 4

    # 0h + 4h
    date_15 = datetime.datetime(2020, 8, 22, 19, 30)
    date_16 = datetime.datetime(2020, 8, 25, 10, 30)
    assert calculate_business_hours_delta(date_15, date_16) == 13
