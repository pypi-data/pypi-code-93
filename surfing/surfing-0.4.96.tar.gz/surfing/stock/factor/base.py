
from typing import Optional, Set, Union
# from functools import lru_cache
import pandas as pd
import time
from ...constant import FundFactorType, StockFactorType
from ...util.singleton import Singleton
from .calculator import Calculator
from .universe import Universe

_STOCK_BUCKET_NAME = 'tl-factors'
_FUND_BUCKET_NAME = 'tl-fund-factors'


class Factor(metaclass=Singleton):


    def __init__(self, f_name: str, f_type: Union[StockFactorType, FundFactorType], f_level: str = 'basic'):
        self._f_name: str = f_name
        self._s3_file_name: str = f'{f_name}.parquet'
        self._f_level = f_level
        if isinstance(f_type, StockFactorType):
            self._s3_uri: str = f's3://{_STOCK_BUCKET_NAME}/factor/'
            self._s3_uri_factor_ret: str = f's3://{_STOCK_BUCKET_NAME}/factor_ret/'
        elif isinstance(f_type, FundFactorType):
            self._s3_uri = f's3://{_FUND_BUCKET_NAME}/{self._f_level}/'
            self._s3_uri_factor_ret = None
        else:
            assert False, f'invalid factor type {f_type}'
        self._f_type: Union[StockFactorType, FundFactorType] = f_type
        self._factor: Optional[pd.DataFrame] = None
        self._deps: Set[Factor] = set()

    # @lru_cache
    def get(self, universe: str = 'default') -> Optional[pd.DataFrame]:
        # 这里我们认为没有必要去存储各个universe下的因子值
        # 因为只要全量(default)的因子值保存了，使用stock_list去过滤出相应universe下的因子值会非常快
        if self._factor is None:
            self._load_data()
        if universe != 'default':
            stock_list = Universe().get(universe)
            if stock_list is not None:
                return self._factor.loc[:, stock_list]
            print(f'get data of universe {universe} failed, use default universe')
        return self._factor

    # delete
    def clear(self, recursive=False):
        if recursive:
            for _dep in self._deps:
                _dep.clear(recursive)
        self._factor = None

    def get_normalized(self, universe: str = 'default'):
        data = self.get(universe)
        return ((data.T - data.mean(axis=1))/data.std(axis=1)).T

    @property
    def name(self):
        return self._f_name

    @property
    def f_type(self):
        return self._f_type

    def save(self) -> bool:
        if self._factor is None:
            return False
        self._factor.to_parquet(self._get_s3_factor_uri, compression='gzip')
        print(f'\t[upload] to s3 success {self._f_name} {self._get_s3_factor_uri}')
        return True

    def calc(self):
        assert False, f'should impl specialized calc algo for the {self._f_name} factor'

    def _load_data(self) -> Optional[pd.DataFrame]:
        try:
            t0 = time.time()
            self._factor: pd.DataFrame = pd.read_parquet(self._get_s3_factor_uri)
            t1 = time.time()
            print(f'\t[time][{self._f_level}] fetch factor: {self._f_name} from s3 cost {round(t1 - t0, 4)}')
        except Exception as e:
            print(f'retrieve data from s3 failed, (err_msg){e}; try to re-calc {self._f_name}')
            self.calc()
        return self._factor

    @property
    def _get_s3_factor_uri(self) -> str:
        return f'{self._s3_uri}{self._s3_file_name}'

    def _get_s3_factor_uri_with_universe(self, universe: str) -> str:
        return f'{self._s3_uri}with_universe/{universe}/{self._s3_file_name}'

    def _get_s3_factor_ret_uri(self, universe: str) -> str:
        return f'{self._s3_uri_factor_ret}{universe}/{self._s3_file_name}'
