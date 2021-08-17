#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Tradologics Python SDK
# https://tradologics.com
#
# Copyright 2020-2021 Tradologics, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as _pd


def bars_to_pandas(bars_json, group_by="column"):
    """ convert bars payload to pandas dataframe """
    dfs = newbars = {}

    for dt, values in bars_json['bars'].items():
        for ticker, ohlc in values.items():
            ohlc['ts'] = dt
            if ticker not in newbars:
                newbars[ticker] = []
            newbars[ticker].append(ohlc)

    for ticker, bars in newbars.items():
        dfs[ticker] = _pd.DataFrame(bars)
        dfs[ticker].set_index("ts", inplace=True)
        dfs[ticker].index = _pd.to_datetime(dfs[ticker].index)
        for col in dfs[ticker].columns:
            dfs[ticker][col] = _pd.to_numeric(dfs[ticker][col])

    df = _pd.concat(dfs.values(), axis=1, keys=dfs.keys())
    df.sort_index(level=0, axis=1, inplace=True)

    if group_by == 'column':
        df.columns = df.columns.swaplevel(0, 1)
        df.sort_index(level=0, axis=1, inplace=True)

    return df

