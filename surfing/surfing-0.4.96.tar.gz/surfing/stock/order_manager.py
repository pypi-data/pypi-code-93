from ..structure import PositionInfo, OrderStatus
from ..constant import AssetType
from queue import Queue
import datetime
import copy
from pdb import set_trace

class OrderManager:

    def __init__(self,run_engine=None,strategy_type=None):
        self.run_engine = run_engine
        self.positions = {}
        self._cur_id = 0
        self.pending_orders = Queue()
        self.pending_transfers = [] # item is (insert_time, Transfer)
        self.id_orders = {}
        self.trades = {}
        self.ticks = {}
        self.mvs = {}
        self.pos = {}
        self.strategy_type = strategy_type
        self.cash_list = {}

    def init(self):
        pass

    def add_strategy(self, st_name, position_info=None):
        self.positions[st_name] = position_info if position_info else PositionInfo() 
        
        if self.strategy_type == 'stock_daily':
            beginday_yesterday = self.run_engine._data_manager.wrapper.find_beginday_yesterday()
            self.mvs[st_name] = [(beginday_yesterday, position_info.cash.position )] if position_info.cash.position else []
        else:
            self.mvs[st_name] = [] 
        self.trades[st_name] = []
        self.pos[st_name] = {}
        self.cash_list[st_name] = []

    def on_tick(self, tick):
        self.ticks[tick.ticker] = tick
        if self.strategy_type == 'crypto': #TODO 
            for _, position in self.positions.items():
                position.cal_unrealized(tick)

    def check_order(self, order):
        order.order_id = self.new_order_id()
        # 1. record and check availability
        # if has err, set err_msg
        # order.err_msg = 'something wrong'
        order.status = OrderStatus.RESPONDED
        self.id_orders[order.order_id] = order
        self.pending_orders.put(order)
    
    def check_transfer(self, transfer):
        transfer.transfer_id = self.new_order_id()
        # check if this transfer from is ok otherwise refuse
        if not self.get_position(transfer.source).init_transfer(transfer):
            transfer.err_msg = "rejected by PositionInfo"
        else:
            self.pending_transfers.append((self.run_engine.now(), transfer))

    def cancel_order(self, order_id):
        order = self.id_orders.get(order_id)
        if not order is None:
            order.status = OrderStatus.CANCELLED
            self.id_orders.pop(order_id, None)
            return True
        else:
            return self.run_engine._match_engine.cancel_order(order_id)

    def process_orders(self):
        while not self.pending_orders.empty():
            od = self.pending_orders.get()
            self.id_orders.pop(od.order_id, None)
            if od.status == OrderStatus.RESPONDED:
                od.status = OrderStatus.QUEUEING
                self.run_engine._push_order_status(od)
                self.run_engine._match_engine.process_order(od, on_tick=False)

    def process_orders_daily(self, order_list):
        for order in order_list:
            order = copy.deepcopy(order)
            order.order_id = self.new_order_id()
            self.run_engine._match_engine.process_order_daily(order)

    def process_transfers(self, transfer_timedelta=datetime.timedelta(hours=1)):
        cut_time = self.run_engine.now() - transfer_timedelta
        while len(self.pending_transfers) > 0:
            if self.pending_transfers[0][0] > cut_time:
                break
            transfer = self.pending_transfers[0][1]
            self.get_position(transfer.source).confirm_transfer(transfer)
            self.pending_transfers.remove(self.pending_transfers[0])
            self.run_engine._push_transfer(transfer)

    def process_trade(self, trade):
        # 1. record this trade
        # 2. update position
        self.trades[trade.source].append(trade)
        self.positions[trade.source].process_trade(trade)

    def new_order_id(self):
        self._cur_id += 1
        return self._cur_id

    def get_position(self, name):
        return self.positions.get(name)

    def get_trade(self, name):
        return self.trades.get(name)

    def on_day(self, day_data):
        self.day_data = day_data

    def get_market_value(self, name):  
        pos = self.get_position(name) 
        if self.strategy_type  == 'stock_daily':
            mv = pos.cash.position 
            for pi in pos.holdings:
                pt = pi.get_price_ticker()
                if pt in list(self.day_data.keys()):
                    mv += pi.get_market_value(self.day_data[pt])
            return round(mv)
        elif self.strategy_type  == 'crypto': 
            return pos.get_total_market_value() 
        else:
            mv = pos.cash.position 
            for pi in pos.holdings:
                pt = pi.get_price_ticker()
                if self.ticks.get(pt):
                    mv += pi.get_market_value(self.ticks[pt].last_price)
            return mv

    def switch_day(self):
        for st_pos in self.positions:
            for idx, pi in enumerate(self.positions[st_pos].holdings):
                pi.switch_day()
            self.pos[st_pos][self.run_engine.now()] = {pi.ticker : {'volume':pi.position, 'price':self.day_data[pi.ticker]} for pi in self.positions[st_pos].holdings if abs(pi.position) > 1e-9}
        
        cur_dt = self.run_engine.now()
        for st_name in self.run_engine._strategies.keys():
            self.mvs[st_name].append((cur_dt, self.get_market_value(st_name)))
            self.cash_list[st_name].append((cur_dt, self.get_position(st_name).cash.position))
    
    def terminate(self):
        pass

    def print_result(self, st_name):
        print('---------- {} ----------'.format(st_name))
        for dt, mv in self.mvs[st_name]:
            print('{}: {}'.format(dt, mv))
        print('---------- FINISH ----------')
        print('')