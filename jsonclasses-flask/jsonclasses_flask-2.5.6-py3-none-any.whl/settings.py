from typing import TypedDict, Optional
from jsonclasses.jsonclass_object import JSONClassObject

class CorsSetting(TypedDict):
    allow_headers: Optional[str]
    allow_origin: Optional[str]
    allow_methods: Optional[str]


class OperatorSetting(TypedDict):
    operator_cls: type[JSONClassObject]
    encode_key: str
