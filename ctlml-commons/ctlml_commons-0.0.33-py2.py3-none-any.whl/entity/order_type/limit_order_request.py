from dataclasses import dataclass

from ctlml_commons.entity.execution_type import ExecutionType
from ctlml_commons.entity.order_type.order_request import OrderRequest
from ctlml_commons.entity.time_in_force import TimeInForce


@dataclass
class LimitOrderRequest(OrderRequest):
    """An order that specifies the minimum price to sell a stock or the maximum price to buy it. Allows for a ceiling
    and a floor to be set so once a stock reaches into that range, an order will occur.
    """

    limit_price: float
    extended_hours: bool
    limit_order: bool = True

    def should_execute(self, current_price: float = -1) -> bool:
        # TODO: extended hours check

        # If selling, current price must be higher than limit
        if self.execution_type is ExecutionType.SELL:
            return True if current_price >= self.limit_price else False
        # If buying, current price must be lower than limit
        elif self.execution_type.BUY:
            return True if current_price <= self.limit_price else False
        else:
            raise Exception(f"Unknown execution type: {self.execution_type}")


if __name__ == "__main__":
    sell_order = LimitOrderRequest(
        symbol="AMZN",
        execution_type=ExecutionType.SELL,
        limit_price=5000,
        quantity=1000,
        extended_hours=True,
        time_in_force=TimeInForce.GOOD_TIL_CANCELLED,
    )

    print(sell_order)
    print(sell_order.should_execute(current_price=5001))
    print(sell_order.should_execute(current_price=5000))
    print(sell_order.should_execute(current_price=4999))

    buy_order = LimitOrderRequest(
        symbol="MRO",
        execution_type=ExecutionType.BUY,
        limit_price=1000,
        quantity=2000,
        extended_hours=True,
        time_in_force=TimeInForce.GOOD_TIL_CANCELLED,
    )

    print(buy_order)
    print(buy_order.should_execute(current_price=1000))
    print(buy_order.should_execute(current_price=1001))
    print(buy_order.should_execute(current_price=1002))
