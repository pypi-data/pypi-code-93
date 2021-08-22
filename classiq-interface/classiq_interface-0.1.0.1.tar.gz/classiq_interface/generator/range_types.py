from typing import Optional, Tuple, Generic, TypeVar

import pydantic
from pydantic.generics import GenericModel

RangeType = TypeVar("RangeType", int, float)


class Range(GenericModel, Generic[RangeType]):
    lower_bound: Optional[RangeType] = None
    upper_bound: Optional[RangeType] = None

    @pydantic.validator("upper_bound")
    def validate_bounds_order(cls, upper_bound, values):
        lower_bound = values.get("lower_bound")

        if (
            lower_bound is not None
            and upper_bound is not None
            and lower_bound > upper_bound
        ):
            raise ValueError("lower bound must not be greater than upper bound")

        return upper_bound

    # TODO: Remove default values
    def to_tuple(
        self,
        default_lower_bound: RangeType = -1,
        default_upper_bound: RangeType = float("inf"),
    ) -> Tuple[RangeType, RangeType]:
        return (
            self.lower_bound if self.lower_bound else default_lower_bound,
            self.upper_bound if self.upper_bound else default_upper_bound,
        )


NonNegativeIntRange = Range[pydantic.conint(ge=0)]
NonNegativeFloatRange = Range[pydantic.confloat(ge=0)]
