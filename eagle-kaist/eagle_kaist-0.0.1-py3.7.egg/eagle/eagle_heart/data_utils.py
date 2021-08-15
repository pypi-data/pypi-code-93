import os
from datetime import datetime

import numpy as np
import pandas as pd

from eagle.eagle_heart.configs import (
    FMT_DATE_TIME,
    LAST_HOUR,
    TICKERS_FILE,
    FMT_68,
    FMT_DATE_CONSTANT_TIME,
)


def summarize_data_in_day(input_df):
    """
    Summarize daily data
    """
    high = max(input_df["High"])
    low = min(input_df["Low"])
    close_price = input_df.iloc[-1]["Close"]
    open_price = input_df.iloc[0]["Open"]
    # print(input_df.iloc[0]['Date'])
    # day = datetime.strptime(input_df['Date'].head(1), '%Y-%m-%d')
    day = datetime.strptime(
        input_df.iloc[0]["Date"],
        FMT_DATE_TIME,
    ).strftime("%Y-%m-%d")
    # print(day)
    return day, close_price, open_price, high, low


def generate_features(input_df):
    """
    Generate features
    : param input_df: input dataframe data
    """
    input_df["Money"] = input_df["Volumn"] * input_df["Close"]
    input_df["Money"] = input_df["Money"].cumsum()
    input_df["DailyClose"] = input_df.iloc[-1]["Close"]
    input_df["DailyOpen"] = input_df.iloc[0]["Open"]
    input_df["DailyLow"] = min(input_df["Low"])
    input_df["DailyHigh"] = max(input_df["High"])
    input_df["Stock3"] = input_df["Close"].rolling(3).mean()
    input_df["Stock5"] = input_df["Close"].rolling(5).mean()
    input_df["Increase"] = np.where(
        (input_df["Stock3"] > input_df["Stock5"])
        & (input_df["Stock3"].shift(1) < input_df["Stock5"].shift(1)),
        1,
        0,
    )
    input_df["Decrease"] = np.where(
        (input_df["Stock3"] < input_df["Stock5"])
        & (input_df["Stock3"].shift(1) > input_df["Stock5"].shift(1)),
        1,
        0,
    )
    daily_money = input_df["Money"].sum()
    print(f"daily_money - {daily_money}")
    start_t = min(input_df["Date"])
    end_t = max(input_df["Date"])
    real_duration = diff_time(start_t, end_t, FMT_DATE_TIME)
    print(f"real_duration - {real_duration}")
    # norm_duration = DIFF_MIN
    min_money = daily_money / real_duration
    print(f"min_money - {min_money}")
    return input_df


def diff_time(start_t, end_t, fmt=FMT_DATE_TIME):
    return (
        datetime.strptime(end_t, fmt) - datetime.strptime(start_t, fmt)
    ).total_seconds() / 60.0


def load_tickers_list():
    """
    Load tickers list from file
    """
    tickers_list = []
    with open(TICKERS_FILE) as fp:
        for line in fp:
            ticker = line.strip()
            tickers_list.append(ticker)
    return tickers_list


def add_missing_data(input_df, time_range):
    """
    Drop duplicates Datetime rows.
    Fill in data at missing timestamp from given time range.
    """
    print(f"daily_data before - {input_df}")
    output_df = input_df.drop_duplicates(subset="Date")
    output_df.index = pd.DatetimeIndex(output_df["Date"])
    output_df = output_df.reindex(time_range)
    output_df["Date"] = output_df.index
    output_df["Volumn"] = output_df["Volumn"].fillna(0)
    output_df = output_df.fillna(method="ffill")
    output_df.reset_index(drop=True, inplace=True)
    print(f"daily_data after - {output_df}")
    return output_df


def normalize_data(input_file, output_path):
    """
    Normalize data given from input file
    """
    raw_data = pd.read_csv(input_file)
    if raw_data.empty:
        print("empty data")
        return None

    # find min/max date
    min_date = min(raw_data["Date"])
    max_date = max(raw_data["Date"])
    data_range_in_day = pd.date_range(
        start=min_date,
        end=max_date,
        freq="1D",
        normalize=True,
    ).to_list()

    raw_data["Date"] = pd.to_datetime(
        raw_data["Date"],
        format="%Y-%m-%d %H:%M:%S",
    )

    # round to minute
    for index in raw_data.index:
        raw_data.at[index, "Date"] = raw_data.at[index, "Date"].round("min")
    print(f"raw_data - {raw_data}")

    # iterate through the date range
    for day in data_range_in_day:
        print("-----")
        print(raw_data)
        day_start = day
        day_end = day.strftime("%Y-%m-%d ") + LAST_HOUR
        print(day_start)
        print(day_end)
        print(pd.to_datetime(day_start))
        print(pd.to_datetime(day_end))
        print("-")
        daily_data = raw_data.loc[
            (raw_data["Date"] > pd.to_datetime(day_start))
            & (raw_data["Date"] < pd.to_datetime(day_end))
        ]
        print(daily_data)
        if not daily_data.empty:
            # Generate data for that day:
            out_name = f"{day.strftime('%Y-%m-%d')}_min_base.csv"
            store_path = os.path.join(output_path, out_name)
            daily_data.to_csv(store_path)
            min_time = min(daily_data["Date"])
            max_time = max(daily_data["Date"])
            print(min_time)
            print(max_time)
            data_range_in_min = pd.date_range(
                start=min_time,
                end=max_time,
                freq="1min",
                normalize=False,
            ).to_list()
            print(len(data_range_in_min))

            # print(f"data_range_in_min - {data_range_in_min}")
            # Add missing timestamp minute by minute
            normalized_data = add_missing_data(daily_data, data_range_in_min)
            out_name = f"{day.strftime('%Y-%m-%d')}_min.csv"
            store_path = os.path.join(output_path, out_name)
            normalized_data.to_csv(store_path)


def reformat_cophieu68(cophieu68_data):
    """
    Reformat data from COPHIEU68
    """
    data = pd.DataFrame()
    data["Date"] = pd.to_datetime(
        cophieu68_data["<DTYYYYMMDD>"],
        format=FMT_68,
    )
    data["Close"] = cophieu68_data["<Close>"]
    data["Open"] = cophieu68_data["<Open>"]
    data["High"] = cophieu68_data["<High>"]
    data["Low"] = cophieu68_data["<Low>"]
    data["Volumn"] = cophieu68_data["<Volume>"]
    data["Ticker"] = cophieu68_data["<Ticker>"]
    data = data.sort_values("Date")
    return data


def reformat_vnd(vnd_data):
    """
    Reformat data from VND
    """
    data = vnd_data
    data["Date"] = pd.to_datetime(
        data["Date"],
        format=FMT_DATE_CONSTANT_TIME,
    )
    return data
