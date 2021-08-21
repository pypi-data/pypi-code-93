import datetime
import traceback
import threading
import pandas as pd
from typing import List
from cointraderkr import BybitAPI
from multiprocessing import Queue
from tradernetwork import Service, PubSocket


class BybitBarStreamerService(Service):

    name = None
    market = None
    pub_port = None
    verbose = None
    public_key = None
    private_key = None
    monitor_coins = None

    api = None
    data = {}
    last_hour_time = None
    pub_socket = None
    q = Queue()

    def main(self,
             name: str,
             pub_port: int,
             public_key: str,
             private_key: str,
             monitor_coins: List[str] = ['BTCUSDT'],
             verbose: bool = True):

        self.name = name
        self.public_key = public_key
        self.private_key = private_key
        self.monitor_coins = monitor_coins
        self.verbose = verbose

        self.api = BybitAPI(self.public_key, self.private_key)

        def get_usdt_futures_data(api,
                                  symbol: str,
                                  interval: str,
                                  start_str: str = datetime.datetime.now().strftime('%Y%m%d')):

            interval = interval.replace('m', '')
            if len(start_str) == 8:
                from_timestamp = datetime.datetime.strptime(start_str, '%Y%m%d').timestamp()
            else:
                from_timestamp = datetime.datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S').timestamp()
            res = api.client.LinearKline.LinearKline_get(symbol=symbol,
                                                          interval=interval,
                                                          **{'from': from_timestamp})
            data = res.result()
            df = pd.DataFrame(data[0]['result'])
            df['start_at'] = df['start_at'].apply(lambda t: datetime.datetime.fromtimestamp(t))
            df['open_time'] = df['open_time'].apply(lambda t: datetime.datetime.fromtimestamp(t))
            return df

        self.api.get_usdt_futures_data = get_usdt_futures_data

        self.pub_socket = PubSocket(pub_port)

        self._request_loop()

        while True:
            data = self.q.get()
            self.pub_socket.publish(data)

            if self.verbose:
                print(data)

    def _request_loop(self):
        time_now = datetime.datetime.now()

        if self.last_hour_time is None:
            self._request_data()
        else:
            if len(set([d['data']['timestamp'] for _, d in self.data.items()])) != 1:
                self._request_data()

            if (time_now - self.last_hour_time).seconds >= 60:
                self._request_data()
            else:
                for symbol, data in self.data.items():
                    self.pub_socket.publish(data)

                if self.verbose:
                    print(f'[{time_now}] Sent data')

        timer = threading.Timer(1, self._request_loop)
        timer.setDaemon(True)
        timer.start()

    def _request_data(self):
        for symbol in self.monitor_coins:
            t = threading.Thread(target=self._request_hour_data, args=(symbol,))
            t.start()

    def _request_hour_data(self, symbol: str):
        try:
            # yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
            yesterday = (datetime.datetime.now() - datetime.timedelta(seconds=3600)).strftime('%Y-%m-%d %H:%M:%S')
            data = self.api.get_usdt_futures_data(self.api, symbol, '1m', yesterday)
            data['timestamp'] = data['start_at'].shift(-1)
            data = data[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            data = data[data['timestamp'].notna()]
            curr_data: dict = data.iloc[-1].to_dict()
            self.last_hour_time = curr_data['timestamp']
            curr_data['timestamp'] = curr_data['timestamp'].strftime('%Y%m%d%H%M%S')
            curr_data = {
                'source': 'bybit',
                'symbol': f'usdt.{symbol}',
                'data': curr_data
            }
            self.data[symbol] = curr_data
            self.q.put(curr_data)
        except:
            traceback.print_exc()


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv(override=True)

    bybit_public_key = os.getenv('BYBIT_PUBLIC_KEY')
    bybit_private_key = os.getenv('BYBIT_PRIVATE_KEY')

    svc = BybitBarStreamerService('bybit-bar-streamer-svc',
                                  'bybit_bar_streamer',
                                  options={'auto_restart': True},
                                  name='bybit-bar-streamer',
                                  pub_port=1000,
                                  public_key=bybit_public_key,
                                  private_key=bybit_private_key,
                                  monitor_coins=['BTCUSDT', 'ETHUSDT', 'XRPUSDT'])
    svc.start()