import pandas as pd
import numpy as np
from cointraderkr import bybit_tickers

SECOND_TABLE = {
    date: i for i, date in
    enumerate([d.strftime('%H%M%S') for d in pd.date_range('00:00:00', '23:59:59', freq='S')])
}

SYMBOL_TABLE = {
    f'usdt.{symbol}': i for i, symbol in enumerate(bybit_tickers)
}
SYMBOL_TABLE['coinm.BTCUSD'] = len(bybit_tickers)

FIELD_LIST = [
    'timestamp',         # shared_memory에 데이터가 들어가는 시간
    'local_timestamp',   # 데이터가 컴퓨터로 도달한 시간 (소켓으로 스트리밍하기 전)
    'server_timestamp',  # 서버에서 데이터를 보낸 시간
    'latency',           # server_timestamp - local_timestamp
    'current_price',     # 체결
    'open',
    'high',
    'low',
    'close',
    'volume',
    'tick_cnt',
    'buy_cnt',
    'buy_amt',
    'sell_cnt',
    'sell_amt'
]
FIELD_LIST.extend([f'sell_hoga{i}' for i in range(1, 26)])
FIELD_LIST.extend([f'sell_hoga{i}_stack' for i in range(1, 26)])
FIELD_LIST.extend([f'buy_hoga{i}' for i in range(1, 26)])
FIELD_LIST.extend([f'buy_hoga{i}_stack' for i in range(1, 26)])

FIELD_TABLE = {field: i for i, field in enumerate(FIELD_LIST)}


MEMORY_INDEX = {
    'second': SECOND_TABLE,
    'symbol': SYMBOL_TABLE,
    'field': FIELD_TABLE
}

def make_mock_memory_array():
    shape = (len(SECOND_TABLE), len(SYMBOL_TABLE), len(FIELD_TABLE))
    array = np.zeros(shape)
    array.fill(np.nan)
    print(f'Creating mock memory array with shape: {shape}')
    return array


if __name__ == '__main__':
    print(SECOND_TABLE)
    print(SYMBOL_TABLE)
    print(FIELD_TABLE)

    array = make_mock_memory_array()
    print(array)