#!/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function
from builtins import (bytes, str, super, range, zip, round, pow, object)

from ._time import EtaTime
from .utils import *

class StrategyPositionContext(object):
    __slots__ = '__positions'

    def __init__(self, positions):
        self.__positions = positions

    @property
    def long(self):
        side = 'long'

        if len(self.__positions) == 0:
            empty_position = SymbolPosition()
            empty_position.positionSide = side
            return empty_position
        elif len(self.__positions) == 1:
            empty_position = SymbolPosition()
            empty_position.positionSide = side
            return empty_position if self.__positions[0].positionSide != side else self.__positions[0]
        else:
            return self.__positions[0]

    @property
    def short(self):
        side = 'short'

        if len(self.__positions) == 0:
            empty_position = SymbolPosition()
            empty_position.positionSide = side
            return empty_position
        elif len(self.__positions) == 1:
            empty_position = SymbolPosition()
            empty_position.positionSide = side
            return empty_position if self.__positions[0].positionSide != side else self.__positions[0]
        else:
            return self.__positions[1]

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.__positions[item]

    def __bool__(self):
        return len(self.__positions) != 0

    def __iter__(self):
        return self.__positions.__iter__()

    def __next__(self):
        return self.__positions.__next__()

    def __repr__(self):
        return self.__positions.__repr__()


class StrategyPositionsContext(object):
    __slots__ = '__api'

    def __init__(self, api):
        self.__api = api

    def __bool__(self):
        return len(self.__api.getPositionSymbols()) != 0

    def __getitem__(self, item):
        if type(item) == int:
            return self.__api.getSymbolPositions()[item]
        elif item in self.__api.getPositionSymbols():
            return StrategyPositionContext([x for x in self.__api.getSymbolPositions() if item == x.symbol])
        else:
            return StrategyPositionContext([])

    @property
    def long(self):
        return StrategyPositionContext([x for x in self.__api.getSymbolPositions() if x.positionSide ==
            'long'])

    @property
    def short(self):
        return StrategyPositionContext([x for x in self.__api.getSymbolPositions() if x.positionSide ==
            'short'])

    def __repr__(self):
        return self.__api.getSymbolPositions().__repr__()


class StrategyContext(object):
    __slots__ = ['__api', 'positions']

    def __init__(self, api):
        self.__api = api
        self.positions = StrategyPositionsContext(api)

    def __getitem__(self, item):
        return StrategyContext(Context.get_api(item))

    def __getattribute__(self, item):
        if item in {'id', 'dailyPnL', 'urPnL', 'overallPnL', 'totalCommission'}:
            return self.__api.getStrategyPnL().__getattribute__(item)
        else:
            return object.__getattribute__(self, item)

    def __repr__(self):
        return self.__api.getStrategyPnL().__str__()


class AccountPositionContext(object):
    __slots__ = '__api'

    def __init__(self, api):
        self.__api = api

    def __getitem__(self, item):
        return self.__api.getOverallPosition(item)

    def __repr__(self):
        return self.__api.getOverallPositions().__repr__()
    
    def __len__(self):
        return len(self.__api.getOverallPosition())


class PoolContext(object):
    __slots__ = '__api'
    
    def __init__(self, api):
        self.__api = api

    @property
    def all(self):
        return self.__api.getSymbolPool()

    @property
    def focus(self):
        return self.__api.getFocusAndPositionSymbols()

    @focus.setter
    def focus(self, value):
        if not isinstance(value, list) and not isinstance(value, set) and not isinstance(value, str):
            raise Exception('invalid focus symbols type, need list or set or str type')

        self.__api.setFocusSymbols(value)

    @property
    def position(self):
        return self.__api.getPositionSymbols()

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)


class PreparedBarContext(object):
    __slots__ = ['__api', 'bars']

    def __init__(self, api):
        self.__api = api
        self.bars = []

    def append(self, bar):
        self.__api.setRequireBars(bar['interval'], bar['count'])
        self.bars.append(bar)

    def __setitem__(self, key, value):
        if not hasattr(self.__api, 'init_time') or not self.__api.init_time:
            raise StrategyException('can\'t setup init param at this time! just set in on_initialize.')

        etaapi.setRequireBarsCpp(key, value)

    def set_bars(self, bars):
        for bar in bars:
            etaapi.setRequireBarsCpp(bar['interval'], bar['count'])
        self.bars = bars

    def __iter__(self):
        return self.bars.__iter__()

    def __next__(self):
        return self.bars.__next__()

    def __repr__(self):
        return self.bars.__repr__()


class CashContext(object):
    __slots__ = ['__api', '__market']

    def __init__(self, api):
        self.__api = api
        self.__market = ['CS', 'CF', 'SJ', 'HK']

    def __setitem__(self, key, value):
        if not hasattr(self.__api, 'init_time') or not self.__api.init_time:
            raise StrategyException('can\'t setup init param at this time! just set in on_initialize.')

        if key in self.__market:
            init_param.setBTCash(key, value)

    def __getitem__(self, item):
        if item in self.__market:
            return init_param.getBTCash(item)

    def setup(self, value):
        for market in value:
            if market in self.__market:
                init_param.setBTCash(market, value[market])
            else:
                raise Exception('unknown cash market! market: ' + market)

    def __repr__(self):
        all_cashs = {}
        for market in ['CS', 'CF', 'SJ', 'HK']:
            all_cashs[market] = init_param.getBTCash(market)

        return 'cash({})'.format(all_cashs)


class BackTestContext(object):
    def __init__(self, api):
        self.__api = api
        self.__cash = CashContext(api)

    def setup(self, value):
        keys = ['start_date', 'end_date', 'slippage', 'cash']
        for key in keys:
            if key in value:
                self.__setattr__(key, value[key])

    @property
    def start_date(self):
        return init_param.getBTStartDate()

    @start_date.setter
    def start_date(self, value):
        init_param.setBTStartDate(value)

    @property
    def end_date(self):
        return init_param.getBTEndDate()

    @end_date.setter
    def end_date(self, value):
        init_param.setBTEndDate(value)

    @property
    def slippage(self):
        return init_param.getBTSlippage()

    @slippage.setter
    def slippage(self, value):
        init_param.setBTSlippage(value)

    @property
    def cash(self):
        return self.__cash

    @cash.setter
    def cash(self, value):
        self.__cash.setup(value)

    def __setattr__(self, key, value):
        if '_BackTestContext__' in key:
            object.__setattr__(self, key, value)
            return

        if not hasattr(self.__api, 'init_time') or not self.__api.init_time:
            raise StrategyException('can\'t setup init param at this time! just set in on_initialize.')

        object.__setattr__(self, key, value)

    def __repr__(self):
        return 'backtest(start_date={}, end_date={}, slippage={}, cash={})'.format(self.start_date, self.end_date,
                                                                                   self.slippage, self.cash)


class RealTimeContext(object):
    __slots__ = ('__api', '__timeout', '__mode', '__timer_cycle')

    def __init__(self, api):
        self.__api = api
        self.__timeout = 5000
        self.__mode = 'single_only'
        self.__timer_cycle = 0

    def setup(self, value):
        keys = ['group_timeout', 'timer_cycle', 'pre_market_time', 'closing_time', ]
        for key in keys:
            if key in value:
                self.__setattr__(key, value[key])

    @property
    def timer_cycle(self):
        return self.__timer_cycle

    @timer_cycle.setter
    def timer_cycle(self, value):
        self.__timer_cycle = value
        self.__api.setTimerCycle(self.__timer_cycle)

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = value
        if value == 'group_only':
            self.__api.setGroupMode(timeOutMs=self.__timeout, onlyGroup=True)
        elif value == 'single_only':
            self.__api.setGroupMode(timeOutMs=self.__timeout, group_mode=False)
        elif value == 'both':
            self.__api.setGroupMode(timeOutMs=self.__timeout, onlyGroup=False)

    @property
    def group_timeout(self):
        return self.__timeout

    @group_timeout.setter
    def group_timeout(self, value):
        self.__timeout = value
        if self.__mode == 'group_only':
            self.__api.setGroupMode(timeOutMs=self.__timeout, onlyGroup=True)
        elif self.__mode == 'both':
            self.__api.setGroupMode(timeOutMs=self.__timeout, onlyGroup=False)

    @property
    def pre_market_time(self):
        return init_param.getPreMarketTime()

    @pre_market_time.setter
    def pre_market_time(self, value):
        init_param.setPreMarketTime(value)

    @property
    def closing_time(self):
        return init_param.getClosingTime()

    @closing_time.setter
    def closing_time(self, value):
        init_param.setClosingTime(value)

    def __setattr__(self, key, value):
        if '_RealTimeContext__' in key:
            object.__setattr__(self, key, value)
            return

        if not hasattr(self.__api, 'init_time') or not self.__api.init_time:
            raise StrategyException('can\'t setup init param at this time! just set in on_initialize.')

        object.__setattr__(self, key, value)

    def __repr__(self):
        return 'realtime(pre_market_time={}, closing_time={}, group_timeout={}, cash={})'.format(self.pre_market_time,
                                                                                                 self.closing_time,
                                                                                                 self.group_timeout,
                                                                                                 self.timer_cycle)


class MatchParamContext(object):
    def __init__(self, api):
        self.__api = api
        init_param.setMatchTimeRanges([])

    def upload_interval(self, value):
        self.__setattr__('interval', value)

    def set_time_ranges(self, value):
        self.__setattr__('time_ranges', value)

    @property
    def interval(self):
        return init_param.getMatchInterval()

    @interval.setter
    def interval(self, value):
        init_param.setMatchInterval(value)

    @property
    def time_ranges(self):
        return init_param.getMatchTimeRanges()

    @time_ranges.setter
    def time_ranges(self, value):
        if value is None:
            init_param.setMatchTimeRanges([])
        elif isinstance(value, list) or isinstance(value, set) or isinstance(value, tuple):
            init_param.setMatchTimeRanges(list(value))
        else:
            raise Exception('unknown time_ranges param!! None, list, set, tuple possible')

    @property
    def period(self):
        return init_param.getMatchPeriod()

    @period.setter
    def period(self, value):
        if isinstance(value, list) and len(value) == 2:
            value = (value[0], value[1])
        init_param.setMatchPeriod(value)

    def __setattr__(self, key, value):
        if '_MatchParamContext__' in key:
            object.__setattr__(self, key, value)
            return

        if not hasattr(self.__api, 'init_time') or not self.__api.init_time:
            raise StrategyException('can\'t setup init param at this time! just set in on_initialize.')

        object.__setattr__(self, key, value)

    def setup(self, value):
        keys = ['interval', 'time_ranges', 'period']
        for key in keys:
            if key in value:
                self.__setattr__(key, value[key])

    def __repr__(self):
        return 'match_param(interval={}, time_ranges={})'.format(self.interval,
                                                                 ['begin={} -> end={}'.format(tr[0], tr[1]) for tr in
                                                                  self.time_ranges])


class AlgoContext(object):
    def __init__(self, api):
        self.__api = api
        self.__param = AlgoParam()

    def __setattr__(self, key, value):
        if '_AlgoContext__' in key:
            object.__setattr__(self, key, value)
            return

        if not hasattr(self.__api, 'init_time') or not self.__api.init_time:
            raise StrategyException('can\'t setup init param at this time! just set in on_initialize.')

        object.__setattr__(self, key, value)

    @property
    def mode(self):
        return 'vwap' if self.__param.on else 'none'

    @mode.setter
    def mode(self, value):
        if value == 'vwap':
            self.__param.on = True
            init_param.setAlgrParam(self.__param)

    @property
    def avg_count(self):
        return self.__param.avg_count

    @avg_count.setter
    def avg_count(self, value):
        self.__param.avg_count = value
        init_param.setAlgrParam(self.__param)

    @property
    def interval(self):
        return self.__param.time_span

    @interval.setter
    def interval(self, value):
        self.__param.time_span = value
        init_param.setAlgrParam(self.__param)

    @property
    def end_time(self):
        return self.__param.end_time[0:1] + ':' +self.__param.end_time[2:3]

    @end_time.setter
    def end_time(self, value):
        self.__param.end_time = value[0:2] + value[3:5] + '00'
        init_param.setAlgrParam(self.__param)

    def setup(self, value):
        keys = ['mode', 'avg_count', 'interval', 'end_time']
        for key in keys:
            if key in value:
                self.__setattr__(key, value[key])

    def __repr__(self):
        return 'match_param(mode={}, avg_count={}, interval={}, end_time={})'.format(self.mode, self.avg_count, self.interval, self.end_time)


class InitContext(object):
    def __init__(self, api):
        self.__api = api
        self.__backtest = BackTestContext(api)
        self.__realtime = RealTimeContext(api)
        self.__match_param = MatchParamContext(self.__api)
        self.__bar = PreparedBarContext(self.__api)
        self.__fields = []
        self.__algo = AlgoContext(api)

    def setup(self, value):
        keys = {'symbols', 'symbol_sets', 'mode', 'prepared_bars', 'fields',
                'commission', 'match_param', 'backtest', 'realtime', 'algo'}
        for key in keys:
            if key in value:
                self.__setattr__(key, value[key])

    @property
    def symbols(self):
        return init_param.getSymbols(self.__api.get_strategy_name())

    @symbols.setter
    def symbols(self, value):
        value = conv_list_str(value)
        init_param.setSymbols(self.__api.get_strategy_name(), value)

    @property
    def symbol_sets(self):
        return init_param.getSymbols(self.__api.get_strategy_name())

    @symbol_sets.setter
    def symbol_sets(self, value):
        value = conv_list_str(value)
        init_param.setSymbolSets(self.__api.get_strategy_name(), value)

    @property
    def fields(self):
        return self.__fields

    @fields.setter
    def fields(self, value):
        value = conv_list_str(value)
        self.__api.setRequireFields(value)
        self.__fields = value

    @property
    def mode(self):
        return self.__realtime.mode

    @mode.setter
    def mode(self, value):
        self.__realtime.mode = value

    @property
    def prepared_bars(self):
        return self.__bar

    @prepared_bars.setter
    def prepared_bars(self, value):
        self.__bar.set_bars(value)

    @property
    def commission(self):
        return init_param.getCommission()

    @commission.setter
    def commission(self, value):
        init_param.setCommission(value)

    @property
    def match_param(self):
        return self.__match_param

    @match_param.setter
    def match_param(self, value):
        self.__match_param.setup(value)

    @property
    def backtest(self):
        return self.__backtest

    @backtest.setter
    def backtest(self, value):
        self.__backtest.setup(value)

    @property
    def realtime(self):
        return self.__realtime

    @realtime.setter
    def realtime(self, value):
        self.__realtime.setup(value)

    @property
    def algo(self):
        return self.__algo

    @algo.setter
    def algo(self, value):
        self.__algo.setup(value)

    def __setattr__(self, key, value):
        if '_InitContext__' in key:
            object.__setattr__(self, key, value)
            return

        if not hasattr(self.__api, 'init_time') or not self.__api.init_time:
            raise StrategyException('can\'t setup init param at this time! just set in on_initialize.')

        object.__setattr__(self, key, value)

    def __repr__(self):
        if self.__api.isBackTest():
            return "init(mode={}, bars={}, match_param={}, commission={}, backtest={}, algo={})".format(self.mode,
                                                                                                        self.bars,
                                                                                                        self.match_param,
                                                                                                        self.commission,
                                                                                                        self.backtest,
                                                                                                        self.algo)
        else:
            return "init(mode={}, bars={}, match_param={}, commission={}, realtime={}, algo={})".format(self.mode,
                                                                                                        self.bars,
                                                                                                        self.match_param,
                                                                                                        self.commission,
                                                                                                        self.realtime,
                                                                                                        self.algo)


class StdSymbolsContext(object):
    def __init__(self, api):
        self.__api = api

    def __getitem__(self, item):
        if type(item) == list or set:
            values = set()
            for each in item:
                ref_data = self.__api.getRefData(each)
                if ref_data is not None:
                    if ref_data.isStandard:
                        values.add(each)
                    else:
                        values.update(self.__api.getConstituentSymbols(each))

            return values
        elif type(item) == str:
            values = set(self.__api.getConstituentSymbols(item))
            return values
        else:
            raise Exception('no supported item type, please offer list, set or str')


class NoStdSymbolsContext(object):
    def __init__(self, api):
        self.__api = api

    def __getitem__(self, item):
        if type(item) == list or set:
            values = set()
            for each in item:
                ref_data = self.__api.getRefData(each)
                if ref_data is not None:
                    if ref_data.isStandard:
                        values.add(each)
                    elif ref_data.marketName == 'CF':
                        values.add(each)
                    else:
                        values.update(self.__api.getConstituentSymbols(each))

            return values
        elif type(item) == str:
            ref_data = self.__api.getRefData(item)
            if ref_data is not None:
                values = self.__api.getConstituentSymbols(item)
                return values
        else:
            raise Exception('no supported item type, please offer list, set or str')


class SymbolsContext(object):
    def __init__(self, api):
        self.std = StdSymbolsContext(api)
        self.nostd = NoStdSymbolsContext(api)


class DynamicContext(object):
    def __init__(self, api):
        self.__api = api

    def __getitem__(self, item):
        return self.__api.get_dynamic_value(item)

    def __repr__(self):
        return self.__api.print_dynamic()


class BarContext(object):
    __slots__ = '__api'

    def __init__(self, api):
        self.__api = api

    def __getitem__(self, item):
        if isinstance(item, list) or isinstance(item, tuple) or isinstance(item, set):
            return self.__api.get_bars_now(list(item))
        else:
            return self.__api.get_bars_now([item])

    @property
    def focus(self):
        return self.__api.get_bars_now(self.__api.getFocusAndPositionSymbols())

    @property
    def position(self):
        return self.__api.get_bars_now(self.__api.getPositionSymbols())

    def __repr__(self):
        return 'bar(focus=..., position=...)'


class AccountContext(object):
    def __init__(self, api):
        self.__api = api

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.__api.getAccount(market=item)

        raise Exception('unknown account param')

    def __repr__(self):
        return '"CS": {}, "CF": {}'.format(self.__api.getAccount(market='CS'), self.__api.getAccount(market='CF'), self.__api.getAccount(market='SJ'), self.__api.getAccount(market='HK'))


class ConfigContext(object):
    __slots__ = ()

    @property
    def host(self):
        return init_param.getHost()

    @property
    def port(self):
        return init_param.getPort()

    @property
    def user(self):
        return init_param.getUser()

    def __repr__(self):
        return 'host:{}, port:{}, user:{}'.format(self.host, self.port, self.user)


class Context(object):
    __apis = {}
    __slots__ = ('__api', '__account', 'strategy', 'positions', 'pool', '__init', 'symbols', 'dynamic', 'bar', '__env', 'config')

    def __init__(self, analyser_name):
        self.__api = Context.__apis[analyser_name]
        self.__account = AccountContext(self.__api)
        self.strategy = StrategyContext(self.__api)
        self.positions = AccountPositionContext(self.__api)
        self.pool = PoolContext(self.__api)
        self.__init = InitContext(self.__api)
        self.symbols = SymbolsContext(self.__api)
        self.dynamic = DynamicContext(self.__api)
        self.bar = BarContext(self.__api)
        self.config = ConfigContext()
        self.__env = None

    @property
    def init(self):
        return self.__init

    @init.setter
    def init(self, value):
        self.__init.setup(value)

    @property
    def account(self):
        return self.__account

    @property
    def env(self):
        if self.__env is None:
            if self.__api.isBackTest:
                self.__env = 'backtest'
            elif self.__api.isRealEnv:
                self.__env = 'real'
            else:
                self.__env = 'sim'
        return self.__env

    @property
    def time(self):
        return EtaTime(self.__api.timeNow())

    @staticmethod
    def register(api):
        Context.__apis[api.get_strategy_name()] = api

    @staticmethod
    def get_api(analyser_name=None):
        if analyser_name is None:
            return Context.__apis

        return Context.__apis[analyser_name]

    def __getitem__(self, item):
        if item in Context.__apis:
            return Context(item)
