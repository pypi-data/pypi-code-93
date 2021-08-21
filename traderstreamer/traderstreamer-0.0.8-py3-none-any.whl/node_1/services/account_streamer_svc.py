import os
import datetime
import threading
from typing import List
from multiprocessing import Queue

from cointraderkr import BybitWebsocket
from tradernetwork import Service, PubSocket


class BybitAccountStreamerService(Service):

    name = None
    market = None
    pub_port = None
    verbose = None
    public_key = None
    private_key = None

    pub_socket = None
    usdt_socket = None
    coinm_socket = None
    q = Queue()

    def main(self,
             name: str,
             market: str,
             pub_port: int,
             public_key: str,
             private_key: str,
             monitor_coins: List[str] = [],
             verbose: bool = True):

        self.public_key = public_key
        self.private_key = private_key
        self.monitor_coins = monitor_coins

        self.name = name
        self.market = market
        self.pub_port = pub_port
        self.verbose = verbose

        self.ping_status = None

        if market == 'usdt':
            self._start_usdt_socket()

        if market == 'coinm':
            self._start_coinm_socket()

        if self.ping_status:
            self._ping_loop()
            self._healthcheck_loop()

            self.pub_socket = PubSocket(pub_port)

            while True:
                data = self.q.get()

                req_op = data.get('request', {}).get('op', '')

                if req_op in ['auth', 'subscribe']:
                    pass

                elif req_op == 'ping':
                    self.ping_status = self._time()

                else:
                    self.pub_socket.publish(data)

    def _time(self):
        return datetime.datetime.now()

    def _start_usdt_socket(self):
        url = 'wss://stream.bytick.com/realtime_private'
        self.usdt_socket = BybitWebsocket(url,
                                          self.public_key,
                                          self.private_key,
                                          self.callback)

        self.ping_status = self._time()

        self.usdt_socket.subscribe_position()
        self.usdt_socket.subscribe_execution()
        self.usdt_socket.subscribe_order()
        self.usdt_socket.subscribe_stop_order()
        self.usdt_socket.subscribe_wallet()

    def _start_coinm_socket(self):
        url = 'wss://stream.bytick.com/realtime'
        self.coinm_socket = BybitWebsocket(url,
                                           self.public_key,
                                           self.private_key,
                                           self.callback)

        self.ping_status = self._time()

        self.coinm_socket.subscribe_position()
        self.coinm_socket.subscribe_execution()
        self.coinm_socket.subscribe_order()
        self.coinm_socket.subscribe_stop_order()
        self.coinm_socket.subscribe_wallet()

    def callback(self, data: dict):
        self.q.put(data)

    def _ping_loop(self):
        for socket in [self.usdt_socket, self.coinm_socket]:
            if socket is not None:
                socket.ping()

        timer = threading.Timer(5, self._ping_loop)
        timer.setDaemon(True)
        timer.start()

    def _healthcheck_loop(self):
        time_now = self._time()

        if (self.pub_socket is not None) and (self.ping_status is not None):
            if (time_now - self.ping_status).seconds >= 10:
                self.pub_socket.publish({'source': 'bybit',
                                         'asset_type': self.market,
                                         'type': 'socket_status',
                                         'status': 'OFF'})
            else:
                self.pub_socket.publish({'source': 'bybit',
                                         'asset_type': self.market,
                                         'type': 'socket_status',
                                         'status': 'ON'})

        timer = threading.Timer(1, self._healthcheck_loop)
        timer.setDaemon(True)
        timer.start()


if __name__ == '__main__':
    bybit_public_key = os.getenv('BYBIT_PUBLIC_KEY')
    bybit_private_key = os.getenv('BYBIT_PRIVATE_KEY')

    svc = BybitAccountStreamerService('bybit-account-streamer-svc',
                                      'bybit_account_streamer',
                                      options={'auto_restart': True},
                                      name='test_bybit_streamer',
                                      market='usdt',
                                      pub_port=888,
                                      public_key=bybit_public_key,
                                      private_key=bybit_private_key)
    svc.start()