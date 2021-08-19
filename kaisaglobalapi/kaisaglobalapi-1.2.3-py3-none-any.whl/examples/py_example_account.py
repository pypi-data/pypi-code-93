
# -*- coding: utf-8 -*-

# ===================================================================
# This example is written by Kaisa FinTech Quant Team.
# KaisaGlobal OpenAPI provides a friendly way to trade in Global Markets.
# and now Hong Kong market is suported.
# This code is shown to our clients how to query information of account.
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
        print("\n**** trade ws receice ****")
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

    ### trade auth.
    ret_ok, ret_msg = KaisaGw.trade_auth()
    if ret_ok:
        print("trade auth success.")
    else:
        print("trade auth fail. as follows.")
        print(ret_msg)

    ### query porfolio of client's account
    ret_ok, ret_data = KaisaGw.query_portfolio()
    if ret_ok:
        print('query portfolio success.')
        print(ret_data)
    else:
        print("query portfolio fail.")
        print(ret_data)

    ### query position of client's account
    ret_ok, ret_data = KaisaGw.query_position()
    if ret_ok:
        print("query position success.")
        print(ret_data)
    else:
        print("query position success.")
        print(ret_data)

    ### query order of client's account
    ret_ok, ret_data = KaisaGw.query_order()
    if ret_ok:
        print("query order success.")
        print(ret_data)
    else:
        print("query order fail.")
        print(ret_data)

