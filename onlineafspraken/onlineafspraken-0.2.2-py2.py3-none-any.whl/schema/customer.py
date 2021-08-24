from typing import Optional, Dict, List

from onlineafspraken.schema.response import OnlineAfsprakenBase, BaseResponseContent


class CustomerSchema(OnlineAfsprakenBase):
    id: int
    account_number: int
    first_name: Optional[str]
    last_name: Optional[str]
    insertions: Optional[str]
    birth_date: Optional[str]
    gender: Optional[str]
    street: Optional[str]
    house_nr: Optional[int]
    house_nr_addition: Optional[str]
    zip_code: Optional[str]
    city: Optional[str]
    country: Optional[str]
    phone: Optional[str]
    mobile_phone: Optional[str]
    email: Optional[str]
    status: int
    update_time: str
    create_time: str


class SetCustomerSchema(OnlineAfsprakenBase):
    id: int
    status: int


class FieldsSchema(OnlineAfsprakenBase):
    id: int
    label: str
    key: str
    type: str
    required: int


class PasswordRecoverySchema(OnlineAfsprakenBase):
    message: str


class SetCustomerResponse(BaseResponseContent):
    objects: Optional[Dict[str, SetCustomerSchema]]


class PasswordRecoveryResponse(BaseResponseContent):
    data: CustomerSchema


class GetCustomerResponse(BaseResponseContent):
    customer: CustomerSchema


class GetCustomersResponse(BaseResponseContent):
    objects: Dict[str, List[CustomerSchema]]


class GetFieldsResponse(BaseResponseContent):
    objects: Optional[Dict[str, FieldsSchema]]
