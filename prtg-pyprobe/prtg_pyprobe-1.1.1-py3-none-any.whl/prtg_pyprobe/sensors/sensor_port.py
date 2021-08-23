import asyncio
import logging
import socket
import time

from prtg_pyprobe.sensors.helpers import (
    SensorData,
    SensorDefinitionGroup,
    SensorDefinition,
)
from prtg_pyprobe.sensors.sensor import SensorBase


class Sensor(SensorBase):
    @property
    def name(self) -> str:
        return "Port"

    @property
    def kind(self) -> str:
        return "mpport"

    @property
    def definition(self) -> dict:
        port_def = SensorDefinition(
            name=self.name,
            kind=self.kind,
            description="Monitors the availability of a port on a target system",
            sensor_help="Monitors the availability of a port on a target system",
            tag="mpportsensor",
        )
        port_def_group_port_spec = SensorDefinitionGroup(name="portspecific", caption="Port specific")

        port_def_group_port_spec.add_field_timeout(60, 1, 900)
        port_def_group_port_spec.add_field(
            field_type="integer",
            name="targetport",
            caption="Port",
            required="1",
            default=110,
            minimum=1,
            maximum=65534,
            help="This is the port that you want to monitor if it's open or closed",
        )
        port_def.add_group(group=port_def_group_port_spec)
        return port_def.data

    async def work(self, task_data: dict, q: asyncio.Queue) -> None:
        port_data = SensorData(sensor_id=task_data["sensorid"])
        connection_timeout = int(task_data.get("timeout", 2))
        try:
            start_time = time.time()
            connection = asyncio.open_connection(host=task_data["host"], port=int(task_data["targetport"]))
            reader, writer = await asyncio.wait_for(connection, timeout=connection_timeout)
            writer.close()
            await writer.wait_closed()
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            port_data.message = f"OK Port {task_data['targetport']} available"
            port_data.add_channel(
                name="Available",
                mode="float",
                kind="TimeResponse",
                value=float(response_time),
            )
        except (TimeoutError, asyncio.TimeoutError, ConnectionError, socket.gaierror):
            port_data.error = "Exception"
            port_data.error_code = 1
            port_data.message = "Port check failed. See log for details"
            logging.exception(
                "There has been a connection error - host:{} - port:{}".format(
                    task_data["host"], task_data["targetport"]
                )
            )

        await q.put(port_data.data)
        q.task_done()
