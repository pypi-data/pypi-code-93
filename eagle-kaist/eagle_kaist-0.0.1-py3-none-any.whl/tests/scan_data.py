import os
import pandas as pd
import json
from pprint import pprint
from eagle.eagle_downloader.vnd_downloader.qnaut import Stock
from eagle.paw import get_cophieu68_data, reformat_data

FMT_DAY_CONSTANT_HOUR = '%Y-%m-%d 07:00:00+07:00'
import datetime
NOW = datetime.datetime.now()#.strftime('%Y-%m-%d')

def check_sectors(input_file):
    with open(input_file) as fp:
        data = json.load(fp)
        print(data)
        print(len(data))
        return data

def parse_vnd(vnd_data):
    data = vnd_data
    data['Date'] = pd.to_datetime(data['Date'], format=FMT_DAY_CONSTANT_HOUR)
    return data


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

## create group_tickers.json
# vn30_tickers = load_tickers_list("./eagle_datastore/data_refs/vn30.txt")
# all_tickers = load_tickers_list("./eagle_datastore/data_refs/tickers.txt")
# data = check_sectors("./eagle_datastore/data_refs/sector_tickers.json")
# data['vn30'] = vn30_tickers
# data['all'] = all_tickers
# pprint(data)

# with open("./eagle_datastore/data_refs/group_tickers.json", "w") as fp:
#     json.dump(data, fp)

## time division
all_tickers = load_tickers_list("./eagle/eagle_datastore/data_refs/tickers.txt")

time_tickers = {
    "groupA": [], # history length is over 1800 days
    "groupB": [], # history length is from 1500 to 1800 days
    "groupC": [], # history length is from 1200 to 1500 days
    "groupD": [], # history length is from 900 to 1200 days
    "groupE": [], # history length is from 600 to 900 days
    "groupF": [], # history length is from 300 to 600 days
    "groupG": [], # history length is under 300 days
}
time_df = pd.DataFrame(columns=['ticker', 'startDate', 'historyLength', 'group'])
count = -1
data_all = get_cophieu68_data()
data_all = reformat_data(data_all, source='COPHIEU68')
for ticker in all_tickers:
    stock = Stock(symbol=ticker)
    if not stock.is_exists():
        continue
    # input_file = (f"./eagle_datastore/vnd_datastore/2021-06-18/stock_{ticker}/{ticker}_price_hist_daily.csv")
    # data = parse_vnd(pd.read_csv(input_file))
    data = data_all[data_all['Ticker'] == ticker]
    start = min(data['Date'])
    diff = (NOW - start).days
    print(f'{ticker} - {diff}')
    # time_tickers[ticker] = {"start_date": start, "history_length": diff}
    if diff >= 1800:
        time_tickers['groupA'].append(ticker)
        gr = "A"
    elif 1500 <= diff < 1800:
        time_tickers['groupB'].append(ticker)
        gr = "B"
    elif 1200 <= diff < 1500:
        time_tickers['groupC'].append(ticker)
        gr = "C"
    elif 900 <= diff < 1200:
        time_tickers['groupD'].append(ticker)
        gr = "D"
    elif 600 <= diff < 900:
        time_tickers['groupE'].append(ticker)
        gr = "E"
    elif 300 <= diff < 600:
        time_tickers['groupF'].append(ticker)
        gr = "F"
    else:
        time_tickers['groupG'].append(ticker)
        gr = "G"
    count += 1
    time_df.loc[count] = [ticker, start, diff, gr]

with open("./eagle/eagle_datastore/data_refs/time_tickers_COPHIEU68.json", "w") as fp:
    json.dump(time_tickers, fp)
    
time_df.to_csv('time_tickers_COPHIEU68.csv')


# def parse_arguments():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         '--vnd_data_path',
#         help='path to vnd stock data',
#         # default='./test_database/test_vnd_vs_cophieu68/2021-06-18/stock_HPG/HPG_price_hist_daily.csv',
#         default='./eagle_datastore/vnd_datastore/2021-06-18/',
#     )
#     return parser

# def main():
#     parser = parse_arguments()
#     args = parser.parse_args()
    
# if __name__ == "__main__":
#     main()
