from eagle.paw import check_data_update_date
from eagle.paw import get_cophieu68_data
from eagle.paw import list_group_of_stock
from eagle.paw import list_stock_from_group
from eagle.paw import get_history_range
from eagle.paw import extract_stock_from_cophieu68
from eagle.paw import reformat_data
import pandas as pd

# print(list_group_of_stock())
# print(list_stock_from_group("etf"))
# print(check_data_update_date())
# print(get_cophieu68_data())
# print(get_history_range("HPG"))
# import datetime

# print(extract_stock_from_cophieu68("HPG", start="2008-10-17"))

vn30_tickers = list_stock_from_group("vn30")
print(vn30_tickers)

data = get_cophieu68_data()
data = reformat_data(data, source='COPHIEU68')

time_range = pd.DataFrame(columns=['Ticker', 'Start_date', 'End_date'])
count = -1
for ticker in vn30_tickers:
    count += 1
    # print(ticker, get_history_range(data, ticker))
    start, end = get_history_range(data, ticker)
    time_range.loc[count] = [ticker, start, end]

time_range = time_range.sort_values('Start_date')
print(time_range)
time_range.to_csv("VN30_time_range.csv")
