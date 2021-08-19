import pandas as pd
from .data_tables import StocksDataTables
from ..api.raw import RawDataApi, RawDatabaseConnector
from ..fund.derived.stocks.compute_stock import compute_stock


class StockDataManager:

    def __init__(self):
        self.sdt = StocksDataTables()
        self.stock_info = pd.DataFrame([])

    def collect(self, stock_id=None):
        self.stock_info = self.read_stock_info()
        if stock_id:
            params = [{'stock_id': stock_id}]
        else:
            params = [{'stock_id': stock_id} for stock_id in self.stock_info['stock_id']]

        for i in params:
            data = compute_stock(i)
            print(i['stock_id'], 'Done!')
            self.sdt.stocks.update(data)

    def pickle_save(self, file_path=None):
        print(self.sdt.stocks.keys())
        if not file_path:
            file_path = './stock_manager'
        import pickle
        with open(file_path, 'wb') as fp:
            pickle.dump(self, fp)

    def read_stock_info(self):
        df = RawDataApi().get_em_stock_info()
        if not isinstance(df, pd.DataFrame) and not df:
            print(df)
            raise Exception('No stock info!')
        return df

