import asyncio
import json
import logging
from json import JSONDecodeError
from sys import getsizeof

import httpx

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "HTTP"

    @property
    def kind(self) -> str:
        return "mphttp"

    @property
    def definition(self) -> dict:
        http_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors an HTTP target",
            sensor_help="Monitors the availability and response time of an HTTP target",
            tag="mphttpsensor",
        )
        http_def_group_target = SensorDefinitionGroup(name="targetinfo", caption="Target Information")
        http_def_group_target.add_field_timeout(10, 10, 900)
        http_def_group_target.add_field(
            field_type="edit",
            name="target",
            caption="HTTP Target",
            required="1",
            default="https://",
            help="Enter a valid HTTP target to monitor.  The format should be http(s)://xyz.com",
        )
        http_def_group_target.add_field(
            field_type="radio",
            name="request_type",
            caption="Request Type",
            required="1",
            options={"GET": "GET", "POST": "POST", "HEAD": "HEAD"},
            default="GET",
        )
        http_def_group_target.add_field(
            field_type="edit",
            name="headers",
            caption="HTTP Headers",
            default="",
            help="Enter HTTP Headers as dictionary. e.g. {'my header':'my value'}",
        ),
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
        http_def.add_group(group=http_def_group_target)
        return http_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        http_data = SensorData(sensor_id=task_data["sensorid"])
        # todo: basic auth
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

            http_data.add_channel(
                name="Response Time",
                mode="float",
                kind="TimeResponse",
                value=float(response.elapsed.microseconds / 1000),
            )
            http_data.add_channel(
                name="HTTP Status Code",
                mode="integer",
                kind="Custom",
                customunit="",
                value=response.status_code,
            )
            http_data.add_channel(
                name="Response Size",
                mode="float",
                kind="BytesFile",
                value=float(getsizeof(response.text)),
            )
            http_data.message = (
                f"HTTP target returned {response.status_code}, Request Type: {task_data['request_type']}"
            )

        except httpx.HTTPStatusError:
            http_data.error = "Exception"
            http_data.error_code = 1
            http_data.message = f"Status Code {response.status_code} not in acceptable list"
            logging.exception("HTTP Status did not match any in the acceptable list.")
        except httpx.HTTPError:
            http_data.error = "Exception"
            http_data.error_code = 1
            http_data.message = "HTTP request failed. See log for details"
            logging.exception("There was an error in httpx.")
        except JSONDecodeError:
            http_data.error = "Exception"
            http_data.error_code = 1
            http_data.message = "POST Data or HTTP Headers not in correct format."
            logging.exception("POST data or headers not in correct format")

        await q.put(http_data.data)
        q.task_done()
