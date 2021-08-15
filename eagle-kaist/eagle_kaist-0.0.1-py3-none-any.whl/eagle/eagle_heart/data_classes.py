import json
import os
from functools import reduce
from typing import List

import numpy as np
import pandas as pd

from eagle.eagle_downloader.vnd_downloader.qnaut import *
from eagle.eagle_heart.configs import LAST_UPDATED_ON

pd.options.mode.chained_assignment = None


class StockDataBuilder:
    """
    Data Builder for a Single Stock
    """

    def __init__(self, data, ticker):
        self.ticker = ticker
        self.start_date = min(data["Date"])
        self.end_date = max(data["Date"])
        self.data = self.calc_indicators(data)

    def calc_indicators(self, data):
        data["return"] = data["Close"] / data["Close"].shift(1) - 1
        data.loc[data["return"] <= -0.07, "return"] = -0.07
        data.loc[data["return"] >= 0.07, "return"] = 0.07
        # data['return'] = data['return'].clip(-0.07, 0.07)
        # data['return'].where(data['return'] <= -0.07, -0.07)
        # data['return'].where(data['return'] >= 0.07, 0.07)
        # data['return'][data['return'] < -0.07] = -0.07
        data["alpha"] = data["return"].shift(1).rolling(window=5).sum()
        data.loc[data["alpha"] <= 0, "alpha"] = 0.0
        data["pnl_daily"] = data["alpha"] * data["return"]
        # data['pnl_daily'] = data['pnl_daily'].fillna(0)
        data["pnl_sum"] = data["pnl_daily"].cumsum()
        data["sharpe"] = (
            data["pnl_daily"].mean() / data["pnl_daily"].std() * np.sqrt(252)
        )
        return data

    def present(self):
        print(f"Ticker - {self.ticker}")
        print(f"Start date - {self.start_date}")
        print(f"End date - {self.end_date}")
        print(f"Data - {self.data}")

    def to_csv(self, out_csv):
        self.data.to_csv(out_csv)


class StockGroupDataBuilder:
    """
    Data Builder for a Group of stocks
    """

    def __init__(self, stock_data_builders: List[StockDataBuilder]):
        self.data, self.tickers = self.merge(stock_data_builders)

    def merge(self, stock_data_builders):
        tickers = []
        df_total_list = []
        for stock_data_builder in stock_data_builders:
            ticker = stock_data_builder.ticker
            tickers.append(ticker)
            _data = pd.DataFrame()
            _data["Date"] = stock_data_builder.data["Date"]
            _data[f"pnl_daily_{ticker}"] = stock_data_builder.data["pnl_daily"]
            _data[f"sharpe_{ticker}"] = stock_data_builder.data["sharpe"]
            df_total_list.append(_data)
        data = reduce(
            lambda left, right: pd.merge(
                left,
                right,
                on="Date",
                how="inner",
            ),
            df_total_list,
        )
        print(data)
        data["pnl_daily_total"] = sum(data[f"pnl_daily_{ticker}"] for ticker in tickers)
        data["pnl_daily_total"] = data["pnl_daily_total"].fillna(0)
        data["sharpe_total"] = (
            data["pnl_daily_total"].mean()
            / data["pnl_daily_total"].std()
            * np.sqrt(252)
        )
        data["pnl_daily_total_cumsum"] = data["pnl_daily_total"].cumsum()
        return data, tickers

    def present(self):
        print(f"Ticker - {self.tickers}")
        print(f"Data - {self.data}")

    def to_csv(self, out_csv):
        self.data.to_csv(out_csv)


class StockDataLoader:
    """
    Stocker Data Loader from VNDirect
    """

    START_DATE = "2000-01-01"
    FREQUENCIES = [
        "daily",
        "weekly",
        "monthly",
        "60min",
        "30min",
        "15min",
        "10min",
        "5min",
        "1min",
    ]

    def __init__(self, ticker, store_path, start=None, end=None):
        self.ticker = ticker
        self.stock = Stock(symbol=ticker)
        self.price = Prices(symbol=ticker)
        self.start = start
        self.end = end
        if self.start and self.end:
            self.stock_dir = os.path.join(
                store_path,
                LAST_UPDATED_ON,
                "stock_" + ticker + f"_from{self.start}_to{self.end}",
            )
        else:
            self.stock_dir = os.path.join(
                store_path,
                LAST_UPDATED_ON,
                "stock_" + ticker,
            )
        if not os.path.isdir(self.stock_dir):
            os.makedirs(self.stock_dir, exist_ok=True)

    def load_all(self):
        self.load_stock_info()
        self.load_stock_event()
        self.load_price_hists_all()

    def load_stock_info(self):
        stock_info_json = os.path.join(
            self.stock_dir,
            f"{self.ticker}_info.json",
        )
        stock_info = self.stock.get_info()
        with open(stock_info_json, "w") as fp:
            json.dump(stock_info, fp)

    def load_stock_event(self):
        stock_event_json = os.path.join(
            self.stock_dir,
            f"{self.ticker}_event.json",
        )
        stock_event = self.stock.get_events()
        with open(stock_event_json, "w") as fp:
            json.dump(stock_event, fp)

    def load_price_hists_all(self):
        for freq in StockDataLoader.FREQUENCIES:
            self.load_price_hists_with_freq(freq)

    def load_price_hists_with_freq(self, frequency):
        price_hist_json = os.path.join(
            self.stock_dir,
            f"{self.ticker}_price_hist_{frequency}.csv",
        )
        if self.start and self.end:
            price_hist = self.price.get_historical_prices(
                frequency=frequency,
                save=True,
                start=self.start,
                end=self.end,
            )
        else:
            price_hist = self.price.get_historical_prices(
                frequency=frequency,
                save=True,
                start=StockDataLoader.START_DATE,
            )
        price_hist.to_csv(price_hist_json)


class StockTrader:
    def __init__(self, source_file):
        self.table = pd.read_csv(source_file)

    def build_feature(self):
        self.table["sma_5"] = self.table.Close.rolling(5).mean()
        self.table["sma_10"] = self.table.Close.rolling(10).mean()

    def trade(self, method=1):
        if method == 1:
            self.trade_1()

    def trade_1(self):
        """
        Buy when Cross(MA5, MA10) turn from (-) to (+)
        Sell when Cross(MA10, MA5) turn from (-) to (+)
        """
        self.table["buy"] = np.where(
            (self.table.sma_5 > self.table.sma_10)
            & (self.table.sma_5.shift(1) < self.table.sma_10.shift(1)),
            "buy",
            np.nan,
        )
        self.table["sell"] = np.where(
            (self.table.sma_5 < self.table.sma_10)
            & (self.table.sma_5.shift(1) > self.table.sma_10.shift(1)),
            "sell",
            np.nan,
        )

    def profit_or_loss(self):
        self.table["inc"] = np.where(
            self.table.Close.shift(-1) > self.table.Close,
            True,
            False,
        )
        self.table["profit"] = np.where(
            ((self.table.buy == "buy") & self.table.inc)
            | ((self.table.sell == "sell") & ~self.table.inc),
            "profit",
            np.nan,
        )
        self.table["loss"] = np.where(
            ((self.table.buy == "buy") & ~self.table.inc)
            | ((self.table.sell == "sell") & self.table.inc),
            "loss",
            np.nan,
        )
        self.table["delta"] = self.table.Close.shift(-1) - self.table.Close

    def present(self):
        print(self.table.head(20))
        print("buy -", self.table.groupby("buy").count())
        print("sell -", self.table.groupby("sell").count())
        print("inc -", self.table.groupby("inc").count())
        print("profit -", self.table.groupby("profit").count())
