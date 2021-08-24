from shioaji.base import BaseModel
from shioaji.contracts import Contract
from shioaji.constant import Action, StockOrderCond, TradeType
from shioaji.account import Account
from shioaji.data import BaseMapping
import typing


class Position(BaseMapping):
    code: str
    direction: Action
    quantity: int
    price: float
    last_price: float
    pnl: float
    yd_quantity: int
    cond: StockOrderCond = StockOrderCond.Cash


class ProfitLoss(BaseMapping):
    id: int
    code: str
    seqno: str
    dseq: str
    quantity: int
    price: float
    pnl: float
    pr_ratio: float
    cond: StockOrderCond
    date: str


class Settlement(BaseMapping):
    t_money: float
    t1_money: float
    t2_money: float
    t_day: str
    t1_day: str
    t2_day: str


class AccountBalance(BaseMapping):
    acc_balance: float
    date: str
    errmsg: str


class ProfitLossDetail(BaseMapping):
    date: str
    cond: StockOrderCond
    code: str
    quantity: int
    price: float
    cost: int
    dseq: str
    rep_margintrading_amt: int
    rep_collateral: int
    rep_margin: int
    fee: int
    interest: int
    tax: int
    shortselling_fee: int
    currency: str
    trade_type: TradeType
