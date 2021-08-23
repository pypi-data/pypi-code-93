from typing import List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator

__all__ = [
    "Bin",
    "BinningRules",
]

Number = Union[float, int]


class Bin(BaseModel):
    ge: Optional[Number]
    lt: Optional[Number]

    @root_validator
    def check_bin_extremities(cls, values):
        ge = values.get("ge")
        lt = values.get("lt")
        if (ge is None and lt is None) or (ge is not None and lt is not None and lt <= ge):
            raise ValueError("invalid bin values")
        return values

    def __str__(self):
        return str(self.ge) + "-" + str(self.lt)


class BinningRules(BaseModel):
    bins: List[Bin] = Field(..., min_items=2)

    @validator("bins")
    def sort_bins(cls, v):
        # sort by `ge` attribute, with None first
        return sorted(v, key=lambda x: (x.ge is not None, x.ge))

    @validator("bins")
    def null_bin_value_validator(cls, v):
        checks = (
            v[0].lt is None,
            v[-1].ge is None,
            any(x.ge is None or x.lt is None for x in v[1:-1]),
        )
        if any(checks):
            raise ValueError("null values found in prohibited properties")
        return v

    @validator("bins")
    def overlapping_bin_validator(cls, v):
        for i, b in enumerate(v[:-1]):
            if b.lt > v[i + 1].ge:
                raise ValueError("found overlapping bins")
        return v
