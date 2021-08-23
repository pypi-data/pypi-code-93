"""
股票市场宏观类指标
"""
import pandas as pd
from datetime import datetime
from hbshare.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class StockValuation:
    def __init__(self, start_date, end_date, is_increment=1):
        self.start_date = start_date
        self.end_date = end_date
        self.is_increment = is_increment
        self.table_name1 = 'mac_stock_pe_ttm'
        self.table_name2 = 'mac_stock_pe_est'

    def get_stock_market_data(self):
        """
        股票市场估值类数据：包含上证50、沪深300、中证500、中证1000、上证指数的PE_TTM和预测PE数据
        """
        index_list = ['000001.SH', '000016.SH', '000300.SH', '000905.SH', '000852.SH']
        # PE_TTM
        res = w.wsd(','.join(index_list), 'pe_ttm', self.start_date, self.end_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch pe_ttm data error: start_date = {}, end_date = {}".format(
                self.start_date, self.end_date))
        else:
            if len(res.Data) == 1:
                data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
            else:
                data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        pe_ttm = data.copy()
        # pe_est
        data['year'] = data['trade_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d').year)
        a, b = data.groupby('year')['trade_date'].min(), data.groupby('year')['trade_date'].max()
        interval_df = pd.merge(a.to_frame('start'), b.to_frame('end'), left_index=True, right_index=True)
        pe_est = []
        for year in interval_df.index:
            start_date, end_date = interval_df.loc[year, 'start'], interval_df.loc[year, 'end']
            res = w.wsd(','.join(index_list), 'pe_est', start_date, end_date, "year={}".format(year))
            if res.ErrorCode != 0:
                data = pd.DataFrame()
                print("fetch pe_est data error: start_date = {}, end_date = {}".format(start_date, end_date))
            else:
                if len(res.Data) == 1:
                    data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times).T
                else:
                    data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
                data.index.name = 'trade_date'
                data.reset_index(inplace=True)
                data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
            pe_est.append(data)
        pe_est = pd.concat(pe_est)

        pe_ttm.rename(columns={"000001.SH": "SZZS", "000016.SH": "SZ50", "000300.SH": "HS300",
                               "000905.SH": "ZZ500", "000852.SH": "ZZ1000"}, inplace=True)
        pe_est.rename(columns={"000001.SH": "SZZS", "000016.SH": "SZ50", "000300.SH": "HS300",
                               "000905.SH": "ZZ500", "000852.SH": "ZZ1000"}, inplace=True)

        return pe_ttm, pe_est

    def get_construct_result(self):
        if self.is_increment == 1:
            pe_ttm, pe_est = self.get_stock_market_data()
            # pe_ttm
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name1, ','.join(pe_ttm['trade_date'].tolist()))
            delete_duplicate_records(sql_script)
            WriteToDB().write_to_db(pe_ttm, self.table_name1)
            # pe_est
            sql_script = "delete from {} where trade_date in ({})".format(
                self.table_name2, ','.join(pe_est['trade_date'].tolist()))
            delete_duplicate_records(sql_script)
            WriteToDB().write_to_db(pe_est, self.table_name2)
        else:
            pe_ttm, pe_est = self.get_stock_market_data()
            # pe_ttm
            sql_script = """
                    create table mac_stock_pe_ttm(
                    id int auto_increment primary key,
                    trade_date date not null unique,
                    SZZS decimal(5, 2),
                    SZ50 decimal(5, 2),
                    HS300 decimal(5, 2),
                    ZZ500 decimal(5, 2),
                    ZZ1000 decimal(5, 2)) 
                """
            create_table(self.table_name1, sql_script)
            WriteToDB().write_to_db(pe_ttm, self.table_name1)
            # pe_est
            sql_script = """
                    create table mac_stock_pe_est(
                    id int auto_increment primary key,
                    trade_date date not null unique,
                    SZZS decimal(5, 2),
                    SZ50 decimal(5, 2),
                    HS300 decimal(5, 2),
                    ZZ500 decimal(5, 2),
                    ZZ1000 decimal(5, 2)) 
                """
            create_table(self.table_name2, sql_script)
            WriteToDB().write_to_db(pe_est, self.table_name2)


if __name__ == '__main__':
    StockValuation('2021-04-22', '2021-04-23', is_increment=1).get_construct_result()
