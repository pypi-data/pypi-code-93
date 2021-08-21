import os
from typing import List
from dotenv import load_dotenv
from tradernetwork import Node, ServiceTable

from node_1.memory import MEMORY_INDEX, SYMBOL_TABLE
from node_1.services import (
    BybitSecondBarService,
    BybitDataHandlerService,
    BybitMarketStreamerService,
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

coin_list = list(SYMBOL_TABLE.keys())
usdt_coin_list = [coin.replace('usdt.', '') for coin in coin_list if coin.split('.')[0] == 'usdt']

LIST_1 = ['BTCUSD', 'BTCUSDT']
LIST_2 = ['ETHUSDT', 'XRPUSDT', 'ADAUSDT', 'BNBUSDT', 'DOGEUSDT', 'DOTUSDT']
LIST_3 = [coin for coin in usdt_coin_list if coin not in LIST_1 and coin not in LIST_2]

coin_table = [
    {'market': 'both', 'monitor_coins': LIST_1},
    {'market': 'usdt', 'monitor_coins': LIST_2},
    {'market': 'usdt', 'monitor_coins': LIST_3}
]


class Node_1:

    def __init__(self,
                 node_name: str = 'node-1',
                 node_tag: str = 'bybit_node',
                 port_range: List[int] = list(range(10000, 10010)),
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

        services = {
            'bybit-market-streamer-svc-1': {
                'service': BybitMarketStreamerService,
                'params': {
                    'svc_name': 'bybit-market-streamer-svc-1',
                    'svc_tag': 'bybit_market_streamer_1',
                    'options': {'auto_restart': True},
                    'name': 'bybit_market_1',
                    **coin_table[0],
                    'pub_port': port_range[0],
                    'influxdb_host': influxdb_host,
                    'influxdb_token': influxdb_token,
                    'influxdb_org': influxdb_org,
                    'influxdb_bucket': influxdb_bucket,
                    'verbose': False
                }
            },
            'bybit-market-streamer-svc-2': {
                'service': BybitMarketStreamerService,
                'params': {
                    'svc_name': 'bybit-market-streamer-svc-2',
                    'svc_tag': 'bybit_market_streamer_2',
                    'options': {'auto_restart': True},
                    'name': 'bybit_market_2',
                    **coin_table[1],
                    'pub_port': port_range[1],
                    'influxdb_host': influxdb_host,
                    'influxdb_token': influxdb_token,
                    'influxdb_org': influxdb_org,
                    'influxdb_bucket': influxdb_bucket,
                    'verbose': False
                }
            },
            'bybit-market-streamer-svc-3': {
                'service': BybitMarketStreamerService,
                'params': {
                    'svc_name': 'bybit-market-streamer-svc-3',
                    'svc_tag': 'bybit_market_streamer_3',
                    'options': {'auto_restart': True},
                    'name': 'bybit_market_3',
                    **coin_table[2],
                    'pub_port': port_range[2],
                    'influxdb_host': influxdb_host,
                    'influxdb_token': influxdb_token,
                    'influxdb_org': influxdb_org,
                    'influxdb_bucket': influxdb_bucket,
                    'verbose': False
                }
            },
            'bybit-second-bar-svc-1': {
                'service': BybitSecondBarService,
                'params': {
                    'svc_name': 'bybit-second-bar-svc-1',
                    'svc_tag': 'bybit_second_bar_1',
                    'options': {'auto_restart': True},
                    'push_port': port_range[3],
                    'sub_host': host,
                    'sub_ports': {'bybit_market_1': port_range[0]},
                    'monitor_coins': ['coinm.BTCUSD', 'usdt.BTCUSDT'],
                    'use_timestamp': 'local_timestamp',
                    'verbose': False
                }
            },
            'bybit-second-bar-svc-2': {
                'service': BybitSecondBarService,
                'params': {
                    'svc_name': 'bybit-second-bar-svc-2',
                    'svc_tag': 'bybit_second_bar_2',
                    'options': {'auto_restart': True},
                    'push_port': port_range[4],
                    'sub_host': host,
                    'sub_ports': {'bybit_market_2': port_range[1]},
                    'monitor_coins': [f'usdt.{coin}' for coin in LIST_2],
                    'use_timestamp': 'local_timestamp',
                    'verbose': False
                }
            },
            'bybit-second-bar-svc-3': {
                'service': BybitSecondBarService,
                'params': {
                    'svc_name': 'bybit-second-bar-svc-3',
                    'svc_tag': 'bybit_second_bar_3',
                    'options': {'auto_restart': True},
                    'push_port': port_range[5],
                    'sub_host': host,
                    'sub_ports': {'bybit_market_3': port_range[2]},
                    'monitor_coins': [f'usdt.{coin}' for coin in LIST_3],
                    'use_timestamp': 'local_timestamp',
                    'verbose': False
                }
            },
            'bybit-data-handler-svc': {
                'service': BybitDataHandlerService,
                'params': {
                    'svc_name': 'bybit-data-handler-svc',
                    'svc_tag': 'bybit_data_handler',
                    'options': {'auto_restart': True},
                    'memory': ['mem'],
                    'pub_port': port_range[6],
                    'sub_ports': {'bybit_market_1': port_range[3],
                                  'bybit_market_2': port_range[4],
                                  'bybit_market_3': port_range[5]}
                }
            }
        }

        self.svc_table = ServiceTable(services)

        self.node = Node(node_name=node_name,
                         node_tag=node_tag,
                         port=6776,
                         service_table=self.svc_table)

    def _create_memory(self):
        self.node.create_memory('mem', MEMORY_INDEX)

    def start(self,
              rep_port: int = 2997,
              pub_port: int = 2998,
              mem_port: int = 2999,
              no_memory: bool = False):

        self.node.start(rep_port=rep_port,
                        pub_port=pub_port,
                        mem_port=mem_port)

        if not no_memory:
            self._create_memory()

