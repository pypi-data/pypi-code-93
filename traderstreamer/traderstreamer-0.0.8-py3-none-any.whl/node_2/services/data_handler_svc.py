import datetime
import traceback
from typing import Dict, List
from tradernetwork import (
    Service,
    PubSocket,
    SubSocket,
    ProxySocket,
)

from node_2.memory import (
    MEMORY_INDEX,
    make_memory_index,
    make_mock_memory_array,
)


class BinanceDataHandlerService(Service):

    latest_time = datetime.datetime.now()

    def main(self,
             pub_port: int,
             sub_ports: Dict[str, int],
             monitor_coins: List[str] = []):

        if monitor_coins:
            self.index_table = make_memory_index(monitor_coins)
        else:
            self.index_table = MEMORY_INDEX

        self._memory_setup()

        self.pub_socket = PubSocket(pub_port)

        sub_sockets = {name: SubSocket(port) for name, port in sub_ports.items()}
        proxy_socket = ProxySocket(sub_sockets)
        proxy_socket.callback = self.callback
        proxy_socket.start_proxy_server_loop()

    def _memory_setup(self):
        """
        테스트를 진행할 때는 Node에서 memory를 꽂아줄 수 없기 때문에 mock memory를 생성한다.
        """
        if self.mem == {}:
            self.mem['mem'] = make_mock_memory_array(self.index_table['second'],
                                                     self.index_table['symbol'],
                                                     self.index_table['field'])

        self.memory = self.mem['mem']

    def callback(self, socket_name: str, data: dict):
        try:
            self.update_memory(data['symbol'], data['data'])
        except:
            traceback.print_exc()
            print(f'[{socket_name}] Error with data: {data}')

    def update_memory(self, symbol: str, data: dict):
        data_time = datetime.datetime.strptime(data['timestamp'], '%Y%m%d%H%M%S%f')
        timestamp_str = data_time.strftime('%H%M%S')

        time_passed = (data_time - self.latest_time).seconds

        second_idx = self.index_table['second'][timestamp_str]
        symbol_idx = self.index_table['symbol'][symbol]

        data['timestamp'] = float(data['timestamp'])
        data['local_timestamp'] = float(data['local_timestamp'])
        data['server_timestamp'] = float(data['server_timestamp'])
        self.memory[second_idx, symbol_idx, :] = list(data.values())

        if time_passed >= 1:
            self.latest_time = data_time
            self.pub_socket.publish({'event': 'second'})


if __name__ == '__main__':
    svc = BinanceDataHandlerService('binance-data-handler-svc',
                                    'binance',
                                    options={'auto_restart': True},
                                    memory=['mem'],
                                    pub_port=1000,
                                    sub_ports={'binance_1': 999},
                                    monitor_coins=['spot.BTCUSDT', 'spot.ETHUSDT'])
    svc.start()