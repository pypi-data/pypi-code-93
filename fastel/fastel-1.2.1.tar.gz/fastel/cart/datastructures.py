from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, validator

from fastel.exceptions import APIException

from .base import BaseCartConfig


class PaymentSubTypes(str, Enum):
    credit = "credit"
    cvs_cod = "cvs_cod"


class LogisticTypes(str, Enum):
    HOME = "HOME"
    CVS = "CVS"


class HomeSubtypes(str, Enum):
    ECAN = "ECAN"
    TCAT = "TCAT"


class CVSLogisticSubTypes(str, Enum):
    FAMI = "FAMI"
    UNIMART = "UNIMART"
    HILIFE = "HILIFE"
    FAMIC2C = "FAMIC2C"
    UNIMARTC2C = "UNIMARTC2C"
    HILIFEC2C = "HILIFEC2C"
    OKMARTC2C = "OKMARTC2C"


class CartConfig(BaseCartConfig):
    buyer_name: str
    buyer_phone: Optional[str]
    buyer_email: EmailStr
    buyer_zip: Optional[str]
    buyer_city: Optional[str]
    buyer_district: Optional[str]
    buyer_address: Optional[str]
    buyer_tel: Optional[str]
    buyer_tel_ext: Optional[str]
    receiver_name: Optional[str]
    receiver_phone: Optional[str]
    receiver_email: Optional[str]
    receiver_zip: Optional[str]
    receiver_city: Optional[str]
    receiver_district: Optional[str]
    receiver_address: Optional[str]
    receiver_tel: Optional[str]
    receiver_tel_ext: Optional[str]
    payment_subtype: PaymentSubTypes = PaymentSubTypes.credit
    logistics_type: LogisticTypes
    logistics_subtype: str

    @validator("logistics_subtype")
    def validate_logistic_subtype(cls, value: str, values: Dict[str, Any]) -> str:
        if value is None:
            return ""

        try:
            if values["logistics_type"] == LogisticTypes.HOME:
                return HomeSubtypes[value]
            return CVSLogisticSubTypes[value]
        except KeyError:
            raise ValueError("subtype_not_valid")


OptionalCartConfig = CartConfig.model_with_optional_fields()


class SingleConfig(BaseModel):
    name: str
    choice: str


class BoolConfig(BaseModel):
    name: str


class ItemConfig(BaseModel):
    qty: int
    variants: List[Union[SingleConfig, BoolConfig]]

    @validator("qty")
    def positive_qty(cls, qty: int) -> int:
        if qty < 1:
            raise APIException(
                status_code=400, error="invalid_qty_error", detail="quantity must > 0"
            )
        return qty

    @validator("variants")
    def validate_variants(
        cls, value: List[Union[SingleConfig, BoolConfig]]
    ) -> List[Union[SingleConfig, BoolConfig]]:
        names = []
        for variant in value:
            if variant.name in names:
                raise APIException(status_code=400, error="invalid_variant", detail="")
            names.append(variant.name)

        return value


class VariantTypes(str, Enum):
    bool = "bool"
    single = "single"


class SingleChoice(BaseModel):
    name: str
    label: str
    price: int


class SingleVariant(BaseModel):
    type: Literal["single"]
    name: str
    label: str
    choices: List[SingleChoice]


class BooleanVariant(BaseModel):
    type: Literal["bool"]
    name: str
    label: str
    price: int


class ValidatedObjectId(ObjectId):  # type: ignore
    @classmethod
    def __get_validators__(cls) -> Any:
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        return ObjectId(value)


class Product(BaseModel):
    id: ValidatedObjectId = Field(alias="_id")
    name: str
    price: int
    variants: List[Union[SingleVariant, BooleanVariant]] = []
    on_shelf: bool = True
