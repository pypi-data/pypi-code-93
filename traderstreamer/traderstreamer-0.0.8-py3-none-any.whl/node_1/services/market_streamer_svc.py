import os
import datetime
import traceback
import threading
from collections import deque
from dotenv import load_dotenv
from multiprocessing import Queue
from typing import Any, Dict, List

from tradernetwork import Service, PubSocket
from cointraderkr import BybitWebsocket, MetricCollector

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


class BybitMarketStreamerService(Service):

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

        if market == 'usdt':
            self._start_usdt_socket()
        elif market == 'coinm':
            self._start_coinm_socket()
        else:
            self._start_usdt_socket()
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
                if market == 'usdt':
                    self.usdt_socket.exit()
                    del self.usdt_socket

                elif market == 'coinm':
                    self.coinm_socket.exit()
                    del self.coinm_socket

                else:
                    self.usdt_socket.exit()
                    self.coinm_socket.exit()
                    del self.usdt_socket
                    del self.coinm_socket

                if self.pub_socket is not None:
                    self.pub_socket.exit()
                    del self.pub_socket
                    self.pub_socket = None

                break

    def _stop(self):
        self.q.put({'type': 'stop'})
        self.stop()
        self.streaming = False

    def _start_usdt_socket(self):
        url = 'wss://stream.bytick.com/realtime_public'
        self.usdt_socket = BybitWebsocket(url,
                                          None,
                                          None,
                                          self.callback)

        for coin in self.monitor_coins:
            if coin.upper()[-4:] == 'USDT':
                print(f'USDT symbol: {coin}')
                self.usdt_socket.subscribe_trade(coin)
                self.usdt_socket.subscribe_orderBookL2(coin)

    def _start_coinm_socket(self):
        url = 'wss://stream.bybit.com/realtime'
        self.coinm_socket = BybitWebsocket(url,
                                           None,
                                           None,
                                           self.callback)

        for coin in self.monitor_coins:
            if coin.upper()[-3:] == 'USD':
                print(f'Coinm symbol: {coin}')
                self.coinm_socket.subscribe_trade(coin)
                self.coinm_socket.subscribe_orderBookL2(coin)

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
                print(f'[{time_now}] Bybit market data streamer running: tcp://*:{self.pub_port}, Data Count: {avg_data_cnt}, Latency: {avg_latency}')

            points = [{
                'measurement': 'monitor_metrics',
                'field': 'latency',
                'value': float(avg_latency),
                'exchange': 'bybit',
                'market': self.market,
                'name': self.name
            }, {
                'measurement': 'monitor_metrics',
                'field': 'data_cnt',
                'value': float(avg_data_cnt),
                'exchange': 'bybit',
                'market': self.market,
                'name': self.name
            }]
            self.metric_collector.send_metrics(points)

            timer = threading.Timer(5, self._healthcheck_loop)
            timer.setDaemon(True)
            timer.start()


if __name__ == '__main__':
    svc = BybitMarketStreamerService('bybit-market-streamer-svc',
                                     'bybit_market_streamer',
                                     options={'auto_restart': True},
                                     name='test_bybit_streamer',
                                     market='both',
                                     monitor_coins=['BTCUSD', 'BTCUSDT'],
                                     pub_port=888)
    svc.start()

    # from tradernetwork import SubSocket
    #
    # sub = SubSocket(888)
    #
    # while True:
    #     data = sub._recv()