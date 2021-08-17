import unittest

import datetime
from helpsk import date
from helpsk import validation as vld


# noinspection PyMethodMayBeStatic
class TestValidation(unittest.TestCase):

    def test_ymd(self):
        assert vld.raises_exception(lambda: date.ymd('2021-02-31 23:58:59'), ValueError)

        value = date.ymd('2021-01-01')
        assert value.year == 2021
        assert value.month == 1
        assert value.day == 1

        value = date.ymd('2021-01-31')
        assert value.year == 2021
        assert value.month == 1
        assert value.day == 31

        value = date.ymd('2021-12-31')
        assert value.year == 2021
        assert value.month == 12
        assert value.day == 31

        assert vld.raises_exception(lambda: date.ymd('2021-02-31'), ValueError)

    def test_ymd_hms(self):
        assert vld.raises_exception(lambda: date.ymd_hms('2021-02-31'), ValueError)

        value = date.ymd_hms('2021-01-01 00:00:00')
        assert value.year == 2021
        assert value.month == 1
        assert value.day == 1
        assert value.hour == 0
        assert value.minute == 0
        assert value.second == 0

        value = date.ymd_hms('2021-01-01 23:58:59')
        assert value.year == 2021
        assert value.month == 1
        assert value.day == 1
        assert value.hour == 23
        assert value.minute == 58
        assert value.second == 59

        value = date.ymd_hms('2021-01-31 23:58:59')
        assert value.year == 2021
        assert value.month == 1
        assert value.day == 31
        assert value.hour == 23
        assert value.minute == 58
        assert value.second == 59

        value = date.ymd_hms('2021-12-31 23:58:59')
        assert value.year == 2021
        assert value.month == 12
        assert value.day == 31
        assert value.hour == 23
        assert value.minute == 58
        assert value.second == 59

        assert vld.raises_exception(lambda: date.ymd_hms('2021-02-31 23:58:59'), ValueError)

    def test_fiscal_quarter_date(self):
        date_values = ['2020-12-01', '2020-12-15', '2020-12-31',
                       '2021-01-01', '2021-01-15', '2021-01-31',
                       '2021-02-01', '2021-02-15', '2021-02-28',
                       '2021-03-01', '2021-03-15', '2021-03-31',
                       '2021-04-01', '2021-04-15', '2021-04-30',
                       '2021-05-01', '2021-05-15', '2021-05-31',
                       '2021-06-01', '2021-06-15', '2021-06-30',
                       '2021-07-01', '2021-07-15', '2021-07-31',
                       '2021-08-01', '2021-08-15', '2021-08-31',
                       '2021-09-01', '2021-09-15', '2021-09-30',
                       '2021-10-01', '2021-10-15', '2021-10-31',
                       '2021-11-01', '2021-11-15', '2021-11-30',
                       '2021-12-01', '2021-12-15', '2021-12-31',
                       '2022-01-01', '2022-01-15', '2022-01-31']

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=True,
                                       fiscal_start=1) for x in date_values]
        expected = [2020.4, 2020.4, 2020.4,
                    2021.1, 2021.1, 2021.1,
                    2021.1, 2021.1, 2021.1,
                    2021.1, 2021.1, 2021.1,
                    2021.2, 2021.2, 2021.2,
                    2021.2, 2021.2, 2021.2,
                    2021.2, 2021.2, 2021.2,
                    2021.3, 2021.3, 2021.3,
                    2021.3, 2021.3, 2021.3,
                    2021.3, 2021.3, 2021.3,
                    2021.4, 2021.4, 2021.4,
                    2021.4, 2021.4, 2021.4,
                    2021.4, 2021.4, 2021.4,
                    2022.1, 2022.1, 2022.1]
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=False,
                                       fiscal_start=1) for x in date_values]
        expected = [4, 4, 4,
                    1, 1, 1,
                    1, 1, 1,
                    1, 1, 1,
                    2, 2, 2,
                    2, 2, 2,
                    2, 2, 2,
                    3, 3, 3,
                    3, 3, 3,
                    3, 3, 3,
                    4, 4, 4,
                    4, 4, 4,
                    4, 4, 4,
                    1, 1, 1]
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=True,
                                       fiscal_start=2) for x in date_values]
        expected = [2021.4, 2021.4, 2021.4,
                    2021.4, 2021.4, 2021.4,
                    2022.1, 2022.1, 2022.1,
                    2022.1, 2022.1, 2022.1,
                    2022.1, 2022.1, 2022.1,
                    2022.2, 2022.2, 2022.2,
                    2022.2, 2022.2, 2022.2,
                    2022.2, 2022.2, 2022.2,
                    2022.3, 2022.3, 2022.3,
                    2022.3, 2022.3, 2022.3,
                    2022.3, 2022.3, 2022.3,
                    2022.4, 2022.4, 2022.4,
                    2022.4, 2022.4, 2022.4,
                    2022.4, 2022.4, 2022.4]
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=False,
                                       fiscal_start=2) for x in date_values]
        expected = [4, 4, 4,
                    4, 4, 4,
                    1, 1, 1,
                    1, 1, 1,
                    1, 1, 1,
                    2, 2, 2,
                    2, 2, 2,
                    2, 2, 2,
                    3, 3, 3,
                    3, 3, 3,
                    3, 3, 3,
                    4, 4, 4,
                    4, 4, 4,
                    4, 4, 4]
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=True,
                                       fiscal_start=12) for x in date_values]
        expected = [2021.1, 2021.1, 2021.1,  # 2020-Dec
                    2021.1, 2021.1, 2021.1,  # 2021-Jan
                    2021.1, 2021.1, 2021.1,  # 2021-Feb
                    2021.2, 2021.2, 2021.2,  # 2021-Mar
                    2021.2, 2021.2, 2021.2,  # 2021-Apr
                    2021.2, 2021.2, 2021.2,  # 2021-May
                    2021.3, 2021.3, 2021.3,  # 2021-Jun
                    2021.3, 2021.3, 2021.3,  # 2021-Jul
                    2021.3, 2021.3, 2021.3,  # 2021-Aug
                    2021.4, 2021.4, 2021.4,  # 2021-Sep
                    2021.4, 2021.4, 2021.4,  # 2021-Oct
                    2021.4, 2021.4, 2021.4,  # 2021-Nov
                    2022.1, 2022.1, 2022.1,  # 2021-Dec
                    2022.1, 2022.1, 2022.1]  # 2022-Jan
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=False,
                                       fiscal_start=12) for x in date_values]
        expected = [1, 1, 1,  # 2020-Dec
                    1, 1, 1,  # 2021-Jan
                    1, 1, 1,  # 2021-Feb
                    2, 2, 2,  # 2021-Mar
                    2, 2, 2,  # 2021-Apr
                    2, 2, 2,  # 2021-May
                    3, 3, 3,  # 2021-Jun
                    3, 3, 3,  # 2021-Jul
                    3, 3, 3,  # 2021-Aug
                    4, 4, 4,  # 2021-Sep
                    4, 4, 4,  # 2021-Oct
                    4, 4, 4,  # 2021-Nov
                    1, 1, 1,  # 2021-Dec
                    1, 1, 1]  # 2022-Jan
        assert results == expected

    def test_fiscal_quarter_datetime(self):
        date_values = ['2020-12-01', '2020-12-15', '2020-12-31',
                       '2021-01-01', '2021-01-15', '2021-01-31',
                       '2021-02-01', '2021-02-15', '2021-02-28',
                       '2021-03-01', '2021-03-15', '2021-03-31',
                       '2021-04-01', '2021-04-15', '2021-04-30',
                       '2021-05-01', '2021-05-15', '2021-05-31',
                       '2021-06-01', '2021-06-15', '2021-06-30',
                       '2021-07-01', '2021-07-15', '2021-07-31',
                       '2021-08-01', '2021-08-15', '2021-08-31',
                       '2021-09-01', '2021-09-15', '2021-09-30',
                       '2021-10-01', '2021-10-15', '2021-10-31',
                       '2021-11-01', '2021-11-15', '2021-11-30',
                       '2021-12-01', '2021-12-15', '2021-12-31',
                       '2022-01-01', '2022-01-15', '2022-01-31']

        results = [date.fiscal_quarter(value=date.ymd_hms(x + ' 23:59:59'),
                                       include_year=True,
                                       fiscal_start=1) for x in date_values]
        expected = [2020.4, 2020.4, 2020.4,
                    2021.1, 2021.1, 2021.1,
                    2021.1, 2021.1, 2021.1,
                    2021.1, 2021.1, 2021.1,
                    2021.2, 2021.2, 2021.2,
                    2021.2, 2021.2, 2021.2,
                    2021.2, 2021.2, 2021.2,
                    2021.3, 2021.3, 2021.3,
                    2021.3, 2021.3, 2021.3,
                    2021.3, 2021.3, 2021.3,
                    2021.4, 2021.4, 2021.4,
                    2021.4, 2021.4, 2021.4,
                    2021.4, 2021.4, 2021.4,
                    2022.1, 2022.1, 2022.1]
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=False,
                                       fiscal_start=1) for x in date_values]
        expected = [4, 4, 4,
                    1, 1, 1,
                    1, 1, 1,
                    1, 1, 1,
                    2, 2, 2,
                    2, 2, 2,
                    2, 2, 2,
                    3, 3, 3,
                    3, 3, 3,
                    3, 3, 3,
                    4, 4, 4,
                    4, 4, 4,
                    4, 4, 4,
                    1, 1, 1]
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=True,
                                       fiscal_start=2) for x in date_values]
        expected = [2021.4, 2021.4, 2021.4,
                    2021.4, 2021.4, 2021.4,
                    2022.1, 2022.1, 2022.1,
                    2022.1, 2022.1, 2022.1,
                    2022.1, 2022.1, 2022.1,
                    2022.2, 2022.2, 2022.2,
                    2022.2, 2022.2, 2022.2,
                    2022.2, 2022.2, 2022.2,
                    2022.3, 2022.3, 2022.3,
                    2022.3, 2022.3, 2022.3,
                    2022.3, 2022.3, 2022.3,
                    2022.4, 2022.4, 2022.4,
                    2022.4, 2022.4, 2022.4,
                    2022.4, 2022.4, 2022.4]
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=False,
                                       fiscal_start=2) for x in date_values]
        expected = [4, 4, 4,
                    4, 4, 4,
                    1, 1, 1,
                    1, 1, 1,
                    1, 1, 1,
                    2, 2, 2,
                    2, 2, 2,
                    2, 2, 2,
                    3, 3, 3,
                    3, 3, 3,
                    3, 3, 3,
                    4, 4, 4,
                    4, 4, 4,
                    4, 4, 4]
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=True,
                                       fiscal_start=12) for x in date_values]
        expected = [2021.1, 2021.1, 2021.1,  # 2020-Dec
                    2021.1, 2021.1, 2021.1,  # 2021-Jan
                    2021.1, 2021.1, 2021.1,  # 2021-Feb
                    2021.2, 2021.2, 2021.2,  # 2021-Mar
                    2021.2, 2021.2, 2021.2,  # 2021-Apr
                    2021.2, 2021.2, 2021.2,  # 2021-May
                    2021.3, 2021.3, 2021.3,  # 2021-Jun
                    2021.3, 2021.3, 2021.3,  # 2021-Jul
                    2021.3, 2021.3, 2021.3,  # 2021-Aug
                    2021.4, 2021.4, 2021.4,  # 2021-Sep
                    2021.4, 2021.4, 2021.4,  # 2021-Oct
                    2021.4, 2021.4, 2021.4,  # 2021-Nov
                    2022.1, 2022.1, 2022.1,  # 2021-Dec
                    2022.1, 2022.1, 2022.1]  # 2022-Jan
        assert results == expected

        results = [date.fiscal_quarter(value=date.ymd(x),
                                       include_year=False,
                                       fiscal_start=12) for x in date_values]
        expected = [1, 1, 1,  # 2020-Dec
                    1, 1, 1,  # 2021-Jan
                    1, 1, 1,  # 2021-Feb
                    2, 2, 2,  # 2021-Mar
                    2, 2, 2,  # 2021-Apr
                    2, 2, 2,  # 2021-May
                    3, 3, 3,  # 2021-Jun
                    3, 3, 3,  # 2021-Jul
                    3, 3, 3,  # 2021-Aug
                    4, 4, 4,  # 2021-Sep
                    4, 4, 4,  # 2021-Oct
                    4, 4, 4,  # 2021-Nov
                    1, 1, 1,  # 2021-Dec
                    1, 1, 1]  # 2022-Jan
        assert results == expected

    def test_to_string_date(self):
        date_values = ['2020-12-01', '2020-12-15', '2020-12-31',
                       '2021-01-01', '2021-01-15', '2021-01-31',
                       '2021-02-01', '2021-02-15', '2021-02-28',
                       '2021-03-01', '2021-03-15', '2021-03-31',
                       '2021-04-01', '2021-04-15', '2021-04-30',
                       '2021-05-01', '2021-05-15', '2021-05-31',
                       '2021-06-01', '2021-06-15', '2021-06-30',
                       '2021-07-01', '2021-07-15', '2021-07-31',
                       '2021-08-01', '2021-08-15', '2021-08-31',
                       '2021-09-01', '2021-09-15', '2021-09-30',
                       '2021-10-01', '2021-10-15', '2021-10-31',
                       '2021-11-01', '2021-11-15', '2021-11-30',
                       '2021-12-01', '2021-12-15', '2021-12-31',
                       '2022-01-01', '2022-01-15', '2022-01-31']

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.DAY) for x in date_values]
        assert results == date_values

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.MONTH) for x in date_values]
        expected = ['2020-Dec', '2020-Dec', '2020-Dec',
                    '2021-Jan', '2021-Jan', '2021-Jan',
                    '2021-Feb', '2021-Feb', '2021-Feb',
                    '2021-Mar', '2021-Mar', '2021-Mar',
                    '2021-Apr', '2021-Apr', '2021-Apr',
                    '2021-May', '2021-May', '2021-May',
                    '2021-Jun', '2021-Jun', '2021-Jun',
                    '2021-Jul', '2021-Jul', '2021-Jul',
                    '2021-Aug', '2021-Aug', '2021-Aug',
                    '2021-Sep', '2021-Sep', '2021-Sep',
                    '2021-Oct', '2021-Oct', '2021-Oct',
                    '2021-Nov', '2021-Nov', '2021-Nov',
                    '2021-Dec', '2021-Dec', '2021-Dec',
                    '2022-Jan', '2022-Jan', '2022-Jan']
        assert results == expected

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.QUARTER,
                                  fiscal_start=1) for x in date_values]
        expected = ['2020-Q4', '2020-Q4', '2020-Q4',  # 2020-Dec
                    '2021-Q1', '2021-Q1', '2021-Q1',  # 2021-Jan
                    '2021-Q1', '2021-Q1', '2021-Q1',  # 2021-Feb
                    '2021-Q1', '2021-Q1', '2021-Q1',  # 2021-Mar
                    '2021-Q2', '2021-Q2', '2021-Q2',  # 2021-Apr
                    '2021-Q2', '2021-Q2', '2021-Q2',  # 2021-May
                    '2021-Q2', '2021-Q2', '2021-Q2',  # 2021-Jun
                    '2021-Q3', '2021-Q3', '2021-Q3',  # 2021-Jul
                    '2021-Q3', '2021-Q3', '2021-Q3',  # 2021-Aug
                    '2021-Q3', '2021-Q3', '2021-Q3',  # 2021-Sep
                    '2021-Q4', '2021-Q4', '2021-Q4',  # 2021-Oct
                    '2021-Q4', '2021-Q4', '2021-Q4',  # 2021-Nov
                    '2021-Q4', '2021-Q4', '2021-Q4',  # 2021-Dec
                    '2022-Q1', '2022-Q1', '2022-Q1']  # 2022-Jan
        assert results == expected

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.QUARTER,
                                  fiscal_start=2) for x in date_values]
        expected = ['2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2020-Dec
                    '2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2021-Jan
                    '2022-FQ1', '2022-FQ1', '2022-FQ1',  # 2021-Feb
                    '2022-FQ1', '2022-FQ1', '2022-FQ1',  # 2021-Mar
                    '2022-FQ1', '2022-FQ1', '2022-FQ1',  # 2021-Apr
                    '2022-FQ2', '2022-FQ2', '2022-FQ2',  # 2021-May
                    '2022-FQ2', '2022-FQ2', '2022-FQ2',  # 2021-Jun
                    '2022-FQ2', '2022-FQ2', '2022-FQ2',  # 2021-Jul
                    '2022-FQ3', '2022-FQ3', '2022-FQ3',  # 2021-Aug
                    '2022-FQ3', '2022-FQ3', '2022-FQ3',  # 2021-Sep
                    '2022-FQ3', '2022-FQ3', '2022-FQ3',  # 2021-Oct
                    '2022-FQ4', '2022-FQ4', '2022-FQ4',  # 2021-Nov
                    '2022-FQ4', '2022-FQ4', '2022-FQ4',  # 2021-Dec
                    '2022-FQ4', '2022-FQ4', '2022-FQ4']  # 2022-Jan
        assert results == expected

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.QUARTER,
                                  fiscal_start=12) for x in date_values]
        expected = ['2021-FQ1', '2021-FQ1', '2021-FQ1',  # 2020-Dec
                    '2021-FQ1', '2021-FQ1', '2021-FQ1',  # 2021-Jan
                    '2021-FQ1', '2021-FQ1', '2021-FQ1',  # 2021-Feb
                    '2021-FQ2', '2021-FQ2', '2021-FQ2',  # 2021-Mar
                    '2021-FQ2', '2021-FQ2', '2021-FQ2',  # 2021-Apr
                    '2021-FQ2', '2021-FQ2', '2021-FQ2',  # 2021-May
                    '2021-FQ3', '2021-FQ3', '2021-FQ3',  # 2021-Jun
                    '2021-FQ3', '2021-FQ3', '2021-FQ3',  # 2021-Jul
                    '2021-FQ3', '2021-FQ3', '2021-FQ3',  # 2021-Aug
                    '2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2021-Sep
                    '2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2021-Oct
                    '2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2021-Nov
                    '2022-FQ1', '2022-FQ1', '2022-FQ1',  # 2021-Dec
                    '2022-FQ1', '2022-FQ1', '2022-FQ1']  # 2022-Jan
        assert results == expected

    def test_to_string_datetime(self):
        date_values = ['2020-12-01', '2020-12-15', '2020-12-31',
                       '2021-01-01', '2021-01-15', '2021-01-31',
                       '2021-02-01', '2021-02-15', '2021-02-28',
                       '2021-03-01', '2021-03-15', '2021-03-31',
                       '2021-04-01', '2021-04-15', '2021-04-30',
                       '2021-05-01', '2021-05-15', '2021-05-31',
                       '2021-06-01', '2021-06-15', '2021-06-30',
                       '2021-07-01', '2021-07-15', '2021-07-31',
                       '2021-08-01', '2021-08-15', '2021-08-31',
                       '2021-09-01', '2021-09-15', '2021-09-30',
                       '2021-10-01', '2021-10-15', '2021-10-31',
                       '2021-11-01', '2021-11-15', '2021-11-30',
                       '2021-12-01', '2021-12-15', '2021-12-31',
                       '2022-01-01', '2022-01-15', '2022-01-31']

        results = [date.to_string(value=date.ymd_hms(x + ' 23:59:59'),
                                  granularity=date.Granularity.DAY) for x in date_values]
        assert results == date_values

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.MONTH) for x in date_values]
        expected = ['2020-Dec', '2020-Dec', '2020-Dec',
                    '2021-Jan', '2021-Jan', '2021-Jan',
                    '2021-Feb', '2021-Feb', '2021-Feb',
                    '2021-Mar', '2021-Mar', '2021-Mar',
                    '2021-Apr', '2021-Apr', '2021-Apr',
                    '2021-May', '2021-May', '2021-May',
                    '2021-Jun', '2021-Jun', '2021-Jun',
                    '2021-Jul', '2021-Jul', '2021-Jul',
                    '2021-Aug', '2021-Aug', '2021-Aug',
                    '2021-Sep', '2021-Sep', '2021-Sep',
                    '2021-Oct', '2021-Oct', '2021-Oct',
                    '2021-Nov', '2021-Nov', '2021-Nov',
                    '2021-Dec', '2021-Dec', '2021-Dec',
                    '2022-Jan', '2022-Jan', '2022-Jan']
        assert results == expected

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.QUARTER,
                                  fiscal_start=1) for x in date_values]
        expected = ['2020-Q4', '2020-Q4', '2020-Q4',  # 2020-Dec
                    '2021-Q1', '2021-Q1', '2021-Q1',  # 2021-Jan
                    '2021-Q1', '2021-Q1', '2021-Q1',  # 2021-Feb
                    '2021-Q1', '2021-Q1', '2021-Q1',  # 2021-Mar
                    '2021-Q2', '2021-Q2', '2021-Q2',  # 2021-Apr
                    '2021-Q2', '2021-Q2', '2021-Q2',  # 2021-May
                    '2021-Q2', '2021-Q2', '2021-Q2',  # 2021-Jun
                    '2021-Q3', '2021-Q3', '2021-Q3',  # 2021-Jul
                    '2021-Q3', '2021-Q3', '2021-Q3',  # 2021-Aug
                    '2021-Q3', '2021-Q3', '2021-Q3',  # 2021-Sep
                    '2021-Q4', '2021-Q4', '2021-Q4',  # 2021-Oct
                    '2021-Q4', '2021-Q4', '2021-Q4',  # 2021-Nov
                    '2021-Q4', '2021-Q4', '2021-Q4',  # 2021-Dec
                    '2022-Q1', '2022-Q1', '2022-Q1']  # 2022-Jan
        assert results == expected

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.QUARTER,
                                  fiscal_start=2) for x in date_values]
        expected = ['2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2020-Dec
                    '2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2021-Jan
                    '2022-FQ1', '2022-FQ1', '2022-FQ1',  # 2021-Feb
                    '2022-FQ1', '2022-FQ1', '2022-FQ1',  # 2021-Mar
                    '2022-FQ1', '2022-FQ1', '2022-FQ1',  # 2021-Apr
                    '2022-FQ2', '2022-FQ2', '2022-FQ2',  # 2021-May
                    '2022-FQ2', '2022-FQ2', '2022-FQ2',  # 2021-Jun
                    '2022-FQ2', '2022-FQ2', '2022-FQ2',  # 2021-Jul
                    '2022-FQ3', '2022-FQ3', '2022-FQ3',  # 2021-Aug
                    '2022-FQ3', '2022-FQ3', '2022-FQ3',  # 2021-Sep
                    '2022-FQ3', '2022-FQ3', '2022-FQ3',  # 2021-Oct
                    '2022-FQ4', '2022-FQ4', '2022-FQ4',  # 2021-Nov
                    '2022-FQ4', '2022-FQ4', '2022-FQ4',  # 2021-Dec
                    '2022-FQ4', '2022-FQ4', '2022-FQ4']  # 2022-Jan
        assert results == expected

        results = [date.to_string(value=date.ymd(x),
                                  granularity=date.Granularity.QUARTER,
                                  fiscal_start=12) for x in date_values]
        expected = ['2021-FQ1', '2021-FQ1', '2021-FQ1',  # 2020-Dec
                    '2021-FQ1', '2021-FQ1', '2021-FQ1',  # 2021-Jan
                    '2021-FQ1', '2021-FQ1', '2021-FQ1',  # 2021-Feb
                    '2021-FQ2', '2021-FQ2', '2021-FQ2',  # 2021-Mar
                    '2021-FQ2', '2021-FQ2', '2021-FQ2',  # 2021-Apr
                    '2021-FQ2', '2021-FQ2', '2021-FQ2',  # 2021-May
                    '2021-FQ3', '2021-FQ3', '2021-FQ3',  # 2021-Jun
                    '2021-FQ3', '2021-FQ3', '2021-FQ3',  # 2021-Jul
                    '2021-FQ3', '2021-FQ3', '2021-FQ3',  # 2021-Aug
                    '2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2021-Sep
                    '2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2021-Oct
                    '2021-FQ4', '2021-FQ4', '2021-FQ4',  # 2021-Nov
                    '2022-FQ1', '2022-FQ1', '2022-FQ1',  # 2021-Dec
                    '2022-FQ1', '2022-FQ1', '2022-FQ1']  # 2022-Jan
        assert results == expected

    def test_floor_day(self):
        # test datetime
        value = datetime.datetime(year=2021, month=2, day=13, hour=23, minute=45, second=55)
        assert date.floor(value, granularity=date.Granularity.DAY) == date.ymd('2021-02-13')
        assert date.floor(value) == date.ymd('2021-02-13')
        # test date
        value = datetime.date(year=2021, month=2, day=13)
        assert date.floor(value, granularity=date.Granularity.DAY) == date.ymd('2021-02-13')
        assert date.floor(value) == date.ymd('2021-02-13')

    def test_floor_month(self):
        # test datetime
        value = datetime.datetime(year=2021, month=1, day=1, hour=23, minute=45, second=55)
        assert date.floor(value, granularity=date.Granularity.MONTH) == date.ymd('2021-01-01')
        value = datetime.datetime(year=2021, month=1, day=31, hour=23, minute=45, second=55)
        assert date.floor(value, granularity=date.Granularity.MONTH) == date.ymd('2021-01-01')
        value = datetime.datetime(year=2021, month=12, day=1, hour=23, minute=45, second=55)
        assert date.floor(value, granularity=date.Granularity.MONTH) == date.ymd('2021-12-01')
        value = datetime.datetime(year=2021, month=12, day=31, hour=23, minute=45, second=55)
        assert date.floor(value, granularity=date.Granularity.MONTH) == date.ymd('2021-12-01')

        # test date
        assert date.floor(date.ymd('2021-01-01'), granularity=date.Granularity.MONTH) == date.ymd('2021-01-01')
        assert date.floor(date.ymd('2021-01-31'), granularity=date.Granularity.MONTH) == date.ymd('2021-01-01')
        assert date.floor(date.ymd('2021-12-01'), granularity=date.Granularity.MONTH) == date.ymd('2021-12-01')
        assert date.floor(date.ymd('2021-12-31'), granularity=date.Granularity.MONTH) == date.ymd('2021-12-01')

    def test_floor_quarter(self):
        # default argument fiscal_start of 1
        assert date.floor(date.ymd('2021-01-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-01-01')
        assert date.floor(date.ymd('2021-01-31'), granularity=date.Granularity.QUARTER) == date.ymd('2021-01-01')
        assert date.floor(date.ymd('2021-02-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-01-01')
        assert date.floor(date.ymd('2021-02-28'), granularity=date.Granularity.QUARTER) == date.ymd('2021-01-01')
        assert date.floor(date.ymd('2021-03-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-01-01')
        assert date.floor(date.ymd('2021-03-31'), granularity=date.Granularity.QUARTER) == date.ymd('2021-01-01')
        assert date.floor(date.ymd('2021-04-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-04-01')
        assert date.floor(date.ymd('2021-04-30'), granularity=date.Granularity.QUARTER) == date.ymd('2021-04-01')
        assert date.floor(date.ymd('2021-05-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-04-01')
        assert date.floor(date.ymd('2021-05-31'), granularity=date.Granularity.QUARTER) == date.ymd('2021-04-01')
        assert date.floor(date.ymd('2021-06-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-04-01')
        assert date.floor(date.ymd('2021-06-30'), granularity=date.Granularity.QUARTER) == date.ymd('2021-04-01')
        assert date.floor(date.ymd('2021-07-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-07-01')
        assert date.floor(date.ymd('2021-07-31'), granularity=date.Granularity.QUARTER) == date.ymd('2021-07-01')
        assert date.floor(date.ymd('2021-08-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-07-01')
        assert date.floor(date.ymd('2021-08-31'), granularity=date.Granularity.QUARTER) == date.ymd('2021-07-01')
        assert date.floor(date.ymd('2021-09-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-07-01')
        assert date.floor(date.ymd('2021-09-30'), granularity=date.Granularity.QUARTER) == date.ymd('2021-07-01')
        assert date.floor(date.ymd('2021-10-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-10-01')
        assert date.floor(date.ymd('2021-10-31'), granularity=date.Granularity.QUARTER) == date.ymd('2021-10-01')
        assert date.floor(date.ymd('2021-11-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-10-01')
        assert date.floor(date.ymd('2021-11-30'), granularity=date.Granularity.QUARTER) == date.ymd('2021-10-01')
        assert date.floor(date.ymd('2021-12-01'), granularity=date.Granularity.QUARTER) == date.ymd('2021-10-01')
        assert date.floor(date.ymd('2021-12-31'), granularity=date.Granularity.QUARTER) == date.ymd('2021-10-01')

        # fiscal quarter starts in February
        assert date.floor(date.ymd('2021-01-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2020-11-01')
        assert date.floor(date.ymd('2021-01-31'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2020-11-01')
        assert date.floor(date.ymd('2021-02-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-02-28'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-03-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-03-31'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-04-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-04-30'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-05-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-05-31'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-06-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-06-30'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-07-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-07-31'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-08-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-08-31'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-09-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-09-30'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-10-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-10-31'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-11-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-11-01')
        assert date.floor(date.ymd('2021-11-30'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-11-01')
        assert date.floor(date.ymd('2021-12-01'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-11-01')
        assert date.floor(date.ymd('2021-12-31'), granularity=date.Granularity.QUARTER, fiscal_start=2) == date.ymd('2021-11-01')

        # fiscal quarter starts in November (should be same as February)
        assert date.floor(date.ymd('2021-01-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2020-11-01')
        assert date.floor(date.ymd('2021-01-31'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2020-11-01')
        assert date.floor(date.ymd('2021-02-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-02-28'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-03-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-03-31'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-04-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-04-30'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-02-01')
        assert date.floor(date.ymd('2021-05-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-05-31'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-06-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-06-30'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-07-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-07-31'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-05-01')
        assert date.floor(date.ymd('2021-08-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-08-31'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-09-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-09-30'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-10-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-10-31'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-08-01')
        assert date.floor(date.ymd('2021-11-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-11-01')
        assert date.floor(date.ymd('2021-11-30'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-11-01')
        assert date.floor(date.ymd('2021-12-01'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-11-01')
        assert date.floor(date.ymd('2021-12-31'), granularity=date.Granularity.QUARTER, fiscal_start=11) == date.ymd('2021-11-01')

        # fiscal quarter starts in June
        assert date.floor(date.ymd('2021-01-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2020-12-01')
        assert date.floor(date.ymd('2021-01-31'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2020-12-01')
        assert date.floor(date.ymd('2021-02-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2020-12-01')
        assert date.floor(date.ymd('2021-02-28'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2020-12-01')
        assert date.floor(date.ymd('2021-03-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-03-01')
        assert date.floor(date.ymd('2021-03-31'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-03-01')
        assert date.floor(date.ymd('2021-04-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-03-01')
        assert date.floor(date.ymd('2021-04-30'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-03-01')
        assert date.floor(date.ymd('2021-05-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-03-01')
        assert date.floor(date.ymd('2021-05-31'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-03-01')
        assert date.floor(date.ymd('2021-06-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-06-01')
        assert date.floor(date.ymd('2021-06-30'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-06-01')
        assert date.floor(date.ymd('2021-07-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-06-01')
        assert date.floor(date.ymd('2021-07-31'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-06-01')
        assert date.floor(date.ymd('2021-08-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-06-01')
        assert date.floor(date.ymd('2021-08-31'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-06-01')
        assert date.floor(date.ymd('2021-09-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-09-01')
        assert date.floor(date.ymd('2021-09-30'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-09-01')
        assert date.floor(date.ymd('2021-10-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-09-01')
        assert date.floor(date.ymd('2021-10-31'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-09-01')
        assert date.floor(date.ymd('2021-11-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-09-01')
        assert date.floor(date.ymd('2021-11-30'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-09-01')
        assert date.floor(date.ymd('2021-12-01'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-12-01')
        assert date.floor(date.ymd('2021-12-31'), granularity=date.Granularity.QUARTER, fiscal_start=6) == date.ymd('2021-12-01')
