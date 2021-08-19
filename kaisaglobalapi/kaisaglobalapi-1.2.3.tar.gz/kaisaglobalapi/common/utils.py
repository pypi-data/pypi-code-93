# -*- coding: utf-8 -*-

# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# KaisaGlobal rights are reserved.
# ===================================================================

"""
This code provide utils function for KaisaGlobal-Open.

developed by KaisaGlobal quant team.
2020.12.11
"""


import numpy as np
import pandas as pd

import time
import datetime

def generate_datetime(timestamp: str) -> datetime:
    """"""
    if "." in timestamp:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    else:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return dt

def generate_timestamp():
    return str(int(time.time()*1000))

def user_help(user_id=None, use_type=None):
    # user_help to send http service
    pass
