from datetime import datetime

from notecoin.huobi.history.core import merge_all_symbol

merge_all_symbol(period='1min',
                     date=datetime(2021, 5, 19),
                     download_dir='/root/workspace/tmp/coin/merge/1min')
