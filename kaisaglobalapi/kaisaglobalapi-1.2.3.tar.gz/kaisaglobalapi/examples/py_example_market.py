
# -*- coding: utf-8 -*-

# ===================================================================
# This example is written by Kaisa FinTech Quant Team.
# KaisaGlobal OpenAPI provides a friendly way to trade in Global Markets.
# and now Hong Kong market is suported.
# This code is shown to our clients how to connect to market and request/subscribe market data.
# Dec. 14, 2020
# ===================================================================

import os, sys, json
import datetime, time
import numpy as np
import pandas as pd
from copy import deepcopy
from kaisaglobalapi.common import KaisaGateway

my_token = "__my_token__"

class KaisaDemo(KaisaGateway):
    def __init__(self, *args, **kwargs):
        super(KaisaGateway, self).__init__(*args, **kwargs)

    def on_market_data(self, data):
        print("\n**** market ws receive ****")
        print(data)

    def on_trade_data(self, data):
        print("\n**** trade ws receive ****")
        print(data)

if __name__=='__main__':

    print('example of request/subscribe market data.')

    default_config = {
        "user_id": "86,182******",
        "user_pwd": "******",
        "account_code": "9604******",
        "account_pwd": "******",
        "environment": "actual",
        "openapi_token": my_token,
        "ip_address": "104.193.**.**"
    }

    KaisaGw = KaisaDemo()
    KaisaGw.jq_user_config(**default_config)
    auth_status = KaisaGw.gateway_auth()
    if auth_status:
        print("gateway connect success.")
    else:
        print("gateway connect fail.")

    ### after gateway login;

    ### connect to market quotation;
    KaisaGw.market_connect_ws()
    time.sleep(3)
    ret_ok, ret_data = KaisaGw.get_market_connect_ws_status()
    if ret_ok:
        print("market-ws connected.")
    else:
        print('market-ws disconnected as follows:')
        print(ret_data)

    ### example of query_history_kline
    ret_ok, ret_data = KaisaGw.query_history_kline(symbol='01638', market='HK', klinetype='1min', adjfactortype='0', pagesize=10, pagenum=1)
    if ret_ok:
        print("query ok. kline as follows.")
        for item in ret_data:
            print(item)
    else:
        print("query fail. error msg as follows.")
        print(ret_data)

    ### example of query_history_tick
    ret_ok, ret_data = KaisaGw.query_history_tick(symbol='01638', market='HK', pagesize=10, pagenum=1)
    if ret_ok:
        print("query ok. tick as follows.")
        print(ret_data)
    else:
        print("query fail. error msg as follows.")
        print(ret_data)

    ### example of query_detailstate
    ret_ok, ret_data = KaisaGw.query_detailstate(symbol='00700', market='HK')
    if ret_ok:
        print("query ok. detailstate as follows.")
        print(ret_data)
    else:
        print("query fail. error msg as follows.")
        print(ret_data)

    ### 订阅分时和分笔数据;
    KaisaGw.subscribe_marketdata([{'code':'00700', 'market':'HK'}])

    while True:
        time.sleep(1)

