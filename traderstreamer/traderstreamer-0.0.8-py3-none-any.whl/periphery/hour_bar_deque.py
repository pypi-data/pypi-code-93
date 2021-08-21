import threading
import pandas as pd
from collections import deque
from tradernetwork import SubSocket, ProxySocket


class HourBarDeque:

    df = {}
    raw_data = {}
    data = {}
    received_dates = {}

    def __init__(self,
                 sub_host: str = 'localhost',
                 sub_port: int = 1000,
                 maxlen: int = 200):

        self.maxlen = maxlen

        self.sockets = {
            'bybit_hr_streamer': SubSocket(sub_port, sub_host)
        }

        self._start_proxy()

    def _start_proxy(self):
        self.proxy = ProxySocket(self.sockets)
        self.proxy.callback = self.callback

        t = threading.Thread(target=self.proxy.start_proxy_server_loop)
        t.start()

    def _format_df(self, df: pd.DataFrame):
        df.index = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M%S')
        df.drop('timestamp', axis=1, inplace=True)
        return df

    def _update_bar(self, symbol: str, data: dict):
        if symbol not in self.raw_data:
            self.raw_data[symbol] = deque([], maxlen=self.maxlen)

        self.raw_data[symbol].append(data['data'])
        self.df[symbol] = self._format_df(pd.DataFrame(self.raw_data[symbol]))

        if len(set([d[-1]['timestamp'] for _, d in self.raw_data.items()])) == 1:
            close_data = {}
            volume_data = {}
            for symbol, raw_data in self.raw_data.items():
                if 'timestamp' not in close_data:
                    close_data['timestamp'] = [d['timestamp'] for d in self.raw_data[symbol]]
                if 'timestamp' not in volume_data:
                    volume_data['timestamp'] = [d['timestamp'] for d in self.raw_data[symbol]]
                close_data[symbol] = [d['close'] for d in self.raw_data[symbol]]
                volume_data[symbol] = [d['volume'] for d in self.raw_data[symbol]]

            close_df = pd.DataFrame(close_data)
            volume_df = pd.DataFrame(volume_data)

            self.data['close'] = self._format_df(close_df)
            self.data['volume'] = self._format_df(volume_df)

    def callback(self, socket_name: str, data: dict):
        symbol = data['symbol']
        timestamp = data['data']['timestamp']

        if symbol not in self.received_dates:
            self.received_dates[symbol] = deque([], maxlen=24)

        if timestamp not in self.received_dates[symbol]:
            self.received_dates[symbol].append(timestamp)
            self._update_bar(symbol, data)


if __name__ == '__main__':
    import time

    dq = HourBarDeque(sub_port=1001)

    time.sleep(5)

    print(dq.data['close'])


