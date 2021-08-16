
from ..structure import Order, Direction, OrderType, AssetType, ExchangeID, TransferRequest, Trade, Sell

class StrategyBase:

    def __init__(self, name):
        self._name = name
        pass

    def set_context(self, context):
        self.context = context

    def init(self, params=None):
        pass
 
    def on_tick(self, tick):
        pass

    def on_trade(self, trade):
        pass

    def on_order(self, order_id, order_status):
        pass

    def on_transfer(self, transfer):
        pass
    
    def insert_order(self, ticker, direction, volume, price=None, exchange=ExchangeID.NOT_AVAILABLE, asset_type=None):
        # price is None if this is a market order
        # return order_id if success
        # return None if there is a error
        order = Order(ticker=ticker, direction=direction, volume=volume, exchange=exchange, 
                      asset_type=self.context._asset_types[ticker] if asset_type is None else asset_type,
                      order_type=OrderType.LIMIT if price else OrderType.MARKET, price=price, source=self._name)
        return self.context.insert_order(order)

    def build_order(self, ticker, direction, volume, price=None, exchange=ExchangeID.NOT_AVAILABLE, asset_type=None):        
        order = Order(ticker=ticker, direction=direction, volume=volume, exchange=exchange, 
                      asset_type=self.context._asset_types[ticker] if asset_type is None else asset_type,
                      order_type=OrderType.LIMIT if price else OrderType.MARKET, price=price, source=self._name)
        
        return order

    def cancel_order(self, order_id):
        # input:  order_id (return value of insert_order)
        # output: 
        #         True if the order is cancelled
        #         False if the order is not exists or has already been filled
        return self.context.cancel_order(order_id)

    
    def insert_transfer(self, from_ticker, to_ticker, from_exchange, to_exchange, volume):
        # input: position ticker ('rmb', 'btc', 'usdt' etc.)
        # output:
        #         transfer_id if transfer permitted
        #         None if transfer failed.
        transfer = TransferRequest(from_ticker=from_ticker, to_ticker=to_ticker, from_exchange=from_exchange, to_exchange=to_exchange, volume=volume, source=self._name)
        return self.context.insert_transfer(transfer)

    def get_position(self):
        return self.context.get_position(self._name)

    def get_trade_buy(self, date):
        return [Sell(ti.ticker, ti.trade_volume) for ti in self.context.get_trade(self._name) if (ti.time == date and ti.direction == Direction.BUY)]
            
    def get_market_value(self):
        return self.context.get_market_value(self._name)

    def switch_day(self):
        pass

    def get_sell_day(self, today, period):
        try:
            idx = self.context._data_manager.wrapper.date_list.index(today) - period
            if idx < 0:
                return None
            else:
                return self.context._data_manager.wrapper.date_list[idx]
        except:
            return None