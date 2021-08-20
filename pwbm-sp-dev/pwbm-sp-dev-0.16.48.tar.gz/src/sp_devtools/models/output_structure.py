import decimal
import json
from datetime import date
from functools import partial
from typing import List, Literal, Optional, Union
from uuid import UUID

import pydantic
from pydantic import conint, constr, root_validator, stricturl, validator

from sp_devtools.constants import PeriodicityTypes, NA_FIELD

# Overall number of allowed decimal places in a Decimal number
DECIMAL_PRECISION = 28
# Number of allowed decimal places in the fractional part of a Decimal number
DECIMAL_SCALE = 10
# Number of allowed decimal places in the integer part of a Decimal number
DECIMAL_INTEGRAL_PLACES = DECIMAL_PRECISION - DECIMAL_SCALE


# Drop-in replacement for decimal.Decimal type.
# gt and lt limitations are checked only when used in pydantic models.
# For other circumstances decimal context limitations are used.
Decimal = pydantic.condecimal(
    ge=decimal.Decimal(-(10 ** DECIMAL_INTEGRAL_PLACES)) + decimal.Decimal(1) / (10 ** DECIMAL_SCALE),
    le=decimal.Decimal(+(10 ** DECIMAL_INTEGRAL_PLACES)) - decimal.Decimal(1) / (10 ** DECIMAL_SCALE),
)


def configure_decimal():
    """Sets-up application-level settings of pythonic Decimal type to conform to the DB decimal type."""

    # Set application-wide defaults for all threads about to be launched
    decimal.DefaultContext.prec = DECIMAL_PRECISION
    decimal.DefaultContext.Emax = DECIMAL_INTEGRAL_PLACES - 1
    decimal.DefaultContext.rounding = decimal.ROUND_DOWN

    # Replaces the current context in case Decimals were already used prior to reconfiguration
    decimal.setcontext(
        decimal.Context()
    )
configure_decimal()


def decimal_formatter(value: Optional[Decimal]) -> Decimal:
    """Get string representation of the DataValue. Rounds the value to fit the scale, strips off all trailing zeros."""

    if value is not None:
        if value.to_integral() == value:
            return value.quantize(decimal.Decimal('1'))
        return value.quantize(
            decimal.Decimal(f'0.{"0" * (DECIMAL_SCALE - 1)}{"1" if DECIMAL_SCALE else ""}')
        ).normalize()


class BaseModel(pydantic.BaseModel):
    class Config:
        extra = pydantic.Extra.forbid
        json_dumps = partial(json.dumps, sort_keys=True)
        json_encoders = {
            decimal.Decimal: lambda value: str(decimal_formatter(value)),
        }


class TableRow(BaseModel):
    series_correlation_id: Optional[constr(strict=True, strip_whitespace=True, min_length=1)]
    series_id: Optional[Optional[UUID]]
    number: Optional[conint(ge=0)]
    indent: Optional[conint(ge=0)]
    label: Optional[constr(strict=True, strip_whitespace=True)]

    @root_validator(pre=True)
    def validate_number(cls, values):
        for key in ('number', 'indent'):
            if isinstance(values[key], str) and not values[key].isdigit():
                values[key] = None
        return values


class Table(BaseModel):
    correlation_id: constr(strict=True, strip_whitespace=True, min_length=1)
    id: Optional[Optional[UUID]]
    name: Optional[constr(strict=True, strip_whitespace=True)]
    description: Optional[constr(strict=True, strip_whitespace=True)]
    source_url: Optional[stricturl(tld_required=False, strip_whitespace=True)]
    rows: Optional[List[TableRow]]


class Tag(BaseModel):
    name: constr(strict=True, strip_whitespace=True, min_length=1)
    value: Optional[constr(strict=True, strip_whitespace=True)]


class DataPoint(BaseModel):
    periodicity: constr(strict=True, strip_whitespace=True, min_length=1)
    period: constr(strict=True, strip_whitespace=True, min_length=1)
    value: Union[Literal['NA'], Decimal] = NA_FIELD

    @validator('period')
    def validate_period(cls, period, values):
        if values['periodicity'] != PeriodicityTypes.custom:
            try:
                date.fromisoformat(period)
            except ValueError:
                raise ValueError(f'Period "{period}" is invalid ISO format string')
        return period


class Series(BaseModel):
    correlation_id: constr(strict=True, strip_whitespace=True, min_length=1)
    id: Optional[UUID]
    name: constr(strict=True, strip_whitespace=True)
    description: Optional[constr(strict=True, strip_whitespace=True)]
    source_url: Optional[stricturl(tld_required=False, strip_whitespace=True)]
    data_type: Optional[constr(strict=True, strip_whitespace=True, min_length=1)]
    tags: Optional[List[Tag]]
    data_values: Optional[List[DataPoint]]

    @validator('data_type')
    def prepare_data_type(cls, data_type):
        if data_type:
            return data_type.lower()


class Meta(BaseModel):
    producer: constr(strict=True, strip_whitespace=True, min_length=1) = 'PWBM Scraping Platform'
    namespace: constr(strict=True, strip_whitespace=True, min_length=1)
    task_id: Optional[conint(strict=True, ge=0)]


class UploadStructure(BaseModel):
    format_version: Literal['0.2'] = '0.2'
    file_meta: Meta
    tables: Optional[List[Table]]
    series: Optional[List[Series]]
