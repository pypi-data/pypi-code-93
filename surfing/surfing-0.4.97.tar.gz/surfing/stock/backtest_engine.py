import datetime
import copy
import json
import numpy as np
import pandas as pd
import os
from .order_manager import OrderManager
from .backtest_report import BacktestReport
from ..aws_util import backtest_result_to_dynamodb
from ..data.manager_stock import StockDataManager
from ..match_engine import MatchEngine
from ..structure import AssetType, PositionInfo, BacktestKey
from ..data.manager_stock import StockDailyWrapper
from ..constant import Direction

class BacktestEngine:

    def __init__(self,data_manager=None,data_path=None,start_time=None,end_time=None,universe=None,datatype=None,asset_types=None,stock_pool=None,price_type=None,strategy_type=None,factor_path=None,factor_name=None,vwap_limit=None):
        self._strategies = {}
        self._universe = universe
        self._to_stop = False
        self._current_dt = start_time if isinstance(start_time, datetime.datetime) else datetime.datetime.strptime(start_time,'%Y%m%d')
        self.strategy_type = strategy_type
        
        self._order_manager = OrderManager(self, strategy_type)
        self._match_engine = MatchEngine(self, strategy_type)
        self._asset_types = {}
        self.stock_pool = stock_pool
        if datatype != StockDailyWrapper:
            print(start_time, end_time, universe)
            for ticker in self._universe:
                if isinstance(asset_types, dict):
                    self._asset_types[ticker] = asset_types.get(ticker)
                elif isinstance(asset_types, int):
                    self._asset_types[ticker] = asset_types
                elif asset_types is None:
                    self._asset_types[ticker] = AssetType.STOCK
        else:
            self._all_asset_types = AssetType.STOCK

        self._data_manager = data_manager if data_manager else StockDataManager(data_path    = data_path, 
                                                                                start_time   = start_time, 
                                                                                end_time     = end_time, 
                                                                                universe     = universe,
                                                                                datatype     = datatype,
                                                                                stock_pool   = stock_pool,
                                                                                price_type   = price_type,
                                                                                factor_path  = factor_path,
                                                                                factor_name  = factor_name,
                                                                                vwap_limit   = vwap_limit)

    def _add_strategy(self, strategy, position_info=None):
        strategy.set_context(self)
        self._strategies[strategy._name] = strategy
        self._order_manager.add_strategy(strategy._name, position_info)

    def _init(self):
        self._data_manager.init()
        self._order_manager.init()
        self._match_engine.init()
        for st in self._strategies.values():
            st.init()

    def _terminate(self):
        self._data_manager.terminate()
        self._order_manager.terminate()
        self._match_engine.terminate()

    def _run_daily(self):
        day_data = self._data_manager.get_next_day()
        while day_data is not None:
            self._set_dt(day_data['time'])
            self._match_engine.on_day(day_data)
            self._order_manager.on_day(day_data)
            for st in self._strategies.values():
                st.on_day(day_data)
                # include build order with id, match price, and trade 
                # slippage calculated during match, trade fee calculated in structure.process_trade 
                self._order_manager.process_orders_daily(st.order_list) 

            self._switch_day()                
            day_data = self._data_manager.get_next_day()
                
    def _run_next_tick(self):
        tk = self._data_manager.get_next_tick()
        while tk is not None:
            self._set_dt(self._data_manager.current_index.to_pydatetime())
            self._match_engine.on_tick(tk)
            self._order_manager.on_tick(tk)
            for st in self._strategies.values():
                st.on_tick(tk)
            self._order_manager.process_orders()
            self._order_manager.process_transfers()
            tk = self._data_manager.get_next_tick()

    def _run(self):
        df = self._data_manager.get_data()
        for index, row in df.iterrows():
            if self._to_stop:
                self._terminate()
                return
            cur_dt = pd.to_datetime(index, format='%Y-%m-%dT%H:%M:%S.%fZ')
            self._set_dt(cur_dt)
            tk = self._data_manager.parse_row(index, row)
            self._match_engine.on_tick(tk)
            self._order_manager.on_tick(tk)
            for st in self._strategies.values():
                st.on_tick(tk)
            self._order_manager.process_orders()
            self._order_manager.process_transfers()

    def print_result(self, st_name=None):
        if st_name is None:
            for nm in self._strategies.keys():
                self._order_manager.print_result(nm)
        else:
            self._order_manager.print_result(st_name)      

    def _set_dt(self, dt):
        if self.strategy_type != 'stock_daily':
            if self._current_dt is None or self._current_dt.day != dt.day:
                self._switch_day()
        self._current_dt = dt
    
    def _switch_day(self):
        self._order_manager.switch_day()
        self._match_engine.switch_day()
        for st in self._strategies.values():
            st.switch_day()

    # field member may use
    def _push_trade(self, trade):
        ## called by match_engine
        self._order_manager.process_trade(trade)
        self._strategies[trade.source].on_trade(trade)

    def _push_order_status(self, order):
        self._strategies[order.source].on_order(order.order_id, order.status)
        
    def _push_transfer(self, transfer):
        self._strategies[transfer.source].on_transfer(transfer)

    # utility functions that strategy may use
    def now(self):
        return self._current_dt

    def insert_order(self, order):
        od = copy.deepcopy(order)
        self._order_manager.check_order(od)
        order.order_id = od.order_id
        return None if od.err_msg else od.order_id

    def insert_order_daily(self, order_list):
        self._order_manager.process_orders_daily(order_list)

    def insert_transfer(self, transfer):
        tr = copy.deepcopy(transfer)
        self._order_manager.check_transfer(tr)
        transfer.transfer_id = tr.transfer_id
        return None if tr.err_msg else tr.transfer_id

    def cancel_order(self, order_id):
        res = self._order_manager.cancel_order(order_id)
        return res is True

    def get_position(self, name):
        return self._order_manager.get_position(name)

    def get_trade(self, name):
        return self._order_manager.get_trade(name)

    def get_market_value(self, name):
        return self._order_manager.get_market_value(name)

    def stop(self):
        self._to_stop = True
    
    def save_backtest_result(self):
        self.backtest_result = {}
        for st in self._strategies.values():
            self.backtest_result[st._name] = {}
            trade_data = [[ti.trade_id, ti.ticker, Direction.read(ti.direction), ti.trade_price, ti.trade_volume, ti.time] for ti in self.get_trade(st._name) ]
            self.backtest_result[st._name]['trade'] = {  
                'columns'   :['trade_id','ticker','direction','trade_price','trade_volume','trade_time'],
                'data'      :trade_data,
            }
            self.backtest_result[st._name]['cash'] ={
                'columns'   : ['date', 'cash'],
                'data'      : [[d, int(c)] for d, c in self._order_manager.cash_list[st._name]],
            }
            self.backtest_result[st._name]['pos'] = self._order_manager.pos[st._name]
            self.backtest_result[st._name]['mv'] ={
                'columns'   : ['date', 'mv'],
                'data'      : [[d, int(c)] for d, c in self._order_manager.mvs[st._name]],
            }
            self.backtest_result[st._name]['report'] = BacktestReport( 
                                                            backtest_result = self.backtest_result[st._name],
                                                            period          = self._strategies[st._name].period,
                                                            date_list       = self._data_manager.wrapper.date_list,
                                                            price_data      = self._data_manager.wrapper.price_data,
                                                            factor_data     = self._data_manager.wrapper.factor_data,
                                                            stock_pool_data = self._data_manager.wrapper.stock_pool_data,
                                                            stock_info      = self._data_manager.wrapper.stock_info,
                                                            base_path       = self._data_manager.wrapper.base_path,
                                                            common_pool     = self._data_manager.wrapper.common_pool,
                                                            pool            = self.stock_pool
            ).analysis_backtest_result()

            self.backtest_id = BacktestKey(
                strategy_name   =   st._name,
                factor          =   st.factor_name,
                pool            =   self.stock_pool,
                longshort       =   st.longshort[2],
                top             =   st.top,
                period          =   self._strategies[st._name].period,
                buy_price       =   self._data_manager.wrapper.price_type,
                sell_price      =   self._data_manager.wrapper.price_type,
                fee             =   self.backtest_result[st._name]['report']['total_trade_fee'],
                start           =   self._data_manager.start_time.strftime('%Y-%m_%d'),
                end             =   self._data_manager.end_time.strftime('%Y-%m_%d'),
                vwap_limit      =   self._data_manager.wrapper.vwap_limit,
            ).key()

            self.backtest_result[st._name]['report']['pool']        = self.stock_pool
            self.backtest_result[st._name]['report']['factor_name'] = st.factor_name
            self.backtest_result[st._name]['report']['longshort']   = st.longshort[2]
            self.backtest_result[st._name]['report']['top']         = st.top
            self.backtest_result[st._name]['report']['buy_price']   = self._data_manager.wrapper.price_type
            self.backtest_result[st._name]['report']['sell_price']  = self._data_manager.wrapper.price_type
            self.backtest_result[st._name]['report']['vwap_limit']  = self._data_manager.wrapper.vwap_limit
            self.backtest_result[st._name]['report']['strategy_name'] = st._name
            self.backtest_result[st._name]['report']['backtest_id'] = self.backtest_id

            self.log_path = './backtest_log'
            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)

            with open(f'{self.log_path}/{st._name}.json','w') as f:
                f.write(json.dumps(self.backtest_result))

            backtest_result_to_dynamodb(self.backtest_result[st._name]['report'])

        
  
