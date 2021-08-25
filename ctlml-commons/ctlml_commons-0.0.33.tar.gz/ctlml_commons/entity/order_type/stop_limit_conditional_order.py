from dataclasses import dataclass

from ctlml_commons.entity.execution_type import ExecutionType
from ctlml_commons.entity.order_type.order_request import OrderRequest
from ctlml_commons.entity.time_in_force import TimeInForce


@dataclass
class StopLimitOrderRequest(OrderRequest):
    stop_price: float
    limit_price: float
    extended_hours: bool
    limit_order: bool = True

    #  TODO: should_execute


if __name__ == "__main__":
    order = StopLimitOrderRequest(
        symbol="AMZN",
        execution_type=ExecutionType.SELL,
        stop_price=5000,
        limit_price=6000,
        price=5500,
        quantity=1000,
        extended_hours=True,
        time_in_force=TimeInForce.GOOD_TIL_CANCELLED,
    )

    print(order)
