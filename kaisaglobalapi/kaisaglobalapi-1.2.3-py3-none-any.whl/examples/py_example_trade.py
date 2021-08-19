
# -*- coding: utf-8 -*-

# ===================================================================
# This example is written by Kaisa FinTech Quant Team.
# KaisaGlobal OpenAPI provides a friendly way to trade in Global Markets.
# and now Hong Kong market is suported.
# This code is shown to our clients how to send trade order(s) or cancel order(s).
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

if __name__=="__main__":

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
    auth_status, auth_msg = KaisaGw.gateway_auth()
    if auth_status:
        print("gateway connect success.")
    else:
        print("gateway connect fail.")

    ### connect to trade.
    ret_ok, ret_msg = KaisaGw.trade_connect()
    if ret_ok:
        print('trade login success.')
    else:
        print('trade login fail.')
        print(ret_msg)

    # build websocket connect to trade-center;
    # the information will be received from websocket connect.
    KaisaGw.trade_connect_ws()
    time.sleep(3)

    ### trade auth.
    ret_ok, ret_msg = KaisaGw.trade_auth()
    if ret_ok:
        print("trade auth success.")
    else:
        print("trade auth fail. as follows.")
        print(ret_msg)

    ### 下单;
    ret_ok, ret_data = KaisaGw.place_order(code='01638', bsFlag='B', price=3.80, qty=1000)
    if ret_ok:
        print('\nplace order success.')
        print(ret_data)
    else:
        print('place order fail.')
        print(ret_data)

    ### 撤单;
    if 'orderID' in ret_data:
        sys_orderid = ret_data['orderID']
        ret_ok, ret_data = KaisaGw.cancel_order(sys_orderid)
        if ret_ok:
            print("\ncancel order success.")
            print(ret_data)
        else:
            print("cancel order fail.")
            print(ret_data)

    time.sleep(5)
