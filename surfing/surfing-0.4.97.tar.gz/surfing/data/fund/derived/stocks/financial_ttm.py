import pandas as pd
from datetime import date
from .reader import read_income_quarterly_sheet, read_cash_flow_quarterly_sheet


def convert_quarterly_to_ttm(df: pd.DataFrame):
    """
    根据单季计算TTM
    :param df: columns 必须是日期，index 为财报条目
    :return:
    """
    dfc = df[sorted(list(df.columns))]
    dfc = dfc.rolling(4, min_periods=4, axis=1).sum()

    dfc = dfc.dropna(axis=1, how='all')
    return dfc


def handle_income_ttm(income: pd.DataFrame):
    income = income.T
    income_ttm = convert_quarterly_to_ttm(income)
    income_ttm.index = [x.replace('单季度.', 'TTM.') for x in income_ttm.index]
    return income_ttm.T


def handle_cash_flow_ttm(cash_flow: pd.DataFrame):
    df = cash_flow.T
    df_ttm = convert_quarterly_to_ttm(df)
    df_ttm.index = [x.replace('单季度.', 'TTM.') for x in df_ttm.index]
    return df_ttm.T

