from typing import Optional, Dict, Type, Any, TypeVar, Mapping, List

from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper
from pydantic.fields import ModelField
from pydantic.utils import ROOT_KEY

from onlineafspraken.schema.response import (
    BaseResponseContent,
    OnlineAfsprakenBase,
    ResponseStatus,
)


class AgendaSchema(OnlineAfsprakenBase):
    id: int
    name: str = None
    date_format: str = None
    time_format: str = None
    align_grid: int
    is_default: int


class AppointmentTypeSchema(OnlineAfsprakenBase):
    id: int
    name: str
    description: Optional[str]
    status: int
    price_type: int
    price: float
    duration: int
    min_time_before_appointment: int
    max_time_before_appointment: int
    buffer: int
    can_be_booked_by_consumer: int
    category: str
    category_id: Optional[int]


class ResourceSchema(OnlineAfsprakenBase):
    id: int
    name: str
    code: Optional[str]
    phone: Optional[str]
    mobile_phone: Optional[str]
    email: Optional[str]
    status: Optional[str]
    label: Optional[str]


class RequiresConfirmationSchema(OnlineAfsprakenBase):
    required: str


class ListResponse(OnlineAfsprakenBase):
    # @ Todo create generic class method for parsing and validating
    status: ResponseStatus

    @classmethod
    def obj_to_schema(cls, obj, schema):
        objects_field = ModelField(
            name="objects",
            alias="Objects",
            type_=schema,
            class_validators={},
            model_config=cls.__fields__["status"].model_config,
        )
        cls.__fields__["objects"] = objects_field
        cls.parse_obj(obj)

        return cls(**obj)


class GetAgendasResponse(BaseResponseContent):
    objects: Optional[Dict[str, List[AgendaSchema]]]


class GetAgendaResponse(BaseResponseContent):
    agenda: AgendaSchema


class GetAppointmentTypesResponse(BaseResponseContent):
    objects: Dict[str, List[AppointmentTypeSchema]]


class GetAppointmentTypeResponse(BaseResponseContent):
    appointment_type: AppointmentTypeSchema


class GetResourcesResponse(BaseResponseContent):
    objects: Optional[Dict[str, List[ResourceSchema]]]


class GetResourceResponse(BaseResponseContent):
    resource: ResourceSchema


class RequiresConfirmationResponse(OnlineAfsprakenBase):
    required: RequiresConfirmationSchema
