"""
Compare two sources of data
"""
import argparse
import os
import pandas as pd
from pprint import pprint
from datetime import datetime
from eagle.eagle_heart.configs import FMT_DATE_CONSTANT_TIME, FMT_68
from eagle.eagle_heart.data_utils import load_tickers_list
from eagle.eagle_downloader.vnd_downloader.qnaut import Stock

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--vnd_data_path',
        help='path to vnd stock data',
        # default='./test_database/test_vnd_vs_cophieu68/2021-06-18/stock_HPG/HPG_price_hist_daily.csv',
        default='./eagle_datastore/vnd_datastore/2021-06-18/',
    )
    parser.add_argument(
        '--cophieu68_data_path',
        help='path to cophieu68 stock data',
        # default='./test_database/test_vnd_vs_cophieu68/hpg-9.txt',
        default='./eagle_datastore/data_refs/amibroker_all_data_2.txt',
    )
    parser.add_argument(
        '--ticker', help='input ticker to load data', default='all',
    )
    # parser.add_argument(
    #     '--start', help='start date to check', default=None,
    # )
    # parser.add_argument(
    #     '--end', help='end date to check', default=None,
    # )
    return parser

def extract_cophieu68_all(data_all, ticker=""):
    # data = pd.read_csv(input_file)
    data = data_all[data_all['<Ticker>'] == ticker]
    return data

def parse_cophieu68(cophieu68_data):
    data = pd.DataFrame()
    data['Date'] = pd.to_datetime(cophieu68_data['<DTYYYYMMDD>'], format=FMT_68)
    data['Close'] = cophieu68_data['<Close>']
    data['Open'] = cophieu68_data['<Open>']
    data['High'] = cophieu68_data['<High>']
    data['Low'] = cophieu68_data['<Low>']
    data['Volumn'] = cophieu68_data['<Volume>']
    data = data.sort_values("Date")
    return data
    
def parse_vnd(vnd_data):
    data = vnd_data
    data['Date'] = pd.to_datetime(data['Date'], format=FMT_DATE_CONSTANT_TIME)
    return data

def calc_diff(vnd_data, cophieu68_data):
    res = vnd_data.merge(cophieu68_data, how='inner', right_index=True, left_index=False, on='Date')
    res['Delta_Close'] = res['Close_y'] - res['Close_x']
    res['Delta_Open'] = res['Open_y'] - res['Open_x']
    res['Delta_High'] = res['High_y'] - res['High_x']
    res['Delta_Low'] = res['Low_y'] - res['Low_x']
    res['Delta_Volumn'] = res['Volumn_y'] - res['Volumn_x']
    return res

def report(res, out_csv=None):
    max_delta_close = max(res.Delta_Close.abs())
    max_delta_open = max(res.Delta_Open.abs())
    max_delta_high = max(res.Delta_High.abs())
    max_delta_low = max(res.Delta_Low.abs())
    max_delta_volumn = max(res.Delta_Volumn.abs())
    return max_delta_close, max_delta_open, max_delta_high, max_delta_low, max_delta_volumn
    # print(f"max of delta close - {max_delta_close}")
    # print(f"max of delta open - {max_delta_open}")
    # print(f"max of delta high - {max_delta_high}")
    # print(f"max of delta low - {max_delta_low}")
    # print(f"max of delta volumn - {max_delta_volumn}")
    # res.to_csv(out_csv)

def main():
    parser = parse_arguments()
    args = parser.parse_args()
    # from_vnd = parse_vnd(pd.read_csv(args.vnd_data_path))
    # print(from_vnd)
    # from_cophieu68 = parse_cophieu68(pd.read_csv(args.cophieu68_data_path))
    # print(from_cophieu68)
    # res = calc_diff(from_vnd, from_cophieu68)
    # report_diff(res=res, out_csv="diff_vnd_cophieu68.csv")
    
    if args.ticker == "all":
        tickers_list = load_tickers_list()
    else:
        tickers_list = [args.ticker]

    cophieu68_data_all = pd.read_csv(args.cophieu68_data_path)
    
    diff_df = pd.DataFrame(columns=['ticker', 'max_delta_close', 'max_delta_open', 'max_delta_high', 'max_delta_low', 'max_delta_volumn'])
    count = -1
    for ticker in tickers_list:
        stock = Stock(symbol=ticker)
        if not stock.is_exists():
            continue
        print(f"processing {ticker}..")
        vnd_path = os.path.join(args.vnd_data_path, f"stock_{ticker}", f"{ticker}_price_hist_daily.csv")
        assert os.path.isfile(vnd_path), f"{vnd_path} does not exist"
        vnd_data = parse_vnd(pd.read_csv(vnd_path))
        cophieu68_data = parse_cophieu68(extract_cophieu68_all(cophieu68_data_all, ticker=ticker))
        max_delta_close, max_delta_open, max_delta_high, max_delta_low, max_delta_volumn = report(calc_diff(vnd_data, cophieu68_data))
        count += 1
        diff_df.loc[count] = [ticker, max_delta_close, max_delta_open, max_delta_high, max_delta_low, max_delta_volumn]
        # diff_df.append(
        #     {
        #         "ticker": ticker,
        #         "max_delta_close": max_delta_close,
        #         "max_delta_open": max_delta_open, 
        #         "max_delta_high": max_delta_high,
        #         "max_delta_low": max_delta_low,
        #         "max_delta_volumn": max_delta_volumn,
        #     }
        #     )
    diff_df.to_csv("diff_vnd_cophieu68_all.csv")

if __name__ == '__main__':
    main()
