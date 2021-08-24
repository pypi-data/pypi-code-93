from typing import Dict, Optional, List

from onlineafspraken.schema.response import BaseResponseContent, OnlineAfsprakenBase


class BookableDaySchema(OnlineAfsprakenBase):
    date: str
    month: int
    day: int


class BookableTimeSchema(OnlineAfsprakenBase):
    date: str
    start_time: str
    end_time: str
    timestamp: int
    appointment_type_id: int
    resource_id: int


class GetBookableDaysResponse(BaseResponseContent):
    objects: Optional[Dict[str, List[BookableDaySchema]]]


class GetBookableTimesResponse(BaseResponseContent):
    objects: Optional[Dict[str, List[BookableTimeSchema]]]
