import os.path
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, cast

from pydantic import Field

from ..json import fast_dumps as dumps
from ..typing.dataclass import dataclass
from .env import Env


class Type(str, Enum):
    int = "int"
    bigint = "bigint"
    enum = "enum"

    str = "str"
    uuid = "uuid"
    email = "email"
    url = "url"

    float = "float"

    date = "date"
    datetime = "datetime"
    auto_now = "now"
    auto_now_add = "auto_now_add"

    timedelta = "timedelta"

    json = "json"
    binary = "binary"

    foreign = "foreign"
    m2m = "m2m"


@dataclass
class Field:
    name: str
    type: Type
    length: int = 0

    description: str = ""

    default: Any = None
    index: bool = False
    required: bool = False
    unique: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)

    to: Optional[str] = None

    @property
    def enums(self) -> Tuple[str, List[Any]]:
        if self.type == Type.enum:
            name, choices = self.config.get("name", ""), self.config.get("choices", [])
            assert isinstance(name, str)
            assert isinstance(choices, list)
            assert len(choices) > 0
            choice = choices[0]
            assert isinstance(choice, dict)
            value: Any = cast(Dict[str, Any], choice).get("value", "")
            assert value
            return name.title(), choices
        return "", []

    def field_define(self, pk: bool) -> str:
        field_type, kwargs = self.field(pk=pk)
        if pk:
            del kwargs["default"]
        kwargs_define = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        return f"{field_type}({kwargs_define})"

    def field(self, pk: bool) -> Tuple[str, Dict[str, Any]]:
        kwargs: Dict[str, Any] = {
            "pk": pk,
            "description": dumps(self.description),
            "index": self.index,
            "null": False,
        }
        if self.type == Type.int:
            kwargs["default"] = self.default or 0
            return "fields.IntField", kwargs
        if self.type == Type.bigint:
            kwargs["default"] = self.default or 0
            return "fields.BigIntField", kwargs
        if self.type == Type.enum:
            name, choices = self.enums
            kwargs["enum_type"] = name
            kwargs["default"] = f"{name}.{choices[0].value}"
            return "fields.CharEnumField", kwargs
        if self.type == Type.str or self.type == Type.email or self.type == Type.url:
            kwargs["default"] = dumps(self.default or "")
            if self.unique:
                if kwargs["default"] == "":
                    del kwargs["default"]
                kwargs["unique"] = True
                kwargs["null"] = True

            if self.type == Type.email:
                self.length = 320
            elif self.type == Type.url:
                self.length = 2049

            if self.length == 0:
                return "fields.TextField", kwargs

            assert self.length > 0
            kwargs["max_length"] = self.length
            return "fields.CharField", kwargs
        if self.type == Type.uuid:
            kwargs["unique"] = True
            return "fields.UUIDField", kwargs
        if self.type == Type.float:
            kwargs["default"] = self.default or 0
            return "fields.FloatField", kwargs
        if self.type == Type.date:
            return "fields.DateField", kwargs
        if (
            self.type == Type.datetime
            or self.type == Type.auto_now
            or self.type == Type.auto_now_add
        ):
            if self.type == Type.auto_now:
                kwargs["auto_now"] = True
            elif self.type == Type.auto_now_add:
                kwargs["auto_now_add"] = True

            return "fields.DatetimeField", kwargs
        if self.type == Type.timedelta:
            kwargs["default"] = self.default or 0
            return "fields.TimeDeltaField", kwargs
        if self.type == Type.json:
            kwargs["default"] = self.default or {}
            return "afields.JSONField", kwargs
        if self.type == Type.binary:
            return "fields.BinaryField", kwargs
        if self.type == Type.foreign:
            assert self.to
            kwargs["model_name"] = self.to
            return "fields.ForeignKeyField", kwargs
        if self.type == Type.m2m:
            assert self.to
            kwargs["model_name"] = self.to
            return "fields.ManyToManyField", kwargs
        assert False


@dataclass
class Scheme:
    name: str

    fields: List[Field]
    pk: str = "id"

    @property
    def enums(self) -> List[Tuple[str, List[Any]]]:
        enums: List[Tuple[str, List[Any]]] = []
        for field in self.fields:
            r = field.enums
            if r[0]:
                enums.append(r)
        return enums

    async def generate(self, env: Env, output: str):
        await env.save(
            "model/model.jinja2",
            os.path.join(output, f"{self.name}.py"),
            scheme=self,
        )
        await env.save(
            "model/generated/model.jinja2",
            os.path.join(output, f"generated/{self.name}.py"),
            scheme=self,
        )
