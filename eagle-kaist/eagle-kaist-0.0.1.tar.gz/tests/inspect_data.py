import argparse
import os
import pandas as pd
from tests.verify_data import *

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--diff_path',
        help='path to diff file',
        default='./diff_vnd_cophieu68_all.csv',
    )
    parser.add_argument(
        '--ticker', help='input ticker to load data', default='',
    )
    return parser

def main():
    parser = parse_arguments()
    args = parser.parse_args()
    diff_data = pd.read_csv(args.diff_path)
    list_inspect_close = diff_data[diff_data['max_delta_close']>1].ticker.to_list()
    print(f"list_inspect_close - {list_inspect_close}")
    print(f"number - {len(list_inspect_close)}")

    ## Check VND:
    ticker = "SCS"
    vnd_data_path = f"./eagle_datastore/vnd_datastore/2021-06-18/stock_{ticker}/{ticker}_price_hist_daily.csv"
    vnd_data = parse_vnd(pd.read_csv(vnd_data_path))
    cophieu68_data_path = "./eagle_datastore/data_refs/amibroker_all_data_2.txt"
    cophieu68_data_all = pd.read_csv(cophieu68_data_path)
    cophieu68_data = parse_cophieu68(extract_cophieu68_all(cophieu68_data_all, ticker=ticker))
    diff_data_ticker = calc_diff(vnd_data, cophieu68_data)
    print(diff_data_ticker)
    diff_data_ticker.to_csv(f"diff_vnd_cophieu68_{ticker}.csv")

if __name__ == "__main__":
    main()
