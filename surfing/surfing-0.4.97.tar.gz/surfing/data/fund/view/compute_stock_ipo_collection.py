import pandas as pd
import numpy as np
import datetime
import traceback
from ...api.raw import *
from ....util.calculator_item import *
from ...wrapper.mysql import ViewDatabaseConnector
from ...view.view_models import StockIpoCollection, ConvBondIpoCollection

class StockIpoCollectionProcessor(object):

    def append_data(self, table_name, data_append_directly_data_df):
        if not data_append_directly_data_df.empty:
            with ViewDatabaseConnector().managed_session() as mn_session:
                try:
                    mn_session.execute(f'TRUNCATE TABLE {table_name}')
                    mn_session.commit()
                except Exception as e:
                    print(f'Failed to truncate table {table_name} <err_msg> {e}')
            data_append_directly_data_df.to_sql(table_name, ViewDatabaseConnector().get_engine(), index = False, if_exists = 'append')
            print('新数据已插入')
        else:
            print('没有需要插入的新数据')

    def calc(self):
        col_dic = {
            'IPOPRICE':'发行价',
            'IPOISSUEDATE':'首发发行日期',
            'IPOSHARESVOL':'首发数量',
            'IPOPE':'发行市盈率',
            'NAME':'股票简称',
            'SUCRATIOONL':'中签率',
            'PURCHACODEONL':'网上申购代码带市场',
            'CEILINGONL':'申购上限',
            'EMIND2016':'东财行业',
            'TRADEMARKET':'上市板块',
            'IPOPURCHDATEONL':'申购日期',
            'IPOANNCDATE':'发行公告日',
            'WSZQJGGGDATE':'中签公布',
            'LISTDATE':'上市日期',
            'CODES':'股票代码',
        }  
        try:
            with RawDatabaseConnector().managed_session() as db_session:
                query = db_session.query(EmStockIpoInfo)
                df = pd.read_sql(query.statement, query.session.bind)
            stock_list = df.CODES.tolist()
            df = df.rename(columns=col_dic) 
            stock_close = RawDataApi().get_em_stock_price(stock_list=stock_list)
            stock_close = stock_close.pivot_table(index='datetime',columns='stock_id',values='close')
            res = []
            for r in df.itertuples():
                stock_code = r.股票代码
                dates = stock_close.index.values
                if stock_code not in stock_close.columns:
                    continue
                values = stock_close[stock_code].values
                ipo_price = r.发行价
                list_date = r.上市日期
                ipo_date = r.首发发行日期
                trade_market = r.上市板块
                stock_name = r.股票简称
                res_status = CalculatorBase.stock_ipo_continue_up_limit(dates=dates,
                                    values=values,
                                    ipo_price=ipo_price,
                                    list_date=list_date,
                                    ipo_date=ipo_date,
                                    trade_market=trade_market,
                                    stock_name=stock_name,
                                    stock_code=stock_code)
                res.append(res_status)
            self.result = pd.DataFrame(res)
            self.result.replace([np.Inf,-np.Inf],np.nan,regex=True, inplace = True)
            self.append_data(StockIpoCollection.__tablename__, self.result)
            return True

        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def process(self):
        failed_tasks = []
        if not self.calc():
            failed_tasks.append('collection_stock_ipo')
        return failed_tasks


class ConcBondIpoCollectionProcessor(object):

    def append_data(self, table_name, data_append_directly_data_df):
        if not data_append_directly_data_df.empty:
            with ViewDatabaseConnector().managed_session() as mn_session:
                try:
                    mn_session.execute(f'TRUNCATE TABLE {table_name}')
                    mn_session.commit()
                except Exception as e:
                    print(f'Failed to truncate table {table_name} <err_msg> {e}')
            data_append_directly_data_df.to_sql(table_name, ViewDatabaseConnector().get_engine(), index = False, if_exists = 'append')
            print('新数据已插入')
        else:
            print('没有需要插入的新数据')

    def calc(self):
        col_dic = {
            'CODES':'转债代码',
            'CBCODE' : '转债代码无市场',
            'CBNAME' : '转债简称',
            'CBSTOCKCODE':'正股代码',
            'CBSTOCKNAME':'正股简称',
            'CBISSUEAMT':'发行总额(亿)',
            'IPOANNCDATE':'发行公告日',
            'CBIPOTYPE':'发行方式',
            'CBPURCODEONL':'网上发行申购代码',
            'ISSRATE':'发行时债项评级',
            'CBTERM':'发行期限',
            'CBISSUEPRICE':'发行价格',
            'ISSUEONLEDATE':'上网发行截止日期',
            'CBCONVPRICE':'转股价',
            'CBDATEONL':'上网发行日期',
            'CBLISTDATE':'上市日期',
            'CBRESULTDATE':'中签公布',
            'CBSUCRATEONL':'中签率',
            'QUANTLIMITINTRO':'网上发行认购数量限制说明',   
        }
        try:
            with RawDatabaseConnector().managed_session() as db_session:
                query = db_session.query(EmConvBondIpoInfo)
                df = pd.read_sql(query.statement, query.session.bind)
            df = df.rename(columns=col_dic)
            conv_bond_list = df.转债代码.tolist()
            data = RawDataApi().get_em_conv_bond_dirty_price(codes=conv_bond_list)
            conv_bond_close = data.pivot_table(index='datetime',columns='bond_id',values='close')
            conv_bond_open = data.pivot_table(index='datetime',columns='bond_id',values='open')
            res = []
            for r in df.itertuples():
                bond_id = r.转债代码
                bond_name = r.转债简称
                list_date = r.上市日期
                ipo_price = r.发行价格
                dates = conv_bond_close.index.values
                if bond_id not in conv_bond_close.columns.tolist():
                    continue
                if r.发行方式 == '私募':
                    continue
                close_values = conv_bond_close[bond_id].values
                open_values = conv_bond_open[bond_id].values
                rate = r.中签率
                limit_num = r.网上发行认购数量限制说明
                res_i = CalculatorBase.conv_bond_ipo_result(bond_id=bond_id,
                                                    bond_name=bond_name,
                                                    list_date=list_date,
                                                    ipo_price=ipo_price,
                                                    dates=dates,
                                                    close_values=close_values,
                                                    open_values=open_values,
                                                    rate=rate,
                                                    limit_num=limit_num,
                                                )
                res.append(res_i)
            self.result = pd.DataFrame(res)
            self.result.replace([np.Inf,-np.Inf],np.nan,regex=True,inplace=True)
            self.append_data(ConvBondIpoCollection.__tablename__, self.result)
            return True

        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def process(self):
        failed_tasks = []
        if not self.calc():
            failed_tasks.append('collection_conv_bond_ipo')
        return failed_tasks


if __name__ == '__main__':
    ConcBondIpoCollectionProcessor().process()
