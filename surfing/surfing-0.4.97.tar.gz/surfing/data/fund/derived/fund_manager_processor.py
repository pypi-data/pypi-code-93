import pandas as pd
import numpy as np
import datetime
import traceback
import time
from typing import List, Dict, Optional
from functools import partial
from multiprocessing import Pool

from ....util.calculator import Calculator
from ...api.basic import BasicDataApi
from ...api.derived import DerivedDataApi
from ...wrapper.mysql import BasicDatabaseConnector, DerivedDatabaseConnector
from ...view.basic_models import FundNav, Fund_size_and_hold_rate, FundInfo, FundStatusLatest, FundOpenInfo
from ...view.derived_models import FundManagerInfo, FundManagerIndex, FundManagerScore
from .derived_data_helper import DerivedDataHelper, FUND_CLASSIFIER, normalize, score_rescale
from ...manager.fund_info_filter import EHR_PROBLEM_EKYWORDS
 
class ManagerProcessor:

    INDEX_LIST = {'csi_boodfund': 'H11023.CSI', 'csi_f_hybrid': 'H11022.CSI', 'csi_f_qdii': 'H11026.CSI', 'csi_stockfund': 'H11021.CSI', 'mmf': 'H11025.CSI'}
    REPLACE_DICT = {'stock': 'H11021.CSI', 'bond': 'H11023.CSI', 'mmf': 'H11025.CSI', 'QDII': 'H11026.CSI', 'mix': 'H11022.CSI'}
    DATE_DICT = {'stock': datetime.date(2007,1,1), 'bond': datetime.date(2003,1,1), 'mmf': datetime.date(2004,1,7), 'QDII': datetime.date(2008,1,1), 'mix': datetime.date(2007,1,1)}

    def __init__(self, data_helper: DerivedDataHelper):
        self._data_helper: DerivedDataHelper = data_helper
        self._basic_api = BasicDataApi()
        self.mng_index_list: Dict[str, pd.DataFrame] = {}  # 基金经理指数
        self.mng_indicator_list: Dict[str, pd.DataFrame] = {}  # 基金经理评分

    def init(self, start_date: str, end_date: datetime.date, print_time=False, is_mng_index=False, is_mng_indicator=False):
        self.start_date = start_date if isinstance(start_date, datetime.date) else pd.to_datetime(start_date, infer_datetime_format=True).date()
        self.end_date = end_date if isinstance(end_date, datetime.date) else pd.to_datetime(end_date, infer_datetime_format=True).date()

        with BasicDatabaseConnector().managed_session() as quant_session:
            # 交易日序列
            self.trading_days: pd.DataFrame = self._basic_api.get_trading_day_list()
            self.trading_days_list = self.trading_days.datetime
            self.trim_days = self.trading_days[(self.trading_days.datetime >= self.start_date) & (self.trading_days.datetime <= self.end_date)].datetime

            # 指数价格
            self.index_price = self._basic_api.get_index_price(index_list=list(self.INDEX_LIST.keys()))
            self.index_price['index_id'] = self.index_price['index_id'].map(self.INDEX_LIST)
            self.index_price = self.index_price.pivot(index='datetime', columns='index_id', values='close').reindex(self.trim_days).ffill().dropna(how='all', axis=1)

            # 场内基金列表
            fund_status_query = quant_session.query(FundStatusLatest)
            self.fund_status = pd.read_sql(fund_status_query.statement, fund_status_query.session.bind)
            self.in_market_fund_list = self.fund_status[~self.fund_status.trade_status.isnull()].fund_id.tolist()

            # 封闭基金列表
            fund_open_info_query = quant_session.query(FundOpenInfo)
            self.fund_close = pd.read_sql(fund_open_info_query.statement, fund_open_info_query.session.bind)
            self.close_fund_list = self.fund_close.fund_id.tolist()

            # 基金信息
            fund_info_query = quant_session.query(FundInfo)
            self.fund_info: pd.DataFrame = pd.read_sql(fund_info_query.statement, fund_info_query.session.bind)

            # EHR类基金
            self.ehr_funds = []
            for r in self.fund_info[['desc_name', 'fund_id']].itertuples():
                for type_word, problem_words in EHR_PROBLEM_EKYWORDS.items():
                    i = r.desc_name
                    for problem_i in problem_words:
                        i = i.replace(problem_i, '')
                    if type_word in i:
                        self.ehr_funds.append(r.fund_id)
                    
            ## 计算基金经理指数时只去掉分级基金子基金， 不能回测交易的基金依然影响基金经理能力
            self.fund_info = self.fund_info[self.fund_info.structure_type <= 1]
            # 基金规模 报告期数据填充交易日 然后再只取交易日，保证和基金收益序列一致
            fund_size_query = quant_session.query(
                Fund_size_and_hold_rate.fund_id,
                Fund_size_and_hold_rate.datetime,
                Fund_size_and_hold_rate.size
            )
            self.fund_size = pd.read_sql(fund_size_query.statement, fund_size_query.session.bind)
            self.fund_size = self.fund_size.pivot_table(index='datetime', columns='fund_id', values='size')
            self.fund_size = self.fund_size.reindex(self.fund_size.index.union(self.trim_days)).dropna(axis=1, how='all')
            self.fund_size = self.fund_size.ffill()# + self.fund_size.bfill() - self.fund_size.bfill()

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
                self.fund_ret = self.fund_nav.pct_change(fill_method=None)
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
            self.fund_manager_info = self.fund_manager_info[self.fund_manager_info.fund_id != 'not_exist']
            self.fund_manager_info = pd.merge(self.fund_manager_info, self.fund_info[['fund_id','company_id']], how='left', on='fund_id' )

        self.manager_name_dict = dict(zip(self.fund_manager_info['manager_id'].tolist(), self.fund_manager_info['name'].tolist()))
        # 基金经理数据 根据资产分类
        if is_mng_index:
            self.class_fund = {}
            self.class_index: Dict[str, pd.DataFrame] = {}
            self.class_info: Dict[str, pd.DataFrame] = {}
            self.manager_name_dict = dict(zip(self.fund_manager_info['manager_id'].tolist(), self.fund_manager_info['name'].tolist()))
            for class_name, index_id in self.REPLACE_DICT.items():
                self.mng_index_list[class_name] = pd.DataFrame(index=self.fund_ret.index)
                fund = self.fund_info[self.fund_info['wind_class_2'].isin(FUND_CLASSIFIER[class_name])].fund_id
                info = self.fund_manager_info.loc[self.fund_manager_info['fund_id'].isin(fund), :]
                info = info[info['fund_id'].isin(self.fund_ret.columns.intersection(self.fund_size.columns))]
                self.class_info[class_name] = info
                self.class_index[class_name] = self.index_price[index_id].pct_change(fill_method=None)
                self.class_fund[class_name] = fund

        if is_mng_indicator:
            self.class_fund = {}
            for class_name, index_id in self.REPLACE_DICT.items():
                self.class_fund[class_name] = self.fund_info[self.fund_info['wind_class_2'].isin(FUND_CLASSIFIER[class_name])].fund_id

    @staticmethod
    def _lambda_func_1(single_fund_info: pd.DataFrame, x: pd.Series) -> pd.Series:
        result: List[pd.Series] = []
        for row in single_fund_info.itertuples(index=False):
            result.append(pd.Series((x.index >= row.start) & (x.index <= row.end), index=x.index))
        return pd.concat(result, axis=1).sum(axis=1) > 0

    def calc_index(self):
        # 遍历每个基金经理
        #_tm_part2_start = time.time()
        for m_id in self.manager_name_dict:# 遍历每个资产类别
            for class_name in self.REPLACE_DICT:
                idx = self.index_calculation(m_id, class_name)
                if idx is not None:
                    self.mng_index_list[class_name].loc[:, m_id] = idx # 该资产类别下记录计算结果
        for class_name in self.REPLACE_DICT:
            self.mng_index_list[class_name] = self.mng_index_list[class_name].replace(0, np.nan).dropna(how='all')
        # _tm_part2_end = time.time()
        # print(f' part2 cost time {_tm_part2_end - _tm_part2_start}')

    def index_calculation(self, manager: str, class_name: str):
        '''
        计算基金经理指数
        manager：基金经理的ID
        fund_kind：基金的分类（'stock', 'bond', 'money', 'mix', 'QDII'）
        replace_index：空窗期选择替代的指数的代码
        rate_df：基金日收益率的dataframe
        scale_df：基金规模的dataframe
        返回基金经理指数的Series，时间是从第一个产品的任职到最后一个产品的离职
        replace_index为空时，空窗期按照_REPLACE_DICT中的指数来代替（如果没有指定基金的分类，按照沪深300的指数）
        基金规模按照上期季报的规模作为权重
        如果该日基金净值缺失，则用之前的净值代替，如果历史上并没有该日的净值数据，那么在计算基金经理指数的过程中该基金产品不再拥有权重
        如果因该日基金净值缺失而导致该日基金经理没有基金产品可供计算指数，按照空窗期来处理
        '''
        class_info = self.class_info[class_name]
        m_info = class_info[class_info['manager_id'] == manager]
        index_rate = self.class_index[class_name]
        if m_info.shape[0] == 0:
            # raise Exception('该经理没有相关基金产品')
            return
        m_start = m_info['start'].min()
        m_end = m_info['end'].max()
        unique_fund_ids = m_info['fund_id'].unique()
        rate: pd.DataFrame = self.fund_ret.loc[m_start:m_end, unique_fund_ids]
        scale: pd.DataFrame = self.fund_size.loc[m_start:m_end, unique_fund_ids]
        for fund_id in unique_fund_ids:
            single_fund_info: pd.DataFrame = m_info[m_info.fund_id == fund_id]
            rate.loc[:, fund_id] = rate[fund_id].where(partial(ManagerProcessor._lambda_func_1, single_fund_info), 0)
            scale.loc[:, fund_id] = scale[fund_id].where(partial(ManagerProcessor._lambda_func_1, single_fund_info), 0)
        scale = scale + rate - rate  # rate为NaN的地方也让scale变为NaN
        scale = scale.fillna(0)  # 这里在将NaN全变为0
        ratio = (rate * scale).sum(axis=1) / scale.sum(axis=1).replace(0, 1)
        if ratio.shape[0] == 0:
            return
        ratio = pd.Series(np.where(ratio, ratio, index_rate.loc[ratio.index[0]:ratio.index[-1]]), index=ratio.index).fillna(0)
        # 基金经理指数从1开始，即第一日收益为0
        last_trading_day = self.trading_days_list[self.trading_days_list < ratio.index.values[0]].values[-1]
        ratio.loc[last_trading_day] = 0
        ratio = ratio.sort_index()
        return np.exp(np.log(1 + ratio).cumsum())

    def _calc_part3(self, eval_date_dt):
        eval_start_date = (eval_date_dt - datetime.timedelta(days=365))
        self._do_calc_part3(eval_start_date, eval_date_dt)

    def _do_calc_part3(self, eval_start_date, eval_date):
        _rank_list = {}
        _tm_part3_start = time.time()
        fund_size_col = self.fund_size.columns.tolist()
        print(f'eval_start_date {eval_start_date} eval_date {eval_date}')
        for class_name, index_id in self.REPLACE_DICT.items():
            the_eval_start_date = max(eval_start_date, self.DATE_DICT[class_name])
            class_df = self.mng_index_list[class_name]
            bm = self.index_price[index_id]
            fund_ids = self.fund_manager_info['fund_id'].isin(self.class_fund[class_name])
            try:
                cols = class_df.loc[eval_date].dropna().index
            except KeyError:
                continue
            benchmark_stat_result = []
            for i in cols:
                df = class_df[i].loc[the_eval_start_date:eval_date].dropna()
                # 计算年度收益std 如果只有一个， 返回nan
                df_whole = class_df[i].loc[:eval_date].dropna()
                _df = pd.DataFrame(df_whole.rename('mng_id'))
                _df['year'] = _df.index.map(lambda x : x.year)
                year_ret_std = _df.groupby('year').apply( lambda x : (x.iloc[-1]['mng_id'] / x.iloc[0]['mng_id']) - 1).std(ddof=1)
                if df.shape[0] < 5:
                    continue
                dic = Calculator.get_manager_stat_result(df.index.array, df.array, bm.loc[df.index].array)
                dic['name'] = self.manager_name_dict[i]
                dic['index'] = i
                dic['year_ret_std'] = year_ret_std
                fund_df = self.fund_manager_info[self.fund_manager_info['manager_id'].isin([i]) & fund_ids]
                _fund_df = fund_df[fund_df['end'] >= eval_date]
                _fund_list = _fund_df.fund_id.tolist()
                comp_now = _fund_df.company_id.unique()[0]
                _start_com_date = fund_df[fund_df['company_id'] == comp_now].start.min()
                dic['start_date'] = min(_fund_df['start'])
                dic['trade_year'] = (dic['end_date'] - dic['start_date']).days / 365
                _fund_list = [ i for i in _fund_list if i in fund_size_col]
                dic['fund_size'] = self.fund_size.loc[eval_date,_fund_list].sum()
                dic['now_comp_year'] = (dic['end_date'] - _start_com_date).days / 365
                benchmark_stat_result.append(dic)
            stats: pd.DataFrame = pd.DataFrame(benchmark_stat_result).set_index('index')
            rf = 1.025 ** (1 / 365) - 1
            cl_result = []
            for i in stats.index:
                df = class_df[i].loc[the_eval_start_date: eval_date].dropna()
                total = pd.concat([bm.loc[df.index].pct_change(fill_method=None) - rf, df.pct_change(fill_method=None)], axis=1)
                total = total[total.notna().all(axis=1)]
                res = DerivedDataHelper._lambda_cl(total.to_numpy())
                cl_result.append(res)
            temp = pd.DataFrame(cl_result)
            stats = stats.assign(model_alpha=temp['alpha'].array, model_beta=temp['beta'].array)
            # 存进去原始数据而不是rank
            _rank_list[class_name] = stats
        _tm_part3_end = time.time()
        print(f' part3 cost time {_tm_part3_end - _tm_part3_start}')
        res = []
        _tm_part4_start = time.time()
        for class_name in self.REPLACE_DICT.keys():
            stats = _rank_list[class_name].drop(columns=['name', 'start_date', 'end_date'])
            if class_name != 'money':
                stats['score'] = score_rescale(normalize(stats['trade_year']) + normalize(stats['annualized_ret']) + normalize(stats['sharpe']) + normalize(-stats['mdd']) + normalize(stats['model_alpha']) + normalize(stats['model_beta']))
            else:
                stats['score'] = score_rescale(normalize(stats['trade_year']) + normalize(stats['annualized_ret']) + normalize(-stats['annualized_vol']))
            #stats = stats[stats.notna().any(axis=1)]
            stats = stats.rename_axis(index='manager_id').reset_index()
            stats['fund_type'] = class_name
            stats['datetime'] = eval_date
            res.append(stats)
        self._result = pd.concat(res)
        self._data_helper._upload_derived(self._result, FundManagerScore.__table__.name)
        _tm_part4_end = time.time()
        print(f' part4 cost time {_tm_part4_end - _tm_part4_start}')
        print(f'{eval_date} done, cost {_tm_part4_end - _tm_part3_start}')

    def _preprocess_manager_index_df(self, x):
        df = x.drop(columns='fund_type').pivot(index='datetime', columns='manager_id', values='manager_index')
        self.mng_index_list[x.fund_type.array[0]] = df.set_axis(df.index)

    def calc_mng_indicator(self, start_date: str, end_date: str):
        self.init(start_date=start_date, end_date=end_date, is_mng_indicator=True)
        eval_date_dt_list = []
        for eval_date in self.trim_days.sort_values(ascending=False).array:
            eval_date_dt = pd.to_datetime(eval_date, infer_datetime_format=True).date()
            eval_date_dt_list.append(eval_date_dt)
        eval_date_dt_list = [ i for i in eval_date_dt_list if i.weekday() == 4]
        #eval_date_dt_list = [i for i in eval_date_dt_list if i < last_date ]
        #eval_date_dt_list = [i for i in eval_date_dt_list if i > datetime.date(2011,1,1)]
        p = Pool()
        for i in p.imap_unordered(partial(self._calc_part3), eval_date_dt_list, 16):
            pass
        print('all done, to close and join')
        p.close()
        p.join()

    def _do_score_history(self, start_date: str, end_date: str):
        self.trading_days: pd.DataFrame = self._basic_api.get_trading_day_list()
        self.trading_days['datetime'] = self.trading_days.datetime.map(str)
        self.trading_days = self.trading_days[(self.trading_days.datetime >= start_date) & (self.trading_days.datetime <= end_date)]
        print('load td done')

        with DerivedDatabaseConnector().managed_session() as quant_session:
            mng_query = quant_session.query(
                FundManagerInfo.mng_id,
                FundManagerInfo.start_date,
                FundManagerInfo.fund_id,
                FundManagerInfo.mng_name,
                FundManagerInfo.end_date)
            self.fund_manager_info: pd.DataFrame = pd.read_sql(mng_query.statement, mng_query.session.bind)
            self.fund_manager_info = ManagerProcessor._clean_fm(self.fund_manager_info)
            print('load fm done')

        self.index_price: pd.DataFrame = self._basic_api.get_index_price(index_list=list(self.INDEX_LIST.keys()))
        self.index_price = self._clean_index(self.index_price, self.trading_days).loc[start_date:end_date]
        print('load base index done')

        with BasicDatabaseConnector().managed_session() as quant_session:
            fund_info_query = quant_session.query(FundInfo)
        self.fund_info: pd.DataFrame = pd.read_sql(fund_info_query.statement, fund_info_query.session.bind)
        print('load info done')

        fund_manager_index: pd.DataFrame = DerivedDataApi().get_fund_manager_index().drop(columns='_update_time')
        print('load fund manager index done')
        fund_manager_index.groupby(by='fund_type', sort=False).apply(self._preprocess_manager_index_df)
        print('process fund manager index done')

        self.manager_name_dict = dict(zip(self.fund_manager_info['manager_id'].tolist(), self.fund_manager_info['name'].tolist()))
        self.class_fund = {}
        for class_name, index_id in self.REPLACE_DICT.items():
            self.class_fund[class_name] = self.fund_info[self.fund_info['wind_class_2'].isin(FUND_CLASSIFIER[class_name])].fund_id
        print('all data done, to calc fund manager score day by day')

        eval_date_dt_list: List[datetime.date] = []
        min_date = fund_manager_index.datetime.min()
        for eval_date in self.trading_days.datetime.sort_values(ascending=False).array:
            eval_date_dt = pd.to_datetime(eval_date, infer_datetime_format=True).date()
            if eval_date_dt < min_date:
                continue

            eval_date_dt_list.append(eval_date_dt)
            # eval_start_date_dt = eval_date_dt - datetime.timedelta(days=365)
            # self._calc_part3(eval_start_date_dt.isoformat(), eval_date_dt.isoformat(), self.manager_name_dict, self.class_fund)
            # print(f'{eval_date_dt} done')

        p = Pool()
        for i in p.imap_unordered(partial(self._calc_part3, self.manager_name_dict, self.class_fund), eval_date_dt_list, 16):
            pass
        print('all done, to close and join')
        p.close()
        p.join()

    def do_score_update(self, eval_date_dt: datetime.date):
        self.manager_name_dict = dict(zip(self.fund_manager_info['manager_id'].tolist(), self.fund_manager_info['name'].tolist()))
        self.class_fund = {}
        for class_name, index_id in self.REPLACE_DICT.items():
            self.class_fund[class_name] = self.fund_info[self.fund_info['wind_class_2'].isin(FUND_CLASSIFIER[class_name])].fund_id
        self._calc_part3(eval_date_dt)

    def do_index_history(self, start_date: str, end_date: datetime.date, history: bool = False) -> List[str]:
        self.init(start_date, end_date, is_mng_index=True)
        print('init done, to calc manager index')
        self.calc_index()
        for class_type, df in self.mng_index_list.items():
            self.index_to_inserted = df.rename_axis(index='datetime', columns='manager_id').stack().rename('manager_index').reset_index()
            if not history:
                self.index_to_inserted = self.index_to_inserted[self.index_to_inserted.datetime == end_date]
            self.index_to_inserted['fund_type'] = class_type
            self._data_helper._upload_derived(self.index_to_inserted, FundManagerIndex.__table__.name)

    def process(self, end_date: str):
        failed_tasks = []
        try:
            end_date_dt: datetime.date = pd.to_datetime(end_date, infer_datetime_format=True).date()
            self.do_index_history('2005-01-01', end_date_dt)
            self.do_score_update(end_date_dt)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_manager_processor')
        return failed_tasks


if __name__ == '__main__':
    fmis = ManagerProcessor(DerivedDataHelper())
    fmis.process('20210128')
    # fmis.do_index_history(start_date='2005-01-01', end_date='2020-09-07', eval_date='2020-09-07', eval_start_date='2005-01-01')
    # fmis.do_score_history(start_date='2005-01-01', end_date='2020-09-07')
