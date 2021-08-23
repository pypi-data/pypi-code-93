import json

import pandas as pd
from notecoin.huobi.dataset.core import *
from notecoin.huobi.history.core import (ALL_DATA_TYPES, ALL_PERIODS,
                                         ALL_TYPES, HistoryDownload)
from notetool.log import logger


class PathManage:
    def __init__(self, symbol, download_dir):
        self.symbol = symbol
        self.download_dir = download_dir

    def period_path(self, period, data_type=ALL_DATA_TYPES[0], _type=ALL_TYPES[0]):
        return os.path.join(self.download_dir, self.symbol, data_type, _type, period)

    def file_list(self, period, *args, **kwargs):
        parent_path = self.period_path(period, *args, **kwargs)
        return [os.path.join(parent_path, file) for file in os.listdir(parent_path)]

    def min1_list(self):
        return self.file_list('1min')

    def min5_list(self):
        return self.file_list('5min')

    def min15_list(self):
        return self.file_list('15min')

    def min30_list(self):
        return self.file_list('30min')

    def min60_list(self):
        return self.file_list('60min')

    def hour4_list(self):
        return self.file_list('4hour')

    def day1_list(self):
        return self.file_list('1day')


class SymbolHistory:
    def __init__(self, dir_path='/root/workspace/tmp/coin/', symbol='SHIBUSDT'):
        db_path = os.path.join(dir_path, 'dbs', f'huobi-{symbol}.db')
        self.file_dir = os.path.join(dir_path, 'files')

        self.symbol = symbol
        self.tradeDB = TradeDetail(db_path=db_path)
        self.kline_1min = Kline1MinDetail(db_path=db_path, conn=self.tradeDB.conn)
        self.kline_5min = Kline5MinDetail(db_path=db_path, conn=self.tradeDB.conn)
        self.kline_15min = Kline15MinDetail(db_path=db_path, conn=self.tradeDB.conn)
        self.kline_30min = Kline30MinDetail(db_path=db_path, conn=self.tradeDB.conn)
        self.kline_60min = Kline60MinDetail(db_path=db_path, conn=self.tradeDB.conn)
        self.kline_4hour = Kline4HourDetail(db_path=db_path, conn=self.tradeDB.conn)
        self.kline_1day = Kline1DayDetail(db_path=db_path, conn=self.tradeDB.conn)
        self.init()

    def init(self):
        self.tradeDB.create()
        self.kline_1min.create()
        self.kline_5min.create()
        self.kline_15min.create()
        self.kline_30min.create()
        self.kline_60min.create()
        self.kline_4hour.create()
        self.kline_1day.create()

    def insert_trades(self, start_date, end_date):
        pass

    def insert_kline(self, kline_db: KlineDetail, file_list):
        for file in file_list:
            try:
                df = pd.read_csv(file, index_col=None, header=None)
                df.columns = ['id', 'open', 'close', 'high', 'low', 'vol', 'amount']
                df['symbol'] = self.symbol
                kline_db.insert_list(json.loads(df.to_json(orient='records')))
            except Exception as e:
                logger.info(f'error file {file}')
                print(e)

    def insert_klines(self, start_date, end_date):
        history = HistoryDownload(data_type="klines", start_date=start_date, end_date=end_date, all_periods=ALL_PERIODS,
                                  all_symbols=[self.symbol], download_dir=self.file_dir)

        history.download_klines()
        path_manage = PathManage(symbol=self.symbol, download_dir=history.download_dir)
        self.insert_kline(self.kline_1min, path_manage.min1_list())
        self.insert_kline(self.kline_5min, path_manage.min5_list())
        self.insert_kline(self.kline_15min, path_manage.min15_list())
        self.insert_kline(self.kline_30min, path_manage.min30_list())
        self.insert_kline(self.kline_60min, path_manage.min60_list())
        self.insert_kline(self.kline_4hour, path_manage.hour4_list())
        self.insert_kline(self.kline_1day, path_manage.day1_list())

    def insert_data(self, start_date, end_date):
        self.insert_trades(start_date, end_date)
        self.insert_klines(start_date, end_date)

        print(self.tradeDB.select('select count(1) as num from ' + self.tradeDB.table_name))
        print("1min\t{}".format(self.kline_1min.select('select count(1) as num from ' + self.kline_1min.table_name)))
        print("5min\t{}".format(self.kline_5min.select('select count(1) as num from ' + self.kline_5min.table_name)))
        print("15min\t{}".format(self.kline_15min.select('select count(1) as num from ' + self.kline_15min.table_name)))
        print("30min\t{}".format(self.kline_30min.select('select count(1) as num from ' + self.kline_30min.table_name)))
        print("60min\t{}".format(self.kline_60min.select('select count(1) as num from ' + self.kline_60min.table_name)))
        print("4hour\t{}".format(self.kline_4hour.select('select count(1) as num from ' + self.kline_4hour.table_name)))
        print("1day\t{}".format(self.kline_1day.select('select count(1) as num from ' + self.kline_1day.table_name)))

    def run(self, start_date=datetime.datetime(2021, 5, 25), end_date=datetime.datetime(2021, 6, 23), ):
        self.insert_data(start_date, end_date)

    def test(self):
        import pandas as pd
        condition = 'id>=1619400078439 and id<=1619452799999 limit 111'
        sql = "select * from {} where {}".format(self.kline_1day.table_name, condition)
        print(sql)
        result = pd.read_sql(sql=sql, con=self.kline_1day.conn)
        print(result.head(10))


history = SymbolHistory()
history.run()
