
from typing import Dict, Optional, Union, Tuple, List
from . import DataManager
import pandas as pd
import numpy as np
import datetime
import time
import io
import copy
import json
import contextlib
import re
from ...stock.factor.api import StockFactorApi
from ..wrapper.mysql import RawDatabaseConnector, BasicDatabaseConnector, DerivedDatabaseConnector
from .fund_info_filter import filter_fund_info, fund_info_update, active_fund_info, get_conv_funds
from ..struct import AssetPrice, FundScoreParam, TaaTunerParam, AssetTimeSpan
from .score import FundScoreManager, ScoreFunc
from .data_tables import FundDataTables
from .etl_tool import S3RetrieverForDM
from ..view.raw_models import CSIndexComponent
from ..view.basic_models import *
from ..view.derived_models import *
from .combine_single_fac import combine_factor, combine_factor_test

INDEX_REPLACE = {'active':'csi_stockfund',
                 'conv_bond':'csi_convex'}
INDEX_REPLACE_REVERSE = {v : k for k, v in INDEX_REPLACE.items()}

@contextlib.contextmanager
def profiled(file_name=None):
    import cProfile
    import pstats

    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    # uncomment this to see who's calling what
    # ps.print_callers()
    if file_name is None:
        print(s.getvalue())
    else:
        open(file_name, 'w').write(s.getvalue())


class FundDataManager(DataManager):

    _BLOCK_DF_LIST = ['fund_manager_score']

    def __init__(self, start_time=None, end_time=None, fund_score_param: FundScoreParam = None, score_manager: FundScoreManager = None, s3_retriever_activation: Optional[List[str]] = None):
        DataManager.__init__(self,
            start_time or datetime.datetime(2011, 1, 1),
            end_time or datetime.datetime.now()
        )
        self._s3_retriever = S3RetrieverForDM(activation=s3_retriever_activation)
        self._fund_score_param = fund_score_param or FundScoreParam(tag_type=1, score_method=1, is_full=1)
        self.dts = FundDataTables()
        self._is_inited = False
        self._score_manager = score_manager or FundScoreManager()
        self.set_score_param(self._fund_score_param)
        self.fund_list_with_nav = set()
        self.access_token_dic = {}


    @property
    def inited(self):
        return self._is_inited

    def _init_from_s3_part(self) -> bool:
        # 获取所有dts
        failed_tasks: List[str] = self._s3_retriever.retrieve_all_dfs(self)
        if failed_tasks:
            print(f'retrieve dm failed from s3 (err_info){failed_tasks}')
            return False

        # 其余初始化流程
        self.fund_list_with_nav = set(self.dts.fund_nav.columns.union(self.dts.fund_unit_nav.columns).array)
        self.end_date_dic = self.dts.fund_info[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
        self.dts.fix_data()
        self._score_manager.set_dts(self.dts)
        return True

    # 使用全默认配置的DM(包括DM自己的参数以及FundScoreManager等)
    def _init_from_s3_with_all_default_config(self):
        print('try to init from s3 with all default config')

        # 初始化取得默认配置的DM
        if not self._init_from_s3_part():
            return

        # 取得默认算好的fund score
        failed_tasks: List[str] = self._s3_retriever.retrieve_fund_score(self._score_manager)
        if failed_tasks:
            print(f'retrieve fund score for dm from s3 failed (err_info){failed_tasks}')
            return

        self._is_inited = True
        print('init from s3 with all default config done')

    # 使用默认配置的DM+自定义的FundScoreManager
    def _init_from_s3_with_score_customized(self, score_pre_calc, use_weekly_monthly_indicators):
        print('try to init from s3 with score customized')

        # 初始化取得默认配置的DM
        if not self._init_from_s3_part():
            return

        _t0 = time.time()
        if score_pre_calc:
            # 由于FundScoreManager是自定义的，这里重新算一下
            self._score_manager.pre_calculate(is_filter_c=True, use_weekly_monthly_indicators=use_weekly_monthly_indicators)
            self._score_manager.pre_calculate_manager()
        _t1 = time.time()

        self._is_inited = True
        print(f'init from s3 with score customized done, score pre calculation costs {_t1 - _t0}')

    def try_to_init_from_s3(self, default_value_flag: List[bool], score_pre_calc, use_weekly_monthly_indicators, block_df_list) -> bool:
        # 判断init中的参数是否都是与默认值相同的值
        if not all(default_value_flag):
            return False

        # 判断FundScoreManager相关的参数是否是默认的
        score_manager = FundScoreManager()
        score_manager.set_param(FundScoreParam(tag_type=1, score_method=1, is_full=1))
        if self._score_manager == score_manager:
            self._init_from_s3_with_all_default_config()
        else:
            self._init_from_s3_with_score_customized(score_pre_calc, use_weekly_monthly_indicators)
        if not self._is_inited:
            print('init failed from s3')
            return False

        # 干掉不用的字段以节省内存
        self.dts.remove_fields(block_df_list)
        return True

    def init(self, index_list=None, score_pre_calc=True, print_time=False, use_weekly_monthly_indicators=False, block_df_list=_BLOCK_DF_LIST):
        
        if self._s3_retriever.is_activated:
            # Caution!! 这里应始终保持init传进来的参数与try_to_init_from_s3第一个参数相适应，以正确判断是否为默认配置
            # 如果init中的参数改成keyword类型，可以使用__kwdefaults__来帮助判断
            std_dm = DataManager(datetime.datetime(2011, 1, 1), datetime.datetime.now())
            if self.try_to_init_from_s3([self.start_date == std_dm.start_date,
                                        self.end_date == std_dm.end_date,
                                        index_list is None or not index_list,
                                        use_weekly_monthly_indicators is False,
                                        ], score_pre_calc, use_weekly_monthly_indicators, block_df_list):
                # 从s3成功读取数据，直接返回
                return
        print('could not init from s3 directly, do normal initialization')
        _tm_start = time.time()
        index_list = index_list or list(AssetTimeSpan.__dataclass_fields__.keys())
        index_list = [INDEX_REPLACE.get(_, _) for _ in index_list]

        def fetch_table(session, view):
            query = session.query(view)
            return self._s3_retriever.fetch_table(query)

        def _index_price_filter(query, index_list):
            def _index_price_filter_etl(x):
                return x[x.index_id.isin(index_list) & (x.datetime >= self.start_date) & (x.datetime <= self.end_date)].reset_index(drop=True)

            return query.filter(
                IndexPrice.index_id.in_(index_list),
                IndexPrice.datetime >= self.start_date,
                IndexPrice.datetime <= self.end_date
            ), _index_price_filter_etl

        def _fund_nav_filter(query, fund_id_list):
            def _fund_nav_filter_etl(x):
                return x[x.fund_id.isin(fund_id_list) & (x.datetime >= self.start_date) & (x.datetime <= self.end_date)].reset_index(drop=True)

            return query.filter(
                FundNav.fund_id.in_(fund_id_list),
                FundNav.datetime >= self.start_date,
                FundNav.datetime <= self.end_date,
            ), _fund_nav_filter_etl

        def _fund_size_and_hold_rate_filter(query, fund_id_list):
            def _fund_size_and_hold_rate_filter_etl(x):
                return x[x.fund_id.isin(fund_id_list) & (x.datetime >= self.start_date - datetime.timedelta(days=200)) & (x.datetime <= self.end_date)].reset_index(drop=True)

            return query.filter(
                Fund_size_and_hold_rate.fund_id.in_(fund_id_list),
                Fund_size_and_hold_rate.datetime >= self.start_date - datetime.timedelta(days=200),
                Fund_size_and_hold_rate.datetime <= self.end_date,
            ), _fund_size_and_hold_rate_filter_etl

        def _fund_indicator_filter(query, fund_id_list):
            def _fund_indicator_filter_etl(x):
                return x[x.fund_id.isin(fund_id_list) & (x.datetime >= self.start_date) & (x.datetime <= self.end_date)].reset_index(drop=True)

            return query.filter(
                FundIndicator.fund_id.in_(fund_id_list),
                FundIndicator.datetime >= self.start_date,
                FundIndicator.datetime <= self.end_date,
            ), _fund_indicator_filter_etl

        def _fund_indicator_annual_filter(query):
            def _fund_indicator_annual_filter_etl(x):
                return x[x.fund_id.isin(self.dts.fund_list) & (x.datetime <= self.end_date)].reset_index(drop=True)

            return query.filter(
                FundIndicatorAnnual.fund_id.in_(self.dts.fund_list),
                FundIndicatorAnnual.datetime <= self.end_date,
            ), _fund_indicator_annual_filter_etl

        def _index_valuation_long_term_filter(query, pct_index_list):
            def _index_valuation_long_term_filter_etl(x):
                x = x[x.index_id.isin(pct_index_list) & (x.datetime >= self.start_date) & (x.datetime <= self.end_date)].reset_index(drop=True)
                return x.sort_values(by='datetime', axis=0)

            return query.filter(
                IndexValuationLongTerm.index_id.in_(pct_index_list),
                IndexValuationLongTerm.datetime >= self.start_date,
                IndexValuationLongTerm.datetime <= self.end_date,
            ).order_by(IndexValuationLongTerm.datetime.asc()), _index_valuation_long_term_filter_etl

        def _fund_indicator_weekly_filter(query):
            def _fund_indicator_weekly_filter_etl(x):
                return x[x.fund_id.isin(self.dts.fund_list) & (x.datetime >= self.start_date) & (x.datetime <= self.end_date)].reset_index(drop=True)

            return query.filter(
                FundIndicatorWeekly.fund_id.in_(self.dts.fund_list),
                FundIndicatorWeekly.datetime >= self.start_date,
                FundIndicatorWeekly.datetime <= self.end_date,
            ), _fund_indicator_weekly_filter_etl

        def _fund_manager_score_filter(query):
            def _fund_manager_score_filter_etl(x):
                return x[x.fund_type.isin(['stock']) & (x.datetime >= (self.start_date - datetime.timedelta(days=20))) & (x.datetime <= self.end_date)].reset_index(drop=True)

            return query.filter(
                FundManagerScore.fund_type.in_(['stock']),
                FundManagerScore.datetime >= self.start_date - datetime.timedelta(days=20),
                FundManagerScore.datetime <= self.end_date,
            ), _fund_manager_score_filter_etl

        def _fund_manager_fund_rank_info_filter(query):
            def _fund_manager_fund_rank_info_filter_etl(x):
                return x[(x.datetime >= self.start_date) & (x.datetime <= self.end_date)].reset_index(drop=True)

            return query.filter(
                FundManagerFundRank.datetime >= self.start_date,
                FundManagerFundRank.datetime <= self.end_date,
                #ManagerFundDetail.datetime >= self.start_date,
                #ManagerFundDetail.datetime <= self.end_date,
            ), _fund_manager_fund_rank_info_filter_etl

        with RawDatabaseConnector().managed_session() as raw_session:
            _tm_raw_start = time.time()
            self.dts.cs_index_component = fetch_table(raw_session, CSIndexComponent)
            _tm_raw_cs_index_component = time.time()
            if print_time:
                print(f'\t[time][raw] fetch cs index component: {_tm_raw_cs_index_component - _tm_raw_start}')

        # info is necessary
        with BasicDatabaseConnector().managed_session() as quant_session:
            _tm_basic_start = time.time()
            self.dts.fund_info = fetch_table(quant_session, FundInfo)
            self.dts.fund_benchmark_info = fetch_table(quant_session, FundBenchmark)
            self.dts.active_fund_info = active_fund_info(self.dts.fund_info, self.dts.fund_benchmark_info)
            _tm_basic_fetch_info = time.time()
            self.dts.fund_info = fund_info_update(self.dts.fund_info)
            self.dts.fund_status_latest = fetch_table(quant_session, FundStatusLatest)
            self.dts.fund_end_date_dict = self.dts.fund_info.set_index('fund_id').to_dict()['end_date']
            _fund_open_info = fetch_table(quant_session, FundOpenInfo)
            _filter_fund_info = filter_fund_info(self.dts.fund_info, index_list)
            _tm_basic_filter_info = time.time()
            self.dts.fund_list = set(_filter_fund_info.fund_id)
            self.dts.all_fund_list = self.dts.fund_list.union(self.dts.active_fund_info.fund_id)
            _in_market_fund_df = self.dts.fund_status_latest[~self.dts.fund_status_latest['trade_status'].isnull()]
            in_market_fund_list = _in_market_fund_df[~((_in_market_fund_df.redem_status == '正常赎回') & (_in_market_fund_df.purch_status == '正常申购'))]
            in_market_fund_list = in_market_fund_list.fund_id.tolist()
            close_fund_list = _fund_open_info.fund_id.tolist()
            self.dts.fund_ipo_stats = fetch_table(quant_session, FundIPOStats)
            self.dts.fund_conv_stats = fetch_table(quant_session, FundConvStats)
            self.dts.fund_conv_list = get_conv_funds(self.dts.fund_conv_stats, self.dts.fund_info)
            self.dts.fund_conv_list = {i for i in self.dts.fund_conv_list if (i not in in_market_fund_list) and (i not in close_fund_list)}
            self.dts.all_fund_list = {i for i in self.dts.all_fund_list if (i not in in_market_fund_list) and (i not in close_fund_list)}
            self.dts.all_fund_list = self.dts.all_fund_list.union(self.dts.fund_conv_list)
            _normal_funds_index_dic = {cur.fund_id: cur.index_id for cur in _filter_fund_info.itertuples()}
            _active_funds_index_dic = {i.fund_id: i.index_id for i in self.dts.active_fund_info.itertuples()}
            self.dts.fund_index_map = {**_normal_funds_index_dic, **_active_funds_index_dic}
            self.end_date_dic = self.dts.fund_info[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
            _tm_basic_prep_struct = time.time()
            self.dts.trading_days = fetch_table(quant_session, TradingDayList)
            self.dts.trading_days = self.dts.trading_days[self.dts.trading_days.datetime <= self.end_date]
            trim_trading_days = self.dts.trading_days[(self.dts.trading_days.datetime >= self.start_date) & (self.dts.trading_days.datetime <= self.end_date)].datetime
            ipo_weight_last_year_df = self.dts.fund_ipo_stats.pivot_table(index='end_date', columns='fund_id', values='ipo_allocation_weight').fillna(0)
            _trim_trading_days = ipo_weight_last_year_df.index.union(trim_trading_days)
            ipo_weight_last_year_df = ipo_weight_last_year_df + ipo_weight_last_year_df.shift(1).fillna(0) + ipo_weight_last_year_df.shift(2).fillna(0) + ipo_weight_last_year_df.shift(3).fillna(0)
            ipo_weight_last_year_df = ipo_weight_last_year_df.reindex(_trim_trading_days).fillna(method='ffill').stack().reset_index().rename(columns={0:'ipo_weight','level_0':'datetime'})
            _tm_basic_fetch_days = time.time()
            # index
            self.dts.index_info = fetch_table(quant_session, IndexInfo)
            _tm_basic_fetch_index_info = time.time()
            _index_query = quant_session.query(
                IndexPrice.index_id,
                IndexPrice.datetime,
                IndexPrice.close
            )
            _index_query, _index_price_filter_func = _index_price_filter(_index_query, index_list)
            index_price_raw = self._s3_retriever.fetch_table(_index_query, _index_price_filter_func)
            self.dts.index_price = index_price_raw.pivot_table(index='datetime', columns='index_id', values='close').reindex(trim_trading_days).fillna(method='ffill').rename(columns = INDEX_REPLACE_REVERSE)
            _tm_basic_fetch_index_price = time.time()
            # fund nav
            _fund_nav_query = quant_session.query(
                FundNav.fund_id,
                FundNav.adjusted_net_value,
                FundNav.unit_net_value,
                FundNav.datetime
                # FundNav.subscribe_status,
                # FundNav.redeem_status,
            )
            _fund_nav_query, _fund_nav_filter_func = _fund_nav_filter(_fund_nav_query,self.dts.all_fund_list)
            _nav_df = self._s3_retriever.fetch_table(_fund_nav_query, _fund_nav_filter_func)
            _tm_basic_fetch_fund_nav = time.time()

            # 这里我们制作一个总的pivot_table再取值，会比分别两次pivot_table快一些
            # 如果index-column pair有重复的值，pivot会报错而pivot_table不会，所以这里用pivot也许更好些
            # 但是pivot里边会调用set_index，导致datetime列的dtype从object变为datetime64[ns]
            _temp_fund_nav = _nav_df.pivot_table(index='datetime', columns='fund_id')
            self.dts.fund_nav = _temp_fund_nav['adjusted_net_value'].dropna(axis=1, how='all').fillna(method='ffill')
            self.dts.fund_unit_nav = _temp_fund_nav['unit_net_value'].dropna(axis=1, how='all').fillna(method='ffill')
            self.fund_list_with_nav = set(self.dts.fund_nav.columns.union(self.dts.fund_unit_nav.columns).array)
            _tm_basic_pivot_fund_nav = time.time()

            # fund size and fund com hold
            # 机构持仓比例每六个月更新，提前取半年以上, 填充空白值用
            # fund_com_hold fund_size 和 fund_nav同结构，日期纵轴，基金代码横轴
            _fund_size_and_hold_rate_query = quant_session.query(
                Fund_size_and_hold_rate.fund_id,
                Fund_size_and_hold_rate.size,
                Fund_size_and_hold_rate.institution_holds,
                Fund_size_and_hold_rate.datetime
            )
            _fund_size_and_hold_rate_query, _fund_size_and_hold_rate_filter_func = _fund_size_and_hold_rate_filter(_fund_size_and_hold_rate_query,self.dts.all_fund_list)
            _size_and_hold_rate = self._s3_retriever.fetch_table(_fund_size_and_hold_rate_query, _fund_size_and_hold_rate_filter_func)
            _temp_size_and_hold_rate = _size_and_hold_rate.pivot(index='datetime', columns='fund_id')
            _temp_size_and_hold_rate.index = [i.date() for i in _temp_size_and_hold_rate.index]
            _dt_index = _temp_size_and_hold_rate.index.union(self.dts.trading_days[self.dts.trading_days.datetime >= (self.start_date - datetime.timedelta(days=200))].datetime)
            _temp_size_and_hold_rate = _temp_size_and_hold_rate.reindex(_dt_index).fillna(method='ffill')
            self.dts.fund_size = _temp_size_and_hold_rate['size']
            self.dts.fund_com_hold = _temp_size_and_hold_rate['institution_holds']
            _tm_basic_fetch_fund_size = time.time()
            # _hedge_fund_nav: Optional[pd.DataFrame] = fetch_table(quant_session, HedgeFundNAV)
            # _hedge_fund_nav = _hedge_fund_nav.sort_values(by=['fund_id', 'datetime', 'insert_time']).drop_duplicates(subset=['fund_id', 'datetime'], keep='last')
            # self.dts._hedge_fund_nav = _hedge_fund_nav.pivot(index='datetime', columns='fund_id', values='v_net_value')
            # _tm_basic_fetch_hedge_fund_nav = time.time()

            if print_time:
                print(f'\t[time][basic] fetch fund info : {_tm_basic_fetch_info - _tm_basic_start}')
                print(f'\t[time][basic] filter fund info: {_tm_basic_filter_info - _tm_basic_fetch_info}')
                print(f'\t[time][basic] prep fund struct: {_tm_basic_prep_struct - _tm_basic_filter_info}')
                print(f'\t[time][basic] fetch trade days: {_tm_basic_fetch_days - _tm_basic_prep_struct}')
                print(f'\t[time][basic] fetch index info: {_tm_basic_fetch_index_info - _tm_basic_fetch_days}')
                print(f'\t[time][basic] fetch index price: {_tm_basic_fetch_index_price - _tm_basic_fetch_index_info}')
                print(f'\t[time][basic] fetch fund navs: {_tm_basic_fetch_fund_nav - _tm_basic_fetch_index_price}')
                print(f'\t[time][basic] pivot fund navs: {_tm_basic_pivot_fund_nav - _tm_basic_fetch_fund_nav}')
                print(f'\t[time][basic] fetch fund size: {_tm_basic_fetch_fund_size - _tm_basic_pivot_fund_nav}')
                # print(f'\t[time][basic] fetch hedge nav: {_tm_basic_fetch_hedge_fund_nav - _tm_basic_fetch_fund_size}')
        _tm_basic = time.time()

        # 连续四个季度可转债占比 大于20%
        conv_df = self.dts.fund_conv_stats.pivot_table(index='datetime', values='conv_weights', columns='fund_id')
        _date_list = conv_df.index.tolist()
        conv_dict = {}
        for idx, dt in enumerate(_date_list):
            _df = conv_df.iloc[max(idx-4,0):(idx+1)]
            fund_list = _df.columns[_df.min() > 20].values.tolist()
            conv_dict[dt] = fund_list

        # get derived data first
        with DerivedDatabaseConnector().managed_session() as derived_session:
            _tm_deriv_start = time.time()
            _fund_indicator_query = derived_session.query(
                FundIndicator.fund_id,
                FundIndicator.datetime,
                FundIndicator.alpha,
                FundIndicator.beta,
                FundIndicator.fee_rate,
                FundIndicator.track_err,
                FundIndicator.year_length,
                FundIndicator.info_ratio,
                FundIndicator.alpha_bond,
                FundIndicator.beta_bond,
                FundIndicator.alpha_hs300,
                FundIndicator.beta_hs300,
                # FundIndicator.down_risk,
                # FundIndicator.ret_over_period,
                # FundIndicator.treynor,
                # FundIndicator.mdd,
                # FundIndicator.m_square,
                # FundIndicator.var,
                # FundIndicator.r_square,
                # FundIndicator.sharpe,
                # FundIndicator.annual_ret,
                # FundIndicator.annual_vol,
                # FundIndicator.time_ret,
            )
            _fund_indicator_query, _fund_indicator_filter_func = _fund_indicator_filter(_fund_indicator_query, self.dts.all_fund_list)
            self.dts.fund_indicator = self._s3_retriever.fetch_table(_fund_indicator_query, _fund_indicator_filter_func)
            _tm_deriv_fetch_fund_indicator = time.time()
            _tm_deriv_apply_fund_indicator = time.time()
            _fund_indicator_query = derived_session.query(
                FundIndicatorAnnual
            )
            _fund_indicator_query, _fund_indicator_filter_func = _fund_indicator_annual_filter(_fund_indicator_query)
            self.dts.fund_indicator_annual = self._s3_retriever.fetch_table(_fund_indicator_query, _fund_indicator_filter_func)
            self.dts.fund_indicator_annual = self.dts.fund_indicator_annual.set_index(['fund_id','datetime'])
            _tm_deriv_fetch_fund_indicator_annual = time.time()
            # fetch index val data from derived table, and choose different pct value for different index_id
            _tm_deriv_fetch_index_pct = time.time()
            pct_index_list = list(TaaTunerParam.POOL.keys())
            _index_pct_query = derived_session.query(
                IndexValuationLongTerm
            )
            _index_pct_query, _index_pct_filter_func = _index_valuation_long_term_filter(_index_pct_query, pct_index_list)
            self.dts._index_pct_df = self._s3_retriever.fetch_table(_index_pct_query, _index_pct_filter_func).set_index('index_id')
            # 按照trading date 作为index, fillna
            date_list = self.dts.trading_days.datetime.tolist()
            res = []
            for index_id in pct_index_list:
                df = self.dts._index_pct_df[self.dts._index_pct_df.index == index_id].set_index('datetime').reindex(date_list).reset_index().fillna(method='ffill')
                df.loc[:, 'index_id'] = index_id
                res.append(df)
            _index_pct_df = pd.concat(res, axis=0)
            index_val_list = list(TaaTunerParam.INDEX_PCT_SELECTED.keys())
            self.dts.index_pct = _index_pct_df[['datetime','index_id'] + index_val_list].rename(
                columns=TaaTunerParam.INDEX_PCT_SELECTED).pivot_table(index=['datetime', 'index_id'], values=['pe_pct', 'pb_pct', 'ps_pct'])
            self.dts.index_date_list = list(self.dts.index_pct.index.remove_unused_levels().levels[0])
            _tm_deriv_apply_index_pct = time.time()

            _fund_manager_score_query = derived_session.query(
                FundManagerScore.manager_id,
                FundManagerScore.datetime,
                FundManagerScore.trade_year,
                FundManagerScore.annualized_ret,
                FundManagerScore.annualized_vol,
                FundManagerScore.model_alpha,
                FundManagerScore.model_beta,
                FundManagerScore.sharpe,
                FundManagerScore.fund_type,
                FundManagerScore.fund_size,
                FundManagerScore.now_comp_year,
                FundManagerScore.year_ret_std,
            )
            _fund_manager_score_query, _fund_manager_score_filter_func = _fund_manager_score_filter(_fund_manager_score_query)
            self.dts.fund_manager_score = self._s3_retriever.fetch_table(_fund_manager_score_query, _fund_manager_score_filter_func).drop(columns='fund_type')
            _dt =self.dts.trading_days[self.dts.trading_days.datetime >= self.dts.fund_manager_score.datetime.min()].datetime
            self.dts.fund_manager_score = self.dts.fund_manager_score.pivot_table(index='datetime', columns='manager_id').reindex(_dt).fillna(method='ffill').reindex(trim_trading_days).stack().reset_index()
            _tm_deriv_apply_active_indicator = time.time()
            _fund_manager_info_query = derived_session.query(
                FundManagerInfo
            )
            self.dts.fund_manager_info = self._s3_retriever.fetch_table(_fund_manager_info_query)
            _df = self.dts.fund_manager_info[self.dts.fund_manager_info['end_date'] == datetime.date(2040,1,1)][['mng_id','fund_id']].groupby('mng_id').count()
            self.dts.fund_manager_info = self.dts.fund_manager_info.set_index('mng_id')
            self.dts.fund_manager_info = self.dts.fund_manager_info.join(_df.rename(columns={'fund_id':'fund_num'}))
            _tm_deriv_apply_manager_info = time.time()
            _fund_manager_fund_rank_info_query = derived_session.query(
                #ManagerFundDetail.mng_id,
                #ManagerFundDetail.datetime,
                #ManagerFundDetail.stock_fund_list,
                FundManagerFundRank.mng_id,
                FundManagerFundRank.datetime,
                FundManagerFundRank.fund_list,
            )
            _fund_manager_fund_rank_info_query, _fund_manager_fund_rank_info_filter_func = _fund_manager_fund_rank_info_filter(_fund_manager_fund_rank_info_query)
            self.dts.fund_manager_rank = self._s3_retriever.fetch_table(_fund_manager_fund_rank_info_query, _fund_manager_fund_rank_info_filter_func)
            #self.dts.fund_manager_rank['stock_fund_list'] = [ json.loads(i) for i in self.dts.fund_manager_rank.stock_fund_list]
            self.dts.fund_manager_rank['stock_fund_list'] = [ json.loads(i) for i in self.dts.fund_manager_rank.fund_list]
            self.dts.fund_manager_rank = self.dts.fund_manager_rank.set_index(['datetime','mng_id']).drop(columns=['fund_list'])
            _fund_manager_score = self.dts.fund_manager_score.rename(columns={'manager_id':'mng_id'}).set_index(['datetime','mng_id'])
            _df = _fund_manager_score.join(self.dts.fund_manager_rank).copy()
            _df = _df.explode('stock_fund_list').dropna()
            _df = _df.reset_index().drop('mng_id',axis=1).rename(columns={'stock_fund_list':'fund_id'})
            _cols = _df.columns.tolist()
            _mng_score_dic = { c : f'mng_{c}' for c in _cols if c not in ['datetime', 'fund_id']}
            _df = _df.rename(columns = _mng_score_dic)
            _df['datetime'] = _df.datetime.dt.date
            self.dts.fund_indicator = pd.merge(self.dts.fund_indicator, _df,how='left',left_on=['fund_id','datetime'],right_on=['fund_id','datetime'])
            _index_list = ['hs300','csi500','gem']

            self.dts.fund_indicator['index_id'] = self.dts.fund_indicator.fund_id.apply(lambda x: self.dts.fund_index_map.get(x, None))
            _fund_indicator_whole = self.dts.fund_indicator.copy()
            self.dts.fund_indicator = self.dts.fund_indicator.dropna(subset=['index_id'])
            conv_indicator_df = self.ipo_conv_indicator_process(conv_dict, 'conv_bond', _fund_indicator_whole)
            self.dts.fund_indicator = self.dts.fund_indicator.append(conv_indicator_df)
            self.dts.fund_indicator = pd.merge(self.dts.fund_indicator, ipo_weight_last_year_df,
                                                how='left', left_on=['fund_id','datetime'], right_on=['fund_id','datetime'])
            self.dts.fund_indicator['ipo_weight'] = self.dts.fund_indicator['ipo_weight'].fillna(0)
            _fund_size = self.dts.fund_size.stack().reset_index().rename(columns={0:'fund_size','level_0':'datetime'})
            self.dts.fund_indicator = pd.merge(self.dts.fund_indicator, _fund_size,
                                            how='left', left_on=['fund_id','datetime'], right_on=['fund_id','datetime'])
            self.dts.fund_indicator['fund_size'] = self.dts.fund_indicator['fund_size'].fillna(0)
            _single_fac_df = combine_factor()
            #_single_fac_df = combine_factor_test()
            self.dts.fund_indicator = pd.merge(self.dts.fund_indicator, _single_fac_df, how='outer', on=['datetime','fund_id'])
            self.dts.fund_indicator['active'] = self.dts.fund_indicator.fund_id.transform(lambda x: 0 if x in _normal_funds_index_dic and _normal_funds_index_dic[x] in _index_list else 1)
            self.dts.fund_indicator['index_id'] = self.dts.fund_indicator.fund_id.apply(lambda x: self.dts.fund_index_map.get(x, None))
            self.dts.fund_indicator = self.dts.fund_indicator.drop_duplicates(subset=['fund_id','datetime'])

            _tm_deriv_apply_manager_rank = time.time()

            if use_weekly_monthly_indicators:
                # indicator weekly 只有周日有值 在每一个fund上fillna, merge week_ly into indicator
                _fund_indicator_weekly_query = derived_session.query(
                    FundIndicatorWeekly.fund_id,
                    FundIndicatorWeekly.datetime,
                    FundIndicatorWeekly.alpha_w,
                    FundIndicatorWeekly.beta_w,
                    FundIndicatorWeekly.track_err_w,
                )
                _fund_indicator_weekly_query, _fund_indicator_weekly_filter_func = _fund_indicator_weekly_filter(_fund_indicator_weekly_query)
                _fund_indicator_weekly = self._s3_retriever.fetch_table(_fund_indicator_weekly_query, _fund_indicator_weekly_filter_func)
                _fund_indicator_weekly = _fund_indicator_weekly.pivot_table(index='datetime', columns='fund_id')
                _dt = _fund_indicator_weekly.index.union(date_list).set_names('datetime')  # 交易日，和现有indicator index 周日做并集
                _fund_indicator_weekly = _fund_indicator_weekly.reindex(index=_dt).fillna(method='ffill').stack().swaplevel()
                _fund_indicator_weekly = _fund_indicator_weekly.groupby(level='fund_id').apply(lambda x: x.droplevel(level=0).loc[:self.end_date_dic[x.index.get_level_values(0).array[0]], :])
                _tm_process_indicator_weekly = time.time()

                # indicator monthly 只有每月最后一天有值 在每一个fund上fillna, merge monthly into indicator
                _fund_indicator_monthly = fetch_table(derived_session, FundIndicatorMonthly)
                _fund_indicator_monthly = _fund_indicator_monthly.pivot_table(index='datetime', columns='fund_id')
                _dt = _fund_indicator_monthly.index.union(date_list).set_names('datetime')  # 交易日，和现有indicator index做并集
                _fund_indicator_monthly = _fund_indicator_monthly.reindex(index=_dt).fillna(method='ffill').stack().swaplevel()
                _fund_indicator_monthly = _fund_indicator_monthly.groupby(level='fund_id').apply(lambda x: x.droplevel(level=0).loc[:self.end_date_dic[x.index.get_level_values(0).array[0]], :])
                _tm_process_indicator_monthly = time.time()
                # 本来join可以传一个list of df进去一起join，效率应该更高，但这里用了on参数指定fund_indicator的其中两列（而不是index），这样便只能一次传一个df进去（pandas不支持这种情况下传一个list）
                for df in [_fund_indicator_weekly, _fund_indicator_monthly]:
                    self.dts.fund_indicator = self.dts.fund_indicator.join(df, on=['fund_id', 'datetime'], how='left')
                _tm_process_indicator_join = time.time()
                self.dts.fund_indicator_annual.index.set_levels(self.dts.fund_indicator_annual.index.levels[1].date, level=1, inplace=True)
                the_dict = self.dts.fund_indicator_annual.to_dict(orient='index')
                _res = self.dts.fund_indicator[['fund_id', 'datetime']].apply(lambda x : self._make_annual_fac(the_dict, x), axis=1)
                _tm_process_fund_annual_apply = time.time()
                _annual_fac_df = pd.DataFrame(_res.tolist())
                self.dts.fund_indicator = pd.merge(self.dts.fund_indicator,_annual_fac_df,how='left',left_on=['fund_id','datetime'],right_on=['fund_id','datetime'])
                _tm_process_fund_annual_join = time.time()
            else:
                _tm_process_indicator_weekly = time.time()
                _tm_process_indicator_monthly = _tm_process_indicator_weekly
                _tm_process_indicator_join = _tm_process_indicator_weekly
                _tm_process_fund_annual_apply = _tm_process_indicator_weekly
                _tm_process_fund_annual_join = _tm_process_indicator_weekly

            self.dts._barra_cne5_factor_return = fetch_table(derived_session, BarraCNE5FactorReturn)
            _tm_deriv_fetch_barra_cne5_factor_return = time.time()

            if print_time:
                print(f'\t[time][deriv] fetch fund indicator: {_tm_deriv_fetch_fund_indicator - _tm_deriv_start}')
                print(f'\t[time][deriv] apply fund indicator: {_tm_deriv_apply_fund_indicator - _tm_deriv_fetch_fund_indicator}')
                print(f'\t[time][deriv] fetch fund indicator annual: {_tm_deriv_fetch_fund_indicator_annual - _tm_deriv_apply_fund_indicator}')
                print(f'\t[time][deriv] fetch index val: {_tm_deriv_fetch_index_pct - _tm_deriv_fetch_fund_indicator_annual}')
                print(f'\t[time][deriv] pivot raw index: {_tm_deriv_apply_index_pct - _tm_deriv_fetch_index_pct}')
                print(f'\t[time][deriv] fetch active indicator score:  {_tm_deriv_apply_active_indicator - _tm_deriv_apply_index_pct}')
                print(f'\t[time][deriv] fetch manager info:  {_tm_deriv_apply_manager_info - _tm_deriv_apply_active_indicator}')
                print(f'\t[time][deriv] fetch manager rank :  {_tm_deriv_apply_manager_rank - _tm_deriv_apply_manager_info}')
                print(f'\t[time][deriv] process indicator weekly: {_tm_process_indicator_weekly - _tm_deriv_apply_manager_rank}')
                print(f'\t[time][deriv] process indicator monthly: {_tm_process_indicator_monthly - _tm_process_indicator_weekly}')
                print(f'\t[time][deriv] process indicator join: {_tm_process_indicator_join - _tm_process_indicator_monthly}')
                print(f'\t[time][deriv] process indicator annually apply: {_tm_process_fund_annual_apply - _tm_process_indicator_join}')
                print(f'\t[time][deriv] merge annual fac: {_tm_process_fund_annual_join - _tm_process_fund_annual_apply}')
                print(f'\t[time][deriv] fetch barra cne5 factor return: {_tm_deriv_fetch_barra_cne5_factor_return - _tm_process_fund_annual_join}')
        _tm_derived = time.time()
        self.dts.fix_data()
        _tm_fix = time.time()

        self._is_inited = True
        self._score_manager.set_dts(self.dts)
        if score_pre_calc:
            self._score_manager.pre_calculate(is_filter_c=True, use_weekly_monthly_indicators=use_weekly_monthly_indicators)
            self._score_manager.pre_calculate_manager()

        failed_tasks = self._s3_retriever.retrieve_dts(self.dts, ['mng_indicator_score', 'fund_indicator_score'])
        if failed_tasks:
            print(f'retrieve dm failed from s3 (err_info){failed_tasks}')

        failed_tasks = self._s3_retriever.retrieve_misc(self, ['mng_index_list'])
        if failed_tasks:
            print(f'retrieve dm failed from s3 (err_info){failed_tasks}')

        # 干掉不用的字段以节省内存
        self.dts.remove_fields(block_df_list)

        _tm_finish = time.time()
        print(self.dts)
        if print_time:
            print(f'[time] basic: {_tm_basic - _tm_start}')
            print(f'[time] deriv: {_tm_derived - _tm_basic}')
            print(f'[time] fix_d: {_tm_fix - _tm_derived}')
            print(f'[time] score: {_tm_finish - _tm_fix}')
            print(f'[time] total: {_tm_finish - _tm_start}')

    def _make_annual_fac(self, the_dict, x):
        fund_id = x.fund_id
        dt = x.datetime
        dic = {'fund_id': fund_id, 'datetime': dt}
        last_year = datetime.date(dt.year - 1,12,31)
        last_two_year = datetime.date(dt.year - 2,12,31)
        try:
            dic['last_year_alpha'] = the_dict[(fund_id, last_year)]['alpha_annual']
            dic['last_year_beta'] = the_dict[(fund_id, last_year)]['beta_annual']
            dic['last_two_year_alpha'] = the_dict[(fund_id, last_two_year)]['alpha_annual']
            dic['last_two_year_beta'] = the_dict[(fund_id, last_two_year)]['beta_annual']
        except KeyError:
            pass
        return dic

    def ipo_conv_indicator_process(self, dic, _index_id, _fund_indicator_whole):
        res = []
        _date_list = np.array(sorted(list(dic.keys())))
        for idx, dt in enumerate(_date_list):
            if dt < self.start_date:
                continue
            if (idx + 1) == len(_date_list):
                fund_list = dic[dt]
                if len(fund_list) == 0:
                    continue
                _df = _fund_indicator_whole[(_fund_indicator_whole.fund_id.isin(fund_list))
                                    & (_fund_indicator_whole.datetime >= dt)].copy()
                _df['index_id'] = _index_id
                res.append(_df)
            else:
                next_day = _date_list[idx + 1]
                fund_list = dic[dt]
                if len(fund_list) == 0:
                    continue
                _df = _fund_indicator_whole[(_fund_indicator_whole.fund_id.isin(fund_list))
                                    & (_fund_indicator_whole.datetime >= dt)
                                    & (_fund_indicator_whole.datetime < next_day)].copy()
                _df['index_id'] = _index_id
                res.append(_df)
        if not res:
            return
        return pd.concat(res)

    def _get_annual_alpha_beta(self, _fund_indicator_annual_fund_i, year):
        if year in _fund_indicator_annual_fund_i.index:
            return _fund_indicator_annual_fund_i.loc[year,'alpha_annual'], _fund_indicator_annual_fund_i.loc[year,'beta_annual']
        else:
            return None, None

    def set_score_param(self, score_param: FundScoreParam):
        self._score_manager.set_param(score_param)

    def get_index_pcts(self, dt):
        # jch: only pct within 7 days take effect
        INDEX_PCT_EFFECTIVE_DELAY_DAY_NUM = 7
        res = {}
        for index_id in self.dts.index_pct.columns:
            df = self.dts.index_pct[index_id]
            _filtered = df[(df.index <= dt) & (df.index >= dt - datetime.timedelta(days=INDEX_PCT_EFFECTIVE_DELAY_DAY_NUM))]
            if len(_filtered) > 0:
                res[index_id] = _filtered.iloc[-1]
        return res

    def get_index_pcts_df(self, dt):
        if dt not in self.dts.index_date_list:
            return pd.DataFrame()
        return self.dts.index_pct.loc[dt]

    def get_fund_score(self, dt, index_id, is_filter_c=True, score_func: Optional[ScoreFunc] = None) -> dict:
        return self._score_manager.get_fund_score(dt, index_id, is_filter_c, score_func)

    def get_fund_scores(self, dt, is_filter_c=True, fund_score_funcs: Optional[Dict[str, Union[ScoreFunc, str]]] = None) -> dict:
        return self._score_manager.get_fund_scores(dt, self.dts.index_list, is_filter_c, fund_score_funcs)

    def get_manager_scores(self, dt, score_select):
        manager_score, manager_funds = self._score_manager.get_manager_scores(dt, self.dts.active_fund_info.fund_id, score_select)
        if not manager_funds:
            return {}, {}, {}
        # 保证主动基金不买到相同基金的基金经理， 只保留高分基金经理， 用于fa helper.on_price -> target funds weight
        # 此分数不用于判定换仓 保留有相同最好基金的基金经理分数
        type_i = score_select['active']
        res = []
        _manager_score = manager_score[type_i]
        for mng_id in _manager_score:
            dic = {
                'mng_id':mng_id,
                'score':_manager_score[mng_id],
                'fund_id':manager_funds[mng_id]
            }
            res.append(dic)
        _df = pd.DataFrame(res).sort_values(['fund_id','score'],ascending = (True, False)).drop_duplicates(['fund_id'], keep='first')
        manager_score_cleaned = _df[['mng_id','score']].set_index('mng_id').to_dict()['score']
        return manager_score, manager_funds, {type_i:manager_score_cleaned}

    def get_fund_nav(self, dt):
        df = self.dts.fund_nav
        return df.loc[dt].to_dict()

    def get_fund_unit_nav(self, dt):
        df = self.dts.fund_unit_nav
        return df.loc[dt].to_dict()

    def confirm_fund_nav_exists(self, fund_ids):
        # param "fund_id" is str (id) or list of str (id_list)
        # get fund nav from db
        fund_list = []
        if type(fund_ids) is list:
            fund_list = fund_ids
        elif type(fund_ids) is str:
            fund_list = [fund_ids]
        fund_list_without_nav = []
        for fund_id in fund_list:
            if fund_id not in self.fund_list_with_nav:
                self.fund_list_with_nav.add(fund_id)
                fund_list_without_nav.append(fund_id)
        # print(f'fund_list: {fund_list}')
        # print(f'fund_list_without_nav: {fund_list_without_nav}')
        if fund_list_without_nav:
            with BasicDatabaseConnector().managed_session() as quant_session:
                _fund_nav_query = quant_session.query(
                    FundNav.fund_id,
                    FundNav.adjusted_net_value,
                    FundNav.unit_net_value,
                    FundNav.datetime
                ).filter(
                    FundNav.fund_id.in_(fund_list_without_nav),
                    FundNav.datetime >= self.start_date,
                    FundNav.datetime <= self.end_date,
                )
                _nav_df = pd.read_sql(_fund_nav_query.statement, _fund_nav_query.session.bind)
                if _nav_df is not None and not _nav_df.empty:
                    # 这里我们制作一个总的pivot_table再取值，会比分别两次pivot_table快一些
                    # 如果index-column pair有重复的值，pivot会报错而pivot_table不会，所以这里用pivot也许更好些
                    # 但是pivot里边会调用set_index，导致datetime列的dtype从object变为datetime64[ns]
                    _temp_fund_nav = _nav_df.pivot_table(index='datetime', columns='fund_id')

                    self.dts.fund_nav = self.dts.fund_nav.join(_temp_fund_nav['adjusted_net_value'].dropna(axis=1, how='all'), how='outer').fillna(method='ffill')
                    self.dts.fund_unit_nav = self.dts.fund_unit_nav.join(_temp_fund_nav['unit_net_value'].dropna(axis=1, how='all'), how='outer').fillna(method='ffill')
                else:
                    print(f'[fund_list_without_nav] no nav data of {fund_list_without_nav}')

        print(f'[fund_list_without_nav] fund_ids added: {fund_list_without_nav}')
        return fund_list_without_nav

    def get_fund_purchase_fees(self):
        return self.dts.fund_info.set_index('fund_id').purchase_fee.to_dict()

    def get_fund_redeem_fees(self):
        return self.dts.fund_info.set_index('fund_id').redeem_fee.to_dict()

    def get_fund_info(self):
        return self.dts.fund_info

    def get_trading_days(self):
        return self.dts.trading_days.copy()

    def get_index_price(self, dt=None):
        if dt:
            return self.dts.index_price.loc[dt]
        else:
            return self.dts.index_price.copy()

    def is_update_local_data(self, api_name):
        now = datetime.datetime.now()
        access_token = self.access_token_dic.get(api_name, None)
        if access_token is None or now > access_token:
            return True
        return False 
    
    def update_access_token(self, api_name):
        now = datetime.datetime.now()
        access_token = now + datetime.timedelta(hours=1)
        self.access_token_dic[api_name] = access_token

    def get_stock_ipo_data(self):
        dt = datetime.datetime.now().date()
        api_name = 'get_stock_ipo_data'
        if self.is_update_local_data(api_name):
            df = self.raw_data(func_name='get_em_stock_ipo_recent', dt=dt)
            self.dts.stock_ipo_data[dt] = df
            self.update_access_token(api_name)
        else:
            df = self.dts.stock_ipo_data.get(dt, None)
        return dt ,df
        
    def get_conv_bond_ipo_data(self):
        dt = datetime.datetime.now().date()
        api_name = 'get_conv_bond_ipo_data'
        if self.is_update_local_data(api_name):
            df = self.raw_data(func_name='get_em_conv_bond_ipo_recent', dt=dt)
            self.dts.conv_bond_ipo_data[dt] = df
            self.update_access_token(api_name)
        else:
            df = self.dts.conv_bond_ipo_data.get(dt, None)
        return dt ,df

    def get_stock_ipo_data_detail(self):
        dt = datetime.datetime.now().date()
        api_name = 'get_stock_ipo_data_detail'
        if self.is_update_local_data(api_name):
            df = self.view_data(func_name='get_recent_stock_ipo')
            self.dts.stock_ipo_data_detail[dt] = df
            self.update_access_token(api_name)
        else:
            df = self.dts.stock_ipo_data_detail.get(dt, None)
        return dt ,df

    def get_conv_bond_ipo_data_detail(self):
        dt = datetime.datetime.now().date()
        api_name = 'get_conv_bond_ipo_data_detail'
        if self.is_update_local_data(api_name):
            df = self.view_data(func_name='get_recent_conv_bond_ipo')
            self.dts.conv_bond_ipo_data_detail[dt] = df
            self.update_access_token(api_name)
        else:
            df = self.dts.conv_bond_ipo_data_detail.get(dt, None)
        return dt ,df

    def get_stock_ipo_info(self):
        dt = datetime.datetime.now().date()
        api_name = 'get_stock_ipo_info'
        if self.is_update_local_data(api_name):
            df = self.raw_data(func_name='get_em_stock_ipo_info')
            self.dts.stock_ipo_info[dt] = df
            self.update_access_token(api_name)
        else:
            df = self.dts.stock_ipo_info.get(dt, None)
        return dt ,df

    def get_conv_bond_ipo_info(self):
        dt = datetime.datetime.now().date()
        api_name = 'get_conv_bond_ipo_info'
        if self.is_update_local_data(api_name):
            df = self.raw_data(func_name='get_em_conv_bond_ipo_info')
            self.dts.conv_bond_ipo_info[dt] = df
            self.update_access_token(api_name)
        else:
            df = self.dts.conv_bond_ipo_info.get(dt, None)
        return dt ,df

    def get_stock_ipo_sector_info(self, begin_date, end_date, sector):
        dt, df = self.get_stock_ipo_info()
        if sector == '申购':
            df = df[(df['申购日期'] >= begin_date) & (df['申购日期'] <= end_date)].copy()
        elif sector == '上市':
            df = df[(df['上市日期'] >= begin_date) & (df['上市日期'] <= end_date)].copy()
        elif sector == '公布中签':
            df = df[(df['中签公布'] >= begin_date) & (df['中签公布'] <= end_date)].copy()
        return df

    def get_conv_bond_sector_info(self, begin_date, end_date, sector):
        df, df = self.get_conv_bond_ipo_info()
        if sector == '申购':
            df = df[(df['申购日期'] >= begin_date) & (df['申购日期'] <= end_date)].copy()
        elif sector == '上市':
            df = df[(df['上市日期'] >= begin_date) & (df['上市日期'] <= end_date)].copy()
        elif sector == '公布中签':
            df = df[(df['中签公布'] >= begin_date) & (df['中签公布'] <= end_date)].copy()
        return df

    def get_index_price_data(self, dt):
        _index_price = self.get_index_price(dt)
        return AssetPrice(**_index_price.to_dict())

    def get_cs_index_component(self) -> pd.DataFrame:
        return self.dts.cs_index_component

    def get_fund_indicator_annual(self) -> pd.DataFrame:
        return self.dts.fund_indicator_annual

    def fund_analysis(self, fund_id: str, is_plot: bool = False) -> Tuple[np.ndarray, pd.Series]:
        from ..fund.derived.barra_cne5_factor_processor import BarraCNE5FactorProcessor
        try:
            params, spec_ret, fund_ret, factor_ret_contri = BarraCNE5FactorProcessor.fund_analysis(self.dts._barra_cne5_factor_return, self.dts.fund_nav.loc[:, fund_id])
        except KeyError:
            return
        if is_plot:
            BarraCNE5FactorProcessor.fund_analysis_plot(fund_ret, factor_ret_contri)
        return params, spec_ret

    def _get_fund_nav_and_do_preprocessing(self, fund_id: str) -> Optional[pd.Series]:
        try:
            try:
                fund_nav: pd.Series = self.dts.fund_nav.loc[:, fund_id]
            except KeyError:
                print(f'[fund_analysis_new] do not have nav of {fund_id}, try to retrieve it')
                if not self.confirm_fund_nav_exists(fund_id):
                    return
                fund_nav = self.dts.fund_nav.loc[:, fund_id]
        except KeyError:
            print(f'[fund_analysis_new] do not have nav of {fund_id} as before, can not do analysis')
            return
        return fund_nav.reindex(fund_nav.index.intersection(self.dts.trading_days.datetime))

    def fund_return_analysis_by_stock_factors(self, fund_id: str, universe: str = 'default') -> Optional[pd.DataFrame]:
        '''对基金计算因子收益贡献序列'''
        fund_nav: Optional[pd.Series] = self._get_fund_nav_and_do_preprocessing(fund_id)
        if fund_nav is not None:
            return StockFactorApi.calc_factor_return_contribution(fund_nav.pct_change(), universe)

    def fund_analysis_by_stock_factors(self, fund_id: str, factor_names: Tuple[str], universe: str = 'default') -> Optional[pd.Series]:
        '''对基金计算因子暴露'''
        fund_nav: Optional[pd.Series] = self._get_fund_nav_and_do_preprocessing(fund_id)
        if fund_nav is not None:
            return StockFactorApi.decomp_ret(fund_nav.pct_change(), factor_names, universe)

    def index_return_analysis_by_stock_factors(self, index_id: str) -> Optional[pd.DataFrame]:
        '''对指数计算因子收益贡献序列'''
        try:
            index_price: pd.Series = self.dts.index_price.loc[:, index_id]
        except KeyError:
            print(f'[index_analysis_new] do not have price of {index_id}, can not do analysis')
            return
        return StockFactorApi.calc_factor_return_contribution(index_price.pct_change(), 'default')

    def index_analysis_by_stock_factors(self, index_id: str, factor_names: Tuple[str]) -> Optional[pd.Series]:
        '''对指数计算因子暴露'''
        try:
            index_price: pd.Series = self.dts.index_price.loc[:, index_id]
        except KeyError:
            print(f'[index_analysis_new] do not have price of {index_id}, can not do analysis')
            return
        return StockFactorApi.decomp_ret(index_price.pct_change(), factor_names, 'default')

    def fund_pos_analysis_by_stock_factors(self, fund_id: str, factor_names: Tuple[str], report_date: datetime.date) -> Optional[pd.DataFrame]:
        '''对基金持仓计算因子暴露'''
        return StockFactorApi.fac_pos(fund_id, factor_names, report_date)

    def white_and_black_list_filter(self, score, score_raw, disproved_list):
        return self._score_manager._white_and_black_list_filter(score, score_raw, disproved_list)

    def find_same_size_type_funds(self, desc_name):
        fund_info = self.dts.fund_info.copy()
        fund_info['trim_name'] = fund_info.desc_name.map(lambda x : re.subn(r'[ABCDEFR]{1,2}(\(人民币\)|\(美元现汇\)|\(美元现钞\)|1|2|3)?$', '', x)[0])
        fund_info = fund_info.set_index(['trim_name','desc_name'])
        index_1 = fund_info.loc[pd.IndexSlice[:, desc_name], :].index.get_level_values(0).values[0]
        return fund_info.loc[index_1]

    
        
def test():
    # m = FundDataManager('20190101', '20200101', score_manager=FundScoreManager())
    m = FundDataManager('20190101', '20200101')
    m.init()
    print(m.get_fund_info())
    print(m.get_trading_days())
    print(m.get_fund_score(datetime.date(2019, 1, 3), 'hs300'))


if __name__ == '__main__':
    with profiled(file_name='/tmp/test.txt'):
        m = FundDataManager('20190101', '20200101', score_manager=FundScoreManager())
        m.init()
