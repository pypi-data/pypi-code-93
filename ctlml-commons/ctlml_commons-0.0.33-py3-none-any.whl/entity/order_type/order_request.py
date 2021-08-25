from dataclasses import dataclass

from ctlml_commons.entity.execution_type import ExecutionType
from ctlml_commons.entity.order import OrderType
from ctlml_commons.entity.time_in_force import TimeInForce


@dataclass
class OrderRequest:
    symbol: str
    execution_type: ExecutionType
    order_type: OrderType
    quantity: float
    time_in_force: TimeInForce
    notes: str
    price: float

    def should_execute(self, current_price: float = -1) -> bool:
        return True


if __name__ == "__main__":
    order_request = OrderRequest(
        symbol="AMZN",
        execution_type=ExecutionType.SELL,
        order_type=OrderType.MARKET,
        quantity=100,
        price=-2,
        notes="Because",
        time_in_force=TimeInForce.IMMEDIATE_OR_CANCEL,
    )

    print(order_request)
    print(order_request.should_execute())
