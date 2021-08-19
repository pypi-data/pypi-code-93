
from typing import Dict, Union, Optional
import datetime
import copy
import json
import numpy as np
import pandas as pd
import os
import time

from .asset_helper import SAAHelper, TAAHelper, FAHelper
from .trader import AssetTrader, FundTrader, BasicFundTrader
from .report import ReportHelper
from ...data.constant import _DEFAULT_CASH_VALUE
from ...data.struct import FundTrade, FundWeight, FundWeightItem, FundPosItem
from ...data.manager.manager_fund import FundDataManager
from ...data.manager.score import ScoreFunc, FundScoreManager
from ...data.struct import AssetWeight, AssetPrice, AssetPosition, AssetValue, ScoreSelect
from ...data.struct import FundPosition, TAAParam, AssetTradeParam, FundTradeParam, FAParam, ScoreType
from ...util.calculator import Calculator
from ...util.calculator_item import CalculatorBase

class FundEngine:

    DEFAULT_CASH_VALUE = _DEFAULT_CASH_VALUE

    def __init__(self, data_manager: FundDataManager, trader, taa_params:TAAParam=None, fa_params:FAParam=None, taa_param_details:dict=None, is_old_version=False, white_list:set=None, black_list:set=None, fund_score_funcs: Optional[Dict[str, Union[ScoreFunc, str]]] = None, score_select:ScoreSelect=None):
        self._dm = data_manager
        self._saa_helper = SAAHelper()
        self._taa_helper = TAAHelper(taa_params=taa_params, taa_param_details=taa_param_details) if taa_params or taa_param_details else None 
        self._fa_helper = FAHelper(fa_params=fa_params) if fa_params else None
        self._report_helper = ReportHelper()
        self._trader = trader
        self._is_old_version = is_old_version
        self._fund_score_funcs: Union[Dict[str, ScoreFunc], str] = fund_score_funcs
        if self._fund_score_funcs is not None:
            for index_id, func in self._fund_score_funcs.items():
                if isinstance(func, str):
                    print(f'check score func "{func}" for {index_id}')
                    FundScoreManager.test_func(func)
        self._pending_trades = []
        # 黑白名单和全部基金列表处理 得到不允许交易基金列表， 对其中基金评分惩罚
        self.white_list = white_list
        self.black_list = black_list
        self.whole_list = set(self._dm.dts.all_fund_list)
        disproved_set_1 = self.whole_list - self.white_list if self.white_list else set([]) 
        disproved_set_2 = self.black_list if self.black_list else set([])
        self.disproved_set = disproved_set_1.union(disproved_set_2)
        assert not self.is_fund_backtest or self._fa_helper, 'if this is a fund backtest, fa_helper is necessary'
        if self.is_fund_backtest:
            self._trader.set_helper(self._fa_helper)
        self.score_select = ScoreSelect().__dict__ if score_select is None else score_select.__dict__
        if fund_score_funcs is not None:
            for index_id in fund_score_funcs:
                self.score_select[index_id] = ScoreType.Temp

    def init(self):
        if not self._dm.inited:
            self._dm.init()
        self._saa_helper.init()
        if self._taa_helper:
            self._taa_helper.init()
        self._report_helper.init()
        self._trader.init()
        # preps
        self._prep_fund_purchase_fees = None
        self._prep_fund_redeem_fees = None
        self._prep_asset_price = None
        self._prep_fund_nav = None
        self._prep_fund_unit_nav = None
        self._prep_fund_score = None
        self._prep_fund_score_raw = None
        self._prep_target_asset_allocation = None
        self._prep_target_fund_allocation = None
        self._prep_manager_score = None
        self._prep_manager_funds = None
        self._prep_manager_score_cleaned = None

    def setup(self, saa: AssetWeight):
        # setup helpers
        self._saa_helper.setup(saa)
        if self._taa_helper:
            self._taa_helper.setup(saa)
        self._report_helper.setup(saa)
        self._trader.setup(saa)
        if self.is_fund_backtest:
            self._fa_helper.setup(saa)

    @property
    def is_fund_backtest(self):
        return isinstance(self._trader, FundTrader)

    def prep_data(self, dt):
        # basic
        if not self._prep_fund_purchase_fees:
            self._prep_fund_purchase_fees = self._dm.get_fund_purchase_fees()
        if not self._prep_fund_redeem_fees:
            self._prep_fund_redeem_fees = self._dm.get_fund_redeem_fees()
        # DATA
        self._prep_asset_price = self._dm.get_index_price_data(dt)
        self._prep_fund_nav = self._dm.get_fund_nav(dt) if self.is_fund_backtest else {}
        self._prep_fund_unit_nav = self._dm.get_fund_unit_nav(dt) if self.is_fund_backtest else {}
        self._prep_fund_score, self._prep_fund_score_raw = self._dm.get_fund_scores(dt=dt, fund_score_funcs=self._fund_score_funcs) if self.is_fund_backtest else ({}, {})
        self._prep_manager_score, self._prep_manager_funds, self._prep_manager_score_cleaned = self._dm.get_manager_scores(dt, self.score_select)
        self._prep_fund_score['active'] = self._prep_manager_score
        self._prep_fund_score_raw['active'] = self._prep_manager_score
        self._prep_fund_end_date_dict = self._dm.dts.fund_end_date_dict  
        if self.disproved_set:
            self._prep_fund_score, self._prep_fund_score_raw = self._dm.white_and_black_list_filter(self._prep_fund_score, self._prep_fund_score_raw, self.disproved_set)
        # ALLOCATION
        self._prep_target_asset_allocation = self.calc_asset_allocation(dt)
        self._prep_target_fund_allocation = self.calc_fund_allocation(dt) if self.is_fund_backtest else None
       
    def calc_trade(self, dt, cur_asset_position: AssetPosition, cur_fund_position: FundPosition=None, is_real_trade=False):
        if not self.is_fund_backtest:
            v_asset_position, asset_trade_list = self._trader.calc_asset_trade(dt, cur_asset_position, self._prep_asset_price, self._prep_target_asset_allocation)
            return asset_trade_list
        else:
            if self._is_old_version:
                v_asset_position, asset_trade_list = self._trader.calc_asset_trade(dt, cur_asset_position, self._prep_asset_price, self._prep_target_asset_allocation)
                expired_con = self._trader.has_expired_fund(cur_fund_position, self._prep_fund_score )
                if asset_trade_list or expired_con:
                    self._report_helper.update_rebalance_detail(dt, expired_con, {})
                    v_fund_position, fund_trade_list = self._trader.calc_fund_trade(
                        dt, self._prep_target_fund_allocation, cur_fund_position, self._prep_fund_nav, 
                        self._prep_fund_purchase_fees, self._prep_fund_redeem_fees
                    )
                    return fund_trade_list
                else:
                    return None
            assert cur_fund_position, 'cur_fund_position should not be None in fund backtest run'
            assert self._prep_target_fund_allocation, 'target fund allocation should be prepared already'
            v_fund_position, fund_trade_list, trigger_reason, trigger_detail = self._trader.calc_trade(
                dt, self._prep_target_fund_allocation, self._prep_target_asset_allocation,
                cur_fund_position, cur_asset_position, 
                self._prep_fund_nav, self._prep_fund_score, self._prep_asset_price,self._prep_fund_unit_nav, 
                is_real_trade, self._prep_manager_funds, self.score_select, self._prep_fund_end_date_dict
            )
            self._report_helper.update_rebalance_detail(dt, trigger_reason, trigger_detail)
            return fund_trade_list

    def finalize_trade(self, dt, trades: list, cur_asset_position: AssetPosition, cur_fund_position: FundPosition=None, disproved_set: set={}):
        if self.is_fund_backtest:
            assert cur_fund_position, 'cur_fund_position should not be None in fund backtest run'
            self._pending_trades, traded_list = self._trader.finalize_trade(dt, trades, self._prep_asset_price, cur_asset_position, cur_fund_position, self._prep_fund_nav, self._prep_fund_unit_nav,
                self._prep_fund_purchase_fees, self._prep_fund_redeem_fees, disproved_set, self._prep_target_fund_allocation)
        else:
            self._pending_trades, traded_list = self._trader.finalize_trade(dt, trades, self._prep_asset_price, cur_asset_position)
        return traded_list 

    def calc_asset_allocation(self, dt):
        cur_asset_price = self._dm.get_index_price_data(dt)
        cur_saa = self._saa_helper.on_price(dt, cur_asset_price)
        if self._taa_helper:
            asset_pct = self._dm.get_index_pcts_df(dt)
            cur_taa = self._taa_helper.on_price(dt, cur_asset_price, cur_saa, asset_pct, {}, self._prep_fund_score)
        else:
            cur_taa = cur_saa
        return cur_taa

    def calc_fund_allocation(self, dt):
        return self._fa_helper.on_price(dt, self._prep_target_asset_allocation, self._prep_fund_score, self._prep_manager_score_cleaned, self.score_select)

    def update_reporter(self, dt, trade_list, cur_asset_position: AssetPosition, cur_fund_position: FundPosition=None):
        self._report_helper.update(dt, cur_asset_position, self._prep_asset_price, self._pending_trades, cur_fund_position if self.is_fund_backtest else None, self._prep_fund_nav, trade_list, self._prep_fund_score, self._prep_fund_score_raw, self._prep_target_asset_allocation)

class FundBacktestEngine(FundEngine):

    def run(self, saa: AssetWeight, start_date: datetime.date=None, end_date: datetime.date=None, cash: float=None, print_time=False):
        # setup helpers
        self.setup(saa)

        cash = cash or self.DEFAULT_CASH_VALUE
        # init position
        self.cur_asset_position = AssetPosition(cash=cash)
        self.cur_fund_position = FundPosition(cash=cash) if self.is_fund_backtest else None

        self._pending_trades = []

        # init days
        start_date = start_date or self._dm.start_date
        end_date = end_date or self._dm.end_date
        start_date = start_date if isinstance(start_date, datetime.date) else datetime.datetime.strptime(start_date,'%Y%m%d').date()
        end_date = end_date if isinstance(end_date, datetime.date) else datetime.datetime.strptime(end_date,'%Y%m%d').date()

        # loop trading days
        _dts = self._dm.get_trading_days()
        dts = _dts[(_dts.datetime >= start_date) & (_dts.datetime <= end_date)].datetime # df with datetime.date
        for t in dts:
            self._run_on(t, print_time=print_time)
        # init report data
        self._report_helper.plot_init(self._dm, self._taa_helper, self.score_select)
        #print(self._report_helper.get_fund_stat())

    def _run_on(self, dt, print_time=False):
        _tm_start = time.time()
        # prep data
        self.prep_data(dt)
        _tm_prep_data = time.time()
        # finalize trade
        traded_list = self.finalize_trade(dt, self._pending_trades, self.cur_asset_position, self.cur_fund_position, self.disproved_set)
        _tm_finalize_trade = time.time()
        # calc trade
        trade_list = self.calc_trade(dt, self.cur_asset_position, self.cur_fund_position)
        _tm_calc_trade = time.time()
        # book trade
        self.book_trades(trade_list)
        # update
        self.update_reporter(dt, traded_list, self.cur_asset_position, self.cur_fund_position)        
        _tm_finish = time.time()
        if print_time:
            print(f'{dt} (tot){_tm_finish - _tm_start} (prep_data) {_tm_prep_data - _tm_start}  (finalize){_tm_finalize_trade - _tm_prep_data} (calc){_tm_calc_trade - _tm_finalize_trade} (misc){_tm_finish - _tm_calc_trade}')

    def book_trades(self, trade_list: list):
        if trade_list and len(trade_list) > 0:
            self._pending_trades += trade_list

    def get_asset_result(self):
        return self._report_helper.get_asset_stat()

    def get_fund_result(self):
        return self._report_helper.get_fund_stat()

    def get_asset_trade(self):
        return self._report_helper.get_asset_trade()

    def get_fund_trade(self):
        return self._report_helper.get_fund_trade()
        
    def plot(self, is_asset:bool=True, is_fund:bool=True):
        if is_asset:
            self._report_helper.backtest_asset_plot()
        if is_fund:
            self._report_helper.backtest_fund_plot()
    
    def plot_score(self, index_id, is_tuning=False):
        #['csi500', 'gem', 'gold', 'hs300', 'national_debt', 'sp500rmb']
        self._report_helper._plot_fund_score(index_id, is_tuning)

    def plot_taa(self, saa_mv, taa_mv, index_id):
        #['csi500', 'hs300', 'gem', 'sp500rmb']
        self._report_helper._plot_taa_saa(saa_mv, taa_mv, index_id)
        self._report_helper._index_pct_plot(index_id, saa_mv, taa_mv)

    def get_last_position(self,asset_target,result):
        return self._report_helper.get_last_position(asset_target,result,self._dm)

    def get_last_target_fund_allocation(self):
        return self._report_helper.get_last_target_fund_allocation(self._prep_target_fund_allocation.funds)

class BasicFundBacktestEngine(object):

    DEFAULT_CASH_VALUE = _DEFAULT_CASH_VALUE

    def __init__(self, data_manager:FundDataManager, trader, fund_weight_list:list):
        self._dm = data_manager
        fund_ids = []
        self.repair_trade_date(fund_weight_list)
        for dt, fund_weight in fund_weight_list:
            for fund_id, weight in fund_weight:
                fund_ids.append(fund_id)
        self._dm.confirm_fund_nav_exists(fund_ids)
        self._report_helper = ReportHelper()
        self._pending_trades = []
        self._trader = trader
        self._target_fund_weight = {}
        for dt, fund_weight in fund_weight_list:
            dt = dt if isinstance(dt, datetime.date) else datetime.datetime.strptime(dt,'%Y-%m-%d').date()
            self._target_fund_weight[dt] = fund_weight
        wind_index_map = {
            '货币市场型基金': 'mmf',
            '股票型基金': 'hs300',
            '混合型基金': 'csi500',     # TODO: 临时代替，需设置正确映射关系！！！
            '国际(QDII)基金': 'sp500rmb',
            '另类投资基金': 'gold',
            '债券型基金': 'national_debt',
            '其他基金': 'hsi'           # TODO: 临时代替，需设置正确映射关系！！！
        }
        self._fund_wind_class = {
            cur.fund_id: (wind_index_map[cur.wind_class_1] if cur.wind_class_1 in wind_index_map else 'hsi') for cur in self._dm.dts.fund_info.itertuples()
        }

    def repair_trade_date(self, fund_weight_list):
        _dts = self._dm.get_trading_days().datetime
        i = 0
        for dt in _dts:
            if i >= len(fund_weight_list):
                break
            cur_date = datetime.datetime.strptime(fund_weight_list[i][0], '%Y-%m-%d').date()
            if dt < cur_date:
                continue
            if dt == cur_date:
                i += 1
                continue
            if dt > cur_date:
                fund_weight_list[i][0] = datetime.date.strftime(dt, '%Y-%m-%d')
                i += 1

    def repair_dict_trade_date(self, trades):
        _dts = self._dm.get_trading_days().datetime
        i = 0
        for dt in _dts:
            if i >= len(trades):
                break
            cur_date = datetime.datetime.strptime(trades[i].get('trade_date'), '%Y-%m-%d').date()
            if dt < cur_date:
                continue
            if dt == cur_date:
                i += 1
                continue
            if dt > cur_date:
                trades[i]['trade_date'] = datetime.date.strftime(dt, '%Y-%m-%d')
                i += 1

    def init(self):
        if not self._dm.inited:
            self._dm.init()
        self._report_helper.init()
        self._trader.init()
        # preps
        self._prep_fund_purchase_fees = None
        self._prep_fund_redeem_fees = None
        self._prep_asset_price = None
        self._prep_fund_nav = None
        self._prep_fund_unit_nav = None

    def setup(self):
        # setup helpers
        self._report_helper.setup()
        self._trader.setup()

    def prep_data(self, dt):
        # basic
        if not self._prep_fund_purchase_fees:
            self._prep_fund_purchase_fees = self._dm.get_fund_purchase_fees()
        if not self._prep_fund_redeem_fees:
            self._prep_fund_redeem_fees = self._dm.get_fund_redeem_fees()
        # DATA
        self._prep_asset_price = self._dm.get_index_price_data(dt)
        self._prep_fund_nav = self._dm.get_fund_nav(dt)
        self._prep_fund_unit_nav = self._dm.get_fund_unit_nav(dt)

    def calc_trade(self, dt, cur_asset_position: AssetPosition, cur_fund_position: FundPosition=None, is_real_trade=False):
        # TODO: if is_real_trade, use nv instead of nav
        if dt not in self._target_fund_weight:
            return []

        curr_target_fund_weight = FundWeight()
        for fund_id, weight in self._target_fund_weight[dt]:
            index_id = self._fund_wind_class[fund_id]

            curr_target_fund_weight.add(FundWeightItem(fund_id=fund_id, fund_wgt=weight, 
                                                       index_id=index_id, asset_wgt=0, fund_wgt_in_asset=0))
        self._report_helper.update_rebalance_detail(dt, 'Change fund weight',{})
        v_fund_position, fund_trade_list = self._trader.calc_fund_trade(
            dt, curr_target_fund_weight, cur_fund_position, self._prep_fund_nav, 
            self._prep_fund_purchase_fees, self._prep_fund_redeem_fees)
        return fund_trade_list

    def finalize_trade(self, dt, trades: list, cur_asset_position: AssetPosition, cur_fund_position: FundPosition=None, disproved_set: set={}):
        assert cur_fund_position, 'cur_fund_position should not be None in fund backtest run'
        self._pending_trades, traded_list = self._trader.finalize_trade(dt, trades, 
            self._prep_asset_price, cur_asset_position, cur_fund_position, self._prep_fund_nav, self._prep_fund_unit_nav,
            self._prep_fund_purchase_fees, self._prep_fund_redeem_fees, disproved_set)
        return traded_list 

    def update_reporter(self, dt, trade_list, cur_asset_position: AssetPosition, cur_fund_position: FundPosition=None):
        self._report_helper.update(dt, cur_asset_position, self._prep_asset_price, self._pending_trades, 
            cur_fund_position, self._prep_fund_nav, trade_list, None, None, None)

    def run(self, start_date:datetime.date=None, end_date:datetime.date=None, cash:float=None, print_time=False):
        # setup helpers
        self.setup()

        cash = cash or self.DEFAULT_CASH_VALUE
        # init position
        self.cur_asset_position = AssetPosition(cash=cash) # TODO
        self.cur_fund_position = FundPosition(cash=cash)
        self._pending_trades = []

        # init days
        start_date = start_date or self._dm.start_date
        end_date = end_date or self._dm.end_date
        start_date = start_date if isinstance(start_date, datetime.date) else datetime.datetime.strptime(start_date,'%Y%m%d').date()
        end_date = end_date if isinstance(end_date, datetime.date) else datetime.datetime.strptime(end_date,'%Y%m%d').date()

        # loop trading days
        _dts = self._dm.get_trading_days()
        dts = _dts[(_dts.datetime >= start_date) & (_dts.datetime <= end_date)].datetime # df with datetime.date
        for t in dts:
            self._run_on(t, print_time=print_time)
        # init report data
        self._report_helper.plot_init(self._dm)

    def _run_on(self, dt, print_time=False):
        _tm_start = time.time()
        # prep data
        self.prep_data(dt)
        _tm_prep_data = time.time()
        # finalize trade
        traded_list = self.finalize_trade(dt, self._pending_trades, self.cur_asset_position, self.cur_fund_position)
        _tm_finalize_trade = time.time()
        # calc trade
        trade_list = self.calc_trade(dt, self.cur_asset_position, self.cur_fund_position)
        _tm_calc_trade = time.time()
        # book trade
        self.book_trades(trade_list)
        # update
        self.update_reporter(dt, traded_list, self.cur_asset_position, self.cur_fund_position)
        if self._pending_trades:
            print(self._pending_trades)
        _tm_finish = time.time()

        if print_time:
            print(f'{dt} (tot){_tm_finish - _tm_start} (finalize){_tm_finalize_trade - _tm_start} (calc){_tm_calc_trade - _tm_finalize_trade} (misc){_tm_finish - _tm_calc_trade}')

    def book_trades(self, trade_list: list):
        if trade_list and len(trade_list) > 0:
            self._pending_trades += trade_list

    def get_fund_result(self):
        return self._report_helper.get_fund_stat()

    def get_asset_trade(self):
        return self._report_helper.get_asset_trade()

    def get_fund_trade(self):
        return self._report_helper.get_fund_trade()
        
    def plot(self, is_asset:bool=True, is_fund:bool=True):
        if is_asset:
            self._report_helper.backtest_asset_plot()
        if is_fund:
            self._report_helper.backtest_fund_plot()
    
    def plot_score(self, index_id, is_tuning=False):
        #['csi500', 'gem', 'gold', 'hs300', 'national_debt', 'sp500rmb']
        self._report_helper._plot_fund_score(index_id, is_tuning)

    def plot_taa(self, saa_mv, taa_mv, index_id):
        #['csi500', 'hs300', 'gem', 'sp500rmb']
        self._report_helper._plot_taa_saa(saa_mv, taa_mv, index_id)
        self._report_helper._index_pct_plot(index_id, saa_mv, taa_mv)

    def get_last_position(self,asset_target,result):
        return self._report_helper.get_last_position(asset_target,result)

    def get_last_target_fund_allocation(self):
        return self._report_helper.get_last_target_fund_allocation(self._prep_target_fund_allocation.funds)


class AIPFundBackTestEngine(BasicFundBacktestEngine):

    DEFAULT_CASH_VALUE = _DEFAULT_CASH_VALUE

    def __init__(self, data_manager: FundDataManager, trader, fund_weight_list: list):
        self._dm = data_manager
        self.repair_trade_date(fund_weight_list)
        fund_ids = []
        for dt, cash, fund_weight in fund_weight_list:
            for fund_id, weight in fund_weight:
                fund_ids.append(fund_id)
        self._dm.confirm_fund_nav_exists(fund_ids)
        self._report_helper = ReportHelper()
        self._pending_trades = []
        self._trader = trader
        self._new_fund_weight = {}
        self._new_fund_cash = {}
        self.cur_fund_position = None
        self.cur_asset_position = AssetPosition(cash=1)
        self.deposits = []
        self.current_deposit = None

        for dt, cash, fund_weight in fund_weight_list:
            dt = dt if isinstance(dt, datetime.date) else datetime.datetime.strptime(dt, '%Y-%m-%d').date()
            self._new_fund_weight[dt] = fund_weight
            self._new_fund_cash[dt] = cash

        wind_index_map = {
            '货币市场型基金': 'mmf',
            '股票型基金': 'hs300',
            '混合型基金': 'csi500',     # TODO: 临时代替，需设置正确映射关系！！！ 抄袭上面
            '国际(QDII)基金': 'sp500rmb',
            '另类投资基金': 'gold',
            '债券型基金': 'national_debt',
            '其他基金': 'hsi'           # TODO: 临时代替，需设置正确映射关系！！！
        }
        self._fund_wind_class = {
            cur.fund_id: (wind_index_map[cur.wind_class_1] if cur.wind_class_1 in wind_index_map else 'hsi') for cur in self._dm.dts.fund_info.itertuples()
        }

    def run(self, start_date: datetime.date = None, end_date: datetime.date = None, cash: float = None, print_time=False):
        # setup helpers
        self.setup()

        # init days
        start_date = start_date or self._dm.start_date
        end_date = end_date or self._dm.end_date
        start_date = start_date if isinstance(start_date, datetime.date) else datetime.datetime.strptime(start_date,'%Y%m%d').date()
        end_date = end_date if isinstance(end_date, datetime.date) else datetime.datetime.strptime(end_date,'%Y%m%d').date()

        # loop trading days
        _dts = self._dm.get_trading_days()
        dts = _dts[(_dts.datetime >= start_date) & (_dts.datetime <= end_date)].datetime # df with datetime.date
        for t in dts:
            self._run_on(t, print_time=print_time)
        # init report data
        self._report_helper.plot_init(self._dm)

    def _run_on(self, dt, print_time=False, cash=None):
        _tm_start = time.time()
        # prep data
        self.prep_data(dt)
        _tm_prep_data = time.time()
        # finalize trade
        if self.cur_fund_position:
            traded_list = self.finalize_trade(dt, self._pending_trades, self.cur_asset_position, self.cur_fund_position)
        else:
            traded_list = []
        _tm_finalize_trade = time.time()
        # calc trade
        trade_list = self.calc_trade(dt, self.cur_asset_position, self.cur_fund_position)
        _tm_calc_trade = time.time()
        # book trade
        self.book_trades(trade_list)
        # update
        self.update_reporter(dt, traded_list, self.cur_asset_position, self.cur_fund_position)
        self.current_deposit = None
        if self._pending_trades:
            print(self._pending_trades)
        _tm_finish = time.time()

        if print_time:
            print(f'{dt} (tot){_tm_finish - _tm_start} (finalize){_tm_finalize_trade - _tm_start} (calc){_tm_calc_trade - _tm_finalize_trade} (misc){_tm_finish - _tm_calc_trade}')

    def calc_trade(self, dt, cur_asset_position: AssetPosition, cur_fund_position: FundPosition=None, is_real_trade=False):
        if dt not in self._new_fund_weight:
            return []

        curr_target_fund_weight = FundWeight()
        for fund_id, weight in self._new_fund_weight[dt]:
            index_id = self._fund_wind_class[fund_id]

            curr_target_fund_weight.add(FundWeightItem(fund_id=fund_id, fund_wgt=weight,
                                                       index_id=index_id, asset_wgt=0, fund_wgt_in_asset=0))

        cash = self._new_fund_cash[dt]
        new_fund_position = FundPosition(cash=cash)
        if not self.cur_fund_position:
            self.cur_fund_position = new_fund_position
        else:
            self.cur_fund_position.cash = self.cur_fund_position.cash + cash
        self.deposits.append(cash)
        self.current_deposit = cash

        self._report_helper.update_rebalance_detail(dt, 'Change fund weight', {})
        v_fund_position, fund_trade_list = self._trader.calc_fund_trade(
            dt, curr_target_fund_weight, new_fund_position, self._prep_fund_nav,
            self._prep_fund_purchase_fees, self._prep_fund_redeem_fees)
        return fund_trade_list

    def update_reporter(self, dt, trade_list, cur_asset_position: AssetPosition,
                        cur_fund_position: FundPosition = None, current_deposit = None):
        self._report_helper.update(dt, cur_asset_position, self._prep_asset_price, self._pending_trades,
                                   cur_fund_position, self._prep_fund_nav, trade_list, None, None, None,
                                   current_deposit=current_deposit)


class CashbookFundBackTestEngine(BasicFundBacktestEngine):

    DEFAULT_CASH_VALUE = _DEFAULT_CASH_VALUE

    def __init__(self, data_manager: FundDataManager, trader, init_position: list, trades_list: list):
        self._dm = data_manager

        # 修正 fund_weight_list
        if init_position:
            self.repair_trade_date(init_position)
            fund_ids = []
            for dt, fund_weight in init_position:
                for i in fund_weight:
                    fund_ids.append(i.get('fund_id'))
            self._dm.confirm_fund_nav_exists(fund_ids)

        if trades_list:
            self.repair_dict_trade_date(trades_list)
            fund_ids = []
            for i in trades_list:
                fund_ids.append(i.get('fund_id'))
            fund_ids = list(set(fund_ids))
            self._dm.confirm_fund_nav_exists(fund_ids)

        self._report_helper = ReportHelper()
        self._pending_trades = []
        self._trader = trader
        self._new_fund_position = {}
        self._new_fund_cash = {}
        self.cur_fund_position = None
        self.cur_asset_position = AssetPosition(cash=1)
        self.deposits = 0
        self.withdraws = 0

        self.current_deposit = 0
        self.current_withdraw = 0
        self._new_append_trades = {}

        for dt, fund_weight in init_position:
            dt = dt if isinstance(dt, datetime.date) else datetime.datetime.strptime(dt, '%Y-%m-%d').date()
            self._new_fund_position[dt] = fund_weight
            self._new_fund_cash[dt] = 0

        for i in trades_list:
            dt = i.get('trade_date')
            dt = dt if isinstance(dt, datetime.date) else datetime.datetime.strptime(dt, '%Y-%m-%d').date()
            if self._new_append_trades.get(dt):
                self._new_append_trades[dt].append(i)
            else:
                self._new_append_trades[dt] = [i]

        wind_index_map = {
            '货币市场型基金': 'mmf',
            '股票型基金': 'hs300',
            '混合型基金': 'csi500',     # TODO: 临时代替，需设置正确映射关系！！！ 抄袭上面
            '国际(QDII)基金': 'sp500rmb',
            '另类投资基金': 'gold',
            '债券型基金': 'national_debt',
            '其他基金': 'hsi'           # TODO: 临时代替，需设置正确映射关系！！！
        }
        self._fund_wind_class = {
            cur.fund_id: (wind_index_map[cur.wind_class_1] if cur.wind_class_1 in wind_index_map else 'hsi') for cur in self._dm.dts.fund_info.itertuples()
        }

    def run(self, start_date: datetime.date = None, end_date: datetime.date = None, cash: float = None, print_time=False):
        # setup helpers
        self.setup()

        # init days
        start_date = start_date or self._dm.start_date
        end_date = end_date or self._dm.end_date
        end_date = min(end_date, (datetime.datetime.now() - datetime.timedelta(days=1)).date())
        start_date = start_date if isinstance(start_date, datetime.date) else datetime.datetime.strptime(start_date,'%Y%m%d').date()
        end_date = end_date if isinstance(end_date, datetime.date) else datetime.datetime.strptime(end_date,'%Y%m%d').date()

        # loop trading days
        _dts = self._dm.get_trading_days()
        dts = _dts[(_dts.datetime >= start_date) & (_dts.datetime <= end_date)].datetime # df with datetime.date
        for t in dts:
            self._run_on(t, print_time=print_time)
        # init report data
        self._report_helper.plot_init(self._dm)

    def _run_on(self, dt, print_time=False, cash=None):
        _tm_start = time.time()
        # prep data
        self.prep_data(dt)
        _tm_prep_data = time.time()
        # calc trade
        trade_list = self.calc_trade(dt, self.cur_asset_position, self.cur_fund_position)
        _tm_calc_trade = time.time()
        # book trade
        self.book_trades(trade_list)

        # finalize trade
        if self.cur_fund_position:
            traded_list = self.finalize_trade(dt, self._pending_trades, self.cur_asset_position, self.cur_fund_position)
            self.cur_fund_position.cash = 0
        else:
            traded_list = []
        _tm_finalize_trade = time.time()

        # update
        self.update_cash(traded_list)
        self.update_reporter(dt, traded_list, self.cur_asset_position, self.cur_fund_position)
        self.current_withdraw = 0
        self.current_deposit = 0
        if self._pending_trades:
            print(self._pending_trades)
        _tm_finish = time.time()

        if print_time:
            print(f'{dt} (tot){_tm_finish - _tm_start} (finalize){_tm_finalize_trade - _tm_start} (calc){_tm_calc_trade - _tm_finalize_trade} (misc){_tm_finish - _tm_calc_trade}')

    def calc_trade(self, dt, cur_asset_position: AssetPosition, cur_fund_position: FundPosition=None, is_real_trade=False):

        trade_list = []
        if dt in self._new_fund_position:
            position_list = self._new_fund_position[dt]
            cur_cash = sum([i.get('amount') for i in position_list])
            self.cur_fund_position = FundPosition(cash=cur_cash)

            for i in position_list:
                fund_id = i['fund_id']
                _trade = FundTrade(
                    fund_id=fund_id,
                    index_id=self._fund_wind_class[fund_id],
                    mark_price=0,
                    amount=i['amount'],
                    is_buy=True,
                    submit_date=dt
                )
                trade_list.append(_trade)

        if dt in self._new_append_trades:
            if not self.cur_fund_position:
                self.cur_fund_position = FundPosition(cash=0)
            append_trades = self._new_append_trades[dt]

            for i in append_trades:
                trade_type = i.get('trade_type')
                fund_id = i['fund_id']

                if trade_type == 'buy':
                    _trade = FundTrade(
                        fund_id=fund_id,
                        index_id=self._fund_wind_class[fund_id],
                        mark_price=0,
                        amount=i['amount'],
                        is_buy=True,
                        submit_date=dt
                    )
                    self.cur_fund_position.cash = self.cur_fund_position.cash + i['amount']
                    trade_list.append(_trade)
                elif trade_type == 'sell':
                    if i.get('sell_rate'):
                        volume = self.cur_fund_position.funds.get(fund_id).volume * i['sell_rate']
                    else:
                        volume = i['volume']
                    _trade = FundTrade(
                        fund_id=fund_id,
                        index_id=self._fund_wind_class[fund_id],
                        mark_price=0,
                        volume=volume,
                        is_buy=False,
                        submit_date=dt
                    )
                    trade_list.append(_trade)
        return trade_list

    def update_cash(self, traded_list):
        for trd in traded_list:
            if trd.is_buy is True:
                self.current_deposit += trd.amount
                self.deposits += trd.amount
            else:
                self.current_withdraw += trd.amount
                self.withdraws += trd.amount
                self.cur_fund_position.cash = self.cur_asset_position.cash - trd.amount

    def update_reporter(self, dt, trade_list, cur_asset_position: AssetPosition,
                        cur_fund_position: FundPosition = None, current_deposit=None, current_withdraw=None):
        self._report_helper.update(dt, cur_asset_position, self._prep_asset_price, self._pending_trades,
                                   cur_fund_position, self._prep_fund_nav, trade_list, None, None, None,
                                   current_deposit=self.current_deposit, current_withdraw=self.current_withdraw,
                                   deposit=self.deposits, withdraw=self.withdraws,
                                   )

def saa_backtest(m: FundDataManager, saa: AssetWeight):
    asset_param = AssetTradeParam() # type in here
    t = AssetTrader(asset_param)
    b = FundBacktestEngine(data_manager=m, trader=t, taa_params=None)
    b.init()
    b.run(saa=saa)

def taa_backtest(m: FundDataManager, saa: AssetWeight):
    taa_param = TAAParam()  # type in here
    asset_param = AssetTradeParam() # type in here
    t = AssetTrader(asset_param)
    b = FundBacktestEngine(data_manager=m, trader=t, taa_params=taa_param)
    b.init()
    b.run(saa=saa)

def fund_backtest_without_taa(m: FundDataManager, saa: AssetWeight):
    asset_param = AssetTradeParam() # type in here
    fund_param = FundTradeParam() # type in here
    t = FundTrader(asset_param, fund_param)
    fa_param = FAParam() # type in here
    b = FundBacktestEngine(data_manager=m, trader=t, taa_params=None, fa_params=fa_param)
    b.init()
    b.run(saa=saa)

def fund_backtest(m: FundDataManager, saa: AssetWeight):
    asset_param = AssetTradeParam() # type in here
    fund_param = FundTradeParam(EnableCommission=True) # type in here
    t = FundTrader(asset_param, fund_param)
    taa_param = TAAParam()  # type in here
    fa_param = FAParam() # type in here
    b = FundBacktestEngine(data_manager=m, trader=t, taa_params=taa_param, fa_params=fa_param)
    b.init()
    b.run(saa=saa)

def fund_realtime(m: FundDataManager, saa: AssetWeight):
    asset_param = AssetTradeParam() # type in here
    fund_param = FundTradeParam() # type in here
    t = FundTrader(asset_param, fund_param)
    taa_param = TAAParam()  # type in here
    fa_param = FAParam() # type in here
    b = FundEngine(data_manager=m, trader=t, taa_params=taa_param, fa_params=fa_param)
    b.init()
    b.setup(saa)
    _dts = m.get_trading_days()
    dts = _dts[(_dts.datetime >= m.start_date) & (_dts.datetime <= m.end_date)].datetime
    calc_dt = dts.iloc[0]
    final_dt = dts.iloc[1]
    cash = b.DEFAULT_CASH_VALUE
    #real asset position and fund position
    cur_asset_position = AssetPosition(cash=cash)
    cur_fund_position = FundPosition(cash=cash)

    b.prep_data(calc_dt)
    #trade_list = b.calc_trade(calc_dt, cur_asset_position, cur_fund_position, True)
    trade_list = b.calc_trade(calc_dt, cur_asset_position, cur_fund_position)
    b.prep_data(final_dt)
    traded_list = b.finalize_trade(final_dt, trade_list, cur_asset_position, cur_fund_position)
    print(trade_list)
    print(traded_list)
    print(cur_fund_position)
    print(cur_asset_position)

def taa_result(m: FundDataManager):
    start_date=datetime.date(2010,1,1)
    end_date=datetime.date(2020,5,20)
    index_id = 'hs300'
    taaParam = TAAParam(HighThreshold = 1,
                        HighStop = 0.45,
                        HighMinus = 0.07,
                        LowStop = 0.43,
                        LowThreshold = 0.15,
                        LowPlus = 0.06) 
    return ReportHelper.get_taa_result(index_id=index_id, start_date=start_date, end_date=end_date, taaParam=taaParam, dm=m)

def four_dimensions_backtest(m,begin_date, end_date, saa, fund_param, taa_detail, score_select=None):
    asset_param = AssetTradeParam() 
    t = AssetTrader(asset_param)
    saa_bk = FundBacktestEngine(data_manager=m, trader=t, taa_params=None)
    saa_bk.init()
    saa_bk.run(saa=saa,start_date=begin_date,end_date=end_date)
    saa_mv = saa_bk.get_asset_result()['market_value']
    asset_param = AssetTradeParam() 
    t = AssetTrader(asset_param)
    taa_bk = FundBacktestEngine(data_manager=m, trader=t, taa_params=None,taa_param_details=taa_detail)
    taa_bk.init()
    taa_bk.run(saa=saa,start_date=begin_date,end_date=end_date)
    taa_mv = taa_bk.get_asset_result()['market_value']
    asset_param = AssetTradeParam() 
    
    t = FundTrader(asset_param, fund_param)
    fa_param = FAParam() 
    fund_taa = FundBacktestEngine(data_manager=m, trader=t, taa_params=None, fa_params=fa_param, taa_param_details=taa_detail, score_select=score_select)
    fund_taa.init()
    fund_taa.run(saa=saa,start_date=begin_date,end_date=end_date)
    fund_result = fund_taa.get_fund_result()
    fund_mv = fund_result['market_value']
    fund_annual_ret = fund_result['annual_ret']
    fund_mv = fund_mv.rename(columns={'mv':'优选基金'})
    taa_mv = taa_mv.rename(columns={'mv':'战术配置'})
    saa_mv = saa_mv.rename(columns={'mv':'战略配置'})
    mv_df = pd.concat([fund_mv,taa_mv, saa_mv], axis =1)
    mv_df = mv_df.join(m.dts.index_price[['hs300']].rename(columns={'hs300':'沪深300'}))
    res = []
    for port_name in mv_df:
        res_i = Calculator.get_stat_result_from_df(df=mv_df.reset_index(), date_column='date', value_column=port_name).__dict__
        res_i['策略名称'] = port_name
        res.append(res_i)
    stat_df = pd.DataFrame(res).set_index('策略名称').reindex(['沪深300','战略配置','战术配置','优选基金'])#[['annualized_ret','annualized_vol','sharpe','mdd','mdd_date1','mdd_date2']]
    stat_df['annualized_ret'] = stat_df['annualized_ret'].map(lambda x : CalculatorBase.stat_round_pct(x))
    stat_df['annualized_vol'] = stat_df['annualized_vol'].map(lambda x : CalculatorBase.stat_round_pct(x))
    stat_df['worst_3m_ret'] = stat_df['worst_3m_ret'].map(lambda x : CalculatorBase.stat_round_pct(x))
    stat_df['worst_6m_ret'] = stat_df['worst_6m_ret'].map(lambda x : CalculatorBase.stat_round_pct(x))
    stat_df['mdd'] = stat_df['mdd'].map(lambda x : CalculatorBase.stat_round_pct(x))
    stat_df['sharpe'] = stat_df['sharpe'].map(lambda x : round(x,3))
    stat_df['ret_over_mdd'] = stat_df['ret_over_mdd'].map(lambda x : round(x,3))
    stat_df[['start_date', 'end_date','annualized_ret', 'annualized_vol', 'sharpe','mdd','mdd_date1','mdd_date2','worst_3m_ret','worst_6m_ret','ret_over_mdd']].rename(columns={'ret_over_mdd':'calmar'})    
    return mv_df, stat_df, fund_annual_ret

def licaimofang_backtest(m: FundDataManager, saa:AssetWeight):
    json_path = '../../surfing/rpm/etc/licaimofang_white_list.json'
    with open(json_path,'r') as f:
        white_list = set(json.load(f))
    black_list = set(['000356!0','004870!0','008593!0','007404!0','003547!0'])  #基金代码在理财魔方白名单， 对方客服回复不能交易但基金代码

    taa_detail_item_mmf = TAAParam(HighThreshold = 0.95,
                                HighStop = 0.5,
                                HighMinus = 0.05,
                                LowStop = -1,
                                LowThreshold = -1,
                                LowPlus = 0,
                                ToMmf=True)

    taa_detail= {
        'hs300': taa_detail_item_mmf,
        'csi500': taa_detail_item_mmf,
        'gem': taa_detail_item_mmf,
        'sp500rmb': taa_detail_item_mmf,
    }
    asset_param = AssetTradeParam()

    fund_param = FundTradeParam(JudgeIndexDiff=0.06, #大类资产偏离度
                                JudgeFundSelection=0.4, # 基金排名偏离度
                                JudgeFundRebalance=0.8, # 基金比例平均化
                        )

    fa_param = FAParam(MaxFundNumUnderAsset=4 # 同一个大类资产下基金最多数
                    )
    taa_default = TAAParam()
    saa = AssetWeight(hs300=0.14,csi500=0.25,gem=0.20,sp500rmb=0.1,national_debt=0.3,cash=1/100)


    t = FundTrader(asset_param, fund_param)
    end_date = datetime.date.today()
    #end_date = datetime.date(2020,7,8)
    begin_date = datetime.date(2012,1,1)
    bk = FundBacktestEngine(data_manager=m, trader=t, taa_params=taa_default, fa_params=fa_param, taa_param_details=taa_detail,white_list=white_list,black_list=black_list)
    bk.init()
    bk.run(saa=saa, start_date=begin_date, end_date=end_date)
    bk_result = bk.get_fund_result()
    return bk_result

def qieman_backtest(m: FundDataManager, saa:AssetWeight):
    black_list_json = '../../surfing/rpm/etc/qieman_black_list.json'
    white_list_json = '../../surfing/rpm/etc/qieman_white_list.json'
    with open(white_list_json,'r') as f:
        white_list = set(json.load(f))        
    with open(black_list_json,'r') as f:
        black_list = set(json.load(f))
    taa_detail_item_mmf = TAAParam(HighThreshold = 0.95,
                                HighStop = 0.5,
                                HighMinus = 0.05,
                                LowStop = -1,
                                LowThreshold = -1,
                                LowPlus = 0,
                                ToMmf=True)

    taa_detail= {
        'hs300': taa_detail_item_mmf,
        'csi500': taa_detail_item_mmf,
        'gem': taa_detail_item_mmf,
        'sp500rmb': taa_detail_item_mmf,
    }
    asset_param = AssetTradeParam()

    fund_param = FundTradeParam(JudgeIndexDiff=0.06, #大类资产偏离度
                                JudgeFundSelection=0.4, # 基金排名偏离度
                                JudgeFundRebalance=0.8, # 基金比例平均化
                        )

    fa_param = FAParam(MaxFundNumUnderAsset=4 # 同一个大类资产下基金最多数
                    )
    taa_default = TAAParam()
    saa = AssetWeight(hs300=0.14,csi500=0.25,gem=0.20,sp500rmb=0.1,national_debt=0.3,cash=1/100)

    t = FundTrader(asset_param, fund_param)
    end_date = datetime.date.today()
    begin_date = datetime.date(2012,1,1)
    bk = FundBacktestEngine(data_manager=m, trader=t, taa_params=taa_default, fa_params=fa_param, taa_param_details=taa_detail,white_list=white_list,black_list=black_list)
    bk.init()
    bk.run(saa=saa, start_date=begin_date, end_date=end_date)
    bk_result = bk.get_fund_result()
    return bk_result

def change_score_function(m: FundDataManager, saa: AssetWeight):
    t = FundTrader(AssetTradeParam(), FundTradeParam())
    taa_param = TAAParam()
    fa_param = FAParam()
    funcs = {
        'hs300': ScoreFunc(alpha=0, beta=-1, fee_rate=0),
        'csi500': ScoreFunc(alpha=0, beta=-1)
    }
    bk = FundBacktestEngine(data_manager=m, trader=t, taa_params=taa_param, fa_params=fa_param, fund_score_funcs=funcs)
    bk.init()
    bk.run(saa=saa)
    bk_result = bk.get_fund_result()
    return bk_result

def change_formula_score_function(m: FundDataManager, saa: AssetWeight):
    t = FundTrader(AssetTradeParam(), FundTradeParam())
    taa_param = TAAParam()
    fa_param = FAParam()
    func_str = '0.5 * alpha + 0.1 * abs(1 - beta)'
    bk = FundBacktestEngine(data_manager=m, trader=t, taa_params=taa_param, fa_params=fa_param, fund_score_funcs={'hs300': func_str})
    bk.init()
    bk.run(saa=saa)
    bk_result = bk.get_fund_result()
    return bk_result

def test():
    from ...data.manager.score import FundScoreManager
    m = FundDataManager('20150101', '20160101', score_manager=FundScoreManager())
    m.init()

    saa = AssetWeight(
        hs300=15/100,
        csi500=5/100,
        gem=3/100,
        sp500rmb=7/100,
        national_debt=60/100,
        gold=10/100,
        cash=5/100
    )
    
    # saa_backtest(m, saa)
    # taa_backtest(m, saa)
    # fund_backtest_without_taa(m, saa)
    fund_backtest(m, saa)
    # fund_realtime(m, saa)
    # change_score_function(m, saa)
    # change_formula_score_function(m, saa)


params_str = '''
{
    "back_test_type": "basic",
    "fund_weight_list": [
        [
            "2020-01-06",
            [
                [
                    "007404!0",
                    0.1
                ],
                [
                    "008779!0",
                    0.3
                ],
                [
                    "004603!0",
                    0.6
                ]
            ]
        ],
        [
            "2020-02-06",
            [
                [
                    "004603!0",
                    0.3
                ],
                [
                    "000914!0",
                    0.3
                ],
                [
                    "005480!0",
                    0.2
                ],
                [
                    "007404!0",
                    0.2
                ]
            ]
        ],
        [
            "2020-06-01",
            [
                [
                    "511880!0",
                    0.1
                ],
                [
                    "000356!0",
                    0.9
                ]
            ]
        ]
    ],
    "start_date": "2020-01-01",
    "end_date": "2020-08-19"
}
'''

untagged_params_str = '''
{
    "back_test_type": "basic",
    "fund_weight_list": [
        [
            "2020-01-06",
            [
                [
                    "000001!0",
                    0.1
                ],
                [
                    "000003!0",
                    0.3
                ],
                [
                    "004603!0",
                    0.6
                ]
            ]
        ],
        [
            "2020-02-06",
            [
                [
                    "004603!0",
                    0.3
                ],
                [
                    "000914!0",
                    0.3
                ],
                [
                    "005480!0",
                    0.2
                ],
                [
                    "007404!0",
                    0.2
                ]
            ]
        ],
        [
            "2020-06-01",
            [
                [
                    "511880!0",
                    0.1
                ],
                [
                    "000356!0",
                    0.9
                ]
            ]
        ]
    ],
    "start_date": "2020-01-01",
    "end_date": "2020-08-19"
}
'''

params_str_1 = '''
{
    "back_test_type": "basic",
    "fund_weight_list": [
        [
            "2020-08-05",
            1000,
            [
                [
                    "000001!0",
                    1
                ]
            ]
        ]
    ],
    "start_date": "2020-08-05",
    "end_date": "2020-08-25"
}
'''

def test1():
    import json
    import pickle
    with open('/Users/puyuantech/Downloads/robo-advisor/temp/data_manager', 'rb') as fp:
        data_manager = pickle.load(fp)

    t = BasicFundTrader()

    params = json.loads(params_str_1)
    fund_weight_list = params['fund_weight_list']

    start_date = params.get('start_date')
    end_date = params.get('end_date')
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    b = AIPFundBackTestEngine(data_manager=data_manager, trader=t, fund_weight_list=fund_weight_list)
    b.init()
    # print(b._dm.dts.fund_index_map)
    b.run(start_date=start_date, end_date=end_date, print_time=True)
    print(b.get_fund_result())
    print(b._report_helper.get_mdd_stats())

if __name__ == '__main__':
    # profile(file_name='/Users/cjiang/taa_perf1.txt', func=fund_backtest)
    test1()
