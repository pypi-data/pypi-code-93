import re
from os import environ
from typing import Any, Dict, Optional, Pattern

from pydantic import BaseModel, errors
from pydantic.utils import update_not_none
from pydantic.validators import constr_length_validator, strict_str_validator

__all__ = [
    "AttributeUid",
    "AttributeUri",
    "CollectionUid",
    "CollectionUri",
    "DatasourceUid",
    "DatasourceUri",
]

OptionalInt = Optional[int]
RE_MATCH_COLLECTION_NAME = re.compile(r"" + environ.get("IGENIUS_ADAPTER_SDK_RE_MATCH_COLLECTION_NAME", r"^\S+$"))
RE_MATCH_ALL_BUT_NEW_LINES_AND_TABS = re.compile(
    r"" + environ.get("IGENIUS_ADAPTER_SDK_RE_MATCH_ATTRIBUTE_NAME", r"^[\S ]+$")
)


class Uid(str):
    min_length: int = 1
    max_length: OptionalInt = None
    regex: Optional[Pattern[str]] = RE_MATCH_ALL_BUT_NEW_LINES_AND_TABS

    @classmethod
    def __get_validators__(cls):
        yield strict_str_validator
        yield constr_length_validator
        yield cls.validate_format

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        update_not_none(
            field_schema,
            minLength=cls.min_length,
            maxLength=cls.max_length,
        )

    @classmethod
    def validate_format(cls, value):
        if cls.regex:
            if not cls.regex.match(value):
                raise errors.StrRegexError(pattern=cls.regex.pattern)
        return value


class AttributeUid(Uid):
    pass


class CollectionUid(Uid):
    regex: Pattern[str] = RE_MATCH_COLLECTION_NAME


class DatasourceUid(Uid):
    pass


class UriModel(BaseModel):
    def __hash__(self):
        return hash(tuple(self.dict().items()))

    class Config:
        allow_mutation = False


class DatasourceUri(UriModel):
    datasource_uid: DatasourceUid


class CollectionUri(UriModel):
    datasource_uid: DatasourceUid
    collection_uid: CollectionUid


class AttributeUri(UriModel):
    datasource_uid: DatasourceUid
    collection_uid: CollectionUid
    attribute_uid: AttributeUid
