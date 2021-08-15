# from vnquant.DataLoader import DataLoader as CAFEDataLoader
import datetime
import json
from pathlib import Path
import os
import pandas as pd
from eagle.eagle_downloader.vnd_downloader.qnaut import Stock

from eagle.eagle_heart.configs import (
    DATASTORE_COPHIEU68_PATH,
    DATASTORE_VND_PATH,
    FMT_68,
    FMT_DATE_CONSTANT_TIME,
    GROUP_TICKERS_PATH,
    LAST_UPDATED_ON,
    SECTOR_CODES_PATH,
    SECTOR_TICKERS_PATH,
)

from eagle.eagle_heart.data_utils import (
    reformat_cophieu68,
    reformat_vnd,
)

from eagle.eagle_heart.data_classes import (
    StockDataLoader as VNDDataLoader,
    StockTrader,
    StockDataBuilder,
    StockGroupDataBuilder,
)

root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")


def check_exist(ticker):
    """
    Check if one stock exists
    :param ticker: stock ticker
    :return: True if exists
    """
    stock = Stock(symbol=ticker, force_update=True)
    return stock.is_exists()


def get_common_info(ticker):
    """
    Get common information from given ticker
    :param ticker: stock ticker
    :return:
    """
    stock = Stock(ticker, )
    return stock.get_info()

def load_stock_from_vnd(ticker, target_folder, start, end):
    """
    Load stock from VNDirect
    : param ticker: stock ticker
    : param target_folder: target folder to load data to
    : param start: start date to load data from
    : param end: end date to load data to
    : return:
    """
    stock_loader = VNDDataLoader(
        ticker,
        target_folder,
        start,
        end,
    )
    stock_loader.load_all()


def load_stock_from_cafe(ticker, target_folder, start="2000-01-01", end="2022-01-01"):
    """
    Load stock from CAFEF
    : param ticker: stock ticker
    : param target_folder: target folder to load data to
    : param start: start date to load data from
    : param end: end date to load data to
    : return:
    """
    stock_dir = os.path.join(target_folder, LAST_UPDATED_ON, f"stock_{ticker}")
    os.makedirs(stock_dir, exist_ok=True)
    stock_loader = CAFEDataLoader(
        ticker,
        start,
        end,
        data_source="CAFE",
        minimal=False,
    )
    data = stock_loader.download()
    data.to_csv(os.path.join(stock_dir, f"{ticker}_price_hist_daily.csv"))


def extract_stock_from_vnd(ticker, start, end, normalize=False):
    pass


def extract_stock_from_cafe(ticker, start, end, normalize=False):
    pass


def extract_stock_from_cophieu68(data, ticker, start=None, end=None):
    """
    Extract stock prices from COPHIEU68
    : param ticker:
    : param start:
    : param end:
    : param normalize:
    """
    # data = get_cophieu68_data()
    # data = reformat_data(data, source='COPHIEU68')
    if check_exist(ticker):
        data = data[data["Ticker"] == ticker]
        if start:
            start = datetime.datetime.strptime(start, "%Y-%m-%d")
            data = data[data["Date"] > start]
        if end:
            end = datetime.datetime.strptime(end, "%Y-%m-%d")
            data = data[data["Date"] < end]
        return data




def list_stock_from_group(group_name="all"):
    """
    List all stocks from given group
    :param group_name: group name to query
    :return: list of tickers from given group
    """
    group_tickers_path = os.path.join(root_dir, GROUP_TICKERS_PATH)
    with open(group_tickers_path) as fp:
        data = json.load(fp)
        return data[group_name]


def list_group_of_stock():
    """
    List all groups of stock
    """
    group_tickers_path = os.path.join(root_dir, GROUP_TICKERS_PATH)
    with open(group_tickers_path) as fp:
        data = json.load(fp)
        return list(data.keys())


def check_data_update_date(source="COPHIEU68"):
    """
    Check the latest date from a datastore
    """
    if source == "VND":
        check_path = Path(DATASTORE_VND_PATH)
    elif source == "COPHIEU68":
        check_path = Path(DATASTORE_COPHIEU68_PATH)
    else:
        return
    ret = []
    if check_path.exists():
        for path in check_path.iterdir():
            if path.is_dir():
                try:
                    datetime.datetime.strptime(path.name, "%Y-%m-%d")
                    ret.append(path.name)
                except Exception as e:
                    print(f"error to parse {path.name} as datetime")
        return max(ret)


def get_cophieu68_data():
    """
    get all the latest data from COPHIEU68
    """
    source_path = Path(DATASTORE_COPHIEU68_PATH)
    update_date = check_data_update_date()
    if update_date:
        data_path = source_path.joinpath(update_date, "amibroker_all_data.txt")
        try:
            data = pd.read_csv(data_path)
            return data
        except Exception as e:
            print(f"error to load data from COPHIEU68 - {e}")


def get_history_range(data, ticker, source="COPHIEU68"):
    """
    Get the history range from given ticker
    """
    if source == "COPHIEU68":
        # data = get_cophieu68_data()
        # data = reformat_data(data, source='COPHIEU68')
        ret = []
        if check_exist(ticker):
            data = data[data["Ticker"] == ticker]
            start_date = min(data["Date"])
            end_date = max(data["Date"])
            print(end_date > start_date)
            return start_date, end_date
        else:
            return
    else:
        return


def reformat_data(input_data, source="COPHIEU68"):
    """
    Reformat the data given source
    """
    if source == "COPHIEU68":
        return reformat_cophieu68(input_data)
    elif source == "VND":
        return reformat_vnd(input_data)
    else:
        return
