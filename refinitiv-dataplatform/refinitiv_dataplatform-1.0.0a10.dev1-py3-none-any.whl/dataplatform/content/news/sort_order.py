__all__ = ["SortOrder"]

from enum import Enum, unique


@unique
class SortOrder(Enum):
    old_to_new = "oldToNew"
    new_to_old = "newToOld"

    @staticmethod
    def convert_to_str(sort_order):
        if isinstance(sort_order, SortOrder):
            return sort_order.value
        elif sort_order in _SORT_ORDER_VALUES:
            return sort_order
        else:
            raise AttributeError(f"Sort order value must be in {_SORT_ORDER_VALUES}")


_SORT_ORDER_VALUES = [k.value for k in SortOrder]
