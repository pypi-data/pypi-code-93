import os
import datetime
import threading
from dotenv import load_dotenv
from tradernetwork import SubSocket, ProxySocket

from scripts.services import *

load_dotenv(override=True)

DOCKER = bool(int(os.getenv('DOCKER', 0)))

if DOCKER:
    host = 'host.docker.internal'
else:
    host = 'localhost'


class OddStreamerNode:

    streaming = False

    svc1 = bybit_mkt_svc
    svc2 = binance_mkt_svc_1
    svc3 = binance_mkt_svc_2
    svc4 = bybit_sec_svc
    svc5 = binance_sec_svc

    def __init__(self):
        self.data = {'bybit': self._time(), 'binance': self._time()}

        self.proxy = ProxySocket({
            'bybit': SubSocket(803, host),
            'binance': SubSocket(804, host)
        })
        self.proxy.callback = self._proxy_callback

        t = threading.Thread(target=self._start_proxy_server)
        t.start()

        self._monitor()

    def start(self):
        self.streaming = True

        self.svc1.start()
        self.svc2.start()
        self.svc3.start()
        self.svc4.start()
        self.svc5.start()

    def stop(self):
        self.streaming = False

        self.svc1.stop()
        self.svc2.stop()
        self.svc3.stop()
        self.svc4.stop()
        self.svc5.stop()

    def _time(self):
        return datetime.datetime.now()

    def _proxy_callback(self, socket_name: str, data: dict):
        self.data[socket_name] = self._time()

    def _start_proxy_server(self):
        self.proxy.start_proxy_server_loop()

    def _monitor(self):
        time_now = self._time()

        five_mins_after = (time_now + datetime.timedelta(minutes=5)).hour

        if five_mins_after == 0:
            five_mins_after = 24

        if not self.streaming and five_mins_after % 2 != 0:
            print(f'[{time_now}] Streaming start')
            self.start()

        if self.streaming and time_now.hour % 2 == 0 and not (five_mins_after % 2 != 0):
            print(f'[{time_now}] Streaming stop')
            self.stop()

        for exchange, data_time in self.data.items():
            if self.streaming and (time_now - data_time).seconds > 5:
                # raise Exception(f'[{exchange}] Data stopped streaming for more than 5 seconds')
                print(f'[{exchange}] DATA STREAMING STOPPED')

        timer = threading.Timer(1, self._monitor)
        timer.setDaemon(True)
        timer.start()


if __name__ == '__main__':
    odd_node = OddStreamerNode()
    odd_node.start()