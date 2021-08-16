
from typing import List, Dict

from ...util.singleton import Singleton
from ...data.api.raw import RawDataApi


class Universe(metaclass=Singleton):
    def __init__(self):
        self._stock_list: Dict[str, List[str]] = {}

    def get(self, name: str) -> Dict[str, List[str]]:
        try:
            return self._stock_list[name]
        except KeyError:
            return self._load_data(name)

    def _load_data(self, name: str) -> List[str]:
        df = RawDataApi().get_em_index_component(index_list=[name])
        if df is None or df.empty:
            return
        stock_list = df.set_index('datetime').stock_list.sort_index().array[-1]
        self._stock_list[name] = stock_list.split(',')
        return self._stock_list[name]
