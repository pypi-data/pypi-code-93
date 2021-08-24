import json
import pandas as pd
import websocket
import ssl

# 导入常用的固定路径(多平台通用)
from kw618._file_path import *
# 本脚本依赖很多 utils_requests的函数和模块, 直接用*  (注意要避免循环导入问题)
from kw618.k_requests.utils_requests import *
from kw618.k_requests.ocr import *
from kw618.k_python.utils_python import *
from kw618.k_pandas.utils_pandas import *

from kw618.k_finance.const import *
from kw618._file_path import *

# req = myRequest().req
# client = pymongo.MongoClient(f'mongodb://kerwin:kw618@{HOST}:27017/')
# db_for_quant = client["quant"]
# remote_client = pymongo.MongoClient(f'mongodb://kerwin:kw618@{REMOTE_HOST}:27017/')
# remote_db_for_quant = remote_client["quant"]
#

















def main():

    ba = BinanceAccount(settings=LSH_BINANCE_SETTING)

    ba = BinanceAccount(settings=ZL_BINANCE_SETTING)

    ba = BinanceAccount(settings=LB_BINANCE_SETTING)

    ba = BinanceAccount(settings=WYH_BINANCE_SETTING)

    ba = BinanceAccount(settings=MF_BINANCE_SETTING)



if __name__ == '__main__':
    print("Start test!\n\n")
    main()
    print("\n\n\nIt's over!")
