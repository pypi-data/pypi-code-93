from .backtest_engine import BacktestEngine
from .strategy_base import StrategyBase, Direction
from ..structure import AssetType, PositionInfo

class StockDailyStrategy(StrategyBase):

    def __init__(self,strategy_name=None,pool_name=None,factor_name=None,data_path=None,longshort=None,top=None,period=None):

        self.factor_name    = factor_name
        self.longshort      = longshort
        self.top            = top
        self.sell_list      = []
        self.wait_sell_list = [] 
        self.period         = period
        self.cash           = 0
        # input fee here to pre calculate amount of cash used in buying stock
        self.sell_fee       = PositionInfo.FEE_RATE['STOCK']['SLIPPAGE']+PositionInfo.FEE_RATE['STOCK']['SELLFEE']
        self.buy_fee        = PositionInfo.FEE_RATE['STOCK']['SLIPPAGE']+PositionInfo.FEE_RATE['STOCK']['BUYFEE']
        self.cash_spliter   = 1
        StrategyBase.__init__(self, strategy_name)

    def init(self):
        self.pay_count = 5
        self.stop_count = 10
        self.index = 0

    def on_day(self, day_data):
        # strategy main function, daily buy & sell
        self.cash = self.context._order_manager.positions[self._name].cash.position
        self.build_cash_spliter(day_data)        
        sell_day = self.get_sell_day(day_data['time'], self.period)
        if sell_day:
            self.sell_list = self.get_trade_buy(sell_day)
        self.build_long()
        self.build_trade_list(day_data)

    def build_cash_spliter(self, day_data):
        idx = self.context._data_manager.wrapper.date_list.index(day_data['time'])
        if idx < (self.period-1):
            self.cash_spliter = self.period - idx
        else:
            self.cash_spliter = 1

    def build_long(self):
        if self.longshort[0] == 0:
            self.long_list = None
        else:
            ticker_list = [k for k, v in sorted(self.context._data_manager.factor_today.items(), key=lambda item: item[1]) if k not in self.context._data_manager.rm_l_today]
            if self.longshort[0] == 1:
                self.long_list = ticker_list[self.top * -1:]
            elif self.longshort[0] == -1:
                self.long_list = ticker_list[: self.top ]
            
    def build_short(self):
        #TODO such shorttop
        pass

    def build_trade_list(self, day_data):
        # if tick should be sell today but suspended, put it into wait_sell_list
        self.order_list = []
        if self.sell_list:
            sell_list = self.sell_list + self.wait_sell_list
            self.wait_sell_list = []
            for sell_i in sell_list:
                if sell_i.ticker in self.context._data_manager.suspended_today:
                    self.wait_sell_list.append(sell_i)
                    continue
                od = self.build_order(ticker=sell_i.ticker, direction=Direction.SELL, volume=sell_i.volume, price=day_data[sell_i.ticker], asset_type=AssetType.STOCK)
                self.order_list.append(od)
                self.cash += sell_i.volume * day_data[sell_i.ticker] * (1 - self.sell_fee )
        
        for long_i in self.long_list:
            price = day_data[long_i]
            od = self.build_order(ticker=long_i, direction=Direction.BUY, volume=self.cash/self.cash_spliter/price/self.top/(1+self.buy_fee), price=price,asset_type=AssetType.STOCK)
            self.order_list.append(od)

    def on_trade(self, trade):
        pass

    def on_order(self, order_id, order_status):
        pass

