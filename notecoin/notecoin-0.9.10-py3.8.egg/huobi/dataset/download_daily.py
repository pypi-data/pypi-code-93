from datetime import datetime

from notecoin.huobi.history.core import load_daily_all, load_symbol_all

load_daily_all(period='1min',date=datetime(2021, 5, 17))

