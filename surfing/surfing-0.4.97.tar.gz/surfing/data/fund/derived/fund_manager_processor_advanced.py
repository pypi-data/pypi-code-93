
import pandas as pd
import numpy as np
import datetime
import traceback
import time
from typing import List, Dict, Optional
from functools import partial
from multiprocessing import Pool
from scipy.optimize import Bounds, minimize
import statsmodels.api as sm
from statsmodels import regression
from statsmodels.tsa.ar_model import AutoReg
from pandas.tseries.offsets import DateOffset
from ....util.calculator import Calculator
from ...api.basic import BasicDataApi
from ...api.derived import DerivedDataApi
from ...wrapper.mysql import BasicDatabaseConnector, DerivedDatabaseConnector
from ...view.basic_models import FundNav, Fund_size_and_hold_rate, FundInfo, FundStatusLatest, FundOpenInfo
from ...view.derived_models import FundManagerInfo, FundManagerIndex, FundManagerScore
from .derived_data_helper import DerivedDataHelper, normalize, score_rescale
from ...manager.fund_info_filter import EHR_PROBLEM_EKYWORDS


class ManagerProcessorDev:

    #INDEX_LIST = {'csi_boodfund': 'H11023.CSI', 'csi_f_hybrid': 'H11022.CSI', 'csi_f_qdii': 'H11026.CSI', 'csi_stockfund': 'H11021.CSI', 'mmf': 'H11025.CSI','hs300':'hs300'}
    #REPLACE_DICT = {'stock': 'H11021.CSI', 'bond': 'H11023.CSI', 'mmf': 'H11025.CSI', 'QDII': 'H11026.CSI', 'index': 'hs300'}
    #DATE_DICT = {'stock': datetime.date(2007,1,1), 'bond': datetime.date(2003,1,1), 'mmf': datetime.date(2004,1,7), 'QDII': datetime.date(2008,1,1), 'index': datetime.date(2007,1,1)}

    FUND_CLASSIFIER = {
        'stock': ['普通股票型基金', '偏股混合型基金',  '被动指数型基金', '增强指数型基金', '平衡混合型基金', '灵活配置型基金', '股票多空'],
        'bond': ['中长期纯债型基金', '短期纯债型基金', '偏债混合型基金', '增强指数型债券基金', '被动指数型债券基金','混合债券型二级基金', '混合债券型一级基金'], 
        'QDII': ['国际(QDII)股票型基金', '国际(QDII)债券型基金', '国际(QDII)另类投资基金', '国际(QDII)混合型基金', ],
        'mmf': ['货币市场型基金'],
        'index': ['被动指数型基金', '增强指数型基金', '增强指数型债券基金', '被动指数型债券基金', '商品型基金', 'REITs'],
    }
    REPLACE_DICT = {'stock': 'csi_stockfund',
                     'bond': 'national_debt', 
                     'mmf':  'mmf', 
                     'QDII': 'csi_f_qdii', 
                     'index': 'hs300'}
    FILTER_NAV_RATIO = {
        'stock' : 0.1,
        'QDII'  : 0.1,
        'index' : 0.1,
        'bond'  : 0.07,
        'mmf'   : 0.01,
    }

    INDEX_DICT = { v : k for k, v in REPLACE_DICT.items()}
    PUNISH_RATIO = 0.8
    HARD_PUNISH_RATIO = 0.6
    RISK_FEE_RATE = 0.011
    TRADE_DAY_PER_YEAR = 242
    RISK_FEE_RATE_PER_DAY = RISK_FEE_RATE / TRADE_DAY_PER_YEAR
    TRADING_DAYS_PER_MONTH = 20
    # 管理不足 1 年 0.6； 大于1年小于三年 0.8， 三年以上 1

    def __init__(self, data_helper: DerivedDataHelper):
        self._data_helper: DerivedDataHelper = data_helper
        self._basic_api = BasicDataApi()
        self.mng_index_list: Dict[str, pd.DataFrame] = {}  # 基金经理指数
        self.mng_best_fund: Dict[str, pd.DataFrame] = {}  # 基金经理代表作 
        self.mng_indicator_list: Dict[str, pd.DataFrame] = {}  # 基金经理评分

    def init(self, start_date=str, end_date=str, print_time=False, is_mng_index=False, is_mng_indicator=False):
        self.start_date = start_date if isinstance(start_date, datetime.date) else pd.to_datetime(start_date, infer_datetime_format=True).date()
        self.end_date = end_date if isinstance(end_date, datetime.date) else pd.to_datetime(end_date, infer_datetime_format=True).date()

        with BasicDatabaseConnector().managed_session() as quant_session:
            # 交易日序列
            self.trading_days: pd.DataFrame = self._basic_api.get_trading_day_list().set_index('datetime')
            self.trading_days = self.trading_days.loc[: self.end_date]
            self.trading_days_list = self.trading_days.index
            self.trim_days = self.trading_days[(self.trading_days.index >= self.start_date) & (self.trading_days.index <= self.end_date)].index

            # 指数价格
            self.index_price = self._basic_api.get_index_price(index_list=list(self.REPLACE_DICT.values()))
            self.index_price['index_id'] = self.index_price['index_id'].map(self.INDEX_DICT)
            self.index_price = self.index_price.pivot(index='datetime', columns='index_id', values='close').reindex(self.trim_days).ffill().dropna(how='all', axis=1)
            self.index_ret = np.log(self.index_price).diff()
            
            # 基金信息
            fund_info_query = quant_session.query(FundInfo)
            self.fund_info: pd.DataFrame = pd.read_sql(fund_info_query.statement, fund_info_query.session.bind)
        
            ## 计算基金经理指数时只去掉分级基金子基金， 不能回测交易的基金依然影响基金经理能力
            self.fund_info = self.fund_info[(self.fund_info.structure_type <= 1)
                                          & (~self.fund_info.wind_class_2.isnull())]
            # 基金规模 报告期数据填充交易日 然后再只取交易日，保证和基金收益序列一致
            fund_size_query = quant_session.query(
                Fund_size_and_hold_rate.fund_id,
                Fund_size_and_hold_rate.datetime,
                Fund_size_and_hold_rate.size
            )
            self.fund_size = pd.read_sql(fund_size_query.statement, fund_size_query.session.bind)
            self.fund_size = self.fund_size.pivot_table(index='datetime', columns='fund_id', values='size')
            self.fund_size = self.fund_size.reindex(self.fund_size.index.union(self.trim_days)).dropna(axis=1, how='all')
            self.fund_size = self.fund_size.ffill()

            if is_mng_index:
                # 基金净值 和 日收益
                fund_nav_query = quant_session.query(
                    FundNav.fund_id,
                    FundNav.adjusted_net_value,
                    FundNav.datetime
                ).filter(
                    FundNav.datetime >= self.start_date,
                    FundNav.datetime <= self.end_date,
                    FundNav.fund_id.in_(self.fund_info.fund_id)
                )
                self.fund_nav = pd.read_sql(fund_nav_query.statement, fund_nav_query.session.bind)
                self.fund_nav = self.fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value').reindex(self.trim_days).dropna(axis=1, how='all')
                self.fund_nav = self.fund_nav.ffill() + self.fund_nav.bfill() - self.fund_nav.bfill()
                self.fund_ret = np.log(self.fund_nav).diff() 
                
                # 按照不同基金大类类别做净值过滤， 参考FILTER_NAV_RATIO
                _res = []
                _fund_ret_columns = self.fund_ret.columns.tolist()
                for fund_type, filter_ratio in self.FILTER_NAV_RATIO.items():
                    _info_fund_list = self.fund_info[self.fund_info['wind_class_2'].isin(self.FUND_CLASSIFIER[fund_type])].fund_id.tolist()
                    _fund_list = list(set(_info_fund_list).intersection(_fund_ret_columns))
                    fund_ret = self.fund_ret[_fund_list].copy()
                    fund_ret[fund_ret > filter_ratio] = 0
                    _res.append(fund_ret)
                self.fund_ret = pd.concat(_res,axis=1)
                self.fund_ret = self.fund_ret.loc[:,~self.fund_ret.columns.duplicated()].copy()
                self.fund_size = self.fund_size.reindex(self.fund_ret.index)

            elif is_mng_indicator:
                self.fund_manager_index: pd.DataFrame = DerivedDataApi().get_fund_manager_index().drop(columns='_update_time')
                self.fund_manager_index.groupby(by='fund_type', sort=False).apply(self._preprocess_manager_index_df)
                self.fund_size = self.fund_size.reindex(self.trim_days)

        with DerivedDatabaseConnector().managed_session() as quant_session:
            # 基金经理信息
            mng_query = quant_session.query(
                FundManagerInfo.mng_id,
                FundManagerInfo.start_date,
                FundManagerInfo.fund_id,
                FundManagerInfo.mng_name,
                FundManagerInfo.end_date)
            self.fund_manager_info: pd.DataFrame = pd.read_sql(mng_query.statement, mng_query.session.bind)
            self.fund_manager_info = self.fund_manager_info.rename(columns={'mng_id': 'manager_id', 'mng_name': 'name', 'start_date': 'start', 'end_date': 'end'})
            self.fund_manager_info = pd.merge(self.fund_manager_info, self.fund_info[['fund_id','company_id','wind_class_2']], how='left', on='fund_id' )

        self.manager_name_dict = self.fund_manager_info.set_index('manager_id').to_dict()['name'] 
        self.fund_manager_info = self.fund_manager_info.set_index('fund_id')
        # 每个基金经理人数   如果多人给惩罚
        fund_list = self.fund_manager_info.index.unique().tolist()
        self.fund_manager_num_df = self.process_manager_num(fund_list, self.fund_ret.index)
        
        # 每个基金的规模  小于1e 给惩罚
        self.fund_manager_size_df = self.fund_size.copy()
        self.fund_manager_size_df[self.fund_manager_size_df < 1e8] = 0.6
        self.fund_manager_size_df[(self.fund_manager_size_df >= 1e8) & (self.fund_manager_size_df < 2e9)] = 0.7
        self.fund_manager_size_df[(self.fund_manager_size_df >= 2e9) & (self.fund_manager_size_df < 5e9)] = 0.8
        self.fund_manager_size_df[(self.fund_manager_size_df >= 5e9) & (self.fund_manager_size_df < 1e10)] = 0.9
        self.fund_manager_size_df[self.fund_manager_size_df >= 1e10] = 1
        self.fund_manager_size_df = self.fund_manager_size_df.fillna(self.PUNISH_RATIO)

        # 基金经理数据 根据被动主动分类
        pass_fund_id_list = self.fund_info[self.fund_info.wind_class_2.str.contains('被动')].fund_id.tolist()
        pass_fund_id_list = [i for i in pass_fund_id_list if i in self.fund_ret.columns] 
        acti_fund_id_list = [i for i in self.fund_ret.columns if i not in pass_fund_id_list] 
        _df_acti = pd.DataFrame(1, columns=acti_fund_id_list, index=self.fund_ret.index)
        _df_pass = pd.DataFrame(self.PUNISH_RATIO, columns=pass_fund_id_list, index=self.fund_ret.index)
        self.fund_manager_stype_df = pd.concat([_df_acti, _df_pass], axis=1)
        self.period = ['1y', '3y', '5y', 'history']

    def get_resample_ret(self, df, rule='1M', min_count=15):

        return df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).sum(min_count=min_count)

    def get_begin_date(self, period: str):
        if period == '1y':
            return self.trading_days.tail(self.TRADE_DAY_PER_YEAR * 1).index[0]

        if period == '3y':
             return self.trading_days.tail(self.TRADE_DAY_PER_YEAR * 3).index[0]

        if period == '5y':
             return self.trading_days.tail(self.TRADE_DAY_PER_YEAR * 5).index[0]

        if period == 'history':
            return  self.trading_days.index[0]

    def calc_stutzer(self, ex_return: np.ndarray):
        information_statistic = lambda theta: np.log(np.mean(np.exp(theta[0] * ex_return)))
        theta0 = [-1.]
        bounds = Bounds((-np.inf), (0))
        result = minimize(information_statistic, theta0, method='SLSQP', bounds=bounds, tol=1e-16)
        if result.success:
            information_statistic = -result.fun
            if information_statistic <= 0:
                return 0
            stutzer_index = np.abs(np.mean(ex_return)) / np.mean(ex_return) * np.sqrt(2 * information_statistic)
            return stutzer_index
        else:
            return np.nan
    
    def calc_cl_alpha_beta(self, total: np.ndarray):
        if total.shape[0] <= 1:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    }
        X = np.array([total[:, 1], total[:, 1]]).T
        X[:, 0][X[:, 0] < 0] = 0
        X[:, 1][X[:, 1] > 0] = 0
        if np.count_nonzero(X[:, 1]) == 0:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    }
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        return {'beta':est2.params[0] - est2.params[1],
                'alpha':est2.params[-1],
                }

    def calc_continue_regress_v(self, df, period='monthly'):
        if period == 'monthly':
            # 半年周期
            window = 6
            yearly_multiplier = 2
            period_num = 12
        df.loc[:,'annual_ret'] = df.mng_ret.rolling(window=window).apply(lambda x : x.sum() * yearly_multiplier - self.RISK_FEE_RATE)
        df.loc[:,'annual_vol'] = df.mng_ret.rolling(window=window).apply(lambda x : x.std(ddof=1) * np.sqrt(period_num))
        df.loc[:,'sharpe'] = df.loc[:,'annual_ret'] / df.loc[:,'annual_vol']
        df = df.replace(np.Inf, 0).replace(-np.Inf, 0).dropna() # 空值sharpe赋值0
        if df.shape[0] < 6:
            return np.nan
        mod = AutoReg(endog=df['sharpe'].dropna().values, lags=1)
        res = mod.fit()
        continue_regress_v = res.params[0]
        return continue_regress_v

    def lambda_filter_date_range(self, single_fund_info: pd.DataFrame, date_index: pd.Series) -> pd.Series:
        result: List[pd.Series] = []
        for row in single_fund_info.itertuples(index=False):
            result.append(pd.Series((date_index >= row.start) & (date_index <= row.end), index=date_index))
        return pd.concat(result, axis=1).sum(axis=1)

    def process_fund_ret(self, this_manager_fund_ids, this_manager_info, date_index):
        res = []
        for fund_id in this_manager_fund_ids:
            single_fund_info = this_manager_info.loc[[fund_id]]
            res_i =  self.lambda_filter_date_range(single_fund_info, date_index)
            res_i.name = fund_id
            res.append(res_i)
        return pd.concat(res, axis=1)

    def process_manager_num(self, fund_id_list, date_index):
        res = []
        for fund_id in fund_id_list:
            fund_managers_info = self.fund_manager_info.loc[[fund_id]]
            fund_manager_list = fund_managers_info.manager_id.unique()
            _res = []
            for _mng_id in fund_manager_list:
                fund_manager_i = fund_managers_info[fund_managers_info['manager_id'] == _mng_id]
                single_fund_res = self.lambda_filter_date_range(fund_manager_i, date_index)
                single_fund_res = pd.DataFrame(single_fund_res, columns=[_mng_id])
                _res.append(single_fund_res)
            manager_in_same_time = pd.concat(_res,axis=1)
            fund_manger_same_time = pd.DataFrame(manager_in_same_time.sum(axis=1), columns=[fund_id])            
            res.append(fund_manger_same_time)
        fund_manger_same_time = pd.concat(res, axis=1)
        fund_manger_same_time[fund_manger_same_time > 1] = self.PUNISH_RATIO
        return fund_manger_same_time

    def process_manager_experience(self, fund_id_list, this_manager_info, date_index):
        res = []
        for fund_id in fund_id_list:
            single_fund_info = this_manager_info.loc[[fund_id]]
            work_day_df_i = self.lambda_filter_date_range(single_fund_info, date_index)
            work_day_df_i.name = fund_id
            res.append(work_day_df_i)
        work_day_df = pd.DataFrame(res).T
        work_day_df = work_day_df.cumsum()
        low_cons = work_day_df < self.TRADE_DAY_PER_YEAR
        mid_cons = (work_day_df >= self.TRADE_DAY_PER_YEAR) & (work_day_df < 3 * self.TRADE_DAY_PER_YEAR)
        hig_cons = work_day_df >= 3 * self.TRADE_DAY_PER_YEAR
        work_day_df[low_cons] = self.HARD_PUNISH_RATIO
        work_day_df[mid_cons] = self.PUNISH_RATIO
        work_day_df[hig_cons] = 1
        return work_day_df

    def calc_index(self):
        # 遍历每个基金经理
        #_tm_part2_start = time.time()
        for fund_type in self.FUND_CLASSIFIER:
            self.mng_index_list[fund_type] = pd.DataFrame(index=self.fund_ret.index)
            self.mng_best_fund[fund_type] = pd.DataFrame(index=self.fund_ret.index)

        fund_manager_list = list(self.manager_name_dict.keys())
        t0 = time.time()
        for m_id in fund_manager_list:
            _t0 = time.time()
            for fund_type in self.FUND_CLASSIFIER:
                idx = self.index_calculation(m_id, fund_type)
                if idx is not None:
                    self.mng_index_list[fund_type].loc[:, m_id] = idx # 该资产类别下记录计算结果

            _idx = fund_manager_list.index(m_id)
            _t1 = time.time()
            #print(f'm_id {m_id} {_idx} {len(fund_manager_list)} cost time {_t1 - _t0}')
        t1 = time.time()
        print(f'total cost {t1 - t0}')
        for fund_type in self.FUND_CLASSIFIER:
            self.mng_index_list[fund_type] = self.mng_index_list[fund_type].replace(0, np.nan).dropna(how='all')
        # _tm_part2_end = time.time()
        # print(f' part2 cost time {_tm_part2_end - _tm_part2_start}')

    def index_calculation(self, m_id: str, fund_type: str):
        
        wind_class_2_list = self.FUND_CLASSIFIER[fund_type]
        # 该基金经理管理基金信息
        this_manager_info = self.fund_manager_info[(self.fund_manager_info['wind_class_2'].isin(wind_class_2_list))
                            & (self.fund_manager_info['manager_id'] == m_id)]
        if this_manager_info.shape[0] == 0:
            return 
        index_start_date = this_manager_info.start.min()
        index_end_date = this_manager_info.end.max()
        
        # 该基金经理管理的同类基金列表
        this_manager_fund_ids = this_manager_info.index.unique().tolist()
        _fund_id_list1 = self.fund_ret.columns.tolist()
        _fund_id_list2 = self.fund_manager_size_df.columns.tolist()
        this_manager_fund_ids = list(set(this_manager_fund_ids).intersection(_fund_id_list1).intersection(_fund_id_list2))
        if len(this_manager_fund_ids) == 0:
            return
        fund_ret = self.fund_ret.loc[index_start_date:index_end_date, this_manager_fund_ids]

        # 非管理时间，基金收益赋值0
        manager_status = self.process_fund_ret(this_manager_fund_ids, this_manager_info, fund_ret.index)
        fund_ret = fund_ret * manager_status

        # 基金经理管理的基金 人数状态 单人为 1 ，多人为0.8
        manager_num = self.fund_manager_num_df.loc[index_start_date:index_end_date, this_manager_fund_ids]

        # 基金经理管理的基金 规模状态  > 100e : 1, > 50e : 0.9, > 20e : 0.8, > 1e : 0.7, < 1e : 0.6
        manager_size = self.fund_manager_size_df.loc[index_start_date:index_end_date, this_manager_fund_ids]

        # 基金经理管理的基金 负责年限 大于3 1， 大于1 0.8， 小于1 0.6
        manager_year = self.process_manager_experience(this_manager_fund_ids, this_manager_info, fund_ret.index)

        # 基金经理管理的基金 主动 1 , 被动 0.8
        manager_style = self.fund_manager_stype_df.loc[index_start_date:index_end_date, this_manager_fund_ids]

        # 权重累乘
        fund_weight = manager_num * manager_size * manager_year * manager_style * manager_status

        # 权重和归1
        fund_weight['sum'] = fund_weight.sum(axis=1).T
        fund_weight = fund_weight[this_manager_fund_ids].divide(fund_weight['sum'], axis=0)

        # 基金经理 收益
        total_ret = (fund_ret * fund_weight).sum(axis=1)
        total_ret.name = m_id
        total_ret = pd.DataFrame(total_ret)
        if total_ret.shape[0] == 0:
            return 
        # 基金经理 收益 用指数填充待业期
        index_date_list = manager_status.index[manager_status.sum(axis=1) < 1]
        total_ret.loc[index_date_list, m_id] = self.index_ret.loc[index_date_list, fund_type]

        # 收益初值赋0
        last_trading_day = self.trading_days_list[self.trading_days_list < total_ret.index.values[0]].values[-1]
        total_ret.loc[last_trading_day] = 0
        total_ret = total_ret.sort_index()

        # 做指数
        fund_manager_index = np.exp(total_ret.cumsum())

        # 基金经理代表作
        manager_best_fund = pd.DataFrame((fund_weight + manager_status.cumsum()/1e8).idxmax(axis=1), columns=[m_id])
        self.mng_best_fund[fund_type][m_id] = manager_best_fund
        return fund_manager_index

    def calcualtor(self, df, period='monthly'):
        if period == 'monthly':
            yearly_multiplier = 12
            period_days = self.TRADING_DAYS_PER_MONTH
        x = df.benchmark_ret.values
        y = df.mng_ret.values
        x = sm.add_constant(x)
        model = regression.linear_model.OLS(y,x).fit()
        x = x[:,1]
        alpha = model.params[0] * yearly_multiplier
        beta = model.params[1]
        track_err = (y - x).std(ddof=1) * np.sqrt(yearly_multiplier) 
        downside_std = y[y < (self.RISK_FEE_RATE_PER_DAY * period_days)].std(ddof=1)
        info_ratio = alpha / track_err
        treynor = (np.nanmean(y) - self.RISK_FEE_RATE_PER_DAY * period_days) / beta if beta != 0 else np.nan
        mdd_part =  df.mng_index[:] / df.mng_index[:].rolling(window=df.shape[0], min_periods=1).max()
        mdd = 1 - mdd_part.min()
        if np.isnan(mdd):
            mdd_len = np.nan
        else:
            mdd_date2 = mdd_part.idxmin()
            mdd_date1 = df.mng_index[:mdd_date2].idxmax()
            mdd_len = (mdd_date2 - mdd_date1).days

        annual_ret = df.mng_ret.sum() * (yearly_multiplier / df.shape[0]) - self.RISK_FEE_RATE
        annual_vol = df.mng_ret.std(ddof=1) * np.sqrt(yearly_multiplier)
        sharpe = annual_ret / annual_vol
        calma_ratio = annual_ret / mdd if mdd != 0 else np.nan
        var = np.quantile(df.mng_ret, 0.05)
        cvar = df.mng_ret[df.mng_ret <= var].mean()
        stutzer = self.calc_stutzer(df.mng_ret - self.RISK_FEE_RATE_PER_DAY * period_days) * np.sqrt(yearly_multiplier)
        cl_res = self.calc_cl_alpha_beta(df[['mng_ret','benchmark_ret']].to_numpy())
        stock_cl_alpha = cl_res['alpha']
        stock_cl_beta = cl_res['beta']
        return {
            'alpha':alpha,
            'beta':beta,
            'track_err':track_err,
            'downside_std':downside_std,
            'info_ratio':info_ratio,
            'treynor':treynor,
            'mdd':mdd,
            'mdd_len':mdd_len,
            'annual_vol':annual_vol,
            'annual_ret':annual_ret,
            'sharpe':sharpe,
            'calma_ratio':calma_ratio,
            'var':var,
            'cvar':cvar,
            'stutzer':stutzer,
            'stock_cl_alpha':stock_cl_alpha,
            'stock_cl_beta':stock_cl_beta,
        }

    def loop_item(self, mng_id, fund_type):
        _t0 = time.time()
        idx = self.type_manager_list.index(mng_id)
        wind_class_2_list = self.FUND_CLASSIFIER[fund_type]
        this_manager_whole_info = self.fund_manager_info[(self.fund_manager_info['manager_id'] == mng_id)]
        this_manager_info = self.fund_manager_info[(self.fund_manager_info['wind_class_2'].isin(wind_class_2_list))
                            & (self.fund_manager_info['manager_id'] == mng_id)]
        year_df = self.lambda_filter_date_range(this_manager_info, self.fund_ret.index)

        _fund_list = self.fund_size.columns.tolist()
        still_work_fund_ids = this_manager_info[(this_manager_info.end > self.end_date)].index.unique().tolist()
        still_work_fund_ids = [ i for i in still_work_fund_ids if i in _fund_list ]
        mng_ret = self.monthly_ret[[mng_id]].rename(columns={mng_id:'mng_ret'})
        mng_index = self.monthly_nav[[mng_id]].rename(columns={mng_id:'mng_index'})
        mng_data = pd.concat([mng_ret, mng_index, self.benchmark_monthly_ret], axis=1).dropna()
        mng_result = {
            'mng_id': mng_id,
            'datetime': self.end_date
        }
        for period in self.period:
            begin_date = self.get_begin_date(period)
            mng_data_period =  mng_data.loc[begin_date:].copy().dropna()
            if all(mng_data_period.mng_ret == 0) or mng_data_period.shape[0] < 12:
                continue
            period_result = self.calcualtor(mng_data_period, 'monthly')
            period_result = { f'{k}~{period}_m' : v for k, v in period_result.items() }
            mng_result.update(period_result)
        _weekly_ret = self.weekly_ret[mng_id]
        _weekly_ret.name = 'mng_ret'
        _weekly_bench_ret = self.benchmark_weekly_ret
        weekly_data = pd.concat([_weekly_ret,_weekly_bench_ret], axis=1).dropna()
        cl_res = self.calc_cl_alpha_beta(weekly_data[['mng_ret','benchmark_ret']].to_numpy())
        stock_cl_alpha = cl_res['alpha']
        stock_cl_beta = cl_res['beta']
        mng_result.update({'stock_cl_alpha~history_w':stock_cl_alpha})
        mng_result.update({'stock_cl_beta~history_w':stock_cl_beta})  
        mng_result.update({'fund_type':fund_type})  
        mng_result.update({'fund_type_trading_days': int((year_df / year_df).sum())})  
        mng_result.update({'trading_days': (self.end_date - this_manager_whole_info.start.min()).days})  
        mng_result.update({'scale': self.fund_size.loc[self.end_date, still_work_fund_ids].sum()})
        mng_result.update({'total_ret': self.fund_type_df[mng_id].values[-1]})
        _mng_index = self.fund_type_df[mng_id]
        mng_result.update({'mdd~history_daily': 1 - (_mng_index / _mng_index.cummax()).min()})
        _t1 = time.time()
        #print(f'{mng_id} {idx} / {len(self.type_manager_list)} cost time {_t1 - _t0}')
        return mng_result

    def calc_mng_indicator(self):
        self.result = []
        for fund_type in self.FUND_CLASSIFIER:            
            self.fund_type_df = self.mng_index_list[fund_type]
            still_work_mng_list = self.fund_type_df.iloc[-1].dropna().index.tolist()
            daily_ret = np.log(self.fund_type_df[still_work_mng_list]).diff()
            self.weekly_ret = self.get_resample_ret(df=daily_ret, rule='1W', min_count=3).dropna(axis=0, how='all')
            self.weekly_ret.index = self.weekly_ret.index.date
            self.monthly_ret = self.get_resample_ret(df=daily_ret, rule='1M', min_count=15).dropna(axis=0, how='all')
            self.monthly_ret.index = self.monthly_ret.index.date
            self.type_manager_list = self.monthly_ret.columns.tolist()
            self.monthly_nav = np.exp(self.monthly_ret.cumsum())
            daily_index_ret = np.log(self.index_price).diff()
            self.index_monthly_ret = self.get_resample_ret(df=daily_index_ret, rule='1M', min_count=15).dropna(axis=0, how='all')
            self.index_monthly_ret.index = self.index_monthly_ret.index.date
            self.index_weekly_ret = self.get_resample_ret(df=daily_index_ret, rule='1W', min_count=3).dropna(axis=0, how='all')
            self.index_weekly_ret.index = self.index_weekly_ret.index.date
            self.benchmark_monthly_ret = self.index_monthly_ret[[fund_type]].rename(columns={fund_type:'benchmark_ret'})
            self.benchmark_weekly_ret = self.index_weekly_ret[[fund_type]].rename(columns={fund_type:'benchmark_ret'})
            for mng_id in self.type_manager_list:
                res_i = self.loop_item(mng_id, fund_type)
                self.result.append(res_i)
        self.manager_indicator = pd.DataFrame(self.result)

    def calc_score(self):
        res=[]
        for fund_type in self.FUND_CLASSIFIER:
            df = self.manager_indicator[self.manager_indicator['fund_type'] == fund_type].copy()
            if fund_type == 'stock':
                df.loc[:,'ret_ability'] = score_rescale( 0.4 * score_rescale(df['annual_ret~history_m']) + 0.6 * score_rescale(df['total_ret']))
                df.loc[:,'risk_ability'] = score_rescale(0.3 * score_rescale(-df['mdd~history_daily']) + 0.4 * score_rescale(-df['annual_vol~history_m']) + 0.3 * score_rescale(-df['downside_std~history_m']))
                df.loc[:,'select_time'] =  score_rescale(normalize(df['stock_cl_beta~history_w']))
                df.loc[:,'select_stock'] = score_rescale(normalize(df['stock_cl_alpha~history_w']) )
                df.loc[:,'experience'] = score_rescale( 0.8 *  score_rescale(df['fund_type_trading_days']) + 0.2 * score_rescale(df['scale']))
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'risk_ability'] + df.loc[:,'select_time'] + df.loc[:,'select_stock'] + 1.5 * df.loc[:,'experience'])
            
            elif fund_type == 'bond':
                df.loc[:,'ret_ability'] = score_rescale( 0.8 * score_rescale(df['annual_ret~history_m']) + 0.2 * score_rescale(df['total_ret']))
                df.loc[:,'risk_ability'] = score_rescale(0.1 * score_rescale(-df['mdd~history_daily']) + 0.4 * score_rescale(-df['annual_vol~history_m']) + 0.5 * score_rescale(-df['downside_std~history_m']))
                df.loc[:,'select_time'] =  score_rescale(normalize(df['stock_cl_beta~history_w']))
                df.loc[:,'select_stock'] = score_rescale(normalize(df['stock_cl_alpha~history_w']))
                df.loc[:,'experience'] = score_rescale( 0.8 *  score_rescale(df['fund_type_trading_days']) + 0.2 * score_rescale(df['scale']))
                df.loc[:,'total_score'] = score_rescale(1.2 * df.loc[:,'ret_ability'] +  df.loc[:,'risk_ability'] + df.loc[:,'select_time'] + df.loc[:,'select_stock'] + 1.5 * df.loc[:,'experience'])
            
            elif fund_type == 'index':
                df.loc[:,'ret_ability'] = score_rescale( 0.4 * score_rescale(df['annual_ret~history_m']) + 0.6 * score_rescale(df['total_ret']))
                df.loc[:,'risk_ability'] = score_rescale(0.3 * score_rescale(-df['mdd~history_daily']) + 0.4 * score_rescale(-df['annual_vol~history_m']) + 0.3 * score_rescale(-df['downside_std~history_m']))
                df.loc[:,'experience'] = score_rescale( 0.4 *  score_rescale(df['fund_type_trading_days']) + 0.6 * score_rescale(df['scale']))
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'risk_ability'] + 2 * df.loc[:,'experience'] )
            
            elif fund_type == 'QDII':
                df.loc[:,'ret_ability'] = score_rescale( 0.4 * score_rescale(df['annual_ret~history_m']) + 0.6 * score_rescale(df['total_ret']))
                df.loc[:,'risk_ability'] = score_rescale(0.3 * score_rescale(-df['mdd~history_daily']) + 0.4 * score_rescale(-df['annual_vol~history_m']) + 0.3 * score_rescale(-df['downside_std~history_m']))
                df.loc[:,'stable_ability'] = score_rescale(-normalize(df['annual_vol~history_m']))
                df.loc[:,'select_time'] = np.nan
                df.loc[:,'select_stock'] = np.nan
                df.loc[:,'experience'] = score_rescale( 0.8 *  score_rescale(df['fund_type_trading_days']) + 0.2 * score_rescale(df['scale']))
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'risk_ability'] + df.loc[:,'stable_ability'] + 1.5 * df.loc[:,'experience'])
            
            elif fund_type == 'mmf':
                df.loc[:,'ret_ability'] = score_rescale(normalize(df['annual_ret~1y_m']))
                df.loc[:,'experience'] = score_rescale( 0.8 *  score_rescale(df['fund_type_trading_days']) + 0.2 * score_rescale(df['scale']))
                df.loc[:,'total_score'] = score_rescale(df.loc[:,'ret_ability'] + df.loc[:,'experience'])
            res.append(df)
        self.manager_indicator_score = pd.concat(res)
        _df = self.fund_manager_info.reset_index()
        _df = _df[_df.end == datetime.date(2040,1,1)].dropna(subset=['company_id']).copy()
        _df = _df.rename(columns={'manager_id':'mng_id'})[['mng_id','name','company_id']].drop_duplicates(subset=['mng_id','name']).set_index('mng_id')
        self.manager_indicator_score = self.manager_indicator_score.set_index('mng_id').join(_df).reset_index()
    
    def to_s3(self):
        bucket_name = 'tl-fund-dm'
        _s3_bucket_uri: str = f's3://{bucket_name}/dm'

        name = 'mng_best_fund'
        data = self.mng_best_fund
        res_dict = {}
        for k, df in data.items():
            res_dict[k] = df.to_dict('index')
        df = pd.DataFrame(res_dict)    
        df.to_parquet(f'{_s3_bucket_uri}/{name}.parquet', compression='gzip')

        name = 'mng_index_list'
        data = self.mng_index_list
        res_dict = {}
        for k, df in data.items():
            res_dict[k] = df.to_dict('index')
        df = pd.DataFrame(res_dict)    
        df.to_parquet(f'{_s3_bucket_uri}/{name}.parquet', compression='gzip')

        name = 'mng_indicator_score'
        self.manager_indicator_score.to_parquet(f'{_s3_bucket_uri}/{name}.parquet', compression='gzip')

    def process(self, end_date):
        failed_tasks = []
        try:
            start_date = '20050101'
            self.init(start_date=start_date,end_date=end_date,is_mng_index=True)
            self.calc_index()
            self.calc_mng_indicator()
            self.calc_score()
            self.to_s3()
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('manager_indicator_score')
        return failed_tasks


if __name__ == '__main__':
    mpd = ManagerProcessorDev(DerivedDataHelper())
    mpd.process('20210430')
