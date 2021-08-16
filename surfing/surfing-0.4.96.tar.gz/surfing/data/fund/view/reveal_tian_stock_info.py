
from typing import Tuple, List
import math
import datetime
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

from ...api.raw import RawDataApi
# from ...view.view_models import TianStockInfo
# from ...wrapper.mysql import ViewDatabaseConnector


@dataclass
class TianStockInfoProcessor():
    # 一些常量
    YI: float = field(init=False, default=math.pow(10, 8))
    WAN: float = field(init=False, default=math.pow(10, 4))
    FIN_LYR: datetime.date = field(init=False, default=datetime.date.fromisoformat('2019-12-31'))
    FIN_MRQ: datetime.date = field(init=False, default=datetime.date.fromisoformat('2019-09-30'))
    FIN_DATE_LIST: Tuple[datetime.date] = field(init=False, default=tuple(map(datetime.date.fromisoformat, ('2016-12-31', '2017-12-31', '2018-12-31'))))

    # 构造函数参数
    stock_file: str
    wind_file: str
    recent_day: str

    # 内部使用，非参数
    _stocks: List[str] = field(init=False)
    _stock_df: pd.DataFrame = field(init=False)
    _wind_df: pd.DataFrame = field(init=False)
    _names: pd.DataFrame = field(init=False)
    _raw_api: RawDataApi = field(init=False)

    def init(self):
        self._names = pd.read_csv('./config_tian/indicator_name.csv', index_col='NAME')
        # 读取证监会受理的新定增项目的股票列表
        self._stock_df = pd.read_excel(self.stock_file, dtype={'股票代码': str})
        self._stock_df['股票代码'] = self._stock_df.loc[:, '股票代码'].apply(lambda x: x+'.SZ' if x[0] in ('0', '3') else x+'.SH')
        self._stocks = self._stock_df.loc[:, '股票代码'].tolist()
        self._stock_df.set_index('股票代码', inplace=True)
        # 读取wind数据
        self._wind_df = pd.read_excel(self.wind_file, index_col='wind_id')
        self._raw_api = RawDataApi()

    def _calculate_lia_to_asset_ratio(self, x: pd.Series) -> float:
        # 计算资产负债率
        divisor = x['balance_statement_25'] + x['balance_statement_46']
        if divisor == 0:
            return 0
        return (x['balance_statement_93'] + x['balance_statement_103']) * 100 / divisor

    def _calculate_ratio(self, cur_value: pd.Series, prev_value: pd.Series) -> pd.Series:
        return (cur_value - prev_value) * 100 / prev_value

    def _rename_func(self, x: str):
        try:
            return self._names.loc[x, 'DESC']
        except KeyError:
            return x

    def reveal_stock_info(self):
        # 获取对应股票的数据
        info_df = self._raw_api.get_em_stock_info(self._stocks).set_index('stock_id')
        fin_df = self._raw_api.get_em_stock_fin_fac(self._stocks).set_index('stock_id')
        price_df = self._raw_api.get_em_stock_price(self.recent_day, self.recent_day, self._stocks).set_index('stock_id')
        daily_df = self._raw_api.get_em_daily_info(start_date=self.recent_day, end_date=self.recent_day, stock_list=self._stocks).set_index('stock_id')
        # triggered_df = self._raw_api.get_em_daily_info(self._stocks)

        df = pd.DataFrame(index=self._stocks)
        df['name'] = info_df['name']
        df['保荐机构'] = self._stock_df['保荐机构']
        df['是否推荐'] = np.nan
        df['审核状态'] = self._stock_df['审核状态']
        df['受理日期'] = self._stock_df.loc[:, '受理日期'].apply(lambda x: x.date())
        df['wind_ind_4'] = self._wind_df.loc[self._stocks, 'wind_ind_4']
        df['mv'] = price_df['close'] * daily_df['total_share']
        df = df.join(daily_df[['pe_ttm_deducted', 'pb_lyr_n', 'est_peg', 'hold_frozen_amt_accum_ratio']])
        df['liability_to_asset_'+self.FIN_MRQ.isoformat()] = fin_df[fin_df['datetime']==self.FIN_MRQ].apply(self._calculate_lia_to_asset_ratio, axis='columns')
        df['gp_margin_'+self.FIN_MRQ.isoformat()] = fin_df[fin_df['datetime']==self.FIN_MRQ].loc[:, 'gp_margin']
        df['expense_toor_'+self.FIN_MRQ.isoformat()] = fin_df[fin_df['datetime']==self.FIN_MRQ].loc[:, 'expense_toor']
        for date in self.FIN_DATE_LIST:
            df['income_statement_60_'+str(date.year)] = fin_df[fin_df['datetime']==date].loc[:, 'income_statement_60']
        df['performance_express_parent_ni_'+str(self.FIN_LYR.year)] = fin_df[fin_df['datetime']==self.FIN_LYR].loc[:, 'performance_express_parent_ni']
        for date in self.FIN_DATE_LIST:
            df['cashflow_statement_39_'+str(date.year)] = fin_df[fin_df['datetime']==date].loc[:, 'cashflow_statement_39']
        for i in range(1, len(self.FIN_DATE_LIST)):
            df['income_statement_9_ratio_'+str(self.FIN_DATE_LIST[i].year)] = self._calculate_ratio(fin_df[fin_df['datetime']==self.FIN_DATE_LIST[i]].loc[:, 'income_statement_9'], fin_df.loc[fin_df['datetime']==self.FIN_DATE_LIST[i-1]].loc[:, 'income_statement_9'])
        for date in self.FIN_DATE_LIST:
            df['roe_wa_'+str(date.year)] = fin_df.loc[fin_df['datetime']==date].loc[:, 'roe_wa']
        for i in range(1, len(self.FIN_DATE_LIST)):
            df['roe_wa_ratio_'+str(self.FIN_DATE_LIST[i].year)] = self._calculate_ratio(fin_df[fin_df['datetime']==self.FIN_DATE_LIST[i]].loc[:, 'roe_wa'], fin_df[fin_df['datetime']==self.FIN_DATE_LIST[i-1]].loc[:, 'roe_wa'])
        df = df.assign(**{'负面清单': np.nan, '发行规模(亿元)': np.nan, '发行底价': np.nan, '锁定期': np.nan})
        df = df.assign(**{'是否按新规修改': np.nan, '备注': np.nan, '选股报告': np.nan, '分工': np.nan})

        # 以亿元为单位的列
        needed_diveded_yi_columns = ['mv']
        df[needed_diveded_yi_columns] = df.loc[:, needed_diveded_yi_columns].apply(lambda x: x.apply(float).apply(lambda y: round(y/self.YI, 2)))

        # 保留2位小数
        needed_round_columns = ['pe_ttm_deducted', 'pb_lyr_n']
        df[needed_round_columns] = df.loc[:, needed_round_columns].apply(lambda x: x.apply(lambda y: round(y, 2)))

        # 带有日期后缀的列保留2位小数
        needed_round_columns_with_date = ['est_peg', 'liability_to_asset', 'gp_margin', 'expense_toor', 'income_statement_9_ratio', 'roe_wa_ratio']
        for c in needed_round_columns_with_date:
            real_c = list(df.filter(like=c))
            df[real_c] = df[real_c].apply(lambda x: x.apply(lambda y: round(y, 2)))

        # 带有日期后缀的列以万元为单位
        needed_diveded_wan_columns_with_date = ['income_statement_60', 'performance_express_parent_ni', 'cashflow_statement_39']
        for c in needed_diveded_wan_columns_with_date:
            real_c = list(df.filter(like=c))
            df[real_c] = df[real_c].apply(lambda x: x.apply(float).apply(lambda y: round(y/self.WAN, 2)))

        df.rename(columns=self._rename_func).to_excel('./stock_pool.xlsx', engine='xlsxwriter', na_rep='-')
        print(df)


if __name__ == '__main__':
    p = TianStockInfoProcessor('./config_tian/diff_2020-04-30.xlsx', './config_tian/stk_list.xlsx', '2020-04-30')
    p.init()
    p.reveal_stock_info()
