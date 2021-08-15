from typing import Optional, List
from datetime import datetime
from enum import IntEnum
from foreverbull_core.models.base import Base


class Asset(Base):
    sid: Optional[int]
    symbol: str
    asset_name: Optional[str]
    exchange: str
    exchange_full: Optional[str]
    country_code: Optional[str]

    @classmethod
    def create(cls, asset):
        return cls(
            sid=asset.sid,
            symbol=asset.symbol,
            asset_name=asset.asset_name,
            exchange=asset.exchange,
            exchange_full=asset.exchange_full,
            country_code=asset.country_code,
        )


class Price(Base):
    date: datetime
    last_traded: datetime
    price: float
    open: float
    close: float
    high: float
    low: float
    volume: int


class EndOfDay(Price):
    asset: Asset


class OrderStatus(IntEnum):
    OPEN = 0
    FILLED = 1
    CANCELLED = 2
    REJECTED = 3
    HELD = 4


class Order(Base):
    id: Optional[str]
    asset: Optional[Asset]
    amount: Optional[int]
    filled: Optional[int]
    commission: Optional[int]
    limit_price: Optional[int]
    stop_price: Optional[int]
    current_date: Optional[str]
    created_date: Optional[str]
    status: Optional[OrderStatus]

    def update(self, event):
        asset = Asset(
            sid=event.sid.sid,
            symbol=event.sid.symbol,
            asset_name=event.sid.asset_name,
            exchange=event.sid.exchange,
            exchange_full=event.sid.exchange_full,
            country_code=event.sid.country_code,
        )
        self.asset = asset
        self.amount = event.amount
        self.filled = event.filled
        self.commission = event.commission
        self.limit_price = event.limit
        self.stop_price = event.stop
        self.current_date = str(event.dt)
        self.created_date = str(event.created)
        self.status = event.status

    @classmethod
    def create(cls, order):
        asset = Asset(
            sid=order.sid.sid,
            symbol=order.sid.symbol,
            asset_name=order.sid.asset_name,
            exchange=order.sid.exchange,
            exchange_full=order.sid.exchange_full,
            country_code=order.sid.country_code,
        )
        return cls(
            id=order.id,
            asset=asset,
            amount=order.amount,
            filled=order.filled,
            commission=order.commission,
            limit_price=order.limit,
            stop_price=order.stop,
            current_date=str(order.dt),
            created_date=str(order.created),
            status=order.status,
        )


class Position(Base):
    asset: Asset
    amount: int
    cost_basis: float
    last_sale_price: float
    last_sale_date: str


class Portfolio(Base):
    cash_flow: float
    starting_cash: int
    portfolio_value: float
    pnl: float
    returns: float
    cash: float
    positions: List[Position]
    start_date: str
    positions_value: float
    positions_exposure: float

    @classmethod
    def from_backtest(cls, backtest):
        positions = []
        for _, pos in backtest.positions.items():
            asset = Asset(
                sid=pos.asset.sid,
                symbol=pos.asset.symbol,
                asset_name=pos.asset.asset_name,
                exchange=pos.asset.exchange,
                exchange_full=pos.asset.exchange_full,
                country_code=pos.asset.country_code,
            )
            position = Position(
                asset=asset,
                amount=pos.amount,
                cost_basis=pos.cost_basis,
                last_sale_price=pos.last_sale_price,
                last_sale_date=str(pos.last_sale_date),
            )
            positions.append(position)
        portfolio = Portfolio(
            cash_flow=backtest.cash_flow,
            starting_cash=backtest.starting_cash,
            portfolio_value=backtest.portfolio_value,
            pnl=backtest.pnl,
            returns=backtest.returns,
            cash=backtest.cash,
            positions=positions,
            start_date=str(backtest.start_date),
            positions_value=backtest.positions_value,
            positions_exposure=backtest.positions_exposure,
        )
        return portfolio
