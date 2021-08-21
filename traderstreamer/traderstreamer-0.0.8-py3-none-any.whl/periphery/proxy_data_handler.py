import os
from dotenv import load_dotenv

from tradernetwork import SubSocket, ProxySocket

load_dotenv(override=True)

SERVER_1_HOST = os.getenv('SERVER_1_HOST')
SERVER_2_HOST = os.getenv('SERVER_2_HOST')


class ProxyDataHandler:

    def __init__(self,
                 odd_node_host: str = SERVER_1_HOST,
                 even_node_host: str = SERVER_2_HOST):

        sockets = {
            # 'odd_bybit': SubSocket(803, odd_node_host),
            # 'odd_binance': SubSocket(804, odd_node_host),
            'even_bybit': SubSocket(803, even_node_host),
            'even_binance': SubSocket(804, even_node_host)
        }

        self.proxy = ProxySocket(sockets)
        self.proxy.callback = self.callback

    def callback(self, socket_name: str, data: dict):
        print(socket_name, data)

    def start(self):
        self.proxy.start_proxy_server_loop()


if __name__ == '__main__':
    p = ProxyDataHandler()
    p.start()