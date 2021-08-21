import numpy as np
import pandas as pd
from typing import List
from cointraderkr import MONITOR_COINS

SECOND_TABLE = {
    date: i for i, date in
    enumerate([d.strftime('%H%M%S') for d in pd.date_range('00:00:00', '23:59:59', freq='S')])
}

SYMBOL_LIST = [f'spot.{symbol}' for symbol in MONITOR_COINS]
SYMBOL_LIST += [f'usdt.{symbol}' for symbol in MONITOR_COINS]
SYMBOL_LIST += ['coinm.BTCUSD']
SYMBOL_TABLE = {
    symbol: i for i, symbol in enumerate(SYMBOL_LIST)
}

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

def make_memory_index(monitor_coins: List[str]):
    symbol_table = {
        symbol: i for i, symbol in enumerate(monitor_coins)
    }
    return {
        'second': SECOND_TABLE,
        'symbol': symbol_table,
        'field': FIELD_TABLE
    }

def make_mock_memory_array(second_table: dict = SECOND_TABLE,
                           symbol_table: dict = SYMBOL_TABLE,
                           field_table: dict = FIELD_TABLE):

    shape = (len(second_table), len(symbol_table), len(field_table))
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