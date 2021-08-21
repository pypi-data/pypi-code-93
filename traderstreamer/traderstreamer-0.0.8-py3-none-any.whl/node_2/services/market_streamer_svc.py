import os
import datetime
import threading
import traceback
from collections import deque
from dotenv import load_dotenv
from multiprocessing import Queue
from typing import Any, Dict, List

from tradernetwork import Service, PubSocket
from cointraderkr import MetricCollector, BinanceWebsocket

load_dotenv(override=True)

INFLUXDB_HOST = os.getenv('INFLUXDB_HOST')

INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')

INFLUXDB_TEST_TOKEN = os.getenv('INFLUXDB_TEST_TOKEN')
INFLUXDB_TEST_ORG = os.getenv('INFLUXDB_TEST_ORG')
INFLUXDB_TEST_BUCKET = os.getenv('INFLUXDB_TEST_BUCKET')

class MockMetricCollector:

    def send_metrics(self, data: List[Dict[str, Any]]):
        pass


class BinanceMarketStreamerService(Service):

    name = None
    market = None
    pub_port = None
    monitor_coins = None
    verbose = None

    metric_collector = None
    pub_socket = None
    q = Queue()
    latency = deque([], maxlen=100)
    data_cnt = 0
    streaming = False

    def main(self,
             name: str,
             market: str,
             monitor_coins: List[str],
             pub_port: int,
             influxdb_host: str = INFLUXDB_HOST,
             influxdb_token: str = INFLUXDB_TOKEN,
             influxdb_org: str = INFLUXDB_ORG,
             influxdb_bucket: str = INFLUXDB_BUCKET,
             verbose: bool = True):

        try:
            self.metric_collector = MetricCollector(host=influxdb_host,
                                                    token=influxdb_token,
                                                    org=influxdb_org,
                                                    bucket=influxdb_bucket)
        except:
            traceback.print_exc()
            self.metric_collector = MockMetricCollector()

        self.streaming = True
        self.name = name
        self.market = market
        self.pub_port = pub_port
        self.monitor_coins = monitor_coins
        self.verbose = verbose

        if self.pub_socket is None:
            self.pub_socket = PubSocket(pub_port)

        if market == 'spot':
            self._start_spot_socket()
        elif market == 'usdt':
            self._start_usdt_socket()
        elif market == 'coinm':
            self._start_coinm_socket()

        self._healthcheck_loop()

        while True:
            message = self.q.get()

            if message['type'] == 'data':
                data = message['data']
                self.data_cnt += 1
                latency = data.get('latency')
                if latency is not None:
                    if latency >= 0:
                        self.latency.append(latency)
                    else:
                        self.latency.append(0)
                self.pub_socket.publish(data)

            elif message['type'] == 'stop':
                if self.market == 'spot':
                    self.spot_api.close()
                    del self.spot_api

                elif self.market == 'usdt':
                    self.usdt_api.close()
                    del self.usdt_api

                elif self.market == 'coinm':
                    self.coinm_api.close()
                    del self.coinm_api

                if self.pub_socket is not None:
                    self.pub_socket.exit()
                    del self.pub_socket
                    self.pub_socket = None

                break

    def _stop(self):
        self.q.put({'type': 'stop'})
        self.stop()
        self.streaming = False

    def _start_spot_socket(self):
        try:
            self.spot_api = BinanceWebsocket(callback=self.callback, monitor_coins=self.monitor_coins)
            self.spot_api.stream_spot_exchange_data()
            self.spot_api.start()
        except:
            traceback.print_exc()

    def _start_usdt_socket(self):
        try:
            self.usdt_api = BinanceWebsocket(callback=self.callback, monitor_coins=self.monitor_coins)
            self.usdt_api.stream_futures_exchange_data()
            self.usdt_api.start()
        except:
            traceback.print_exc()

    def _start_coinm_socket(self):
        try:
            self.coinm_api = BinanceWebsocket(callback=self.callback, monitor_coins=self.monitor_coins)
            self.coinm_api.stream_coinm_futures_exchange_data()
            self.coinm_api.start()
        except:
            traceback.print_exc()

    def callback(self, data: dict):
        self.q.put({'type': 'data', 'data': data})

    def _healthcheck_loop(self):
        if self.streaming:
            if len(self.latency) != 0:
                avg_latency = sum(self.latency) / len(self.latency)
            else:
                avg_latency = 0

            avg_data_cnt = self.data_cnt / 5 # 5초에 한번 연산하기 때문에 5로 나눠주기
            self.data_cnt = 0

            time_now = datetime.datetime.now()

            if self.verbose:
                print(f'[{time_now}] Binance market data streamer running: tcp://*:{self.pub_port}, Data Count: {avg_data_cnt}, Latency: {avg_latency}')

            points = [{
                'measurement': 'monitor_metrics',
                'field': 'latency',
                'value': float(avg_latency),
                'exchange': 'binance',
                'market': self.market,
                'name': self.name
            }, {
                'measurement': 'monitor_metrics',
                'field': 'data_cnt',
                'value': float(avg_data_cnt),
                'exchange': 'binance',
                'market': self.market,
                'name': self.name
            }]
            self.metric_collector.send_metrics(points)

            timer = threading.Timer(5, self._healthcheck_loop)
            timer.setDaemon(True)
            timer.start()


if __name__ == '__main__':
    svc = BinanceMarketStreamerService('binance-market-streamer-svc',
                                       'binance_market_streamer',
                                       options={'auto_restart': True},
                                       name='test_binance_streamer',
                                       market='spot',
                                       monitor_coins=['BTCUSDT', 'ETHUSDT'],
                                       pub_port=777)
    svc.start()