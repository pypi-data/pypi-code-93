from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Any, Union, Dict, Tuple
import ipaddress

from pydantic import BaseModel, validator, BaseConfig, PydanticValueError, Extra

try:
    import rapidjson as json

    BaseConfig.json_dumps = json.dumps
    BaseConfig.json_loads = json.loads
except ImportError:
    import json


class NotAnIPAddressError(PydanticValueError):
    code = "not_an_ip_address"
    msg_template = 'value is not a valid "IPvAnyAddress", got "{wrong_value}"'


class TelemetryValueV2(BaseModel):
    name: str
    samples: int
    latest: Optional[Any] = None
    min: Union[None, int, float] = None
    max: Union[None, int, float] = None
    sum: Union[None, int, float] = None
    raw: Optional[Dict[datetime, Any]] = None
    all: Optional[List[Tuple[datetime, Any]]] = None


class TelemetryDataV1(BaseModel):
    samples: int
    latest: Optional[Any] = None
    min: Union[None, int, float] = None
    max: Union[None, int, float] = None
    sum: Union[None, int, float] = None
    all: Optional[List[Tuple[datetime, Any]]] = None


class TelemetryValueV1(BaseModel):
    parameterName: str
    data: TelemetryDataV1


class TelemetryV1(BaseModel):
    version: int = 1
    dateTime: datetime
    parameterValues: List[TelemetryValueV1]


class TelemetryV2(BaseModel):
    version: int = 2
    type: str
    timestamp: datetime
    values: List[TelemetryValueV2]
    serial: Optional[str] = None

    class Config:
        extra = Extra.ignore


class TelemetryV3(BaseModel):
    version: int = 3
    type: str
    timestamp: datetime
    uid: str
    values: List[TelemetryValueV2]
    serial: Optional[str] = None


class TelemetryBatchV3(BaseModel):
    __root__: List[TelemetryV3]


class CommandRequestV1(BaseModel):
    id: str
    name: str
    data: Optional[dict] = None
    destination: Optional[str] = None
    created_at: Optional[datetime] = None


class CommandRequestV2(BaseModel):
    id: str
    name: str
    data: Union[Dict[str, Any], List[Any], None] = None
    destination: Optional[str] = None
    created_at: Optional[datetime] = None


class CommandResponseV1(BaseModel):
    id: str
    type: int
    timestamp: datetime
    message: Optional[str]
    data: Optional[dict]


class TopologyChildrenV1(BaseModel):
    type: str
    serial: str
    values: dict


class TopologyV1(BaseModel):
    version: int = 1
    serial: str
    type: str
    timestamp: datetime
    children: List[TopologyChildrenV1]


class TopologyChildrenV2(BaseModel):
    serial: str
    type: str
    values: dict
    children: List[TopologyChildrenV2]


TopologyChildrenV2.update_forward_refs()


class TopologyV2(BaseModel):
    version: int = 2
    timestamp: datetime
    values: dict
    children: List[TopologyChildrenV2]


class HeartbeatV1(BaseModel):
    timestamp: datetime
    ipAddress: str

    @validator("ipAddress")
    def ensure_ipaddress(cls, v):
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise NotAnIPAddressError(wrong_value=v)


class StateV1(BaseModel):
    version: str
    ipAddress: Optional[str]

    @validator("ipAddress")
    def ensure_ipaddress(cls, v):
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise NotAnIPAddressError(wrong_value=v)


class MqttStatusV1(BaseModel):
    connected: bool


class EmptyPayload:
    @staticmethod
    def parse_obj(msg: Optional[dict] = None):
        return EmptyPayload

    @staticmethod
    def json(*args, **kwargs) -> str:
        return ""


def get_model(model: dict) -> BaseModel:
    return globals()[model["name"]]


def model_to_json(model: dict, msg: dict) -> str:
    try:
        model = get_model(model)
    except KeyError:
        return json.dumps(msg)
    return model.parse_obj(msg).json(exclude_none=True)


def model_to_dict(model: dict, msg: str) -> dict:
    try:
        model = get_model(model)
    except KeyError:
        return json.loads(msg)
    return model.parse_raw(msg).dict(exclude_none=True)


if __name__ == "__main__":
    import datetime
    import pyaware.mqtt.transformations

    test_data = {
        "type": "imac-controller-master",
        "hello": "world",
        "timestamp": datetime.datetime(2020, 1, 8, 7, 21, 37, 512471),
        "values": [
            {
                "ethernet-mac-address": {
                    "latest": "00:50:c2:b4:41:d0",
                    "timestamp": datetime.datetime(2020, 1, 8, 7, 21, 37, 512471),
                    "samples": 1,
                }
            },
            {
                "ethernet-ip-mask": {
                    "latest": "255.255.255.0",
                    "timestamp": datetime.datetime(2020, 1, 8, 7, 21, 37, 512471),
                    "samples": 1,
                }
            },
            {
                "ethernet-ip-gateway": {
                    "latest": "10.1.1.1",
                    "timestamp": datetime.datetime(2020, 1, 8, 7, 21, 37, 512471),
                    "samples": 1,
                }
            },
            {
                "ethernet-ip-address": {
                    "latest": "10.1.1.10",
                    "timestamp": datetime.datetime(2020, 1, 8, 7, 21, 37, 512471),
                    "samples": 1,
                }
            },
            {
                "l1-line-speed": {
                    "latest": 500,
                    "timestamp": datetime.datetime(2020, 1, 8, 7, 21, 37, 512471),
                    "samples": 1,
                }
            },
            {
                "ethernet-dhcp": {
                    "latest": False,
                    "timestamp": datetime.datetime(2020, 1, 8, 7, 21, 37, 512471),
                    "samples": 1,
                }
            },
        ],
    }
    print(TelemetryV2.parse_obj(test_data).json(exclude_none=True))
    print(
        pyaware.mqtt.transformations.rename_keys(
            test_data, {"values": "parameterValues"}
        )
    )
    print(
        TelemetryV1.parse_obj(
            pyaware.mqtt.transformations.rename_keys(
                test_data, {"values": "parameterValues", "timestamp": "dateTime"}
            )
        ).json(exclude_none=True)
    )
