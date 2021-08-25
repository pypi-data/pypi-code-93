from dataclasses import dataclass

from ctlml_commons.entity.execution_type import ExecutionType
from ctlml_commons.entity.order_type.order_request import OrderRequest
from ctlml_commons.entity.time_in_force import TimeInForce


@dataclass
class StopOrderRequest(OrderRequest):
    stop_price: float
    limit_order: bool = True

    #  TODO: should_execute


if __name__ == "__main__":
    order = StopOrderRequest(
        symbol="AMZN",
        execution_type=ExecutionType.SELL,
        stop_price=2000,
        quantity=1000,
        time_in_force=TimeInForce.GOOD_TIL_CANCELLED,
    )

    print(order)
