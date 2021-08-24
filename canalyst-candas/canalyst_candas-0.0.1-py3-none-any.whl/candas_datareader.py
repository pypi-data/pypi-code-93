from configuration.config import resolve_config
from utils import calendar_quarter, df_filter
import yahoo_fin.stock_info as si
import pandas as pd
import numpy as np
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm

from fredapi import Fred
import pandas as pd
import json

import os
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

web_url = "https://finviz.com/quote.ashx?t="


def get_news_sentiment(ticker_list):
    news_tables = {}

    for tick in ticker_list:
        print(tick)
        url = web_url + tick
        req = Request(url=url, headers={"User-Agent": "Chrome"})
        try:
            response = urlopen(req)
        except:
            continue
        html = BeautifulSoup(response, "html.parser")
        news_table = html.find(id="news-table")
        news_tables[tick] = news_table

    news_list = []

    for file_name, news_table in news_tables.items():
        for i in news_table.findAll("tr"):

            text = i.a.get_text()

            date_scrape = i.td.text.split()

            if len(date_scrape) == 1:
                time = date_scrape[0]

            else:
                date = date_scrape[0]
                time = date_scrape[1]

            tick = file_name.split("_")[0]

            news_list.append([tick, date, time, text])

    vader = SentimentIntensityAnalyzer()

    columns = ["ticker", "date", "time", "headline"]

    news_df = pd.DataFrame(news_list, columns=columns)

    scores = news_df["headline"].apply(vader.polarity_scores).tolist()

    scores_df = pd.DataFrame(scores)

    news_df = news_df.join(scores_df, rsuffix="_right")

    news_df["date"] = pd.to_datetime(news_df.date).dt.date

    return news_df


def get_betas_wide(betas_list):
    list_df = []
    for item in betas_list:

        df = get_price_data(item)
        list_df.append(df)

    df_long = pd.concat(list_df, axis=0).reset_index()
    df_wide = df_long.pivot_table(
        index=["index"], columns="ticker", values="pct_change"
    )
    return df_wide


def get_parallel_betas_from_list(ticker_list, betas_list):
    df_wide = get_betas_wide(betas_list)
    from joblib import Parallel, delayed
    import multiprocessing

    inputs = range(10)

    def processInput(i):
        return i * i

    num_cores = multiprocessing.cpu_count()
    all_df = Parallel(n_jobs=num_cores)(
        delayed(get_beta_data)(ticker, df_wide, betas_list) for ticker in ticker_list
    )
    df_betas = pd.concat(all_df)
    return df_betas


def get_beta_data(ticker, df_wide, betas_list):
    list_out = []
    print(ticker)
    try:
        df = get_price_data(ticker).reset_index()
    except:
        print("failed")
        return

    dataset = pd.merge(df, df_wide, how="inner", left_on="index", right_on="index")

    beta_lens = [60, 90, 252]  # window for betas
    dict_lens = {}
    for beta_len in beta_lens:
        betas = {}
        ns = {}
        r2s = {}
        for col in dataset.columns:
            if col in betas_list:

                df = dataset[["pct_change", col]].dropna()
                # try:
                beta, r2, n = get_betas(df["pct_change"], df[col], beta_len)
                # except:
                #    print("get_betas error")
                #    return
                betas[col] = beta
                ns[col] = n
                r2s[col] = r2
        dict_lens[beta_len] = [betas, ns, r2s]

        df1 = pd.DataFrame.from_dict(
            dict_lens[beta_len][2], orient="index"
        ).reset_index()

        try:
            df1.columns = ["BETA", ticker]
        except:
            print("df columns error")
            return
        df1 = df1.T
        headers = df1.iloc[0]
        df1 = pd.DataFrame(df1.values[1:], columns=headers)
        df1["ticker"] = ticker
        df1["beta_days"] = beta_len
        list_out.append(df1)
    df = pd.concat(list_out)
    return df


def get_price_data(ticker):
    price_data = si.get_data(ticker, start_date="01/01/2009")
    df = pd.DataFrame(price_data)
    df = df[["adjclose"]]
    df["pct_change"] = df.adjclose.pct_change()
    df["log_return"] = np.log(1 + df["pct_change"].astype(float))
    df["ticker"] = ticker
    return df


def get_betas(x, y, n=0):
    if n > 0:
        x = x.iloc[
            -n:,
        ]
        y = y.iloc[
            -n:,
        ]
    res = sm.OLS(y, x).fit()
    beta = res.params[0]
    r2 = res.rsquared
    n = len(x)
    return [beta, r2, n]


def get_fred_data(series_list):
    config = resolve_config()
    FRED = Fred(config.fred_key)

    df_fred = pd.DataFrame()
    for fred_series in series_list:
        s = pd.DataFrame(
            FRED.get_series(
                fred_series, observation_start="2014-09-02", observation_end="2021-03-1"
            )
        ).reset_index()
        s.columns = ["end_date", fred_series]
        s = calendar_quarter(s, "end_date")
        s = s.groupby("end_date_CALENDAR_QUARTER").last().reset_index()
        if df_fred.shape[0] > 0:
            s = s.drop(columns="end_date")
            df_fred = pd.merge(
                df_fred,
                s,
                how="inner",
                left_on="end_date_CALENDAR_QUARTER",
                right_on="end_date_CALENDAR_QUARTER",
            )
        else:
            df_fred = s
    return df_fred


def append_price_data(df):

    df = calendar_quarter(df, "end_date")

    pd.set_option("mode.chained_assignment", None)
    ticker = df.iloc[0]["ticker"]
    stock_ticker = ticker.split(" ")[0]
    df_prices = get_price_data(stock_ticker)
    df_prices = df_prices.reset_index()
    df_prices = df_prices[["pricing_date", "adjclose"]]
    df_prices.columns = ["end_date", "adjclose"]

    df_prices = calendar_quarter(df_prices, "end_date")
    df_prices = df_prices.sort_values("end_date")
    df_prices = df_prices.groupby("end_date_CALENDAR_QUARTER").last().reset_index()

    # fiscal_quarter
    df = df_filter(df, "period_duration_type", ["fiscal_quarter"])
    dates = list(set(list(df["end_date_CALENDAR_QUARTER"])))
    df_p = df_filter(df_prices, "end_date_CALENDAR_QUARTER", dates)

    df_p.columns = ["end_date_CALENDAR_QUARTER", "end_date", "value"]
    df_p["ticker"] = ticker
    df_p["period"] = ""
    df_p["period_duration_type"] = "fiscal_quarter"
    df_p["category"] = ""
    df_p["type"] = ""
    df_p["row_header"] = "Stock Price"
    df_p["unit"] = "$"
    df_p = df_p.sort_values("end_date")
    df_1 = df_p[
        [
            "ticker",
            "period",
            "period_duration_type",
            "end_date",
            "category",
            "type",
            "row_header",
            "unit",
            "value",
            "end_date_CALENDAR_QUARTER",
        ]
    ]

    df = pd.concat([df, df_1])

    return df
