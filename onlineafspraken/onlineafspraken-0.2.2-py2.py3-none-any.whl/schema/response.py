from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


def to_camel(tag):
    return "".join(word.capitalize() for word in tag.split("_"))


class OnlineAfsprakenBase(BaseModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator = to_camel


class ResponseStatus(OnlineAfsprakenBase):
    api_version: str = Field(None, alias="APIVersion")
    status: str
    date: datetime
    timestamp: str
    code: Optional[str]
    message: Optional[str]


class BaseResponseContent(OnlineAfsprakenBase):
    status: ResponseStatus


class BaseResponse(OnlineAfsprakenBase):
    response: BaseResponseContent
