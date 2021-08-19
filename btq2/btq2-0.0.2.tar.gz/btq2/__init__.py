#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 15:46:40 2021

@author: btq
"""
import psycopg2
import h5py
import getpass
import numpy as np
import pandas as pd
import pdb
from tqdm import tqdm
import copy
def extract(trading_path):
    password = '19981021'
    conn = psycopg2.connect(dbname="topanga", user="btq", password=password, host="pdc", port=5433)

    day_start = "20150801"
    day_end = "20150901"

    data = {}
    symbols = []
    exchange_map = {83: "SSE", 90: "SZSE"}
    with conn as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT secucode, secumarket FROM gildb.secumain WHERE innercode in (SELECT secuinnercode FROM gildb.lc_indexcomponent WHERE indexinnercode=3145 AND indate < %s AND (outdate >= %s OR outdate is null))",
                (day_end, day_start))
            for record in cur.fetchall():
                symbols.append(f"{exchange_map[record[1]]}-{record[0].strip()}")
    print('{} symbols '.format(len(symbols)))

    print('Start to extract data from dataset')
    for symbol in tqdm(symbols):
        with conn as conn:
            with conn.cursor() as cur:
                cur.execute(
                        "SELECT id FROM security WHERE symbol=%s", (symbol,))
                security_id = cur.fetchone()[0]
                cur.execute(
                        "SELECT time_end, open, high, low, factor, volume, close FROM ohlc_stock_1min "
                        "WHERE security_id=%s AND time_end >= %s AND time_end < %s ORDER BY time_end",
                    (security_id, day_start, day_end))
                recent_data = []
                for record in cur.fetchall():
                    recent_data.append((record[0].strftime("%Y-%m-%d %H:%M:%S"), *(record[1:])))
                #print(len(recent_data))
        data[symbol] = recent_data
    print('Extract data finish there is {} stocks'.format(len(data)))

    ## preprocess trade days
    all_trading_days = None
    with h5py.File(trading_path, "r") as f:
        all_trading_days = f['date'][...]
    trading_day = []
    for day in all_trading_days:
        if day >= int(day_start) and day < int(day_end):
            trading_day.append(day)
    tradetime = []
    time_in_day = [('9:30', '11:30'), ('13:00', '15:00')]
    for day in trading_day:
        for x, y in time_in_day:
            start = f"{day//10000}-{(day%10000)//100}-{day%100} {x}"
            end = f"{day//10000}-{(day%10000)//100}-{day%100} {y}"
            tradetime.extend(
                pd.date_range(start, end, tz='Asia/Hong_kong', freq='1min', closed="right"))

    #fill miss values
    print('Start to fill miss values')
    preprocess_data = {}
    miss_count = dict()
    for symbol in tqdm(data.keys(), ncols=150):
        print(symbol)
        symbol_data = []
        tradetime_idx = 0
        filled_data_count = 0
        previous_data = None
        for record in data[symbol]:
            record_time = pd.to_datetime(record[0], utc=False).tz_localize('Asia/Shanghai')
            if (record_time < tradetime[tradetime_idx]): # this record not in trade time
                continue;
            elif (record_time > tradetime[tradetime_idx]):
                while (record_time > tradetime[tradetime_idx]):
                    fill_data = previous_data[1:] if previous_data is not None else list(record)[1:]
                    symbol_data.append(
                            (tradetime[tradetime_idx].strftime("%Y-%m-%d %H:%M:%S"),*fill_data))
                    tradetime_idx += 1
                    filled_data_count += 1
                if (record_time == tradetime[tradetime_idx]):
                    symbol_data.append(record)
                    tradetime_idx += 1
                previous_data = list(record)
            else: # record_time == tradetime[tradetime_idx]
                symbol_data.append(record)
                tradetime_idx += 1
                previous_data = list(record)
        if previous_data is None:  # this symbol has no data
            print("no data")
            miss_count[symbol] = -1
            continue
        for current_time in tradetime[tradetime_idx:]:
    #       print(f"miss data on {current_time}")
            symbol_data.append((current_time.strftime("%Y-%m-%d %H:%M:%S"), *previous_data[1:]))
            filled_data_count += 1
        print(f"fill {filled_data_count} data")
        miss_count[symbol] = filled_data_count
        preprocess_data[symbol] = symbol_data
    select_symbol = []
    for k, v in miss_count.items():
        if v != -1 and v <= 500:
            select_symbol.append(k)

    print('fill data finish')

    #Calculation index
    print('Start to calculate index')
    all_data = []
    for key in tqdm(select_symbol, ncols = 150):
        open_list = []
        high_list = []
        low_list = []
        volume_list = []
        close_list = []
        for record in preprocess_data[key]:
            open_list.append(record[1] * record[4])
            high_list.append(record[2] * record[4])
            low_list.append(record[3] * record[4])
            volume_list.append(record[5])
            close_list.append(record[6] * record[4])
    #     print(len(open_list))
    #     print(len(high_list))
    #     print(len(low_list))
    #     print(len(volume_list))
    #     print(len(close_list))
        one_stock = []
        for i in range(len(open_list)):
            one_time = []
            one_time.append(close_list[i]/open_list[i])
            one_time.append(high_list[i]/open_list[i])
            one_time.append(low_list[i]/open_list[i])
            one_time.append(close_list[i]/high_list[i])
            one_time.append(close_list[i]/low_list[i])
            one_time.append(high_list[i]/low_list[i])
            if i==0:
                one_time.append(1)
            elif volume_list[i-1] ==0:
                one_time.append(1)
                print(key, i)
            else:
                one_time.append(volume_list[i]/volume_list[i-1])
            one_stock.append(one_time)
        print(len(one_stock))
        all_data.append(one_stock)

    length_time = len(all_data[0][:])
    length_stock = len(all_data[:])
    #print('time point is {}'.format(length_time))
    #print('stock is {}'.format(length_stock))
    extract_feature = []
    #print(extract_feature)
    for time in range(length_time):
        one_timepoint = []
        for i in range(length_stock):
            one_time_stock = copy.deepcopy(all_data[i][time])
            one_time_stock.insert(0,(i+1))
            one_time_stock.insert(0,select_symbol[i])
            one_timepoint.append(one_time_stock)
        extract_feature.append([one_timepoint])

    extract_feature = np.array(extract_feature)
    save_path = '/y/Topanga/extract-feature/feature.npy'
    np.save(save_path,extract_feature)
    print(save_path)