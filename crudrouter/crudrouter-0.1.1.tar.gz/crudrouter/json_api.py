from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

ReturnData = TypeVar("ReturnData")


class JsonApiSource(BaseModel):
    pointer: Optional[str]
    parameter: Optional[str]
    meta: Optional[Dict[Any, Any]]


class JsonApiErrorObject(BaseModel):
    id: Optional[str]
    links: Optional[Dict[Any, Any]]
    about: Optional[str]
    status: Optional[int]
    title: Optional[str]
    detail: Optional[str]
    source: Optional[JsonApiSource]
    meta: Optional[Dict[Any, Any]]


class JsonApiSuccessResponse(GenericModel, Generic[ReturnData]):
    data: ReturnData
    jsonapi: Optional[Dict[Any, Any]] = None
    meta: Optional[Dict[Any, Any]] = None


class JsonApiErrorResponse(GenericModel, Generic[ReturnData]):
    jsonapi: Optional[Dict[Any, Any]]
    meta: Optional[Dict[Any, Any]]
    errors: Optional[List[JsonApiErrorObject]]


class JsonApiRequestEntity(GenericModel, Generic[ReturnData]):
    data: ReturnData
