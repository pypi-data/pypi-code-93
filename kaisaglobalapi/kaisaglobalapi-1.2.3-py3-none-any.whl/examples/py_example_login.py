
# -*- coding: utf-8 -*-

# ===================================================================
# This example is written by Kaisa FinTech Quant Team.
# KaisaGlobal OpenAPI provides a friendly way to trade in Global Markets.
# and now Hong Kong market is suported.
# This code is shown to our clients how to login gateway.
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

