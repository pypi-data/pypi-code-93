from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .builders import GraphQLOperationBuilder

__all__ = ("GraphQLBuildState",)


class GraphQLBuildState:
    def __init__(self, operation_builder: GraphQLOperationBuilder) -> None:
        self.current_cost = 0
        self.operation_builder = operation_builder

    def should_end_call(self, cost: int) -> bool:
        self.current_cost += cost
        if self.operation_builder.MAX_COST is None:
            return False
        if self.current_cost > self.operation_builder.MAX_COST:
            self.current_cost = cost
            return True
        return False
