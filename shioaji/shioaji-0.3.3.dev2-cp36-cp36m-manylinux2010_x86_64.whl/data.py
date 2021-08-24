import typing
from collections import abc

from pydantic import validator
from shioaji.base import BaseModel
from shioaji.constant import ChangeType, TickType, Exchange


class BaseMapping(BaseModel, abc.Mapping):
    def __len__(self):
        return len(self.__values__)

    def __getitem__(self, name):
        return getattr(self, name)


class Ticks(BaseModel):
    ts: typing.List[int]
    close: typing.List[float]
    volume: typing.List[int]
    bid_price: typing.List[float]
    bid_volume: typing.List[int]
    ask_price: typing.List[float]
    ask_volume: typing.List[int]

    def lazy_setter(self, **kwargs):
        [
            setattr(self, kwarg, value)
            for kwarg, value in kwargs.items()
            if hasattr(self, kwarg)
        ]


class Snapshot(BaseMapping):
    ts: int
    code: str
    exchange: str
    open: float
    high: float
    low: float
    close: float
    tick_type: TickType
    change_price: float
    change_rate: float
    change_type: ChangeType
    average_price: float
    volume: int
    total_volume: int
    amount: int
    total_amount: int
    yesterday_volume: float
    buy_price: float
    buy_volume: float
    sell_price: float
    sell_volume: int
    volume_ratio: float


class CreditEnquire(BaseMapping):
    update_time: str = ""
    system: str = ""
    stock_id: str = ""
    margin_unit: int = 0
    short_unit: int = 0


class ShortStockSource(BaseMapping):
    code: str
    short_stock_source: int = 0
    ts: int


class Kbars(BaseMapping):
    ts: typing.List[int]
    Open: typing.List[float]
    High: typing.List[float]
    Low: typing.List[float]
    Close: typing.List[float]
    Volume: typing.List[int]

    def lazy_setter(self, **kwargs):
        [
            setattr(self, kwarg, value)
            for kwarg, value in kwargs.items()
            if hasattr(self, kwarg)
        ]


class ChangePercentRank(BaseMapping):
    date: str
    code: str
    name: str
    ts: int
    open: float
    high: float
    low: float
    close: float
    price_range: float
    tick_type: int
    change_price: float
    change_type: int
    average_price: float
    volume: int
    total_volume: int
    amount: int
    total_amount: int
    yesterday_volume: int
    volume_ratio: float
    buy_price: float
    buy_volume: int
    sell_price: float
    sell_volume: int
    bid_orders: int
    bid_volumes: int
    ask_orders: int
    ask_volumes: int
