import sys
import random
import datetime, time
from dateutil import parser
from algo_trader.clients import BitmexOrder
import requests
import os

class Lotus:
    def __init__(self, client, token, pos_size, testnet, settings_file_name):
        self.client = client
        self._token = token
        self._pos_size = pos_size
        self._testnet = testnet
        self._settings_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'settings', settings_file_name))
        self._last_timestamp = datetime.datetime.utcnow()
        self._last_entry = 0
        self._last_sl = 0

        if not self.client.is_connected:
            print(
                "Invalid API ID or API Secret, please restart and provide the right keys", flush=True)
            # empty the inputs
            sys.exit()
        
        if testnet:
            from algo_trader.settings import TESTNET_LOTUS_LINK
            self._api_endpoint = TESTNET_LOTUS_LINK
        else:
            from algo_trader.settings import LIVE_LOTUS_LINK
            self._api_endpoint = LIVE_LOTUS_LINK

    def get_api_signal(self):
        auth = { 'token': self._token }
        r = requests.get(self._api_endpoint, params=auth)
        json = r.json()
        timestamp = parser.parse(json['timestamp'])
        if self._last_timestamp != timestamp:
            self._last_timestamp = timestamp
            if self._last_entry != json['entry'] and self._last_sl != json['stoploss']:
                self._last_entry = json['entry']
                self._last_sl = json['stoploss']
                return json['signal'], json['entry'], json['stoploss']
            else:
                return False, False, False
        else:
            return False, False, False

    def rand_sec(self, start=1, end=10):
        return random.randrange(start, end)

    def check_modify(self, sl):
        res = self.order.modifiy_stop(sl)
        if type(res) is str:
            print('Modify order Error:', res, flush=True)
        else:
            print('Modifying order to new stoploss:', sl, flush=True)
            self.order.SL = sl

    def process_signal(self, start=False):
        newsignal, entry, stoploss = self.get_api_signal()
        if start:
            self.order.check_open_bot_order(entry, stoploss)
            time.sleep(3)
        if newsignal:
            if newsignal in [-1, 1]:  # signal has open position
                if newsignal == 1:
                    if self.order.Qty > 0 or self.client.open_contracts > 0:
                        self.check_modify(stoploss)
                    elif self.client.open_contracts < 0:
                        print('Closing order.', flush=True)
                        close = self.order.close(qty=-self.order.Qty)
                        if close:
                            print('Closed open Bot old short position, because now the Bot\'s Position is long.', flush=True)
                        else:
                            print('Error closing order.', flush=True)
                    else:
                        cp = self.client.last_current_price
                        if cp < entry:
                            sl_dist = abs(stoploss-cp)
                            if sl_dist > 0.15 * sl_dist:
                                time.sleep(2)
                                contracts = self.order.calc_pos_size(sl_dist)
                                print("Open market stop order long into open Signal. Contracts {} Stoploss {}".format(contracts, stoploss), flush=True)
                                self.order.bracket_market_order(contracts, stoploss)
                else:
                    if self.order.Qty < 0 or self.client.open_contracts < 0:
                        self.check_modify(stoploss)
                    elif self.client.open_contracts > 0:
                        print('Closing order.', flush=True)
                        close = self.order.close(qty=-self.order.Qty)
                        if close:
                            print('Closed open Bot old long position, because now the Bot\'s Position is short.', flush=True)
                        else:
                            print('Error closing order.', flush=True)
                    else:
                        cp = self.client.last_current_price
                        if cp > entry:
                            sl_dist = abs(entry-cp)
                            if sl_dist > 0.15 * sl_dist:
                                time.sleep(2)
                                contracts = self.order.calc_pos_size(sl_dist)
                                print("Open market stop order short into open Signal. Contracts {} Stoploss {}".format(contracts, stoploss), flush=True)
                                self.order.bracket_market_order(-contracts, stoploss)
            elif newsignal in [-2, 2]:  # signal has pending order
                if self.order.WaitStop:
                    print("Cancel old order first.")
                    self.order.stoporder_cancel()  # cancel old order first
                    time.sleep(3)
                contracts = self.order.calc_pos_size(abs(entry - stoploss))
                if self.order.Open:
                    print("New signal is bracket stop long, but one bot order is open... closing open order.", flush=True)
                    self.order.close()
                    time.sleep(3)
                if newsignal == 2:
                    if self.order.Qty < 0:
                        print("Canceling stop order in other direction.", flush=True)
                        self.order.stoporder_cancel()
                        time.sleep(3)
                    print("Open bracket stop order long. Contracts {} Entry {} Stoploss {}".format(contracts, entry, stoploss), flush=True)
                    self.order.bracket_stop_order(contracts, entry, stoploss)
                else:
                    if self.order.Qty > 0:
                        print("Canceling stop order in other direction.", flush=True)
                        self.order.stoporder_cancel()
                        time.sleep(3)
                    print("Open bracket stop order short. Contracts {} Entry {} Stoploss {}".format(abs(contracts), entry, stoploss), flush=True)
                    self.order.bracket_stop_order(-contracts, entry, stoploss)
            else:
                if self.order.Open:
                    self.order.close()

    def run(self):
        # Main loop
        self.order = BitmexOrder(self.client, self._settings_path, position_size=self._pos_size)
        self.process_signal(start=True)
        while True:
            time.sleep(10)
            self.order.manage_entries()
            if datetime.datetime.now().minute % 30 == 0:
                time.sleep(19 + self.rand_sec(start=3))
                self.process_signal()
                time.sleep(40)
