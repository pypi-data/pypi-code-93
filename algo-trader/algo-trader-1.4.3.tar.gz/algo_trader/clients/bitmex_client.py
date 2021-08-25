import json
import math
import bitmex
import time
import uuid
import pickle
import sys

from bravado.exception import HTTPUnauthorized, HTTPBadRequest, HTTPNotFound


class BitmexClient:
    def __init__(self, api_key=None, api_secret=None, testnet=True):
        self.client = bitmex.bitmex(
            api_key=api_key, api_secret=api_secret, test=testnet)
        self._last_currentprice = {}
        self.testnet = testnet

    def __call__(self):
        return self.client

    def get_wallet(self, prop):
        return self.client.User.User_getWallet().result()[0][str(prop)]

    def get_position(self, symbol, prop):
        try:
            return self.client.Position.Position_get(
            filter=json.dumps({'symbol': symbol})).result()[0][0][str(prop)]
        except IndexError:
            return False

    def get_histories(self, symbols=['XBTUSD'], binSize='5m', count=15):
        histories = {}
        for symbol in symbols:
            i = 0
            while True:
                for symbol in symbols:
                    try:
                        histories[symbol] = self.client.Trade.Trade_getBucketed(symbol=symbol,
                                                                                binSize=binSize,
                                                                                count=count,
                                                                                reverse=True,
                                                                                ).result()
                    except HTTPBadRequest as e:
                        if 'expired' in str(e):
                            print('Getting {} history failed. Expired error.'.format(
                                symbol), flush=True)
                        else:
                            time.sleep(2)  # try again after 2 seconds
                            print("Can't get history. Trying again...", e)
                            i += 1
                            if i > 1:
                                print("Can't get history for 2nd time.")
                                return False
                            else:
                                continue
        return histories

    def get_current_price(self, symbol):
        try:
            price = self.client.Trade.Trade_get(symbol=symbol,
                                                count=2,
                                                reverse=True,
                                                ).result()[0][0]['price']
            self._last_currentprice[symbol] = price
            return price
        except (IndexError, HTTPBadRequest) as e:
            if 'expired' in str(e):
                # now = datetime.datetime.utcnow()
                # print('Current price expired error. Time:', now, ' Server Time:', now.strftime("%m/%d/%Y, %H:%M:%S"), 'Returning last price.', flush=True)
                print('Current price expired error. Returning last price.', flush=True)
            return self._last_currentprice[symbol]

    def last_current_price(self, symbol):
        if self._last_currentprice:
            return self._last_currentprice[symbol]
        else:
            time.sleep(2)
            return self.get_current_price(symbol)

    def unrealised_pnl(self, symbol):
        return self.get_position(symbol, 'unrealisedPnl')

    def open_contracts(self, symbol):
        res = self.get_position(symbol, 'currentQty')
        if res is not False:
            return res
        else:
            return 0

    def current_price_position(self, symbol):
        return self.get_position(symbol, 'lastPrice')

    @property
    def is_connected(self):
        if not self.acc_balance:
            return False
        else:
            return True

    @property
    def acc_balance(self):
        try:
            return self.get_wallet('amount')
        except HTTPUnauthorized:
            return False


class BitmexOrder:
    def __init__(self, symbols, client, settings, settings_path, magic='algo-trader'):
        self.client = client
        self.settings = settings
        self._settings_path = settings_path
        self.magic = magic

        self.props = {}
        for symbol in symbols:
            self.props[symbol] = {
                'stoploss_id': '', 'stop_id': '', 'entry': .0, 'SL': .0, 'TP': .0, 'open': False, 'wait_stop': False, 'qty': 0}

    def check_open_bot_order(self, symbol, entry, sl):
        settings = pickle.load(open(self._settings_path, 'rb'))
        self.props[symbol]['stoploss_id'] = settings.symbols[symbol]['last_order_id']
        if self.props[symbol]['stoploss_id']:
            try:
                res = self.client.client.Order.Order_getOrders(
                    filter=json.dumps({"symbol": symbol, "open": True})).result()
                if self.props[symbol]['stoploss_id'] in [order['clOrdID'] for order in res[0]]:
                    print("Bot order open, stoploss might be modified", flush=True)
                    self.modifiy_stop(symbol, sl)
                    self.props[symbol]['entry'] = entry
                    self.props[symbol]['open'] = True
            except HTTPBadRequest as e:
                print("Error getting orders.", e)

    def save_open_id(self, symbol, id):
        self.props[symbol]['stoploss_id'] = id
        settings = pickle.load(open(self._settings_path, 'rb'))
        settings.symbols[symbol]['last_order_id'] = id
        pickle.dump(settings, file=open(self._settings_path, 'wb'))

    def manage_entries(self, symbols):
        for symbol in symbols:
            cp = self.client.get_current_price(symbol)
            if self.props[symbol]['wait_stop']:
                time.sleep(0.5)
                if self.props[symbol]['qty'] > 0 and cp >= self.props[symbol]['entry'] and self.client.open_contracts(symbol) != 0:
                    self.props[symbol]['wait_stop'] = False
                    self.props[symbol]['open'] = True
                    print("Long Position has been opened, amending Stoploss to",
                          self.props[symbol]['SL'], flush=True)
                    self.stoploss_order(symbol)
                elif self.props[symbol]['qty'] < 0 and cp <= self.props[symbol]['entry'] and self.client.open_contracts(symbol) != 0:
                    self.props[symbol]['wait_stop'] = False
                    self.props[symbol]['open'] = True
                    print("Short Position has been opened, amending Stoploss to",
                          self.props[symbol]['SL'], flush=True)
                    self.stoploss_order(symbol)
            elif self.props[symbol]['open']:
                if self.props[symbol]['qty'] > 0 and cp <= self.props[symbol]['SL'] and self.client.open_contracts(symbol) == 0:
                    self.props[symbol]['open'] = False
                    self.props[symbol]['qty'] = 0
                    print("Long Position closed. {} Contracts from {} to {}. PnL in Points: {}".format(
                        self.props[symbol]['qty'], self.props[symbol]['entry'], self.props[symbol]['SL'], self.price_decimals(symbol, cp-self.props[symbol]['entry'])), flush=True)
                elif self.props[symbol]['qty'] < 0 and cp >= self.props[symbol]['SL'] and self.client.open_contracts(symbol) == 0:
                    self.props[symbol]['open'] = False
                    self.props[symbol]['qty'] = 0
                    print("Short Position closed. {} Contracts from {} to {}. PnL in Points: {}".format(
                        -self.props[symbol]['qty'], self.props[symbol]['entry'], self.props[symbol]['SL'], self.price_decimals(symbol, cp-self.props[symbol]['entry'])), flush=True)
                else:
                    self.props[symbol]['open'] = False

    def generate_id(self, symbol, _type='stop'):
        return "{}_{}_{}_{}".format(self.magic, symbol, str(uuid.uuid4().fields[-1])[:5], _type)

    def price_decimals(self, symbol, price):
        if symbol == 'XBTUSD':
            return round(price * 2) / 2
        elif symbol == 'ETHUSD':
            return round(price * 20) / 20
        else:
            print('{} is not a valid symbol for price decimal rounding.'.format(symbol))
            sys.exit()

    def calc_pos_size(self, symbol, sl_distance):
        acc_balance = self.client.acc_balance
        ps = float(self.settings.symbols[symbol]['position_size'])
        if symbol == 'XBTUSD':
            btc_usd = self.client.last_current_price(symbol)
            lot_step = 100
            riskvalue = (float(acc_balance) / 100000000) * \
                float(btc_usd) * (ps/100)  # riskvalue in usd
            pos_size = int(
                round((math.floor(riskvalue / (sl_distance / btc_usd)) / lot_step)) * lot_step)
        elif symbol == 'ETHUSD':
            tickvalue = 100
            lot_step = 1
            riskvalue = acc_balance * (ps/100)
            pos_size = int(
                round((math.floor(riskvalue / (sl_distance * tickvalue)) / lot_step)) * lot_step)
        else:
            print('Symbol not supported')
            sys.exit()
        if pos_size < lot_step:
            return lot_step
        else:
            return pos_size

    def stoploss_order(self, symbol, execPrice='LastPrice'):
        try:
            self.props[symbol]['stoploss_id'] = self.generate_id(
                symbol, _type='SL')
            self.save_open_id(symbol, self.props[symbol]['stoploss_id'])
            return self.client.client.Order.Order_new(
                symbol=self.symbol, ordType='Stop', clOrdID=self.StoplossID, orderQty=-self.props[symbol]['qty'],
                stopPx=self.price_decimals(symbol, self.props[symbol]['SL']), execInst=execPrice
            ).result()
        except HTTPBadRequest as e:
            print("Error placing stoploss order.", e, flush=True)

    def order_cancel(self, symbol, orderId):
        try:
            order_res = self.client.client.Order.Order_cancel(
                clOrdID=orderId
            ).result()
            self.props[symbol]['wait_stop'] = False
            return order_res
        except (HTTPBadRequest, HTTPNotFound) as e:
            print("Error canceling order.", e, flush=True)

    def stoploss_cancel(self, symbol):
        self.order_cancel(self.props[symbol]['stoploss_id'])

    def stoporder_cancel(self, symbol):
        self.order_cancel(self.props[symbol]['stop_id'])

    def bracket_stop_order(self, symbol, orderQty, entry, sl, tp=0):
        try:
            self.props[symbol]['stop_id'] = self.generate_id(symbol)
            order_res = self.client.client.Order.Order_new(
                symbol=symbol, ordType='Stop', clOrdID=self.props[symbol]['stop_id'], orderQty=orderQty,
                stopPx=self.price_decimals(symbol, entry), execInst='LastPrice'
            ).result()
            self.props[symbol]['qty'] = orderQty
            self.props[symbol]['wait_stop'] = True
            self.props[symbol]['SL'] = sl
            self.props[symbol]['TP'] = tp
            self.props[symbol]['entry'] = entry
            return order_res
        except HTTPBadRequest as e:
            print("Error placing bracket stop order in {}.".format(
                symbol), e, flush=True)

    def bracket_market_order(self, symbol, orderQty, sl, tp=0):
        try:
            entry = self.market_order(symbol, orderQty)
            self.props[symbol]['SL'] = sl
            self.props[symbol]['TP'] = tp
            time.sleep(5)
            stoploss = self.stoploss_order(symbol)
            self.props[symbol]['qty'] = orderQty
            self.props[symbol]['open'] = True
            return entry, stoploss
        except HTTPBadRequest as e:
            print("Error placing bracket market order in {}.".format(
                symbol), e, flush=True)

    def market_order(self, symbol, orderQty):
        try:
            order_res = self.client.client.Order.Order_new(
                symbol=symbol, ordType='Market', orderQty=orderQty
            ).result()
            self.props[symbol]['qty'] = orderQty
            self.props[symbol]['open'] = True
            return order_res
        except HTTPBadRequest as e:
            print("Error placing market order.", e, flush=True)

    def modifiy_stop(self, symbol, newPrice):
        if self.props[symbol]['wait_stop']:
            try:
                res = self.client.client.Order.Order_amend(
                    orderID=self.props[symbol]['stoploss_id'], stopPx=self.price_decimals(symbol,
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

    def close(self, symbol, qty=0):
        if not qty:
            qty = -self.props[symbol]['qty']
        if self.props[symbol]['open']:
            try:
                return self.client.client.Order.Order_new(
                    symbol=symbol, ordType='Market', execInst='Close', orderQty=qty
                ).result()
            except HTTPBadRequest as e:
                print("Error closing order in {}.".format(symbol), e, flush=True)
        else:
            return False
