import random
import json
import math
import bitmex
import time
import datetime
import uuid
import pickle

from bravado.exception import HTTPUnauthorized, HTTPBadRequest, HTTPNotFound

class BitmexClient:
    def __init__(self, symbol='XBTUSD', api_key=None, api_secret=None, test=True):
        self.client = bitmex.bitmex(api_key=api_key, api_secret=api_secret, test=test)
        self.symbol = symbol
        self._last_currentprice = 0

    def __call__(self):
        return self.client

    def getHistory(self, symbol='XBTUSD', binSize='5m', count=15):
        try:
            return self.client.Trade.Trade_getBucketed(symbol=symbol,
                                                    binSize=binSize,
                                                    count=count,
                                                    reverse=True,
                                                    ).result()
        except HTTPBadRequest as e:
            if 'expired' in str(e):
                now = datetime.datetime.utcnow()
                print('Get history expired error. Time:', now, ' Server Time:', now.strftime("%m/%d/%Y, %H:%M:%S"), 'Returning last price.', flush=True)
            else:
                print('Error getting history', e, flush=True)    

    def getXBTUSDPosition(self, prop):
        return self.client.Position.Position_get(
            filter=json.dumps({'symbol': self.symbol})).result()[0][0][str(prop)]

    def getWallet(self, prop):
        return self.client.User.User_getWallet().result()[0][str(prop)]

    def getPosition(self, property):
        return self.client.Position.Position_get(
            filter=json.dumps({'symbol': self.symbol})).result()[0][0][property]

    @property
    def is_connected(self):  # [test]
        if not self.acc_balance:
            return False
        else:
            return True

    @property
    def acc_balance(self):
        try:
            return self.getWallet('amount')
        except HTTPUnauthorized:
            return False

    @property
    def unrealisedPnl(self):
        return self.getPosition('unrealisedPnl')

    @property
    def open_contracts(self):
        return self.getPosition('currentQty')

    @property
    def current_price_position(self):
        return self.getPosition('lastPrice')

    @property
    def last_current_price(self):
        if self._last_currentprice:
            return self._last_currentprice
        else:
            time.sleep(2)
            return self.current_price

    @property
    def current_price(self):
        cp = 0
        try:
            cp = self.client.Trade.Trade_get(symbol='XBTUSD',
                                             count=2,
                                             reverse=True,
                                             ).result()[0][0]['price']
            self._last_currentprice = cp
            return cp
        except (IndexError, HTTPBadRequest) as e:
            if 'expired' in str(e):
                now = datetime.datetime.utcnow()
                print('Current price expired error. Time:', now, ' Server Time:', now.strftime("%m/%d/%Y, %H:%M:%S"), 'Returning last price.', flush=True)
            return self._last_currentprice


class BitmexOrder:
    def __init__(self, client, settings_path, position_size=1, symbol='XBTUSD', magic='algo-trader_'):
        self._position_size = position_size  # in %
        self.client = client
        self.Magic = magic
        self.BotID = self.Magic + symbol + '_'
        self.symbol = symbol
        self._settings_path = settings_path

        self.Entry = 0 
        self.WaitStop = False
        self.Open = False
        self.Qty = 0

        self.StopID = ''
        self.StoplossID = ''
        self.TakeprofitID = ''

        self.SL = 0
        self.TP = 0

    def check_open_bot_order(self, entry, sl):
        settings = pickle.load(open(self._settings_path, 'rb'))
        self.StoplossID = settings.last_order_id
        if self.StoplossID:
            try:
                res = self.client.client.Order.Order_getOrders(filter=json.dumps({"symbol": "XBTUSD", "open": True})).result()
                if self.StoplossID in [order['clOrdID'] for order in res[0]]:
                    # bot order is open and sl might be modified
                    self.modifiy_stop(sl)
                    self.Entry = entry
                    self.save_open_state(True)
            except HTTPBadRequest as e:
                print("Error getting orders.", e)

    def save_open_id(self, id):
        self.StoplossID = id
        settings = pickle.load(open(self._settings_path, 'rb'))
        settings.last_order_id = self.StoplossID
        pickle.dump(settings, file=open(self._settings_path, 'wb'))

    def manage_entries(self):
        cp = self.client.current_price
        if self.WaitStop:
            time.sleep(2)
            if self.Qty > 0 and cp >= self.Entry and self.client.open_contracts != 0:
                self.save_pending_state(False)
                self.save_open_state(True)
                print("Long Position has been opened, amending Stoploss to", self.SL, flush=True)
                self.stoploss_order()
            elif self.Qty < 0 and cp <= self.Entry and self.client.open_contracts != 0:
                self.save_pending_state(False)
                self.save_open_state(True)
                print("Short Position has been opened, amending Stoploss to", self.SL, flush=True)
                self.stoploss_order()
        elif self.Open:
            if self.Qty > 0 and cp < self.SL and self.client.open_contracts == 0:
                self.save_open_state(False)
                self.save_open_contracts(0)
                print("Long Position closed. {} Contracts from {} to {}. PnL in Points: {}".format(self.Qty, self.Entry, self.SL, self.bitmex_decimals(cp-self.Entry)), flush=True)
            elif self.Qty < 0 and cp > self.SL and self.client.open_contracts == 0:
                self.save_open_state(False)
                self.save_open_contracts(0)
                print("Short Position closed. {} Contracts from {} to {}. PnL in Points: {}".format(-self.Qty, self.Entry, self.SL, self.bitmex_decimals(cp-self.Entry)), flush=True)
            else:
                self.save_open_state(False)

    def generate_id(self, _type='stop'):
        return self.BotID + str(uuid.uuid4().fields[-1])[:5] + '_' + _type

    def save_open_contracts(self, orderQty):
        self.Qty = orderQty

    def save_pending_state(self, state):
        self.WaitStop = state

    def save_open_state(self, state):
        self.Open = state

    def bitmex_decimals(self, price):
        return round(price * 2) / 2

    def order_id():
        return str(random.randint(100000, 999999))

    def calc_pos_size(self, sl_distance):
        acc_balance = self.client.acc_balance
        cp = self.client.last_current_price
        riskvalue = float(acc_balance) / 100000000 * float(cp) * (float(self._position_size)/100)
        pos_size = int(round((math.floor(riskvalue / sl_distance * 5000) / 100)) * 100)
        if pos_size < 100:
            return 100
        else:
            return pos_size

    def stoploss_order(self, execPrice='LastPrice'):
        try:
            self.StoplossID = self.generate_id(_type='SL')
            self.save_open_id(self.StoplossID)
            return self.client.client.Order.Order_new(
                symbol=self.symbol, ordType='Stop', clOrdID=self.StoplossID, orderQty=-self.Qty,
                stopPx=self.bitmex_decimals(self.SL), execInst=execPrice
            ).result()
        except HTTPBadRequest as e:
            print("Error placing stoploss order.", e, flush=True)

    def order_cancel(self, orderId):
        try:
            order_res = self.client.client.Order.Order_cancel(
                clOrdID=orderId
            ).result()
            self.WaitStop = False
            return order_res
        except (HTTPBadRequest, HTTPNotFound) as e:
            print("Error canceling order.", e, flush=True)

    def stoploss_cancel(self):
        self.order_cancel(self.StoplossID)

    def stoporder_cancel(self):
        self.order_cancel(self.StopID)

    def bracket_stop_order(self, orderQty, entry, sl, tp=0):
        try:
            self.StopID = self.generate_id()
            order_res = self.client.client.Order.Order_new(
                symbol=self.symbol, ordType='Stop', clOrdID=self.StopID, orderQty=orderQty,
                stopPx=self.bitmex_decimals(entry), execInst='LastPrice'
            ).result()
            self.save_open_contracts(orderQty)
            self.save_pending_state(True)
            self.SL = sl
            self.TP = tp
            self.Entry = entry
            return order_res
        except HTTPBadRequest as e:
            print("Error placing bracket stop order.", e, flush=True)

    def bracket_market_order(self, orderQty, sl, tp=0):
        try:
            entry = self.market_order(orderQty)
            self.SL = sl
            self.TP = tp
            time.sleep(5)
            stoploss = self.stoploss_order()
            self.save_open_contracts(orderQty)
            self.save_open_state(True)
            return entry, stoploss
        except HTTPBadRequest as e:
            print("Error placing bracket market order.", e, flush=True)

    def market_order(self, orderQty):
        try:
            order_res = self.client.client.Order.Order_new(
                symbol=self.symbol, ordType='Market', orderQty=orderQty
            ).result()
            self.save_open_contracts(orderQty)
            self.save_open_state(True)
            return order_res
        except HTTPBadRequest as e:
            print("Error placing market order.", e, flush=True)

    def modifiy_stop(self, newPrice):
        if self.WaitStop:
            try:
                res = self.client.client.Order.Order_amend(
                    orderID=self.StoplossID, stopPx=self.bitmex_decimals(
                        newPrice)
                ).result()
                return res
            except HTTPBadRequest as e:
                if 'Invalid amend' in str(e):
                    return 'noValChanged'
                elif 'Invalid origClOrdID' in str(e):
                    return 'invalidID'
                else:
                    return str(e)
        else:
            return False

    def close(self, qty=0):
        if not qty:
            qty = -self.Qty
        if self.Open:
            try:
                return self.client.client.Order.Order_new(
                    symbol=self.symbol, ordType='Market', execInst='Close', orderQty=qty
                ).result()
            except HTTPBadRequest as e:
                print("Error closing order.", e, flush=True)
        else:
            return False
