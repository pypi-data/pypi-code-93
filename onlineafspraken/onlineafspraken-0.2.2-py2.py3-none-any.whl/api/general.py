from typing import List

from onlineafspraken.api.client import OnlineAfsprakenAPI, client
from onlineafspraken.api.utils import parse_schema
from onlineafspraken.schema.general import (
    GetAgendaResponse,
    GetAgendasResponse,
    GetAppointmentTypesResponse,
    GetResourceResponse,
    GetResourcesResponse,
    RequiresConfirmationResponse,
    AppointmentTypeSchema,
    AgendaSchema,
    ResourceSchema,
)


def get_agenda(agenda_id) -> AgendaSchema:

    resp = client.get("getAgenda", id=agenda_id)

    return GetAgendaResponse.parse_obj(resp).agenda


def get_agendas() -> List[AgendaSchema]:

    resp = client.get("getAgendas")

    return parse_schema(
        resp,
        parse_key="Agenda",
        schema=GetAgendasResponse,
        enforce_list=True,
    )


def get_appointment_type(type_id) -> AppointmentTypeSchema:

    resp = client.get("getAppointmentType", id=type_id)

    return AppointmentTypeSchema.parse_obj(resp["Objects"]["AppointmentType"])


def get_appointment_types() -> List[AppointmentTypeSchema]:

    resp = client.get("getAppointmentTypes")

    return parse_schema(
        resp,
        parse_key="AppointmentType",
        schema=GetAppointmentTypesResponse,
        enforce_list=True,
    )


def get_resource(resource_id) -> ResourceSchema:

    resp = client.get("getResource", id=resource_id)

    return ResourceSchema.parse_obj(resp["Resource"])


def get_resources() -> List[ResourceSchema]:

    resp = client.get("getResources")

    return parse_schema(
        resp,
        parse_key="Resource",
        schema=GetResourcesResponse,
        enforce_list=True,
    )


def requires_confirmation() -> RequiresConfirmationResponse:

    resp = client.get("requiresConfirmation")

    return RequiresConfirmationResponse.parse_obj(resp)
