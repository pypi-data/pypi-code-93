import asyncio
import logging

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
        return "External IP (Probe)"

    @property
    def kind(self) -> str:
        return "mpexternalip"

    @property
    def definition(self) -> dict:
        ext_ip_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Returns the external ip address of the probe.",
            sensor_help="Returns the external ip address of the probe using the website checkip.amazonaws.com."
            "This is always the case even if added to a different device than the Probe Device.",
            tag="mpexternalipsensor",
        )
        ext_ip_def_settings = SensorDefinitionGroup(name="extipsettings", caption="External IP Settings")
        ext_ip_def_settings.add_field_timeout(30, 10, 300)
        ext_ip_def.add_group(group=ext_ip_def_settings)

        return ext_ip_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        ext_ip_data = SensorData(sensor_id=task_data["sensorid"])
        try:
            request_type = "GET"
            headers = None
            post_data = None
            url = "https://checkip.amazonaws.com/"

            async with httpx.AsyncClient() as client:
                request = client.build_request(
                    method=request_type,
                    url=url,
                    headers=headers,
                    data=post_data,
                )
                response = await client.send(request=request, timeout=int(task_data["timeout"]))

            ext_ip_data.add_channel(
                name="Response Time",
                mode="float",
                kind="TimeResponse",
                value=float(response.elapsed.microseconds / 1000),
            )
            response_text = response.text.replace("\n", "")
            ext_ip_data.message = f"Returned external IP: {response_text}"

        except httpx.HTTPError:
            ext_ip_data.error = "Exception"
            ext_ip_data.error_code = 1
            ext_ip_data.message = "External IP sensor failed. See log for details"
            logging.exception("There was an error in httpx.")

        await q.put(ext_ip_data.data)
        q.task_done()
