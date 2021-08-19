import pandas as pd
from datetime import date, datetime, timedelta
from ....api.raw import RawDataApi, RawDatabaseConnector
from .constants import (
    STOCK_INCOME_MAPPING,
    STOCK_BALANCE_MAPPING,
    STOCK_CASH_FLOW_MAPPING,
    STOCK_CASH_FLOW_QUARTERLY_MAPPING,
    STOCK_INCOME_QUARTERLY_MAPPING
)


def read_balance_sheet(stock_id, columns: list):
    reverse_mapping = {v: k for k, v in STOCK_BALANCE_MAPPING.items()}
    columns = [reverse_mapping[i] for i in columns]
    df = RawDataApi().get_em_stock_balance(stock_id, columns)
    df = df.rename(columns=STOCK_BALANCE_MAPPING).set_index('财报日期')
    return df


def read_income_sheet(stock_id, columns: list):
    reverse_mapping = {v: k for k, v in STOCK_INCOME_MAPPING.items()}
    columns = [reverse_mapping[i] for i in columns]
    df = RawDataApi().get_em_stock_income(stock_id, columns)
    df = df.rename(columns=STOCK_INCOME_MAPPING).set_index('财报日期')
    return df


def read_cash_flow_sheet(stock_id, columns: list):
    reverse_mapping = {v: k for k, v in STOCK_CASH_FLOW_MAPPING.items()}
    columns = [reverse_mapping[i] for i in columns]
    df = RawDataApi().get_em_stock_cash_flow(stock_id, columns)
    df = df.rename(columns=STOCK_CASH_FLOW_MAPPING).set_index('财报日期')
    return df


def read_income_quarterly_sheet(stock_id, columns: list):
    reverse_mapping = {v: k for k, v in STOCK_INCOME_QUARTERLY_MAPPING.items()}
    columns = [reverse_mapping[i] for i in columns]
    df = RawDataApi().get_em_stock_income_quarterly(stock_id, columns)
    df = df.rename(columns=STOCK_INCOME_QUARTERLY_MAPPING)
    df = df.drop(columns=['_update_time', 'CODES']).set_index('财报日期')
    return df


def read_cash_flow_quarterly_sheet(stock_id, columns: list):
    reverse_mapping = {v: k for k, v in STOCK_CASH_FLOW_QUARTERLY_MAPPING.items()}
    columns = [reverse_mapping[i] for i in columns]
    df = RawDataApi().get_em_stock_cash_flow_quarterly(stock_id, columns)
    df = df.rename(columns=STOCK_CASH_FLOW_QUARTERLY_MAPPING)
    df = df.drop(columns=['_update_time', 'CODES']).set_index('财报日期')
    return df


def read_stock_dividend(stock_id):
    """
    将分红信息规整到年
    :param stock_id:
    :return: dividend_df
         CODES       DATES DIVPROGRESS  DIVCASHPSBFTAX DIVSTOCKPS DIVCAPITALIZATIONPS DIVPRENOTICEDATE DIVPLANANNCDATE DIVAGMANNCDATE DIVIMPLANNCDATE DIVRECORDDATE   DIVEXDATE  DIVPAYDATE DIVBONUSLISTEDDATE DIVOBJ DIVORNOT        _update_time dividend_type dividend_year
    0  002242.SZ  2018-12-31        实施分配            0.80       None                None             None      2019-03-30     2019-04-23      2019-05-08    2019-05-14  2019-05-15  2019-05-15               None   全体股东        是 2020-08-23 08:00:20             Y    2018-12-31
    1  002242.SZ  2019-06-30        实施分配            0.50       None                None             None      2019-08-15     2019-09-12      2019-09-25    2019-10-09  2019-10-10  2019-10-10               None   全体股东        是 2020-08-23 07:59:41             N    2019-12-31
    2  002242.SZ  2019-12-31        实施分配            0.58       None                None             None      2020-04-01     2020-04-29      2020-05-22    2020-05-28  2020-05-29  2020-05-29               None   全体股东        是 2020-08-23 07:58:43             Y    2019-12-31
    """
    df = RawDataApi().get_em_stock_dividend_by_id(stock_id)
    if len(df) < 1:
        return pd.DataFrame([], columns=['每股股息'])

    df['dividend_type'] = df['DATES'].apply(lambda x: 'Y' if x.strftime('%Y-%m-%d').endswith('12-31') else 'N')
    df['dividend_year'] = df['DATES'].apply(lambda x: date(x.year, 12, 31))

    dff = df[df['dividend_type'] == 'N']
    if len(dff) > 0:
        for index in dff.index:
            temp = df[(df['dividend_year'] == df.loc[index, 'dividend_year']) & (df['dividend_type'] == 'Y')]
            if len(temp) == 0:
                df.loc[index, 'dividend_type'] = 'Y'
            else:
                current_index = temp.index[0]
                df.loc[current_index, 'DIVCASHPSBFTAX'] += df.loc[index, 'DIVCASHPSBFTAX']

    df = df[df['dividend_type'] == 'Y']
    df = df.set_index('DIVEXDATE')
    df = df[['DIVCASHPSBFTAX']]
    df = df.rename(columns={'DIVCASHPSBFTAX': '每股股息'})
    return df


def read_stock_price_sheet(stock_id):
    prices = RawDataApi().get_em_stock_price(
        stock_list=[stock_id],
        columns=['close'],
        start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
    ).set_index('datetime')
    prices = prices[['close']]
    prices = prices.rename(columns={'close': '收盘价'})
    return prices


def read_stock_equity_sheet(stock_id):
    empties = RawDataApi().get_em_daily_info(
        stock_list=[stock_id],
        columns=['total_share']
    ).set_index('datetime')
    empties = empties[['total_share']]
    empties = empties.rename(columns={'total_share': '总股本'})
    return empties


def read_financial_real_publish_date(stock_id):
    real_dates = RawDataApi().get_em_stock_fin_fac(
        stock_list=[stock_id],
        columns=['stmt_act_date'],
    ).set_index('datetime')
    real_dates = real_dates[['stmt_act_date']]
    return real_dates

