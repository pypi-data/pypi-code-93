import typing
import datetime

from shioaji.base import BaseModel, conint, StrictInt
from shioaji.account import Account
from shioaji.contracts import Contract
from shioaji.constant import (
    Action,
    FuturesPriceType,
    FuturesOrderType,
    FuturesOCType,
    StockPriceType,
    StockOrderType,
    StockOrderCond,
    StockFirstSell,
    Status,
    TFTStockOrderLot,
    TFTOrderType,
    TFTStockPriceType)


class Deal(BaseModel):
    seq: str
    price: typing.Union[StrictInt, float]
    quantity: int
    ts: int


class OrderStatus(BaseModel):
    id: str = ""
    status: Status
    status_code: str = ""
    order_datetime: datetime.datetime = None
    msg: str = ""
    modified_time: datetime.datetime = None
    modified_price: typing.Union[StrictInt, float] = 0
    deal_quantity: int = 0
    cancel_quantity: int = 0
    deals: typing.List[Deal] = None


class BaseOrder(BaseModel):
    action: Action
    price: typing.Union[StrictInt, float]
    quantity: conint(gt=0)
    id: str = ""
    seqno: str = ""
    ordno: str = ""
    account: Account = None
    ca: str = ""

    def __repr_args__(self):
        return [
            (k, v)
            for k, v in self._iter(to_dict=False, exclude_defaults=True, exclude={"ca"})
        ]


class FuturesOrder(BaseOrder):
    price_type: FuturesPriceType
    order_type: FuturesOrderType
    octype: FuturesOCType = FuturesOCType.Auto


class StockOrder(BaseOrder):
    price_type: StockPriceType
    order_type: StockOrderType
    order_cond: StockOrderCond = StockOrderCond.Cash
    first_sell: StockFirstSell = StockFirstSell.No


class TFTStockOrder(BaseOrder):
    price_type: TFTStockPriceType
    order_type: TFTOrderType
    order_lot: TFTStockOrderLot = TFTStockOrderLot.Common
    order_cond: StockOrderCond = StockOrderCond.Cash
    first_sell: StockFirstSell = StockFirstSell.No


class Order(StockOrder, FuturesOrder, TFTStockOrder):
    price_type: typing.Union[StockPriceType, FuturesPriceType, TFTStockPriceType]
    order_type: typing.Union[StockOrderType, FuturesOrderType, TFTOrderType]

    def __init__(
        self,
        price: typing.Union[StrictInt, int],
        quantity: conint(gt=0),
        action: Action,
        price_type: typing.Union[StockPriceType, FuturesPriceType, TFTStockPriceType],
        order_type: typing.Union[StockOrderType, FuturesOrderType, TFTOrderType],
        **kwargs
    ):
        super().__init__(
            **{
                **dict(
                    price=price,
                    quantity=quantity,
                    action=action,
                    price_type=price_type,
                    order_type=order_type,
                ),
                **kwargs,
            }
        )


class Trade(BaseModel):
    contract: Contract
    order: BaseOrder
    status: OrderStatus

    def __init__(self, contract: Contract, order: BaseOrder, status: OrderStatus):
        super().__init__(**dict(contract=contract, order=order, status=status))
