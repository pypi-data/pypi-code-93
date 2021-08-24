from typing import List

from onlineafspraken.api.client import client
from onlineafspraken.api.utils import parse_schema
from onlineafspraken.schema.availability import (
    GetBookableTimesResponse,
    BookableTimeSchema,
    BookableDaySchema,
    GetBookableDaysResponse,
)


def get_bookable_days(
    agenda_id, appointment_type_id, start_date, end_date, resource_id=None
) -> List[BookableDaySchema]:
    resp = client.get(
        "getBookableDays",
        AgendaId=agenda_id,
        AppointmentTypeId=appointment_type_id,
        StartDate=start_date,
        EndDate=end_date,
        ResourceId=resource_id,
    )

    return parse_schema(
        resp, parse_key="BookableDay", schema=GetBookableDaysResponse, enforce_list=True
    )


def get_bookable_times(
    agenda_id,
    appointment_type_id,
    date,
    resource_id=None,
    start_time=None,
    end_time=None,
) -> List[BookableTimeSchema]:

    response_data = client.get(
        "getBookableTimes",
        AgendaId=agenda_id,
        AppointmentTypeId=appointment_type_id,
        Date=date,
        ResourceId=resource_id,
        StartTime=start_time,
        EndTime=end_time,
    )

    return parse_schema(
        response_data,
        parse_key="BookableTime",
        enforce_list=True,
        schema=GetBookableTimesResponse,
    )
