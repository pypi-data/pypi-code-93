import datetime
import traceback
import numpy as np
import pandas as pd
from ...view.raw_models import EMFundHoldBond, WindFundBondPortfolio, EmFundConvInfo
from ...view.basic_models import FundConvStats
from ...wrapper.mysql import RawDatabaseConnector
from .basic_data_helper import BasicDataHelper

class BasicConvStat():
    '''可转债权重历史数据 季度更新'''

    def __init__(self, data_helper: BasicDataHelper):
        self._data_helper = data_helper

    def init(self):
        '''
        做可转债持有比例  持仓明细是wind历史数据，十大中仓债是东财数据，
        第二季度和第四季度用持仓明细， 第一季度和第三季度用十大中仓债
        '''
        # em fund hond data
        with RawDatabaseConnector().managed_session() as db_session:
            query = db_session.query(EMFundHoldBond)
            self.em_hold_bond_top10 = pd.read_sql(query.statement, query.session.bind)

            query = db_session.query(WindFundBondPortfolio)
            self.wind_hold_bond = pd.read_sql(query.statement, query.session.bind)

            query = db_session.query(EmFundConvInfo)
            self.fund_conv_info = pd.read_sql(query.statement, query.session.bind)

        self.conv_bond_list = self.fund_conv_info.conv_bond_id.tolist()

    def em_history(self):
        em_hold_bond_top10 = self.em_hold_bond_top10.dropna(subset=['rank1_bond']).copy()
        em_hold_bond_top10 = em_hold_bond_top10.set_index(['DATES','CODES'])
        em_date_list = em_hold_bond_top10.index.get_level_values(0).unique().tolist()
        em_date_list = pd.Series(em_date_list)
        em_date_list = [i.to_pydatetime().date() for i in em_date_list]
        em_date_list = [i for i in em_date_list if i.month in [3,9]]
        em_hold_bond_top10 = em_hold_bond_top10.loc[em_date_list,:].copy()
        for i in range(1,11):
            bond_id = f'rank{i}_bond_code'
            bond_weight = f'rank{i}_bondweight'
            conv_con_list = [i in self.conv_bond_list for i in em_hold_bond_top10[bond_id]] 
            em_hold_bond_top10[f'rank{i}_conv_w'] = conv_con_list * em_hold_bond_top10[bond_weight]
        em_hold_bond_top10 = em_hold_bond_top10.fillna(0)
        em_hold_bond_top10['conv_weight_sum'] = em_hold_bond_top10[[f'rank{i}_conv_w' for i in range(1,11)]].sum(axis=1)
        em_res = em_hold_bond_top10[['conv_weight_sum']].copy()
        em_res = em_res.reset_index()
        em_res['fund_id'] = em_res.apply(
            lambda x : self._data_helper._get_fund_id_from_order_book_id(x.CODES.split('.')[0], x.DATES), axis=1
        )
        em_res = em_res.dropna(subset=['fund_id']).drop('CODES',axis=1)
        name_dic = {
            'DATES':'datetime',
            'conv_weight_sum':'conv_weights',
        }
        em_res = em_res.rename(columns=name_dic)
        em_res['datetime'] = em_res.datetime.dt.date
        return em_res
    
    def wind_history(self):
        wind_hold_bond = self.wind_hold_bond.copy()
        wind_hold_bond['fund_id'] = wind_hold_bond.apply(
            lambda x : self._data_helper._get_fund_id_from_order_book_id(x.S_INFO_WINDCODE.split('.')[0], x.F_PRT_ENDDATE), axis=1
        )
        wind_hold_bond = wind_hold_bond.dropna(subset=['fund_id'])
        date_con = [((i.month, i.day) in [(12,31),(6,30)]) and (i.year >= 2010) for i in wind_hold_bond.F_PRT_ENDDATE]
        wind_hold_bond = wind_hold_bond[date_con].copy()
        wind_hold_bond = wind_hold_bond.set_index(['F_PRT_ENDDATE','fund_id'])
        date_list = wind_hold_bond.index.get_level_values(0).unique()
        res = []
        for dt in date_list:
            wind_hold_dt = wind_hold_bond.loc[dt]
            fund_list = wind_hold_dt.index.unique()
            for fund_i in fund_list:
                wind_hold_dt_i = wind_hold_dt.loc[fund_i,:]
                if isinstance(wind_hold_dt_i, pd.DataFrame):
                    con_list = wind_hold_dt_i.S_INFO_BONDWINDCODE.isin(self.conv_bond_list)
                    conv_w_sum = sum(con_list * wind_hold_dt_i.F_PRT_BDVALUETONAV)
                else:
                    con_list = wind_hold_dt_i.S_INFO_BONDWINDCODE in self.conv_bond_list
                    conv_w_sum = con_list * wind_hold_dt_i.F_PRT_BDVALUETONAV
                dic = {
                    'datetime':dt.to_pydatetime().date(),
                    'fund_id':fund_i,
                    'conv_weights':conv_w_sum
                }
                res.append(dic)
        wind_res = pd.DataFrame(res)
        return wind_res

    def combine(self):
        em_res = self.em_history()
        wind_res = self.wind_history()
        self.result = pd.concat([wind_res,em_res],axis=0).sort_values('datetime').reset_index(drop=True)
        self._data_helper._upload_basic(self.result, FundConvStats.__table__.name, to_truncate=True)