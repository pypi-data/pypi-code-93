
from .structure import Tick, Order, Trade, OrderStatus, ExecRole, Direction, OrderType, PositionInfo
from .constant import AssetType
from queue import Queue

class MatchEngine:

    def __init__(self,run_engine=None,strategy_type=None):
        self.run_engine = run_engine
        self.ticks = {}
        self.pending_orders = {}
        self.id_orders = {}
        self._cur_trade_id = 1000000
        self.strategy_type = strategy_type
        self.stock_slippage = PositionInfo.FEE_RATE['STOCK']['SLIPPAGE']
 

    def init(self):
        if self.strategy_type != 'stock_daily':
            print(self.strategy_type)
            for ticker in self.run_engine._universe:
                self.pending_orders[ticker] = Queue()

    def process_order(self, order, on_tick=False):
        if order.status == OrderStatus.QUEUEING:
            # TODO: now we assume once traded, all traded, no partly traded
            trades = self.match_order(order, on_tick)
            if trades:
                for td in trades:
                    self.run_engine._push_trade(td)
                order.status = OrderStatus.ALL_TRADED
                self.run_engine._push_order_status(order)
                self.id_orders.pop(order.order_id, None)
            else:
                self.id_orders[order.order_id] = order
                self.pending_orders[order.ticker].put(order)

    def process_order_daily(self, order):
        trades = self.match_order_daily(order)
        if trades:
            for td in trades:# in case one order split into multiple trades
                self.run_engine._push_trade(td)

    def cancel_order(self, order_id):
        order = self.id_orders.get(order_id)
        if not order is None and order.status == OrderStatus.QUEUEING:
            order.status = OrderStatus.CANCELLED
            self.run_engine._push_order_status(order)
            self.id_orders.pop(order_id, None)
            return True
        else:
            return False

    def on_tick(self, tick):
        self.ticks[tick.ticker] = tick
        self.process_orders(tick.ticker, True)

    def on_day(self, day_data):
        self.day_data = day_data        

    def process_orders(self, ticker, on_tick=False):
        i = 0
        sz = self.pending_orders[ticker].qsize()
        # at most we loop over the whole pending orders once.
        while i < sz and not self.pending_orders[ticker].empty():
            od = self.pending_orders[ticker].get()
            self.process_order(od, on_tick)
            i += 1

    #############################
    # on_tick is a bool
    #   True: this matching is triggered by a tick data
    #   False: this matching is triggered by a order
    #############################
    def match_order(self, order, on_tick):
        tick = self.ticks[order.ticker]
        if tick is None:
            return None
        trade = Trade(order_id=order.order_id, exchange=order.exchange, ticker=order.ticker, asset_type=order.asset_type,
                      direction=order.direction, trade_volume=order.volume, source=order.source)
        if order.order_type is OrderType.MARKET:
            trade.trade_price = tick.ask_price1 if order.direction == Direction.BUY else tick.bid_price1
            trade.trade_id = self.new_trade_id()
            trade.exec_role = ExecRole.TAKER
            return [trade]
        else:
            if order.direction == Direction.BUY and order.price >= tick.ask_price1:
                trade.trade_price = order.price if on_tick else tick.ask_price1
                trade.exec_role = ExecRole.MAKER if on_tick else ExecRole.TAKER
                trade.trade_id = self.new_trade_id()
                return [trade]
            elif order.direction == Direction.SELL and order.price <= tick.bid_price1:
                trade.trade_price = order.price if on_tick else tick.bid_price1
                trade.exec_role = ExecRole.MAKER if on_tick else ExecRole.TAKER
                trade.trade_id = self.new_trade_id()
                return [trade]
        return None

    def match_order_daily(self, order):
        trade = Trade(order_id=order.order_id, exchange=order.exchange, ticker=order.ticker, asset_type=order.asset_type,
                      direction=order.direction, trade_volume=order.volume, source=order.source, time=self.day_data['time'])
        trade.trade_id = self.new_trade_id()
        # adjust trade price with trade fee and slippage 
        if order.direction == Direction.BUY:
            trade.trade_price = order.price * (1 + self.stock_slippage)

        elif order.direction == Direction.SELL:
            trade.trade_price = order.price * (1 - self.stock_slippage)
        return [trade]

    def switch_day(self):
        pass

    def terminate(self):
        pass

    def new_trade_id(self):
        self._cur_trade_id += 1
        return self._cur_trade_id