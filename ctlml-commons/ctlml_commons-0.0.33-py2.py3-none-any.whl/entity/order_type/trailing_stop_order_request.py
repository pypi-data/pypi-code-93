from dataclasses import dataclass

from ctlml_commons.entity.execution_type import ExecutionType
from ctlml_commons.entity.order_type.order_request import OrderRequest
from ctlml_commons.entity.time_in_force import TimeInForce


@dataclass
class TrailingStopOrderRequest(OrderRequest):
    """Percentage based buy/sell order below/higher than their previous prices."""

    price: float
    trailing_percentage: float
    extended_hours: bool
    limit_order: bool = True

    def should_execute(self, current_price: float = -1) -> bool:

        if self.execution_type is ExecutionType.SELL:
            return True if current_price <= self.price - (self.price * self.trailing_percentage) else False
        # If buying, current price must be lower than limit
        elif self.execution_type.BUY:
            return True if current_price >= self.price + (self.price * self.trailing_percentage) else False
        else:
            raise Exception(f"Unknown execution type: {self.execution_type}")


if __name__ == "__main__":
    sell_order = TrailingStopOrderRequest(
        symbol="AMZN",
        execution_type=ExecutionType.SELL,
        price=5000,
        trailing_percentage=0.1,
        quantity=1000,
        extended_hours=True,
        time_in_force=TimeInForce.GOOD_TIL_CANCELLED,
    )

    print(sell_order)
    print(sell_order.should_execute(current_price=4501))
    print(sell_order.should_execute(current_price=4500))
    print(sell_order.should_execute(current_price=4499))

    buy_order = TrailingStopOrderRequest(
        symbol="MRO",
        execution_type=ExecutionType.BUY,
        price=1000,
        trailing_percentage=0.2,
        quantity=2000,
        extended_hours=True,
        time_in_force=TimeInForce.GOOD_TIL_CANCELLED,
    )

    print(buy_order)
    print(buy_order.should_execute(current_price=1199))
    print(buy_order.should_execute(current_price=1200))
    print(buy_order.should_execute(current_price=1201))
