from typing import Optional, Dict

from onlineafspraken.schema.response import OnlineAfsprakenBase


class AppointmentSchema(OnlineAfsprakenBase):
    id: int
    name: str
    description: str
    start_time: str
    finish_time: str
    blocked_time: str
    capacity: int
    appointment_type_id: int
    customer_id: int
    customer_name: str
    status: int
    resources: dict
    create_time: str
    update_time: str


class ConfirmAppointmentSchema(OnlineAfsprakenBase):
    confirmed: int


class SetAppointmentSchema(OnlineAfsprakenBase):
    id: int
    status: int


class CancelAppointmentResponse(OnlineAfsprakenBase):
    pass


class ConfirmAppointmentResponse(OnlineAfsprakenBase):
    appointment: ConfirmAppointmentSchema


class GetAppointmentsResponse(OnlineAfsprakenBase):
    objects: Optional[Dict[str, AppointmentSchema]]


class GetAppointmentResponse(OnlineAfsprakenBase):
    appointment: AppointmentSchema


class SetAppointmentResponse(OnlineAfsprakenBase):
    objects: Optional[Dict[str, SetAppointmentSchema]]
