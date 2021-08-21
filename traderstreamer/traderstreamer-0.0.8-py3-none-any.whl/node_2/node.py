import os
from typing import List
from dotenv import load_dotenv
from tradernetwork import Node, ServiceTable

from node_2.memory import make_memory_index
from node_2.services import (
    BinanceSecondBarService,
    BinanceDataHandlerService,
    BinanceMarketStreamerService,
)

load_dotenv(override=True)

DOCKER = bool(int(os.getenv('DOCKER', 0)))

INFLUXDB_HOST = os.getenv('INFLUXDB_HOST')

INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')

INFLUXDB_TEST_TOKEN = os.getenv('INFLUXDB_TEST_TOKEN')
INFLUXDB_TEST_ORG = os.getenv('INFLUXDB_TEST_ORG')
INFLUXDB_TEST_BUCKET = os.getenv('INFLUXDB_TEST_BUCKET')


class Node_2:

    def __init__(self,
                 node_name: str = 'node-2',
                 node_tag: str = 'binance_node',
                 port_range: List[str] = list(range(11000, 11010)),
                 influxdb_host: str = INFLUXDB_HOST,
                 influxdb_token: str = INFLUXDB_TOKEN,
                 influxdb_org: str = INFLUXDB_ORG,
                 influxdb_bucket: str = INFLUXDB_BUCKET):

        if len(port_range) < 7:
            raise Exception('port range length should be at least 7')

        if DOCKER:
            host = 'host.docker.internal'
        else:
            host = 'localhost'

        self.symbol_list = ['spot.BTCUSDT', 'spot.ETHUSDT',
                            'usdt.BTCUSDT', 'usdt.ETHUSDT']

        services = {
            'binance-market-streamer-svc-1': {
                'service': BinanceMarketStreamerService,
                'params': {
                    'svc_name': 'binance-market-streamer-svc-1',
                    'svc_tag': 'binance_market_streamer_1',
                    'options': {'auto_restart': True},
                    'name': 'binance_market_1',
                    'market': 'spot',
                    'monitor_coins': ['BTCUSDT', 'ETHUSDT'],
                    'pub_port': port_range[0],
                    'influxdb_host': influxdb_host,
                    'influxdb_token': influxdb_token,
                    'influxdb_org': influxdb_org,
                    'influxdb_bucket': influxdb_bucket,
                    'verbose': False
                }
            },
            'binance-market-streamer-svc-2': {
                'service': BinanceMarketStreamerService,
                'params': {
                    'svc_name': 'binance-market-streamer-svc-2',
                    'svc_tag': 'binance_market_streamer_2',
                    'options': {'auto_restart': True},
                    'name': 'binance_market_2',
                    'market': 'usdt',
                    'monitor_coins': ['BTCUSDT', 'ETHUSDT'],
                    'pub_port': port_range[1],
                    'influxdb_host': influxdb_host,
                    'influxdb_token': influxdb_token,
                    'influxdb_org': influxdb_org,
                    'influxdb_bucket': influxdb_bucket,
                    'verbose': False
                }
            },
            'binance-second-bar-svc-1': {
                'service': BinanceSecondBarService,
                'params': {
                    'svc_name': 'binance-second-bar-svc-1',
                    'svc_tag': 'binance_second_bar_1',
                    'options': {'auto_restart': True},
                    'push_port': port_range[2],
                    'sub_host': host,
                    'sub_ports': {'bybit_market_1': port_range[0]},
                    'monitor_coins': ['spot.BTCUSDT', 'spot.ETHUSDT'],
                    'use_timestamp': 'local_timestamp',
                    'verbose': False
                }
            },
            'binance-second-bar-svc-2': {
                'service': BinanceSecondBarService,
                'params': {
                    'svc_name': 'binance-second-bar-svc-2',
                    'svc_tag': 'binance_second_bar_2',
                    'options': {'auto_restart': True},
                    'push_port': port_range[3],
                    'sub_host': host,
                    'sub_ports': {'bybit_market_1': port_range[1]},
                    'monitor_coins': ['usdt.BTCUSDT', 'usdt.ETHUSDT'],
                    'use_timestamp': 'local_timestamp',
                    'verbose': False
                }
            },
            'binance-data-handler-svc': {
                'service': BinanceDataHandlerService,
                'params': {
                    'svc_name': 'binance-data-handler-svc',
                    'svc_tag': 'binance_data_handler',
                    'options': {'auto_restart': True},
                    'memory': ['mem'],
                    'pub_port': port_range[4],
                    'sub_ports': {'binance_market_1': port_range[2],
                                  'binance_market_2': port_range[3]},
                    'monitor_coins': self.symbol_list
                }
            }
        }

        self.svc_table = ServiceTable(services)

        self.node = Node(node_name=node_name,
                         node_tag=node_tag,
                         port=6776,
                         service_table=self.svc_table)

    def _create_memory(self):
        memory_index = make_memory_index(self.symbol_list)
        self.node.create_memory('mem', memory_index)

    def start(self,
              rep_port: int = 2897,
              pub_port: int = 2898,
              mem_port: int = 2899,
              no_memory: bool = False):

        self.node.start(rep_port=rep_port,
                        pub_port=pub_port,
                        mem_port=mem_port)

        if not no_memory:
            self._create_memory()