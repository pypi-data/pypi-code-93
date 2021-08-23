import asyncio
import json
import logging
from json import JSONDecodeError
from typing import Any, Union

import httpx
import dpath.util

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "HTTP REST"

    @property
    def kind(self) -> str:
        return "mphttprest"

    @property
    def definition(self) -> dict:
        http_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors a REST response",
            sensor_help="Monitors the availability and REST response of an HTTP target.",
            tag="mphttprestsensor",
        )
        http_def_group_target = SensorDefinitionGroup(name="targetinfo", caption="Target Information")
        http_def_group_rest = SensorDefinitionGroup(name="restinfo", caption="REST Information")
        http_def_group_target.add_field_timeout(10, 10, 900)
        http_def_group_target.add_field(
            field_type="edit",
            name="target",
            caption="REST Target",
            required="1",
            default="https://",
            help="Enter a valid REST target to monitor.  The format should be http(s)://xyz.com",
        )
        http_def_group_target.add_field(
            field_type="radio",
            name="request_type",
            caption="Request Type",
            required="1",
            options={"GET": "GET", "POST": "POST"},
            default="GET",
        )
        http_def_group_target.add_field(
            field_type="edit",
            name="headers",
            caption="HTTP Headers",
            default="",
            help="Enter HTTP Headers as dictionary. e.g. {'my header':'my value'}",
        )
        http_def_group_target.add_field(
            field_type="edit",
            name="post_data",
            caption="POST Data",
            default="",
            help="Enter POST data as dictionary. e.g. {'my header':'my value'}. Only used when Request Type is POST",
        )
        http_def_group_target.add_field(
            field_type="edit",
            name="acceptable_status_codes",
            caption="Acceptable HTTP Status Codes",
            default="200",
            help="Enter acceptable HTTP Status codes. Format is comma separated. Leave empty for no filter.",
        )
        http_def_group_rest.add_field(
            field_type="edit",
            name="dpathselector",
            caption="Selector",
            default="",
            help="Enter a valid selector for a value in XPATH notation. "
            "Leave empty if you only want to measure the API response time.",
        )
        http_def_group_rest.add_field(
            field_type="radio",
            name="value_type",
            caption="Value Type",
            required="1",
            options={"float": "Float", "integer": "Integer"},
            default="float",
        )
        http_def.add_group(group=http_def_group_target)
        http_def.add_group(group=http_def_group_rest)
        return http_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        http_rest_data = SensorData(sensor_id=task_data["sensorid"])
        try:
            headers = None
            post_data = None
            acceptable_status_codes = []
            if task_data["acceptable_status_codes"]:
                acceptable_status_codes = [int(i) for i in task_data["acceptable_status_codes"].split(",")]
            if task_data["headers"]:
                try:
                    headers = json.loads(task_data["headers"])
                except JSONDecodeError:
                    raise
            if task_data["post_data"] and task_data["request_type"] == "POST":
                try:
                    post_data = json.loads(task_data["post_data"])
                except JSONDecodeError:
                    raise

            async with httpx.AsyncClient() as client:
                request = client.build_request(
                    method=task_data["request_type"],
                    url=task_data["target"],
                    headers=headers,
                    data=post_data,
                )
                response = await client.send(request=request, timeout=int(task_data["timeout"]))

            if len(acceptable_status_codes) and response.status_code not in acceptable_status_codes:
                raise httpx.HTTPStatusError("Status Code not in Filter list", request=request, response=response)

            response_dict = response.json()

            if not task_data["dpathselector"] == "":
                response_value = dpath.util.get(response_dict, task_data["dpathselector"])
                http_rest_data.add_channel(
                    name="REST return value",
                    mode=task_data["value_type"],
                    kind="Custom",
                    customunit="",
                    value=self.cast(response_value, task_data["value_type"]),
                )

            http_rest_data.add_channel(
                name="Response Time",
                mode="float",
                kind="TimeResponse",
                value=float(response.elapsed.microseconds / 1000),
            )
            http_rest_data.add_channel(
                name="HTTP Status Code",
                mode="integer",
                kind="Custom",
                customunit="",
                value=response.status_code,
            )
            http_rest_data.message = (
                f"HTTP target returned {response.status_code}, Request Type: {task_data['request_type']}"
            )

        except TypeError:
            http_rest_data.error = "Exception"
            http_rest_data.error_code = 1
            http_rest_data.message = "Response not in correct format."
            logging.exception("Response not in correct format")
        except JSONDecodeError:
            http_rest_data.error = "Exception"
            http_rest_data.error_code = 1
            http_rest_data.message = "POST Data, HTTP Headers or response not in correct format."
            logging.exception("POST data, headers or response not in correct format")
        except KeyError:
            http_rest_data.error = "Exception"
            http_rest_data.error_code = 1
            http_rest_data.message = "Element not found in response."
            logging.exception("Element not found in response. Xpath selector wrong?")
        except ValueError:
            http_rest_data.error = "Exception"
            http_rest_data.error_code = 1
            http_rest_data.message = "Query returned more than one element."
            logging.exception("Too much elements found in response. Xpath selector wrong?")
        except httpx.HTTPStatusError:
            http_rest_data.error = "Exception"
            http_rest_data.error_code = 1
            http_rest_data.message = f"Status Code {response.status_code} not in acceptable list"
            logging.exception("HTTP Status did not match any in the acceptable list.")
        except httpx.HTTPError:
            http_rest_data.error = "Exception"
            http_rest_data.error_code = 1
            http_rest_data.message = "HTTP request failed. See log for details"
            logging.exception("There was an error in httpx.")
        except CastException:
            http_rest_data.error = "Exception"
            http_rest_data.error_code = 1
            http_rest_data.message = "Could not cast the value xpath returned to the correct format."
            logging.exception("Casting error.")

        await q.put(http_rest_data.data)
        q.task_done()

    @staticmethod
    def cast(value: Any, target: str) -> Union[int, float]:
        try:
            value_cast = value
            if target == "integer":
                value_cast = int(value)
            elif target == "float":
                value_cast = float(value)
            return value_cast
        except ValueError:
            raise CastException(value=value, target=target)


class CastException(Exception):
    def __init__(self, value, target):
        self._message = f"Could not convert {value} to {target}"
        super().__init__(self._message)
