import pandas as pd
from ....manager.data_tables import StockInfoDataTables


def unify_dates(sdt: StockInfoDataTables):
    finance = sdt.finance
    finance = pd.concat([finance, sdt.real_dates], axis=1)
    finance = finance.drop_duplicates(subset=['stmt_act_date'], keep='last')
    finance = finance.set_index('stmt_act_date')
    finance = finance.dropna(axis=0, how='all')

    equity = sdt.equity.reindex(sdt.prices.index)
    df = pd.concat([finance, sdt.prices, equity, sdt.dividend], axis=1)
    df['日涨跌'] = df['收盘价'] / df['收盘价'].shift(1) - 1
    df = df.sort_index()
    df = df.fillna(method='pad')

    return df


def compute_value_ratios(sdt: StockInfoDataTables):
    df = unify_dates(sdt)

    df['总市值'] = df['收盘价'] * df['总股本']
    df['年度派息总额'] = df['每股股息'] * df['总股本']
    df['TTM.市盈率'] = df['总市值'] / df['TTM.归属于母公司股东的净利润']
    df['市净率'] = df['总市值'] / df['净资产']
    df['TTM.市销率'] = df['总市值'] / df['TTM.营业总收入']
    df['TTM.市现率'] = df['总市值'] / df['TTM.经营活动产生的现金流量净额']
    df['市息率'] = df['总市值'] / df['年度派息总额']
    df['股息率'] = df['年度派息总额'] / df['总市值']
    df['TTM.派息率'] = df['年度派息总额'] / df['TTM.归属于母公司股东的净利润']

    df['每股净资产'] = df['净资产'] / df['总股本']

    df['PEG'] = df['TTM.市盈率'] / df['近1年净利润增速']
    return df[[
        'TTM.市盈率',
        '市净率',
        'TTM.市销率',
        'TTM.市现率',
        '市息率',
        '股息率',
        'TTM.派息率',
        '每股净资产',
        'PEG',
        '收盘价',
        '日涨跌',
        '总市值',
        '年度派息总额',
        '总股本',
        'TTM.归属于母公司股东的净利润',
        '净资产',
        'TTM.营业总收入',
        'TTM.经营活动产生的现金流量净额',
    ]]

