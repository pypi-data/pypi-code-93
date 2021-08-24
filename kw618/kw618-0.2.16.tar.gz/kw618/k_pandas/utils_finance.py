import pandas as pd
import numpy as np
import math
import collections
import pymongo
import json
import copy
import hashlib
from io import StringIO

import warnings
warnings.filterwarnings("ignore")

# 导入常用的固定路径(多平台通用)
from kw618._file_path import *










class Transaction():

    # 每笔交易费用率
    # ==================
        # 1. 政府印花税: 万10
        # 2. 券商手续费: 万1.8不免5
        # 3. 规费: 万0.69
        # 4. 中登过户费(上海): 万0.2
    def __init__(self, commission_fee_rate=1.8, gui_fee_rate=0.69, transfer_fee_rate=0.2, stamp_tax_rate=10):
        # """
        # 印花税>手续费>规费>过户费
        # (很多券商的手续费是包含规费和过户费的, 这些是必须要交的, 所以手续费中实际能赚到的其实也不多)
        # (如果手续费率包含规费率, 那规费率记为0)
        # """
        u = 0.0001
        self.commission_fee_rate = commission_fee_rate * u
        self.gui_fee_rate = gui_fee_rate * u
        self.transfer_fee_rate = transfer_fee_rate * u
        self.stamp_tax_rate = stamp_tax_rate * u


    def cal_total_fee(self, transaction_amount=10000, transaction_type="in"):
        """
            params:
                transaction_amount: 交易金额
        """
        # 1. 券商手续费
        commission_fee = max(transaction_amount * self.commission_fee_rate, 5)
        # 2. 其他各种银行/政府费率
        other_fee = transaction_amount * (self.stamp_tax_rate + self.gui_fee_rate + self.transfer_fee_rate)
        # 总计费用
        # ==================
        total_fee = commission_fee + other_fee
        # 总费用占比
        # ==================
        fee_proportion = round(total_fee/transaction_amount, 5)
        print(f"\n该笔交易为: {transaction_amount}元 的金额, 共产生 {round(total_fee, 1)}元 的服务费, 占比 {str(fee_proportion*100)}%;\n")
        return total_fee



    def test(self):
        # 从1元到100w元
        for i in [1, 10, 100, 1000, 10000, 100000, 1000000]:
            self.cal_total_fee(i)





















#
