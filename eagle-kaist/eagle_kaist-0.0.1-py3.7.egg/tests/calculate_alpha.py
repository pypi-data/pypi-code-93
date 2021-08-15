"""
Return = log(Close-today) - log(Close-yesterday)
Alpha(5 days) = sum(Return(5 days before today))
PNL(today) = Apha(yesterday) x Return(today)
"""

import os
import pandas as pd
import numpy as np
import json
from tests.verify_data import extract_cophieu68_all, parse_cophieu68
from functools import reduce


input_file = "./eagle/eagle_datastore/cophieu68_datastore/2021-06-18/amibroker_all_data_2.txt"

cophieu68_data_all = pd.read_csv(input_file)

def load_tickers_list(input_file):
    """
    Load tickers list from file
    """
    tickers_list = []
    with open(input_file) as fp:
        for line in fp:
            ticker = line.strip()
            tickers_list.append(ticker)
    return tickers_list

list_tickers = load_tickers_list("./eagle/eagle_datastore/data_refs/vn30.txt")
print(list_tickers)

df_list = []
# list_tickers = ["HDB"]
df_total_list = []
# df_total_shift_1_list = []
for ticker in list_tickers:
    print(f"processing - {ticker}")
    data  = parse_cophieu68(extract_cophieu68_all(cophieu68_data_all, ticker=ticker))
    # print(data)

    # data_HPG['test'] = data_HPG.Close.rolling(min_periods=1, window=5)
    # data['return'] = np.log10(data.Close) - np.log10(data.Close.shift(1))
    data['return'] = data.Close / data.Close.shift(1) - 1
    data.loc[data['return']< -0.07, 'return'] = -0.07
    data.loc[data['return']> 0.07, 'return'] = 0.07
    data['alpha'] = data['return'].shift(1).rolling(window=5).sum()
    # data['alpha'] = data[data['alpha'] > 0]
    data.loc[data['alpha']<0, 'alpha'] = 0
    data['pnl_daily'] = data['alpha'].shift(1) * data['return']
    data['pnl_daily_1'] = data['alpha'].shift(0) * data['return']
    # data['sharp'] = mean(data['pnl_daily_1']) / data['pnl_daily_1'].std()
    data['pnl_sum'] = data['pnl_daily'].cumsum()

    ret_data = pd.DataFrame()
    # ret_data['Date'] = data['Date']
    # ret_data[f'pnl_sum_{ticker}'] = data['pnl_sum']
    # df_list.append(ret_data)

    total_data = pd.DataFrame()
    total_data['Date'] = data['Date']
    total_data[f'pnl_daily_{ticker}'] = data['pnl_daily_1']
    total_data[f'pnl_daily_shift_1_{ticker}'] = data['pnl_daily_1'].shift(1)
    df_total_list.append(total_data)

    # total_shift_1_data = pd.DataFrame()
    # total_shift_1_data['Date'] = data['Date'].shift(1)
    # total_shift_1_data['pnl_daily_{ticker}'] = data['pnl_daily_1'].shift(1)
    # df_total_shift_1_list.append(total_shift_1_data)

    # print(data.head(100))
    # data_HPG.to_csv('HPG_cophieu68_pnl.csv')


# merged_df = reduce(lambda left, right: pd.merge(left, right, on='Date', how='outer'), df_list)
# merged_df['pnl_sum_total'] = sum(merged_df[f'pnl_sum_{ticker}'] for ticker in list_tickers)

merged_df_total = reduce(lambda left, right: pd.merge(left, right, on='Date', how='outer'), df_total_list)
print(merged_df_total)
merged_df_total['pnl_daily_total'] = sum(merged_df_total[f'pnl_daily_{ticker}'] for ticker in list_tickers).fillna(0)
merged_df_total['sharp_total'] = merged_df_total['pnl_daily_total'].mean() / merged_df_total['pnl_daily_total'].std() * np.sqrt(252)
merged_df_total['pnl_daily_total_cumsum'] = merged_df_total[f'pnl_daily_total'].cumsum()
merged_df_total['pnl_daily_total_shift_1'] = sum(merged_df_total[f'pnl_daily_shift_1_{ticker}'] for ticker in list_tickers).fillna(0)
merged_df_total['pnl_daily_total_cumsum_shift_1'] = merged_df_total[f'pnl_daily_total_shift_1'].cumsum()



# print(merged_df.head(20))
# print(merged_df.columns.values)
# print(merged_df.pnl_sum_total.sum())
# merged_df.to_csv("VN30_cophieu68_pnl_1.csv")

print(merged_df_total.head(20))
print(merged_df_total.columns.values)
# print(merged_df_total.pnl_sum_total.sum())
merged_df_total.to_csv("VN30_cophieu68_pnl_2.csv")
